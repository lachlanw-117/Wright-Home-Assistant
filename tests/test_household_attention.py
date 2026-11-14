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
POLICY = yaml.safe_load((ROOT / 'attention/policy.yaml').read_text(encoding='utf8'))
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
        for name in ['observe', 'advance', 'reconcile', 'recipient_route', 'visible', 'presence']})


def evidence(observation='bad', identity='', quality='valid'):
    return dict(observation=observation, identity=identity, quality=quality,
                evidence=[], details=[], failure_at=0)


def presence_inputs():
    """Pure function inputs; network strings are test sentinels, not household data."""
    values = {'input_boolean.household_attention_presence_ready': 'on',
              'input_datetime.household_attention_presence_started_at': AT - 300,
              'input_boolean.attention_presence_routes_migrated': 'on'}
    attrs, reported = {}, {}
    for person in POLICY['people'].values():
        values[person['tracker']] = 'home'
        values[person['ssid']] = 'test-network-a'
        attrs[person['tracker']] = {'source_type': 'gps'}
        reported.update({entity: AT - 20 for entity in person.values()})
    values.update({POLICY['kiosk']['ssid']: 'test-network-a',
                   POLICY['kiosk']['connection_type']: 'Wi-Fi'})
    reported.update({entity: AT - 20 for entity in POLICY['kiosk'].values()})
    return values, attrs, reported


class PresenceTests(unittest.TestCase):
    def test_fresh_home_away_and_other_zone(self):
        values, attrs, reported = presence_inputs()
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'home')
        for state in ['not_home', 'another_zone']:
            values[POLICY['people']['lachlan']['tracker']] = state
            values[POLICY['people']['lachlan']['ssid']] = 'Not Connected'
            self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'away')

    def test_wifi_confirms_home_but_never_away(self):
        values, attrs, reported = presence_inputs()
        tracker, ssid = POLICY['people']['lachlan'].values()
        values[tracker] = 'unknown'
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'home')
        for value in ['Not Connected', 'test-network-b', 'unknown', 'unavailable']:
            values[ssid] = value
            self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'unknown')
        # GPS home remains valid even with Wi-Fi disabled or on a different network.
        values.update({tracker: 'home', ssid: 'test-network-b'})
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'home')

    def test_conflicting_evidence_is_unknown(self):
        values, attrs, reported = presence_inputs()
        values[POLICY['people']['lachlan']['tracker']] = 'not_home'
        result = functions(values, attrs, reported).presence('lachlan', POLICY, AT)
        self.assertEqual(result['status'], 'unknown')
        self.assertIn('disagree', result['reason'])

    def test_15_minute_boundary_expiry_and_future_timestamps(self):
        values, attrs, reported = presence_inputs()
        values['input_datetime.household_attention_presence_started_at'] = AT - 2000
        for entity in reported:
            reported[entity] = AT - 900
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'home')
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT + 1)['status'], 'unknown')
        for entity in reported:
            reported[entity] = AT + 1
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'unknown')

    def test_restart_needs_session_and_post_start_phone_reports(self):
        values, attrs, reported = presence_inputs()
        values['input_boolean.household_attention_presence_ready'] = 'off'
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'unknown')
        values['input_boolean.household_attention_presence_ready'] = 'on'
        values['input_datetime.household_attention_presence_started_at'] = AT - 10
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'unknown')
        tracker = POLICY['people']['lachlan']['tracker']
        reported[tracker] = AT - 5
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'home')
        reported[tracker] = AT - 10  # Equality is not a post-start sample.
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'unknown')

    def test_kiosk_absent_stale_or_not_wifi_does_not_invent_home(self):
        values, attrs, reported = presence_inputs()
        tracker = POLICY['people']['lachlan']['tracker']
        values[tracker] = 'unknown'
        reference = POLICY['kiosk']['ssid']
        reported.pop(reference)
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'unknown')
        reported[reference] = AT - 20
        values[POLICY['kiosk']['connection_type']] = 'Cellular'
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'unknown')
        values[tracker] = 'not_home'
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'away')

    def test_non_gps_or_missing_policy_is_unknown_without_wifi(self):
        values, attrs, reported = presence_inputs()
        values[POLICY['people']['lachlan']['ssid']] = 'Not Connected'
        attrs[POLICY['people']['lachlan']['tracker']]['source_type'] = 'router'
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT)['status'], 'unknown')
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', None, AT)['status'], 'unknown')

    def test_presence_output_contains_only_classification_and_ages(self):
        values, attrs, reported = presence_inputs()
        result = functions(values, attrs, reported).presence('lachlan', POLICY, AT)
        self.assertEqual(set(result), {'status', 'reason', 'gps_age_seconds', 'wifi_age_seconds', 'kiosk_age_seconds'})
        self.assertNotIn('test-network-a', repr(result))

    def test_all_switch_combinations_and_independent_people(self):
        key = 'washing_finished'
        for observation in ['home', 'away', 'unknown']:
            for home in [False, True]:
                for away in [False, True]:
                    with self.subTest(observation=observation, home=home, away=away):
                        values, attrs, reported = presence_inputs()
                        tracker, ssid = POLICY['people']['lachlan'].values()
                        values.update({tracker: {'home': 'home', 'away': 'not_home', 'unknown': 'unknown'}[observation],
                                       ssid: 'Not Connected',
                                       f'input_boolean.attention_{key}_lachlan_home': 'on' if home else 'off',
                                       f'input_boolean.attention_{key}_lachlan_away': 'on' if away else 'off',
                                       f'input_boolean.attention_{key}_lachlan_phone': 'off'})
                        f = functions(values, attrs, reported)
                        expected = (home and away) or (home and observation == 'home') or (away and observation == 'away')
                        self.assertEqual(f.recipient_route(key, 'lachlan', policy=POLICY, at=AT), expected)
                        self.assertFalse(f.recipient_route(key, 'nic', policy=POLICY, at=AT))

    def test_always_bypasses_unknown_even_before_boot_ready(self):
        values = {'input_boolean.attention_presence_routes_migrated': 'on',
                  'input_boolean.attention_fridge_unavailable_lachlan_home': 'on',
                  'input_boolean.attention_fridge_unavailable_lachlan_away': 'on'}
        self.assertTrue(functions(values).recipient_route('fridge_unavailable', 'lachlan', at=AT))

    def test_presence_changes_and_opt_in_do_not_replay_consumed_wash(self):
        source = BY_KEY['washing_finished']
        values, attrs, reported = presence_inputs()
        values.update({source['entities'][0]: EVENT, 'input_boolean.attention_routing_enabled': 'on',
                       'input_boolean.attention_washing_finished_lachlan_home': 'on',
                       POLICY['people']['lachlan']['tracker']: 'not_home',
                       POLICY['people']['lachlan']['ssid']: 'Not Connected'})
        attrs[source['entities'][0]] = {'event_type': 'washing_is_complete'}
        record = functions(values, attrs, reported).reconcile([source], {}, AT, policy=POLICY)
        self.assertEqual(record[source['key']]['delivery_state'], 'suppressed')
        values[POLICY['people']['lachlan']['tracker']] = 'home'
        record = functions(values, attrs, reported).reconcile([source], record, AT + 60, policy=POLICY)
        self.assertEqual(record[source['key']]['phone_routes'], [])
        self.assertFalse(record[source['key']]['active'])

    def test_dispatch_recheck_observes_presence_pause_and_route_changes(self):
        source = BY_KEY['washing_finished']
        values, attrs, reported = presence_inputs()
        values.update({source['entities'][0]: EVENT, 'input_boolean.attention_routing_enabled': 'on',
                       'input_boolean.attention_washing_finished_lachlan_home': 'on'})
        attrs[source['entities'][0]] = {'event_type': 'washing_is_complete'}
        record = functions(values, attrs, reported).reconcile([source], {}, AT, policy=POLICY)[source['key']]
        self.assertEqual(record['phone_routes'], ['lachlan'])
        package = yaml.load((ROOT/'packages/household_attention.yaml').read_text(encoding='utf8'), Loader=yaml.BaseLoader)
        condition = next(step['value_template'] for step in package['script']['household_attention_send_phone']['sequence']
                         if step.get('condition') == 'template')
        env = NativeEnvironment(extensions=['jinja2.ext.do'])
        env.filters['as_function'] = as_function
        def allowed(at):
            env.globals.update(record=record, recipient='lachlan', attention_policy=POLICY,
                states=lambda entity: values.get(entity, 'unknown'), as_timestamp=timestamp,
                now=lambda: at)
            # Compile the actual dispatch condition with the production macro import.
            env.loader = FileSystemLoader(ROOT/'custom_templates')
            env.globals.update(is_state=lambda entity, state: values.get(entity, 'unknown') == state,
                state_attr=lambda entity, name: attrs.get(entity, {}).get(name),
                expand=lambda entity: [types.SimpleNamespace(last_reported=reported[entity])]
                    if entity in reported else [])
            result = env.from_string(condition).render()
            return ast.literal_eval(result.strip()) if isinstance(result, str) else result
        self.assertTrue(allowed(AT))
        values[POLICY['people']['lachlan']['tracker']] = 'not_home'
        values[POLICY['people']['lachlan']['ssid']] = 'Not Connected'
        self.assertFalse(allowed(AT))
        values['input_boolean.attention_washing_finished_lachlan_away'] = 'on'
        self.assertTrue(allowed(AT))
        values['input_datetime.attention_washing_finished_pause_until'] = AT + 10
        self.assertFalse(allowed(AT))
        values['input_datetime.attention_washing_finished_pause_until'] = AT - 10
        values['input_boolean.attention_washing_finished_lachlan_away'] = 'off'
        values[POLICY['people']['lachlan']['tracker']] = 'home'
        self.assertFalse(allowed(AT + 901))


class PresenceMigrationTests(unittest.TestCase):
    def script(self):
        return yaml.load((ROOT/'packages/household_attention.yaml').read_text(encoding='utf8'),
                         Loader=yaml.BaseLoader)['script']['household_attention_migrate_presence_routes']['sequence']

    def render(self, template, values):
        env = NativeEnvironment(undefined=StrictUndefined)
        env.globals.update(attention_sources=SOURCES,
                           states=lambda entity: values.get(entity, 'unknown'),
                           is_state=lambda entity, state: values.get(entity, 'unknown') == state)
        result = env.from_string(template).render()
        return ast.literal_eval(result.strip()) if isinstance(result, str) else result

    def test_exact_copy_keeps_all_48_recipient_choices_and_survives_missing_presence(self):
        sequence = self.script()
        variables = next(step['variables'] for step in sequence if 'enabled' in step.get('variables', {}))
        conditions = [step['value_template'] for step in sequence if step.get('condition') == 'template']
        self.assertEqual(sequence[0]['entity_id'], 'input_boolean.attention_presence_routes_migrated')
        self.assertEqual(sequence[0]['state'], 'off')
        self.assertEqual(sequence[-1]['target']['entity_id'], 'input_boolean.attention_presence_routes_migrated')
        values = {}
        for index, source in enumerate(SOURCES):
            for offset, person in enumerate(['lachlan', 'nic']):
                prefix = f'input_boolean.attention_{source["key"]}_{person}'
                values[prefix+'_phone'] = 'on' if (index+offset) % 2 else 'off'
                values[prefix+'_home'] = 'off'
                values[prefix+'_away'] = 'on'  # Old dormant values must not dictate migration.
        self.assertTrue(self.render(conditions[0], values))
        enabled = self.render(variables['enabled'], values)
        disabled = self.render(variables['disabled'], values)
        self.assertEqual(len(enabled)+len(disabled), 96)
        self.assertFalse(set(enabled) & set(disabled))
        for entity in enabled:
            values[entity] = 'on'
        for entity in disabled:
            values[entity] = 'off'
        self.assertTrue(self.render(conditions[-1], values))
        values['input_boolean.attention_presence_routes_migrated'] = 'on'
        f = functions(values)
        for source in SOURCES:
            for person in ['lachlan','nic']:
                self.assertEqual(f.recipient_route(source['key'], person, policy=POLICY, at=AT),
                                 values[f'input_boolean.attention_{source["key"]}_{person}_phone'] == 'on')

    def test_missing_helpers_or_concurrent_edit_prevent_commit(self):
        sequence = self.script()
        conditions = [step['value_template'] for step in sequence if step.get('condition') == 'template']
        values = {f'input_boolean.attention_{source["key"]}_{person}_{suffix}': 'off'
                  for source in SOURCES for person in ['lachlan','nic'] for suffix in ['phone','home','away']}
        self.assertTrue(self.render(conditions[0], values))
        self.assertTrue(self.render(conditions[-1], values))
        key = 'input_boolean.attention_washing_finished_lachlan_phone'
        values[key] = 'on'
        self.assertFalse(self.render(conditions[-1], values))
        values.pop(key)
        self.assertFalse(self.render(conditions[0], values))

    def test_boot_guard_rejects_same_second_restored_samples(self):
        package = yaml.load((ROOT/'packages/household_attention.yaml').read_text(encoding='utf8'), Loader=yaml.BaseLoader)
        startup = next(rule for rule in package['automation'] if rule['id'] == 'household_attention_presence_session')
        actions = startup['actions']
        self.assertEqual(actions[0]['target']['entity_id'], 'input_datetime.household_attention_presence_started_at')
        self.assertEqual(actions[1]['target']['entity_id'], 'input_boolean.household_attention_presence_ready')
        env = NativeEnvironment()
        env.globals.update(now=lambda: AT + 0.35, as_timestamp=timestamp)
        marker = env.from_string(actions[0]['data']['timestamp']).render()
        self.assertEqual(marker, AT + 1)
        values, attrs, reported = presence_inputs()
        values['input_datetime.household_attention_presence_started_at'] = marker
        for entity in reported:
            reported[entity] = AT + 0.1
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT + 2)['status'], 'unknown')
        reported[POLICY['people']['lachlan']['tracker']] = AT + 1.5
        self.assertEqual(functions(values, attrs, reported).presence('lachlan', POLICY, AT + 2)['status'], 'home')


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

    def test_living_room_pairs_detect_member_loss_and_require_complete_recovery(self):
        for name, member_prefix in [('tv', 'tv'), ('dining', 'dining_table'),
                                    ('hoop', 'basketball_hoop')]:
            source = BY_KEY[f'living_room_{name}_lights_unavailable']
            members = source['entities']
            self.assertEqual(set(members), {
                f'light.living_room_{member_prefix}_light_1',
                f'light.living_room_{member_prefix}_light_2',
            })
            self.assertEqual(set(source['starting_destinations']), {'dashboard', 'tv'})
            values = {entity: 'off' for entity in members}
            # Aggregate entities can look normal while a physical bulb is missing.
            values['light.living_room_living_room_lights'] = 'off'
            values[f'light.living_room_{member_prefix}_light'] = 'off'
            self.assertEqual(functions(values).observe(source, {}, AT)['observation'], 'good')
            for member in members:
                with self.subTest(pair=name, member=member):
                    changed = dict(values, **{member: 'unavailable'})
                    records = functions(changed).reconcile([source], {}, AT)
                    first = records[source['key']]
                    self.assertTrue(first['active'])
                    self.assertEqual(len(first['evidence']), 2)
                    changed.update({entity: 'unavailable' for entity in members})
                    records = functions(changed).reconcile([source], records, AT + 60)
                    self.assertEqual(len(records), 1)
                    self.assertEqual(records[source['key']]['occurrence_id'], first['occurrence_id'])
                    changed = dict(values, **{member: 'unknown'})
                    records = functions(changed).reconcile([source], records, AT + 120)
                    self.assertTrue(records[source['key']]['active'])
                    self.assertEqual(records[source['key']]['quality'], 'unknown')
                    records = functions(values).reconcile([source], records, AT + 180)
                    self.assertFalse(records[source['key']]['active'])
                    changed = dict(values, **{member: 'unavailable'})
                    again = functions(changed).reconcile([source], records, AT + 240)
                    self.assertNotEqual(again[source['key']]['occurrence_id'], first['occurrence_id'])

    def test_living_room_pairs_recover_independently(self):
        sources = [BY_KEY[f'living_room_{name}_lights_unavailable']
                   for name in ['tv', 'dining', 'hoop']]
        values = {entity: 'unavailable' for source in sources for entity in source['entities']}
        records = functions(values).reconcile(sources, {}, AT)
        self.assertEqual(sum(record['active'] for record in records.values()), 3)
        values.update({entity: 'off' for entity in sources[0]['entities']})
        records = functions(values).reconcile(sources, records, AT + 60)
        self.assertFalse(records[sources[0]['key']]['active'])
        self.assertTrue(records[sources[1]['key']]['active'])
        self.assertTrue(records[sources[2]['key']]['active'])

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

    def test_six_controls_keep_plain_phone_values_hidden(self):
        for key in ['internet_disconnected', 'washer_unavailable', 'backup_failed', 'washer_cleaning']:
            routes = BY_KEY[key]['starting_destinations']
            self.assertIn('lachlan_phone', routes)
            self.assertNotIn('nic_phone', routes)
        self.assertEqual(set(BY_KEY['washing_finished']['starting_destinations']),
                         {'dashboard', 'tv', 'lachlan_phone', 'nic_phone'})
        dashboard = yaml.safe_load((ROOT / 'dashboards/household_attention.yaml').read_text(encoding='utf8'))
        def cards_in(cards):
            for card in cards:
                yield card
                yield from cards_in(card.get('cards', []))
        for card in cards_in(dashboard['views'][2]['cards']):
            for row in card.get('entities', []):
                entity = row['entity'] if isinstance(row, dict) else row
                self.assertFalse(entity.endswith('_phone'))
        stacks = [card for card in dashboard['views'][2]['cards'] if card['type'] == 'vertical-stack']
        self.assertEqual(len(stacks), 24)
        for stack in stacks:
            rows = stack['cards'][1]['entities']
            self.assertEqual(len(rows), 7)
            key = rows[-1]['entity'].removeprefix('input_datetime.attention_').removesuffix('_pause_until')
            self.assertEqual({row['entity'] for row in rows[:-1]},
                {f'input_boolean.attention_{key}_{suffix}' for suffix in
                 ['dashboard', 'tv', 'lachlan_home', 'lachlan_away', 'nic_home', 'nic_away']})
        package = (ROOT / 'packages/household_attention.yaml').read_text(encoding='utf8')
        self.assertNotIn('device_tracker.', package)
        self.assertIn('attention/policy.yaml', package)

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
        self.assertEqual(len(controls), 196)
        for source in SOURCES:
            key = source['key']
            for suffix in ['dashboard', 'tv', 'lachlan_phone', 'nic_phone']:
                self.assertIn(f'attention_{key}_{suffix}', controls)
            for suffix in ['lachlan_home', 'lachlan_away', 'nic_home', 'nic_away']:
                self.assertIn(f'attention_{key}_{suffix}', controls)
        for key, helper in controls.items():
            if key == 'household_attention_presence_ready':
                self.assertIs(helper['initial'], False)
            else:
                self.assertNotIn('initial', helper)

    def test_grouped_switch_mappings_and_new_defaults(self):
        expected = {
            'kitchen_lights': ['light.bench', 'light.dish_rack', 'light.pantry', 'light.stove'],
            'kitchen_entrance': ['light.entrance'],
            'ensuite_lights': ['light.toilet', 'light.mirror', 'light.shower'],
            'bathroom_lights': ['light.centre', 'light.sink'],
            'main_bedroom_lights': ['light.in_front_of_sink', 'light.living_room_tradfri'],
            'kids_bedroom_lights': ['light.kids_room_kids_bedroom_light_1', 'light.kids_room_kids_bedroom_light_2'],
            'laundry_light': ['light.laundry_led_strip'],
            'black_fan': ['fan.living_room_black_fan'],
            'kids_tv_plug': ['switch.kids_room_kids_tv_plug'],
            'internet_plug': ['switch.internet_plug'],
            'kiosk_charger': ['switch.living_room_kiosk_phone_charger'],
            'air_conditioner_fingerbot': ['switch.split_system_finger_bot'],
        }
        self.assertEqual(len(SOURCES), 24)
        for prefix, entities in expected.items():
            source = BY_KEY[prefix + '_unavailable']
            self.assertEqual(source['entities'], entities)
            self.assertEqual(source['starting_destinations'], ['dashboard', 'tv'])
            self.assertEqual(source['delivery_delay_seconds'], 900)

    def test_short_names_do_not_reset_occurrences_or_notification_titles(self):
        source = BY_KEY['living_room_tv_lights_unavailable']
        values = {entity: 'unavailable' for entity in source['entities']}
        values.update({'input_boolean.attention_routing_enabled': 'on',
                       'input_boolean.attention_living_room_tv_lights_unavailable_lachlan_phone': 'on'})
        f = functions(values)
        records = f.reconcile([source], {}, AT)
        records = f.reconcile([source], records, AT + 900)
        old = records[source['key']]
        renamed = dict(source, display_name='TV lights renamed')
        record = f.reconcile([renamed], records, AT + 960)[source['key']]
        self.assertEqual(record['display_name'], 'TV lights renamed')
        self.assertEqual(record['title'], source['title'])
        for field in ['occurrence_id', 'first_detected', 'phone_evaluated', 'selected_phone_routes']:
            self.assertEqual(record[field], old[field])
        self.assertEqual(record['phone_routes'], [])
        legacy = dict(source)
        legacy.pop('display_name')
        self.assertEqual(f.reconcile([legacy], records, AT + 960)[source['key']]['display_name'], source['title'])

    def test_dashboard_names_fall_back_and_distinguish_conditions(self):
        source = BY_KEY['living_room_tv_lights_unavailable']
        record = functions().advance(source, {}, evidence(), AT)
        env = SandboxedEnvironment(undefined=StrictUndefined)
        dashboard = yaml.safe_load((ROOT / 'dashboards/household_attention.yaml').read_text(encoding='utf8'))
        for modern in [True, False]:
            item = dict(record)
            if not modern:
                item.pop('display_name')
            attributes = {'items': [item], 'coverage': 'complete', 'health': 'faults',
                          'fault_count': 1, 'uncertain_sources': [], 'recent_events': []}
            env.globals['state_attr'] = lambda entity, attribute: attributes[attribute]
            for view in dashboard['views'][:2]:
                rendered = env.from_string(view['cards'][0]['content']).render()
                self.assertIn('Faults', rendered)
                self.assertIn('Maintenance', rendered)
                self.assertIn(source['title'], rendered)
                if modern:
                    self.assertIn('TV lights', rendered)

    def test_all_new_availability_sets_handle_partial_failure_and_uncertain_recovery(self):
        for source in SOURCES:
            if source['adapter'] != 'availability' or source.get('disconnected_states'):
                continue
            with self.subTest(source=source['key']):
                key, entities = source['key'], source['entities']
                values = {entity: 'off' for entity in entities}
                record = functions(values).reconcile([source], {}, AT)
                self.assertFalse(record[key]['active'])
                values[entities[0]] = 'unavailable'
                record = functions(values).reconcile([source], record, AT + 60)
                first = record[key]['occurrence_id']
                for entity in entities:
                    values[entity] = 'unavailable'
                record = functions(values).reconcile([source], record, AT + 120)
                self.assertEqual(record[key]['occurrence_id'], first)
                values.update({entity: 'off' for entity in entities})
                values[entities[-1]] = 'unknown'
                record = functions(values).reconcile([source], record, AT + 180)
                self.assertTrue(record[key]['active'])
                self.assertEqual(record[key]['quality'], 'unknown')
                values[entities[-1]] = 'off'
                record = functions(values).reconcile([source], record, AT + 240)
                self.assertFalse(record[key]['active'])
                values[entities[0]] = 'unavailable'
                record = functions(values).reconcile([source], record, AT + 300)
                self.assertNotEqual(record[key]['occurrence_id'], first)

    def test_no_excluded_device_or_dynamic_whole_instance_scan(self):
        entities = {entity for source in SOURCES for entity in source['entities']}
        self.assertFalse(any('dads_desk' in entity for entity in entities))
        watched = yaml.safe_load((ROOT / 'attention/watched_entities.yaml').read_text(encoding='utf8'))
        context = {entity for person in POLICY['people'].values() for entity in person.values()}
        context.update(POLICY['kiosk'].values())
        self.assertEqual(set(watched), entities | context)
        self.assertFalse(any(entity.startswith('cover.') for entity in entities | set(watched)))
        for entity in ['update.book_case_window_firmware', 'update.tv_window_firmware', 'update.middle_window_firmware']:
            self.assertIn(entity, entities)
        keys = [source['key'] for source in SOURCES]
        self.assertEqual(len(keys), len(set(keys)))

    def test_blind_records_drop_without_resetting_other_occurrences(self):
        source = BY_KEY['fridge_unavailable']
        values = {source['entities'][0]: 'unavailable', source['entities'][1]: '3'}
        f = functions(values)
        original = f.advance(source, {}, evidence(), AT)
        original['phone_evaluated'] = True
        previous = {source['key']: original,
                    'bookcase_blind_unavailable': dict(original, key='bookcase_blind_unavailable'),
                    'tv_blind_unavailable': dict(original, key='tv_blind_unavailable'),
                    'middle_blind_unavailable': dict(original, key='middle_blind_unavailable')}
        records = f.reconcile(SOURCES, previous, AT + 60)
        self.assertEqual(len(records), 24)
        self.assertFalse(any('blind' in key for key in records))
        self.assertEqual(records[source['key']]['occurrence_id'], original['occurrence_id'])
        self.assertEqual(records[source['key']]['first_detected'], AT)
        self.assertEqual(records[source['key']]['phone_routes'], [])


if __name__ == '__main__':
    unittest.main()
