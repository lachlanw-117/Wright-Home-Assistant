"""Local checks of production Jinja functions and configuration invariants.

No HA installation, entities, device emulator or notification service is created.
Input values exercise pure functions, using the reviewed source configuration.
HA's real include loading/restoration and physical delivery require Pi acceptance.
"""
import datetime as dt
import ast
import importlib.util
import pathlib
import types
import unittest

import yaml
from jinja2 import FileSystemLoader, StrictUndefined
from jinja2.sandbox import SandboxedEnvironment
from jinja2.nativetypes import NativeEnvironment

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = yaml.safe_load((ROOT / 'attention/sources.yaml').read_text(encoding='utf8'))
BY_KEY = {source['key']: source for source in SOURCES}
AT = 1800000000
EVENT = dt.datetime.fromtimestamp(AT, dt.timezone.utc).isoformat()


def timestamp(value, default=0):
    if isinstance(value, (float, int)):
        return value
    try:
        return dt.datetime.fromisoformat(value).timestamp()
    except (ValueError, TypeError):
        return default


def as_function(macro):
    def call(*args, **kwargs):
        result = []
        macro(*args, returns=result.append, **kwargs)
        return result[0]
    return call


def functions(values=None, attrs=None, reported=None):
    values, attrs, reported = values or {}, attrs or {}, reported or {}
    env = SandboxedEnvironment(loader=FileSystemLoader(ROOT / 'custom_templates'),
                               undefined=StrictUndefined, extensions=['jinja2.ext.do'])
    env.filters['as_function'] = as_function
    env.globals.update(
        states=lambda entity: values.get(entity, 'unknown'),
        is_state=lambda entity, state: values.get(entity, 'unknown') == state,
        state_attr=lambda entity, name: attrs.get(entity, {}).get(name),
        as_timestamp=timestamp,
        is_number=lambda value: str(value).replace('.', '', 1).isdigit(),
        expand=lambda entity: [types.SimpleNamespace(last_reported=reported[entity])]
            if entity in reported else [],
    )
    module = env.get_template('household_attention.jinja').module
    return types.SimpleNamespace(**{name: as_function(getattr(module, name))
        for name in ['observe', 'advance', 'reconcile', 'recipient_route', 'visible']})


def evidence(observation='bad', identity='', quality='valid'):
    return dict(observation=observation, identity=identity, quality=quality,
                evidence=[], details=[], failure_at=0)


class LifecycleTests(unittest.TestCase):
    def test_duplicates_independent_recovery_and_recurrence(self):
        f = functions()
        fridge = BY_KEY['fridge_unavailable']
        dyson = BY_KEY['dyson_unavailable']
        first = f.advance(fridge, {}, evidence(), AT)
        duplicate = f.advance(fridge, first, evidence(), AT + 60)
        other = f.advance(dyson, {}, evidence(), AT + 30)
        self.assertEqual(first['first_detected'], duplicate['first_detected'])
        self.assertEqual(first['occurrence_id'], duplicate['occurrence_id'])
        recovered = f.advance(fridge, duplicate, evidence('good'), AT + 120)
        self.assertFalse(recovered['active'])
        self.assertTrue(other['active'])
        recurring = f.advance(fridge, recovered, evidence(), AT + 180)
        self.assertNotEqual(first['occurrence_id'], recurring['occurrence_id'])
        # Restoration reuses the exact same serialized record as the next input.
        restored = yaml.safe_load(yaml.safe_dump(recurring))
        again = f.advance(fridge, restored, evidence(), AT + 240)
        self.assertEqual(recurring['occurrence_id'], again['occurrence_id'])

    def test_unknown_does_not_resolve_or_invent_physical_fault(self):
        f, source = functions(), BY_KEY['fridge_unavailable']
        first = f.advance(source, {}, evidence(), AT)
        uncertain = f.advance(source, first, evidence('unknown', quality='unknown'), AT + 60)
        self.assertTrue(uncertain['active'])
        self.assertEqual(uncertain['last_valid_observation'], AT)
        self.assertEqual(uncertain['quality'], 'unknown')
        gap = f.advance(source, {}, evidence('unknown', quality='unknown'), AT)
        self.assertFalse(gap['active'])

    def test_fridge_either_channel_and_both_recover(self):
        source = BY_KEY['fridge_unavailable']
        plug, lg = source['entities']
        for values, expected in [({plug: 'unavailable', lg: '3'}, 'bad'),
                                 ({plug: 'on', lg: 'unavailable'}, 'bad'),
                                 ({plug: 'on', lg: 'unknown'}, 'unknown'),
                                 ({plug: 'on', lg: '3'}, 'good')]:
            with self.subTest(values=values):
                self.assertEqual(functions(values).observe(source, {}, AT)['observation'], expected)

    def test_off_is_normal_for_fan_but_disconnected_for_wan(self):
        for key, expected in [('dyson_unavailable', 'good'), ('internet_disconnected', 'bad')]:
            source = BY_KEY[key]
            f = functions({source['entities'][0]: 'off'})
            self.assertEqual(f.observe(source, {}, AT)['observation'], expected)

    def test_kiosk_wifi_requires_fresh_explicit_connection_evidence(self):
        source = BY_KEY['kiosk_wifi']
        entity = source['entities'][0]
        for value, age, observation, quality in [
            ('Wi-Fi', 60, 'good', 'valid'),
            ('Cellular', 60, 'bad', 'valid'),
            ('No Connection', 60, 'bad', 'valid'),
            ('Wi-Fi', 901, 'unknown', 'stale'),
            ('No Connection', 901, 'unknown', 'stale'),
            ('unknown', 60, 'unknown', 'unknown'),
            ('unavailable', 60, 'unknown', 'unknown'),
        ]:
            with self.subTest(value=value, age=age):
                result = functions({entity: value}, reported={entity: AT - age}).observe(source, {}, AT)
                self.assertEqual((result['observation'], result['quality']), (observation, quality))
        missing = functions().observe(source, {}, AT)
        self.assertEqual(missing['observation'], 'unknown')

    def test_wash_event_dedup_and_next_occurrence(self):
        f, source = functions(), BY_KEY['washing_finished']
        first = f.advance(source, {}, evidence(identity='2026-11-14T01:00:00Z'), AT)
        repeated = f.advance(source, first, evidence(identity='2026-11-14T01:00:00Z'), AT + 1)
        self.assertEqual(first['occurrence_id'], repeated['occurrence_id'])
        closed = dict(repeated, active=False, resolved_at=AT + 2)
        still_closed = f.advance(source, closed, evidence(identity='2026-11-14T01:00:00Z'), AT + 4)
        self.assertFalse(still_closed['active'])
        next_wash = f.advance(source, closed, evidence(identity='2026-11-15T01:00:00Z'), AT + 86400)
        self.assertTrue(next_wash['active'])
        self.assertNotEqual(first['occurrence_id'], next_wash['occurrence_id'])
        regressed = f.advance(source, next_wash, evidence(identity='2026-11-14T01:00:00Z'), AT + 86401)
        self.assertEqual(regressed['source_occurrence'], next_wash['source_occurrence'])
        self.assertEqual(regressed['occurrence_id'], next_wash['occurrence_id'])

    def test_backup_attempt_or_missing_success_never_resolves_failure(self):
        source = BY_KEY['backup_failed']
        event, success = source['entities']
        failure = {'failure_at': AT - 120}
        for kind, success_value, expected in [('in_progress', AT - 240, 'bad'),
                                             ('completed', 'unknown', 'bad'),
                                             ('completed', AT, 'good')]:
            with self.subTest(kind=kind, success=success_value):
                obs = functions({event: AT - 60, success: success_value},
                                {event: {'event_type': kind}}).observe(source, failure, AT)
                self.assertEqual(obs['observation'], expected)

    def test_grouped_updates_retain_unknown_remove_only_confirmed_clear(self):
        source = BY_KEY['upgrades_available']
        first_id, second_id = source['entities'][:2]
        values = {entity: 'off' for entity in source['entities']}
        values.update({first_id: 'on', second_id: 'on'})
        f = functions(values)
        observation = f.observe(source, {}, AT)
        record = f.advance(source, {}, observation, AT)
        self.assertEqual(len(record['details']), 2)
        self.assertEqual(record['kind'], 'attention')
        values.update({first_id: 'off', second_id: 'unknown'})
        observation = functions(values).observe(source, record, AT + 60)
        self.assertEqual([d['entity_id'] for d in observation['details']], [second_id])
        record = f.advance(source, record, observation, AT + 60)
        self.assertTrue(record['active'])
        values[second_id] = 'off'
        observation = functions(values).observe(source, record, AT + 120)
        self.assertFalse(f.advance(source, record, observation, AT + 120)['active'])


class RoutingTests(unittest.TestCase):
    def test_recipient_switch_is_independent_of_presence_and_dormant_helpers(self):
        key = 'washing_finished'
        for presence in ['home', 'not_home', 'unknown', 'unavailable']:
            values = {'person.lachlan': presence,
                      f'input_boolean.attention_{key}_lachlan_phone': 'on',
                      f'input_boolean.attention_{key}_lachlan_home': 'off',
                      f'input_boolean.attention_{key}_lachlan_away': 'off'}
            f = functions(values)
            self.assertTrue(f.recipient_route(key, 'lachlan'))
            self.assertFalse(f.recipient_route(key, 'nic'))
        values[f'input_boolean.attention_{key}_lachlan_phone'] = 'off'
        values[f'input_boolean.attention_{key}_lachlan_home'] = 'on'
        values[f'input_boolean.attention_{key}_lachlan_away'] = 'on'
        self.assertFalse(functions(values).recipient_route(key, 'lachlan'))

    def test_delay_consumed_even_disabled_no_preference_backlog(self):
        source = dict(BY_KEY['fridge_unavailable'], delivery_delay_seconds=600)
        plug, lg = source['entities']
        values = {plug: 'unavailable', lg: '3', 'input_boolean.attention_routing_enabled': 'on'}
        f = functions(values)
        records = f.reconcile([source], {}, AT)
        records = f.reconcile([source], records, AT + 599)
        self.assertFalse(records[source['key']]['phone_evaluated'])
        records = f.reconcile([source], records, AT + 600)
        self.assertTrue(records[source['key']]['phone_evaluated'])
        self.assertEqual(records[source['key']]['phone_routes'], [])
        values[f'input_boolean.attention_{source["key"]}_lachlan_phone'] = 'on'
        records = functions(values).reconcile([source], records, AT + 660)
        self.assertEqual(records[source['key']]['phone_routes'], [])

    def test_new_eligible_occurrence_routes_once_and_pause_expires(self):
        source = dict(BY_KEY['fridge_unavailable'], delivery_delay_seconds=0)
        key = source['key']
        values = {source['entities'][0]: 'unavailable', source['entities'][1]: '3',
                  'input_boolean.attention_routing_enabled': 'on',
                  f'input_boolean.attention_{key}_lachlan_phone': 'on',
                  f'input_boolean.attention_{key}_tv': 'on'}
        f = functions(values)
        records = f.reconcile([source], {}, AT)
        self.assertEqual(records[key]['phone_routes'], ['lachlan'])
        records = f.reconcile([source], records, AT + 60)
        self.assertEqual(records[key]['phone_routes'], [])
        values[f'input_datetime.attention_{key}_pause_until'] = AT + 120
        f = functions(values)
        paused = f.reconcile([source], {}, AT)
        self.assertTrue(paused[key]['active'])
        self.assertEqual(paused[key]['phone_routes'], [])
        self.assertEqual(f.visible(paused, 'tv', AT), [])
        self.assertEqual(len(f.visible(paused, 'tv', AT + 121)), 1)
        self.assertEqual(f.reconcile([source], paused, AT + 121)[key]['phone_routes'], [])

    def test_unreviewed_policy_legacy_and_disabled_router_never_send(self):
        source = dict(BY_KEY['fridge_unavailable'], delivery_delay_seconds=None)
        f = functions({source['entities'][0]: 'unavailable', source['entities'][1]: '3'})
        records = f.reconcile([source], {}, AT)
        self.assertFalse(records[source['key']]['phone_evaluated'])
        washing = dict(BY_KEY['washing_finished'], delivery_delay_seconds=0, legacy_delivery=True)
        values = {washing['entities'][0]: '2026-11-14T01:00:00Z',
                  'input_boolean.attention_washing_finished_lachlan_phone': 'on'}
        f = functions(values, {washing['entities'][0]: {'event_type': 'washing_is_complete'}})
        records = f.reconcile([washing], {}, AT)
        self.assertEqual(records[washing['key']]['phone_routes'], [])

    def test_one_shot_washing_resolves_only_matching_accepted_routes(self):
        source = BY_KEY['washing_finished']
        key = source['key']
        event = source['entities'][0]
        values = {event: EVENT,
                  'input_boolean.attention_routing_enabled': 'on',
                  'input_boolean.attention_washing_finished_lachlan_phone': 'on',
                  'input_boolean.attention_washing_finished_nic_phone': 'on',
                  'person.lachlan': 'not_home', 'person.nic': 'unknown'}
        f = functions(values, {event: {'event_type': 'washing_is_complete'}})
        records = f.reconcile([source], {}, AT)
        occurrence = records[key]['occurrence_id']
        self.assertEqual(records[key]['phone_routes'], ['lachlan', 'nic'])
        receipt = dict(key=key, occurrence_id='earlier-event', recipient='lachlan')
        records = f.reconcile([source], records, AT + 1, delivery=receipt)
        self.assertEqual(records[key]['delivered_to'], [])
        receipt['occurrence_id'] = occurrence
        records = f.reconcile([source], records, AT + 2, delivery=receipt)
        self.assertTrue(records[key]['active'])
        receipt['recipient'] = 'nic'
        records = f.reconcile([source], records, AT + 3, delivery=receipt)
        self.assertFalse(records[key]['active'])
        self.assertEqual(records[key]['delivery_state'], 'accepted')
        self.assertEqual(records[key]['resolved_at'], AT + 3)
        again = f.reconcile([source], records, AT + 60)
        self.assertFalse(again[key]['active'])
        self.assertEqual(again[key]['phone_routes'], [])

    def test_washing_disabled_recipient_has_no_later_backlog(self):
        source = BY_KEY['washing_finished']
        key, event = source['key'], source['entities'][0]
        values = {event: EVENT,
                  'input_boolean.attention_routing_enabled': 'on',
                  'input_boolean.attention_washing_finished_lachlan_phone': 'off',
                  'person.lachlan': 'not_home'}
        f = functions(values, {event: {'event_type': 'washing_is_complete'}},
                      {'device_tracker.big_lws_iphone_14': AT})
        records = f.reconcile([source], {}, AT)
        self.assertFalse(records[key]['active'])
        self.assertEqual(records[key]['delivery_state'], 'suppressed')
        values['input_boolean.attention_washing_finished_lachlan_phone'] = 'on'
        again = functions(values, {event: {'event_type': 'washing_is_complete'}},
                          {'device_tracker.big_lws_iphone_14': AT + 60}).reconcile(
                              [source], records, AT + 60)
        self.assertEqual(again[key]['phone_routes'], [])

    def test_washing_dispatch_timeout_is_not_a_claim_of_success(self):
        source = BY_KEY['washing_finished']
        key, event = source['key'], source['entities'][0]
        values = {event: EVENT,
                  'input_boolean.attention_routing_enabled': 'on',
                  'input_boolean.attention_washing_finished_lachlan_phone': 'on',
                  'person.lachlan': 'home'}
        f = functions(values, {event: {'event_type': 'washing_is_complete'}},
                      {'device_tracker.big_lws_iphone_14': AT})
        records = f.reconcile([source], {}, AT)
        self.assertTrue(records[key]['active'])
        records = f.reconcile([source], records, AT + 300)
        self.assertFalse(records[key]['active'])
        self.assertEqual(records[key]['delivery_state'], 'unconfirmed')

    def test_old_wash_event_is_retained_without_backlog_or_new_tv_card(self):
        source = BY_KEY['washing_finished']
        key, event = source['key'], source['entities'][0]
        values = {event: EVENT,
                  'input_boolean.attention_routing_enabled': 'on',
                  'input_boolean.attention_washing_finished_lachlan_phone': 'on',
                  'input_boolean.attention_washing_finished_tv': 'on',
                  'person.lachlan': 'home'}
        f = functions(values, {event: {'event_type': 'washing_is_complete'}},
                      {'device_tracker.big_lws_iphone_14': AT + 3600})
        records = f.reconcile([source], {}, AT + 3600)
        self.assertFalse(records[key]['active'])
        self.assertEqual(records[key]['phone_routes'], [])
        self.assertEqual(f.visible(records, 'tv', AT + 3600), [])

    def test_unknown_at_deadline_waits_for_confirmed_failure(self):
        source = dict(BY_KEY['dyson_unavailable'])
        key, entity = source['key'], source['entities'][0]
        values = {entity: 'unavailable', 'input_boolean.attention_routing_enabled': 'on',
                  f'input_boolean.attention_{key}_lachlan_phone': 'on'}
        records = functions(values).reconcile([source], {}, AT)
        values[entity] = 'unknown'
        records = functions(values).reconcile([source], records, AT + 900)
        self.assertTrue(records[key]['active'])
        self.assertFalse(records[key]['phone_evaluated'])
        values[entity] = 'unavailable'
        records = functions(values).reconcile([source], records, AT + 960)
        self.assertEqual(records[key]['phone_routes'], ['lachlan'])


class ConfigurationTests(unittest.TestCase):
    def test_health_uses_only_fault_sources_and_coverage_is_separate(self):
        package = yaml.load((ROOT / 'packages/household_attention.yaml').read_text(encoding='utf8'),
                            Loader=yaml.BaseLoader)
        attrs = package['template'][1]['sensor'][0]['attributes']
        records = {
            'fridge': dict(kind='fault', category='appliances', active=False, quality='valid'),
            'washing': dict(kind='event', category='chores', active=True, quality='valid'),
            'updates': dict(kind='attention', category='maintenance', active=True, quality='unknown'),
        }
        env = NativeEnvironment()
        env.globals['state_attr'] = lambda entity, attribute: records
        def render(name):
            result = env.from_string(attrs[name]).render()
            if isinstance(result, str):
                try:
                    return ast.literal_eval(result.strip())
                except (ValueError, SyntaxError):
                    return result.strip()
            return result
        self.assertEqual(render('health'), 'healthy')
        self.assertEqual(render('coverage'), 'incomplete')
        self.assertEqual(render('fault_count'), 0)
        self.assertEqual(render('category_health')['chores'], 'not_applicable')
        records['fridge']['quality'] = 'unknown'
        self.assertEqual(render('health'), 'incomplete')
        records['fridge']['active'] = True
        self.assertEqual(render('health'), 'faults')
        self.assertEqual(render('fault_count'), 1)

    def test_current_profile_and_controls_park_the_presence_split(self):
        for key in ['internet_disconnected', 'washer_unavailable', 'backup_failed', 'washer_cleaning']:
            routes = BY_KEY[key]['starting_destinations']
            self.assertIn('lachlan_phone', routes)
            self.assertNotIn('nic_phone', routes)
        self.assertEqual(set(BY_KEY['washing_finished']['starting_destinations']),
                         {'dashboard', 'tv', 'lachlan_phone', 'nic_phone'})
        dashboard = yaml.safe_load((ROOT / 'dashboards/household_attention.yaml').read_text(encoding='utf8'))
        for card in dashboard['views'][2]['cards']:
            for row in card.get('entities', []):
                entity = row['entity'] if isinstance(row, dict) else row
                self.assertFalse(entity.endswith(('_home', '_away')))
        package = (ROOT / 'packages/household_attention.yaml').read_text(encoding='utf8')
        self.assertNotIn('device_tracker.', package)
        self.assertNotIn('attention/policy.yaml', package)

    def test_inline_template_syntax(self):
        env = SandboxedEnvironment(extensions=['jinja2.ext.do'])
        env.filters['as_function'] = as_function

        def compile_templates(node):
            if isinstance(node, dict):
                for value in node.values():
                    compile_templates(value)
            elif isinstance(node, list):
                for value in node:
                    compile_templates(value)
            elif isinstance(node, str) and ('{{' in node or '{%' in node):
                env.from_string(node)

        for name in ['packages/household_attention.yaml', 'dashboards/household_attention.yaml']:
            # BaseLoader parses tags as text and never resolves includes/secrets.
            compile_templates(yaml.load((ROOT / name).read_text(encoding='utf8'), Loader=yaml.BaseLoader))

    def test_generated_files_and_restored_preferences(self):
        spec = importlib.util.spec_from_file_location('builder', ROOT / 'tools/build_attention_controls.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name, expected in module.outputs().items():
            self.assertEqual((ROOT / name).read_text(encoding='utf8'), expected)
        controls = yaml.safe_load((ROOT / 'attention/delivery_controls.yaml').read_text(encoding='utf8'))
        self.assertEqual(len(controls), len(SOURCES) * 8 + 2)
        self.assertTrue(all('initial' not in helper for helper in controls.values()))

    def test_no_excluded_device_or_dynamic_whole_instance_scan(self):
        entities = {entity for source in SOURCES for entity in source['entities']}
        self.assertFalse(any('dads_desk' in entity for entity in entities))
        watched = yaml.safe_load((ROOT / 'attention/watched_entities.yaml').read_text(encoding='utf8'))
        self.assertEqual(set(watched), entities)
        keys = [source['key'] for source in SOURCES]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == '__main__':
    unittest.main()
