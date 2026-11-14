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
ACTIVE_DESTINATIONS = {
    'dashboard': 'HA dashboard', 'tv': 'TV screensaver',
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
    controls = {
        'attention_routing_enabled': {'name': 'Enable shared phone routing'},
        'attention_preferences_configured': {'name': 'Attention starting preferences applied'},
    }
    pauses, watched, starting = {}, set(), []
    cards = [
        {'type': 'markdown', 'title': 'Delivery preferences', 'content':
         'Each row has dashboard, TV and one phone switch per person. Phone delivery does not depend on location. '
         'The inbox always keeps active items. '
         'All switches start off on first install and restore thereafter. '
         'A row pause expires automatically and preserves switches. '
         'Apply starting preferences once during the reviewed setup, then enable shared phone routing. '
         'Washing is a one-shot notice; its red laundry lighting stays independent.'},
        {'type': 'entities', 'show_header_toggle': False, 'entities': [
            'script.household_attention_apply_starting_preferences',
            'input_boolean.attention_preferences_configured',
            'input_boolean.attention_routing_enabled']},
    ]
    for source in sources:
        key = source['key']
        name = source.get('display_name', source['title'])
        watched.update(source['entities'])
        rows = []
        # Preserve the earlier six helper IDs and restored values. Home/away
        # helpers are dormant and hidden while the presence split is parked.
        destinations = ((DESTINATIONS | ACTIVE_DESTINATIONS)
                        if source.get('preserve_legacy_presence_helpers', False)
                        else ACTIVE_DESTINATIONS)
        for suffix, label in destinations.items():
            entity = f'attention_{key}_{suffix}'
            # Omit initial: deploying/restarting must preserve restored values.
            controls[entity] = {'name': f'{name} - {label}'}
            if suffix in ACTIVE_DESTINATIONS:
                rows.append({'entity': f'input_boolean.{entity}', 'name': label})
            if suffix in source.get('starting_destinations', []):
                starting.append(f'input_boolean.{entity}')
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
    grouped = cards[:2]
    for category in sorted({source['category'] for source in sources}):
        grouped.append({'type': 'markdown', 'content': f'## {category.title()}'})
        for card in cards[2:]:
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
        catalogue.append('| ' + ' | '.join([
            source.get('display_name', source['title']), source['title'],
            '<br>'.join(f'`{entity}`' for entity in source['entities']),
            ', '.join(source.get('starting_destinations', [])),
            str(source['delivery_delay_seconds']) + ' seconds',
        ]) + ' |')
    catalogue += ['', '## Grouping and limits', '',
        '- Availability groups watch physical members: any unavailable member creates one item; every member must be valid to clear it. Ordinary off states are healthy.',
        '- Kitchen lights are bench, dish rack, pantry and stove. Entrance is separate, pending physical switch confirmation.',
        '- Unknown data means incomplete coverage; it does not prove a fault or clear an existing fault. The three blinds currently report unknown.',
        '- Phone delays begin at fault detection. Decisions are consumed once per occurrence, including when routes are disabled; enabling later does not replay a backlog.',
        '- Kiosk Wi-Fi uses the enabled Connection Type sensor; reports older than 15 minutes are uncertain. Personal phone presence is not used.',
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
