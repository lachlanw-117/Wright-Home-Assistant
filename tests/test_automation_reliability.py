"""Exercise actual YAML/Jinja branches with synthetic HA states. No HA connection."""
import datetime as dt
import math
import pathlib
import subprocess
import types
import unittest

import yaml
from jinja2.nativetypes import NativeEnvironment

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / 'automations.yaml').read_text(encoding='utf8'))
BY_ID = {str(a['id']): a for a in CONFIG}
NOW = dt.datetime(2026, 11, 7, 7, tzinfo=dt.timezone.utc)

def number(value):
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False

def timestamp(value, default=0):
    try:
        return value.timestamp() if hasattr(value, 'timestamp') else float(value)
    except (TypeError, ValueError, AttributeError):
        return default

def environment(battery='50', age=0, unavailable_age=0, missing=False):
    state = None if missing else types.SimpleNamespace(
        last_reported=NOW-dt.timedelta(seconds=age),
        last_changed=NOW-dt.timedelta(seconds=unavailable_age))
    env = NativeEnvironment()
    env.globals.update(states=types.SimpleNamespace(sensor=types.SimpleNamespace(iphone_8_battery_level=state)),
                       as_timestamp=timestamp, now=lambda: NOW, is_number=number)
    # HA's states object is both callable and attribute-accessible.
    class States:
        sensor = types.SimpleNamespace(iphone_8_battery_level=state)
        def __call__(self, entity):
            return battery
    env.globals['states'] = States()
    return env

def render(env, text, variables):
    return env.from_string(text).render(**variables)

def charging(battery, plug, age=0, unavailable_age=0, missing=False):
    auto = BY_ID['1789173535286']
    env = environment(battery, age, unavailable_age, missing)
    variables = {}
    for key, value in auto['actions'][0]['variables'].items():
        variables[key] = render(env, value, variables)
    def condition(c):
        if c['condition'] == 'template':
            return bool(render(env, c['value_template'], variables))
        if c['condition'] == 'state':
            return plug == c['state']
        if c['condition'] == 'numeric_state':
            return number(battery) and ('below' not in c or float(battery) < c['below']) and ('above' not in c or float(battery) > c['above'])
        raise AssertionError(c)
    for branch in auto['actions'][1]['choose']:
        if all(condition(c) for c in branch['conditions']):
            for action in branch['sequence']:
                if 'if' in action:
                    if not all(condition(c) for c in action['if']):
                        continue
                    action = action['then'][0]
                return action['action']
            return None
    return None

class ReliabilityTests(unittest.TestCase):
    def test_hysteresis_and_stale_feedback(self):
        cases = [
            ('40','off',0,0,False,'switch.turn_on'),
            ('41','off',0,0,False,None), ('79','on',0,0,False,None),
            ('80','on',0,0,False,'switch.turn_off'),
            ('80','off',3600,0,False,'switch.turn_on'),
            ('80','on',3600,0,False,None), # no stale on/off oscillation
            ('50','off',3600,0,False,'switch.turn_on'),
            ('unknown','off',0,599,False,None),
            ('unknown','off',0,600,False,'switch.turn_on'),
            ('unavailable','on',0,600,False,None),
            ('unknown','off',0,0,True,'switch.turn_on'),
            ('80','unavailable',3600,0,False,None),
            ('80','on',3599,0,False,'switch.turn_off'),
        ]
        for args in cases:
            with self.subTest(args=args):
                self.assertEqual(charging(*args[:-1]),args[-1])

    def test_washer_transitions(self):
        auto = BY_ID['1792576854357']
        self.assertIn('to', auto['triggers'][0])
        self.assertIsNone(auto['triggers'][0]['to'])
        for old, new, expected in [('29','30',True),('30','31',True),('28','29',False),
                ('30','30',False),('unknown','30',False),('unavailable','31',False),
                ('33','32',False),('32','0',False),('0','1',False),('30','nan',False),
                (None,'30',False),('30',None,False)]:
            trigger = types.SimpleNamespace(from_state=None if old is None else types.SimpleNamespace(state=old),
                to_state=None if new is None else types.SimpleNamespace(state=new))
            result = render(environment(),auto['conditions'][0]['value_template'],{'trigger':trigger})
            with self.subTest(old=old,new=new):
                self.assertEqual(bool(result),expected)
        self.assertTrue(all(a.get('continue_on_error') for a in auto['actions']))

    def test_unrelated_automations_preserved(self):
        previous = yaml.safe_load(subprocess.check_output(['git','show','main:automations.yaml'],cwd=ROOT,encoding='utf8'))
        old = {str(a['id']):a for a in previous}
        self.assertEqual(set(old),set(BY_ID))
        for key in old.keys()-{'1789173535286','1792576854357'}:
            self.assertEqual(old[key],BY_ID[key])

if __name__ == '__main__':
    unittest.main()
