"""Exercise update-notice templates with synthetic update states. No HA connection."""
import pathlib
import types
import unittest

import yaml
from jinja2.nativetypes import NativeEnvironment

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATES = yaml.safe_load((ROOT / 'templates.yaml').read_text(encoding='utf8'))
PENDING_UPDATES = next(
    sensor
    for group in TEMPLATES
    for sensor in group.get('sensor', [])
    if sensor.get('unique_id') == 'pending_updates'
)


def render_updates(updates):
    env = NativeEnvironment()
    env.globals['states'] = types.SimpleNamespace(update=updates)
    count = env.from_string(PENDING_UPDATES['state']).render()
    names = env.from_string(PENDING_UPDATES['attributes']['updates']).render()
    return count, names


def update(name, state, latest, skipped=None):
    return types.SimpleNamespace(
        name=name,
        state=state,
        attributes={'latest_version': latest, 'skipped_version': skipped},
    )


class UpdateNoticeTests(unittest.TestCase):
    def test_pending_upgrade_is_listed(self):
        count, names = render_updates([update('Home Assistant Core', 'on', '2026.11.1')])

        self.assertEqual(count, 1)
        self.assertEqual(names, '- Home Assistant Core (2026.11.1)')

    def test_skipped_upgrade_is_hidden(self):
        count, names = render_updates([
            update('Home Assistant Core', 'on', '2026.11.1', '2026.11.1')
        ])

        self.assertEqual(count, 0)
        self.assertEqual(names, '')

    def test_installed_upgrade_is_hidden(self):
        count, names = render_updates([update('Home Assistant Core', 'off', '2026.11.1')])

        self.assertEqual(count, 0)
        self.assertEqual(names, '')

    def test_later_version_is_listed_after_skip(self):
        count, names = render_updates([
            update('Home Assistant Core', 'on', '2026.11.2', '2026.11.1')
        ])

        self.assertEqual(count, 1)
        self.assertEqual(names, '- Home Assistant Core (2026.11.2)')

if __name__ == '__main__':
    unittest.main()
