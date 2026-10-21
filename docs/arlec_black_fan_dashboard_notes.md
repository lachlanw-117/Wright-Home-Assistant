# Arlec / Tuya Black Fan dashboard

The physical remote is missing. The fan connects through the Tuya integration,
but its exposed controls are limited. Tuya scenes provide the required speed
and swing commands. A version without feedback is already on a local dashboard.

This branch adds the feedback version to the bottom of
`dashboards/our_home_v2.yaml`. Create the six template helpers in Home Assistant
before using it. No sensor definitions are added to `templates.yaml`; these
helpers are being created through the UI.

## Create the speed helpers

Open **Settings > Devices & services > Helpers > Create helper > Template >
Binary sensor**. Use the following entity IDs exactly, with no device class.

| Speed | Reported percentage | Helper entity ID |
|---:|---:|---|
| 1 | 3 | `binary_sensor.black_fan_speed_1_active` |
| 2 | 7 | `binary_sensor.black_fan_speed_2_active` |
| 3 | 11 | `binary_sensor.black_fan_speed_3_active` |
| 4 | 15 | `binary_sensor.black_fan_speed_4_active` |
| 5 | 19 | `binary_sensor.black_fan_speed_5_active` |
| 6 | 23 | `binary_sensor.black_fan_speed_6_active` |

### Speed 1

Entity ID: `binary_sensor.black_fan_speed_1_active`

State template:

```jinja
{{ is_state('fan.living_room_black_fan', 'on') and (state_attr('fan.living_room_black_fan', 'percentage') | int(0)) == 3 }}
```

### Speed 2

Entity ID: `binary_sensor.black_fan_speed_2_active`

State template:

```jinja
{{ is_state('fan.living_room_black_fan', 'on') and (state_attr('fan.living_room_black_fan', 'percentage') | int(0)) == 7 }}
```

### Speed 3

Entity ID: `binary_sensor.black_fan_speed_3_active`

State template:

```jinja
{{ is_state('fan.living_room_black_fan', 'on') and (state_attr('fan.living_room_black_fan', 'percentage') | int(0)) == 11 }}
```

### Speed 4

Entity ID: `binary_sensor.black_fan_speed_4_active`

State template:

```jinja
{{ is_state('fan.living_room_black_fan', 'on') and (state_attr('fan.living_room_black_fan', 'percentage') | int(0)) == 15 }}
```

### Speed 5

Entity ID: `binary_sensor.black_fan_speed_5_active`

State template:

```jinja
{{ is_state('fan.living_room_black_fan', 'on') and (state_attr('fan.living_room_black_fan', 'percentage') | int(0)) == 19 }}
```

### Speed 6

Entity ID: `binary_sensor.black_fan_speed_6_active`

State template:

```jinja
{{ is_state('fan.living_room_black_fan', 'on') and (state_attr('fan.living_room_black_fan', 'percentage') | int(0)) == 23 }}
```

The `int(0)` fallback handles a missing percentage. Requiring the fan to be on
prevents an old percentage highlighting a speed when the fan is off.

## Dashboard controls

The full-width Glance card is appended after Dad's Desk:

- Speeds 1 to 6 display the corresponding template sensor and call
  `scene.fan_speed_1` through `scene.fan_speed_6`.
- The active speed icon uses state coloring. The state text is hidden.
- The swing button calls `scene.fan_swing_on`, matching the original notes.
  It does not toggle swing off or report oscillation state.
  `scene.fan_swing_off` also exists, but is not included in this eight-control row.
- Off calls `fan.turn_off` for `fan.living_room_black_fan`. Its icon is neutral;
  it is an action button, not an off-state indicator.

Scenes are commands, not persistent feedback. Speed highlighting depends on
Tuya updating the fan's reported percentage after a command.

## Review in Home Assistant

1. Create the six helpers and confirm their entity IDs match the table.
2. Review the branch diff before merging or loading it onto Home Assistant.
3. Refresh Our Home V2 after loading the dashboard YAML.
4. Tap each speed and check the physical fan and the matching highlighted icon.
5. Turn the fan off and check that all speed highlights clear.
6. Confirm swing-on works. Swing-off needs a later UI decision if wanted.

The YAML can be checked structurally without a live Home Assistant connection.
Live device behavior and rendering still need to be checked on the installation.

## References

- [Glance card](https://www.home-assistant.io/dashboards/glance/)
- [Sections view](https://www.home-assistant.io/dashboards/sections/)
