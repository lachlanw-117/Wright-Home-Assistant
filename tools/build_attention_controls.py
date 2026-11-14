"""Generate static native HA helper definitions and a dashboard from reviewed rows.

No HA connection; run after adding/removing a source. Runtime helper values are
never generated. --check verifies checked-in outputs without changing them.
"""
import argparse
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DESTINATIONS = {
    'dashboard': 'HA dashboard', 'tv': 'TV screensaver',
    'lachlan_home': 'Lachlan phone when home', 'lachlan_away': 'Lachlan phone when away',
    'nic_home': 'Nic phone when home', 'nic_away': 'Nic phone when away',
}
LEGACY_PHONE_DESTINATIONS = {
    'lachlan_phone': 'Lachlan phone', 'nic_phone': 'Nic phone',
}


class ReadableDumper(yaml.SafeDumper):
    """Keep dashboard templates readable in review."""


def string_representer(dumper, value):
    return dumper.represent_scalar('tag:yaml.org,2002:str', value,
                                   style='|' if '\n' in value else None)


ReadableDumper.add_representer(str, string_representer)


def outputs():
    sources = yaml.safe_load((ROOT / 'attention/sources.yaml').read_text(encoding='utf8'))
    policy = yaml.safe_load((ROOT / 'attention/policy.yaml').read_text(encoding='utf8'))
    controls = {
        'attention_routing_enabled': {'name': 'Enable shared phone routing'},
        'attention_preferences_configured': {'name': 'Attention starting preferences applied'},
        'attention_presence_routes_migrated': {'name': 'Home/away preferences migrated'},
        # Operational boot guard, deliberately reset. This is not a preference.
        'household_attention_presence_ready': {'name': 'Phone presence session ready', 'initial': False},
    }
    pauses = {'household_attention_presence_started_at': {
        'name': 'Phone presence session started', 'has_date': True, 'has_time': True}}
    watched = {entity for person in policy['people'].values() for entity in person.values()}
    watched.update(policy['kiosk'].values())
    starting = []
    cards = [
        {'type': 'markdown', 'title': 'Delivery preferences', 'content':
         'Each row has dashboard, TV and home/away phone switches for each person. '
         'Both phone switches on means always, including when presence is unknown; both off means no phone alert. '
         'Selecting only home or away requires a matching report no older than 15 minutes. '
         'The inbox always keeps active items. '
         'All switches start off on first install and restore thereafter. '
         'A row pause expires automatically and preserves switches. '
         'Existing phone choices are preserved during the reviewed home/away migration. '
         'Washing is a one-shot notice; its red laundry lighting stays independent.\n\n'
         "Home/away controls: {{ 'ready' if is_state('input_boolean.attention_presence_routes_migrated', 'on') "
         "else 'setup pending; current phone delivery stays active' }}."},
        {'type': 'entities', 'show_header_toggle': False, 'entities': [
            'script.household_attention_apply_starting_preferences',
            'input_boolean.attention_preferences_configured',
            'input_boolean.attention_routing_enabled']},
        {'type': 'markdown', 'title': 'Phone presence', 'content':
         "{% for person, label in [('lachlan', 'Lachlan'), ('nic', 'Nic')] %}\n"
         "{% set entity = 'sensor.household_attention_' ~ person ~ '_presence' %}\n"
         "{% set evidence = state_attr(entity, 'evidence') or {} %}\n"
         "**{{ label }}:** {{ states(entity) }} — {{ evidence.get('reason', 'Waiting for reports') }}.\n"
         "Location report age: {{ evidence.get('gps_age_seconds') if evidence.get('gps_age_seconds') is number else 'unknown' }} seconds; "
         "Wi-Fi report age: {{ evidence.get('wifi_age_seconds') if evidence.get('wifi_age_seconds') is number else 'unknown' }} seconds.\n"
         "{% endfor %}"},
    ]
    for source in sources:
        key = source['key']
        name = source.get('display_name', source['title'])
        watched.update(source['entities'])
        rows = []
        # All six destinations are active. Plain phone helpers stay hidden for
        # the one-time preserving migration and a reviewed rollback.
        destinations = DESTINATIONS | LEGACY_PHONE_DESTINATIONS
        for suffix, label in destinations.items():
            entity = f'attention_{key}_{suffix}'
            # Omit initial: deploying/restarting must preserve restored values.
            controls[entity] = {'name': f'{name} - {label}'}
            if suffix in DESTINATIONS:
                rows.append({'entity': f'input_boolean.{entity}', 'name': label})
            if suffix in source.get('starting_destinations', []):
                starting.append(f'input_boolean.{entity}')
                if suffix.endswith('_phone'):
                    for location in ['home', 'away']:
                        starting.append(f'input_boolean.attention_{key}_{suffix.removesuffix("_phone")}_{location}')
        pause = f'attention_{key}_pause_until'
        pauses[pause] = {'name': f'{name} pause until',
                         'has_date': True, 'has_time': True}
        rows.append({'entity': f'input_datetime.{pause}', 'name': 'Pause all routes until'})
        cards.append({'type': 'vertical-stack', 'cards': [
            {'type': 'markdown', 'title': name, 'content': source['title']},
            {'type': 'entities', 'show_header_toggle': False, 'entities': rows},
        ], 'category': source['category']})
    # Preferences are deliberately not store triggers: visible views re-filter
    # immediately; phone decisions happen only once when the source becomes due.
    content = """{% set items = state_attr('sensor.household_attention_inbox', 'items') or [] %}
Health: {{ state_attr('sensor.household_attention_inbox', 'health') }}
Coverage: {{ state_attr('sensor.household_attention_inbox', 'coverage') }}
Confirmed faults: {{ state_attr('sensor.household_attention_inbox', 'fault_count') }}
{% for kind, label in [('fault', 'Faults'), ('attention', 'Maintenance'), ('event', 'Events')] %}
## {{ label }}
{% for category, category_items in items | selectattr('kind', 'eq', kind) | groupby('category') %}
### {{ category | title }}
{% for item in category_items %}
#### {{ item.get('display_name', item.title) }}
{{ item.title }}
{{ item.kind }} · {{ item.severity }} · observation {{ item.quality }}
{% for evidence in item.evidence %}
- {{ evidence.entity_id }}: {{ evidence.state }}
{% endfor %}
{% for detail in item.details %}
- {{ detail.component }}: {{ detail.installed_version }} → {{ detail.latest_version }}
{% endfor %}
{% endfor %}
{% else %}None.{% endfor %}
{% endfor %}
Coverage gaps: {{ state_attr('sensor.household_attention_inbox', 'uncertain_sources') }}

{% for item in state_attr('sensor.household_attention_inbox', 'recent_events') or [] %}
Recent event: **{{ item.get('display_name', item.title) }}** - {{ item.title }} - delivery {{ item.delivery_state }}.
{% endfor %}
"""
    filtered = """{% set items = state_attr('sensor.household_attention_dashboard', 'items') or [] %}
{% for kind, label in [('fault', 'Faults'), ('attention', 'Maintenance'), ('event', 'Events')] %}
## {{ label }}
{% for category, category_items in items | selectattr('kind', 'eq', kind) | groupby('category') %}
### {{ category | title }}
{% for item in category_items %}
- **{{ item.get('display_name', item.title) }}** — {{ item.title }} ({{ item.kind }}, {{ item.quality }})
{% endfor %}
{% else %}None.{% endfor %}
{% endfor %}
All active items remain in Inbox. Coverage: {{ state_attr('sensor.household_attention_inbox', 'coverage') }}"""
    # Keep the setup cards first, then group device controls by category.
    grouped = cards[:3]
    for category in sorted({source['category'] for source in sources}):
        grouped.append({'type': 'markdown', 'content': f'## {category.title()}'})
        for card in cards[3:]:
            if card['category'] == category:
                grouped.append({key: value for key, value in card.items() if key != 'category'})
    dashboard = {'views': [
        {'title': 'Dashboard', 'path': 'dashboard', 'cards': [
            {'type': 'markdown', 'title': 'Household attention', 'content': filtered}]},
        {'title': 'Inbox', 'path': 'inbox', 'cards': [
            {'type': 'markdown', 'title': 'Private household inbox', 'content': content}]},
        {'title': 'Delivery controls', 'path': 'controls', 'cards': grouped},
    ]}
    header = '# Generated by tools/build_attention_controls.py; runtime values are not set here.\n'
    generated = {name: header + yaml.dump(data, Dumper=ReadableDumper, sort_keys=False, allow_unicode=True)
            for name, data in {
                'attention/delivery_controls.yaml': controls,
                'attention/pauses.yaml': pauses,
                'attention/watched_entities.yaml': sorted(watched),
                'attention/starting_destinations.yaml': starting,
                'dashboards/household_attention.yaml': dashboard,
            }.items()}
    catalogue = [
        '# Household attention coverage', '',
        'Generated from `attention/sources.yaml` by `tools/build_attention_controls.py`. Do not edit by hand.', '',
        '| Device | Condition | Physical entities | Starting routes | Phone delay |',
        '|---|---|---|---|---|',
    ]
    for source in sources:
        route_labels = []
        for destination in source.get('starting_destinations', []):
            if destination.endswith('_phone'):
                route_labels.append(destination.removesuffix('_phone').title() + ' home + away')
            else:
                route_labels.append(DESTINATIONS[destination])
        catalogue.append('| ' + ' | '.join([
            source.get('display_name', source['title']), source['title'],
            '<br>'.join(f'`{entity}`' for entity in source['entities']),
            ', '.join(route_labels),
            str(source['delivery_delay_seconds']) + ' seconds',
        ]) + ' |')
    catalogue += ['', '## Grouping and limits', '',
        '- Availability groups watch physical members: any unavailable member creates one item; every member must be valid to clear it. Ordinary off states are healthy.',
        '- Kitchen lights are bench, dish rack, pantry and stove. Entrance is separate, pending physical switch confirmation.',
        '- Unknown data means incomplete coverage; it does not prove a fault or clear an existing fault. Blind availability rows are excluded; blind firmware stays in grouped Updates.',
        '- Phone delays begin at fault detection. Decisions are consumed once per occurrence, including when routes are disabled; enabling later does not replay a backlog.',
        '- Kiosk Wi-Fi uses Connection Type; reports older than 15 minutes are uncertain. Phone home/away routing uses fresh GPS and matching fresh kiosk Wi-Fi evidence after startup; never Wi-Fi absence alone.',
        '- Both home and away switches on means always, even with unknown presence; either alone requires matching evidence. Current phone choices are copied once, not changed to home-only automatically.',
        '- Excluded: Dad’s desk, battery alarms, remotes without reliable heartbeats, duplicate room groups/control channels and optional cloud connectivity.',
        '- Black-fan availability does not prove physical oscillation; FingerBot availability does not prove the air conditioner responded.',
        '- New starting routes require approved setup. Regeneration never changes restored runtime preferences.', '']
    generated['docs/household_attention_coverage.md'] = '\n'.join(catalogue)
    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, text in outputs().items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text(encoding='utf8') != text:
                raise SystemExit(f'Stale generated file: {name}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf8', newline='\n')
    print('PASS attention control files' if args.check else 'Generated attention control files')


if __name__ == '__main__':
    main()
