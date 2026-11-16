"""Verify the dashboard exposes a direct party-mode stop control."""
import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PARTY_SCRIPTS = {
    'script.party_bathroom',
    'script.party_ensuite',
    'script.party_kitchen',
    'script.party_laundry',
    'script.party_kids_room',
    'script.party_living_room',
    'script.party_bedroom',
}


class PartyModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = yaml.safe_load(
            (ROOT / 'scripts.yaml').read_text(encoding='utf8')
        )
        cls.dashboard = yaml.safe_load(
            (ROOT / 'dashboards/our_home_v2.yaml').read_text(encoding='utf8')
        )
        cls.cards = [
            card
            for view in cls.dashboard['views']
            for section in view['sections']
            for card in section['cards']
            if card.get('type') == 'tile'
        ]

    def test_all_lights_off_stops_every_party_script(self):
        stop_action = self.scripts['all_lights_off']['sequence'][0]['action']
        stopped_scripts = set(
            self.scripts['all_lights_off']['sequence'][0]['target']['entity_id']
        )
        self.assertEqual(stop_action, 'script.turn_off')
        self.assertEqual(stopped_scripts, PARTY_SCRIPTS)

    def test_dashboard_has_direct_stop_party_control(self):
        stop_card = next(card for card in self.cards if card.get('name') == 'Stop Party')
        self.assertEqual(
            stop_card['tap_action']['perform_action'],
            'script.all_lights_off',
        )


if __name__ == '__main__':
    unittest.main()
