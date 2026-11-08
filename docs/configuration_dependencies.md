# Configuration outside YAML

Read-only inventory checked on 7 November 2026. This records dependencies that
help explain and reproduce the YAML configuration; it is not a runtime-storage export.

## Fan scenes

The live entity registry reports platform `tuya` for `scene.fan_speed_1` through
`scene.fan_speed_6`, `scene.fan_swing_on` and `scene.fan_swing_off`.
They come from the configured Tuya integration rather than `scenes.yaml`.
Retain the corresponding Tuya scenes and integration when rebuilding the setup.
The speed mappings and feedback limitations are in the [fan notes](arlec_black_fan_dashboard_notes.md).
The integration registry establishes their source; it does not export the cloud-side scene actions.

## Lighting helpers

The available input-helper inventory contains two time-only input_datetime helpers:

| Entity | Name | Value at inspection |
|---|---|---|
| `input_datetime.lighting_day_start` | Lighting Day Start | 06:30:00 |
| `input_datetime.lighting_night_start` | Lighting Night Start | 19:00:00 |

Both have time enabled and date disabled. These values can be changed through the
UI; they are a snapshot, not immutable defaults. Recreate the helpers with the same
entity IDs and choose the intended times when restoring the installation.
No input_boolean, input_number, input_text, input_select, input_button, counter
or timer helpers were returned. Other helper types and integration settings still
need a wider inventory.

## Bravia ambient display

The companion photo/weather host was installed as a local HA app on 7 November
2026, not an automation or core YAML integration. Its last recorded deployment
used `weather.forecast_home`, daily forecasts and `Australia/Sydney`. Its source
and generated package belong in the separate
[Bravia Ambient Display repository](https://github.com/lachlanw-117/Bravia-Ambient-Display).
The [host notes](bravia_ambient_host.md) record installation, private options,
folder/port requirements, BOM source inspection and trial status. They also link
the separately approved enhancement phases and decision log. Phase 0 documents
the plan only; the planned BOM selection and notice helpers are not deployed.
Repository defaults and historical results do not establish current live state.

## Remaining comparisons

The UI-managed Our Home and Fridge dashboards and full live script definitions
still need reviewed exports. Compare only named non-secret files; authentication,
integration credentials, runtime databases and backups do not belong in Git.
Do not copy the whole `.storage` directory to make a configuration backup public.
