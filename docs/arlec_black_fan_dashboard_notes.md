# Arlec / Tuya Black Fan dashboard

The Our Home V2 dashboard adds six speed buttons, a swing toggle and off after Dad's
Desk. It reuses the existing Tuya scene actions; the layout uses native button cards.
The six feedback binary sensors are defined in `templates.yaml`; do not create
duplicate UI helpers.

## Verified live on 7 November 2026

- `fan.living_room_black_fan` and all six speed scenes exist.
- Calling each scene produced the reported percentages below.
- Both swing scenes exist. Lachlan confirmed the deployed toggle and highlighting
  work, then confirmed the final compact layout looks good on his iPhone.
- Before deployment, the Our Home storage dashboard had fan controls without
  feedback. Our Home V2 had no fan card, and the six feedback entities were absent.
- After deployment, all six feedback entities and `switch.black_fan_swing` were
  verified through the API. Lachlan confirmed highlighting works for speeds 1-6.
- The authorised six-speed test ended with the fan reporting off. Later dashboard
  interactions were performed by Lachlan; this is not a statement of current state.

| Speed | Reported percentage | Feedback entity |
|---:|---:|---|
| 1 | 3 | `binary_sensor.black_fan_speed_1_active` |
| 2 | 7 | `binary_sensor.black_fan_speed_2_active` |
| 3 | 11 | `binary_sensor.black_fan_speed_3_active` |
| 4 | 15 | `binary_sensor.black_fan_speed_4_active` |
| 5 | 19 | `binary_sensor.black_fan_speed_5_active` |
| 6 | 23 | `binary_sensor.black_fan_speed_6_active` |

## Behaviour

Speed buttons call `scene.fan_speed_1` through `scene.fan_speed_6`. Their icons
highlight only when the fan reports on and its percentage matches. Feedback is
unavailable when the fan state is unknown/unavailable or percentage is not numeric.
An off fan can retain a percentage, so percentage alone is insufficient.

The controls use a one-grid-row horizontal stack of eight native button cards.
Names and state text are hidden, and icons are 24px high. Each button has its
own outline and centres its icon. This avoids Glance's fixed padding, which
either clipped the icons at one grid row or made the automatic-height card tall.
Swing uses `switch.black_fan_swing`, a template switch calling the existing
`scene.fan_swing_on` and `scene.fan_swing_off` scenes. Its highlighted state means
the fan is on and the swing-on scene was requested more recently than swing-off.
This is last-command feedback, not confirmed physical oscillation: the current
Tuya fan entity exposes no oscillation attribute or separate swing entity.
There is no physical remote. Device resets or commands outside these scenes can
still make the inferred state stale. Both scene timestamps must be valid for the
switch to be available. While the fan is off,
the switch reports off; it does not issue a swing command on power changes.
Off calls `fan.turn_off` and has a neutral icon rather than off-state feedback.
No scene definitions or existing automations are changed.

## Deployment and rollback (explicit approval required)

Before deployment, compare the live files with the repository and keep copies
of the live `templates.yaml` and `dashboards/our_home_v2.yaml`. Deploy only the
reviewed changes, validate the HA configuration, then reload template entities
and refresh the YAML dashboard. Confirm the generated entity IDs match the table;
unique IDs do not guarantee an entity ID if a registry collision exists.

The final iPhone layout and speed/swing highlighting were confirmed by Lachlan.
Unavailable-input behaviour was tested locally, not by disconnecting the live fan.
Future device-action testing requires approval. Local checks do not replace HA
validation.

To roll back, restore the saved live files, reload templates and refresh the
dashboard. Do not overwrite unrelated live changes.

## Validation and deployment record

Completed on 7 November 2026 (Australia/Sydney):

- Parsed the changed YAML and checked that pre-existing dashboard controls and
  template definitions were preserved.
- Exercised 192 speed-feedback cases and 36 swing state/availability cases locally.
- Checked the final button layout preserves all eight entity IDs, icons, actions
  and the off button's colour override. Whitespace checks passed.
- Compared the two original live YAML files with Git HEAD before deployment;
  they matched after normalising line endings and final whitespace.
- Backed up the live files before each approved deployment. Configuration
  validation (`ha core check`) passed before each required template reload.
- Checked live file hashes against local files and read the served dashboard
  configuration after upload. Dashboard-only layout changes needed no template
  reload or HA restart.

The Glance layout was replaced because its fixed padding either clipped icons
at one grid row or produced a card taller than wanted at automatic height.
The final native horizontal stack uses eight icon-only buttons, 24px icons and
`grid_options: {columns: 12, rows: 1}`. No custom frontend dependencies were added.

Timestamped backups of the affected live files were kept outside Git before
each deployment, including the original files and intermediate layouts.

For layout-only rollback, restore the appropriate dashboard copy and refresh it.
For full feature rollback, restore both original files and reload templates after
validation. New template entity-registry entries may remain unavailable and need
separate cleanup. Rollback writes and reloads also require explicit approval.

See [the local development workflow](local_development_workflow.md) for the
Git, MCP, SSH and credential-handling approach.

## References

- [Button card](https://www.home-assistant.io/dashboards/button/)
- [Horizontal stack](https://www.home-assistant.io/dashboards/horizontal-stack/)
