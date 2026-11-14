# Household attention coverage

Generated from `attention/sources.yaml` by `tools/build_attention_controls.py`. Do not edit by hand.

| Device | Condition | Physical entities | Starting routes | Phone delay |
|---|---|---|---|---|
| Fridge | HA cannot reach the fridge through one or more channels | `switch.kitchen_fridge_power_plug`<br>`number.refrigerator_fridge_temperature` | HA dashboard, TV screensaver, Lachlan home + away, Nic home + away | 0 seconds |
| Dyson | HA cannot reach the Dyson Purifier Hot+Cool De-NOx | `fan.purifier_hot_cool_de_nox` | HA dashboard, TV screensaver, Lachlan home + away | 900 seconds |
| TV lights | HA cannot reach one or both living-room TV lights | `light.living_room_tv_light_1`<br>`light.living_room_tv_light_2` | HA dashboard, TV screensaver | 900 seconds |
| Dining-table lights | HA cannot reach one or both dining-table lights | `light.living_room_dining_table_light_1`<br>`light.living_room_dining_table_light_2` | HA dashboard, TV screensaver | 900 seconds |
| Basketball-hoop lights | HA cannot reach one or both basketball-hoop lights | `light.living_room_basketball_hoop_light_1`<br>`light.living_room_basketball_hoop_light_2` | HA dashboard, TV screensaver | 900 seconds |
| Internet | Router reports WAN disconnected or HA cannot read WAN status | `binary_sensor.archer_ax73_wan_status` | HA dashboard, TV screensaver, Lachlan home + away | 900 seconds |
| Washing machine | HA cannot reach the washer | `sensor.washer_current_status` | HA dashboard, TV screensaver, Lachlan home + away | 900 seconds |
| Kiosk phone | Kiosk phone reports it is off Wi-Fi | `sensor.iphone_8_connection_type` | HA dashboard, TV screensaver, Lachlan home + away | 900 seconds |
| Washing machine | Washing finished | `event.washer_notification` | HA dashboard, TV screensaver, Lachlan home + away, Nic home + away | 0 seconds |
| Washing machine | Washer needs a cleaning cycle | `sensor.washer_cycles` | HA dashboard, TV screensaver, Lachlan home + away | 900 seconds |
| Backups | A backup failed; check backup settings and destinations | `event.backup_automatic_backup`<br>`sensor.backup_last_successful_automatic_backup` | HA dashboard, TV screensaver, Lachlan home + away | 900 seconds |
| Updates | Upgrades are available | `update.home_assistant_supervisor_update`<br>`update.home_assistant_core_update`<br>`update.home_assistant_operating_system_update`<br>`update.matter_server_update`<br>`update.file_editor_update`<br>`update.openthread_border_router_update`<br>`update.terminal_ssh_update`<br>`update.bravia_ambient_photo_host_update`<br>`update.apexcharts_card_update`<br>`update.bureau_of_meteorology`<br>`update.raspberry_pi_5_firmware`<br>`update.kids_room_kids_tv_plug_firmware`<br>`update.living_room_ikea_blind_button_firmware`<br>`update.bathroom_red_button_firmware`<br>`update.ensuite_button_firmware`<br>`update.kitchen_fridge_power_plug_firmware`<br>`update.book_case_window_firmware`<br>`update.tv_window_firmware`<br>`update.middle_window_firmware`<br>`update.in_front_of_sink_firmware`<br>`update.living_room_tradfri_firmware`<br>`update.kitchen_fridge_ikea_button_x_4_firmware`<br>`update.laundry_led_strip_firmware`<br>`update.laundry_laundry_switch_firmware`<br>`update.internet_plug_firmware`<br>`update.split_system_finger_bot_firmware`<br>`update.kids_room_kids_bedroom_button_firmware`<br>`update.bedroom_main_bedroom_button_firmware`<br>`update.kids_room_lucys_switch_firmware`<br>`update.living_room_kiosk_phone_charger_firmware`<br>`update.living_room_tv_light_1_firmware`<br>`update.living_room_tv_light_2_firmware`<br>`update.kids_room_kids_bedroom_light_1_firmware`<br>`update.kids_room_kids_bedroom_light_2_firmware`<br>`update.living_room_basketball_hoop_light_1_firmware`<br>`update.living_room_basketball_hoop_light_2_firmware`<br>`update.living_room_dining_table_light_1_firmware`<br>`update.living_room_dining_table_light_2_firmware` | HA dashboard, TV screensaver | 0 seconds |
| Kitchen lights | HA cannot reach one or more kitchen lights | `light.bench`<br>`light.dish_rack`<br>`light.pantry`<br>`light.stove` | HA dashboard, TV screensaver | 900 seconds |
| Kitchen entrance | HA cannot reach the kitchen entrance | `light.entrance` | HA dashboard, TV screensaver | 900 seconds |
| Ensuite lights | HA cannot reach one or more ensuite lights | `light.toilet`<br>`light.mirror`<br>`light.shower` | HA dashboard, TV screensaver | 900 seconds |
| Bathroom lights | HA cannot reach one or more bathroom lights | `light.centre`<br>`light.sink` | HA dashboard, TV screensaver | 900 seconds |
| Main-bedroom lights | HA cannot reach one or more main-bedroom lights | `light.in_front_of_sink`<br>`light.living_room_tradfri` | HA dashboard, TV screensaver | 900 seconds |
| Kids’ bedroom lights | HA cannot reach one or more kids’ bedroom lights | `light.kids_room_kids_bedroom_light_1`<br>`light.kids_room_kids_bedroom_light_2` | HA dashboard, TV screensaver | 900 seconds |
| Laundry light | HA cannot reach the laundry light | `light.laundry_led_strip` | HA dashboard, TV screensaver | 900 seconds |
| Black fan | HA cannot reach the black fan | `fan.living_room_black_fan` | HA dashboard, TV screensaver | 900 seconds |
| Kids’ TV plug | HA cannot reach the kids’ TV plug | `switch.kids_room_kids_tv_plug` | HA dashboard, TV screensaver | 900 seconds |
| Internet plug | HA cannot reach the internet plug | `switch.internet_plug` | HA dashboard, TV screensaver | 900 seconds |
| Kiosk charger | HA cannot reach the kiosk charger | `switch.living_room_kiosk_phone_charger` | HA dashboard, TV screensaver | 900 seconds |
| Air-conditioner FingerBot | HA cannot reach the air-conditioner FingerBot | `switch.split_system_finger_bot` | HA dashboard, TV screensaver | 900 seconds |

## Grouping and limits

- Availability groups watch physical members: any unavailable member creates one item; every member must be valid to clear it. Ordinary off states are healthy.
- Kitchen lights are bench, dish rack, pantry and stove. Entrance is separate, pending physical switch confirmation.
- Unknown data means incomplete coverage; it does not prove a fault or clear an existing fault. Blind availability rows are excluded; blind firmware stays in grouped Updates.
- Phone delays begin at fault detection. Decisions are consumed once per occurrence, including when routes are disabled; enabling later does not replay a backlog.
- Kiosk Wi-Fi uses Connection Type; reports older than 15 minutes are uncertain. Phone home/away routing uses fresh GPS and matching fresh kiosk Wi-Fi evidence after startup; never Wi-Fi absence alone.
- Both home and away switches on means always, even with unknown presence; either alone requires matching evidence. Current phone choices are copied once, not changed to home-only automatically.
- Excluded: Dad’s desk, battery alarms, remotes without reliable heartbeats, duplicate room groups/control channels and optional cloud connectivity.
- Black-fan availability does not prove physical oscillation; FingerBot availability does not prove the air conditioner responded.
- New starting routes require approved setup. Regeneration never changes restored runtime preferences.
