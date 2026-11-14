# Household attention handler - feature draft

Work belongs on `feature/household-attention-handler`, based on
`9b6513203ac89764d8669aaaf998b1878e2199ba`. The original supplied
[accepted handoff](household_attention_accepted_handoff.txt) is preserved as a
dated requirements record. This document describes the implementation and its
remaining gates. No deployment, backup confirmation, physical acceptance, push
or merge has occurred in this implementation session.

## Latest accepted answers - 14 November 2026

- Fridge: immediate capture and phone alert; both people at home or away, TV,
  one item retaining both channels, no repeat/recovery message, clear only when
  both channels recover. The latest explicit "fridge is immediate" overrides
  the earlier agreement to a ten-minute starting proposal. Expiring pause agreed.
- Other unavailable-device phone alerts: 15 minutes, no repeats or recovery message.
- Washing: each person gets a phone alert only when home; one-shot event resolves
  after notification delivery instead of remaining a pending chore. Existing red
  laundry lighting stays independent; no extra light-control helper is requested.
- Backup: only a later successful automatic backup clears the failure.
- Upgrades: grouped dashboard/TV starting routes, no component phone alerts.
- Second Dyson: not in HA; explicitly excluded from this work by Lachlan.
- Kiosk: use ordinary online/on-Wi-Fi presence; do not build complex inference
  from charger/battery behaviour. Existing Wi-Fi/connection-type sensors were
  verified in the registry but are disabled, so enabling a real signal is still
  a separately approved live setup step.

Pending choices: phone recipients for internet/washer-unavailable/backup/cleaning;
presence-report maximum age; enabling kiosk Wi-Fi sensing versus waiting for a
router-based signal. Lights, battery-drain and authentication still lack reviewed
source policies/signals and are not silently added.

## Ownership and implementation

Native HA owns observation, lifecycle and delivery. There is no AI runtime,
external inbox server, lab HA instance, fake device inventory or notification
simulation service. The Bravia application is unchanged.

| File | Responsibility |
|---|---|
| `attention/sources.yaml` | Reviewed source list, meanings and delivery delays |
| `custom_templates/household_attention.jinja` | Observation, lifecycle, destination filtering and one-time phone eligibility |
| `packages/household_attention.yaml` | Restored store, derived inbox/health/dashboard/TV entities, phone delivery automation |
| `attention/delivery_controls.yaml` | Six restored `input_boolean` definitions per row |
| `attention/pauses.yaml` | Restored per-row routing pause deadlines |
| `attention/watched_entities.yaml` | Targeted observation triggers |
| `attention/starting_destinations.yaml` | Reviewed first-install profile, applied only by an explicit guarded setup script |
| `dashboards/household_attention.yaml` | Inbox, filtered dashboard and editable preference rows |
| `tools/build_attention_controls.py` | Local generator for static helper/dashboard/trigger definitions |

`configuration.yaml` adds one explicit package include and one YAML dashboard.
`automations.yaml` changes only the phone cutover in the two washing automations;
their original phone actions are kept behind the shared-routing gate. The exact
completion trigger and laundry lighting action are preserved. Existing repair
automations, `scripts.yaml` and `templates.yaml` are unchanged.
Helpers omit `initial`, so their selected values can restore. They start off on
first installation; choose the starting preferences together during the approved
trial. The guarded `household_attention_apply_starting_preferences` script is an
explicit first-install action, and refuses to reapply once its restored setup
flag is on. It never runs on restart/deploy, and does not enable shared routing.
Inspect its selected values together before turning shared routing on.
Source-rule updates
must preserve existing row keys and helper IDs. Changing/removing keys requires
an explicit migration review.

### Foundation comparison

The installed HA version was verified read-only as **2026.11.0** on 14 November
2026. Neither Alert2 nor Supernotify appeared in the loaded components.

| Option | Fit and gap | Decision |
|---|---|---|
| Native template records + helpers | Restored sensor attributes, explicit source evidence and six independently restored destinations; requires a small reviewed lifecycle/router | Selected for this bounded first draft |
| Native Alert | Repeating condition alert/acknowledgement; does not itself provide the typed shared inbox or event records | No extra layer needed |
| Alert2 | Condition/event lifecycle, reminders, acknowledgement and hierarchies; still needs household-specific inbox/presence/preferences; additional custom integration and periodic restore limitation | Consider if reminders/acknowledgement become substantially more complex |
| Supernotify | Useful occupancy/delivery policies; does not replace incident identity or persistence | Native per-person actions suffice for this slice |

References: [template restoration](https://www.home-assistant.io/integrations/template/),
[input boolean restoration](https://www.home-assistant.io/integrations/input_boolean/),
[custom macros](https://www.home-assistant.io/docs/templating/custom-templates/),
[packages](https://www.home-assistant.io/docs/configuration/packages/),
[native Alert](https://www.home-assistant.io/integrations/alert/),
[Alert2](https://github.com/redstone99/hass-alert2/blob/master/README.md),
[Supernotify deliveries](https://supernotify.rhizomatics.org.uk/latest/configuration/deliveries/).
This choice is an engineering assessment, not Pi runtime acceptance.

## Verified mappings and open source policies

Live evidence comes from read-only entity states, selected full entity reads,
registry platform/device associations, notify action inventory and two selected
battery histories. It does not establish live YAML equality with Git.
No credentials, private keys, runtime storage or backups were read or copied.

| Row/source | Verified mapping and semantics | Remaining policy |
|---|---|---|
| Fridge unavailable | `switch.kitchen_fridge_power_plug` (ZHA) OR `number.refrigerator_fridge_temperature` (LG ThinQ). Either unavailable creates one visibility-loss item retaining both channels. Both must be valid to clear. The LG number is a setpoint, not proof of actual cooling. | Immediate; dashboard/TV and both people home/away in the starting profile. No repeats/escalation/recovery message. |
| Dyson unavailable | `fan.purifier_hot_cool_de_nox` (Matter). `off` is normal. | 15 minutes; dashboard/TV and Lachlan home/away starting profile. Second Dyson explicitly removed from scope. |
| Internet disconnected | `binary_sensor.archer_ax73_wan_status` (UPnP), including the registry ID used by repair automation `1786235041388`. Live `on`, device class connectivity. `off` means WAN disconnected. | 15 minutes; phone recipients pending. WAN is router evidence, not comprehensive internet reachability. Repair remains unchanged. |
| Washer unavailable | `sensor.washer_current_status` (LG ThinQ); `initial` is a normal current state. | 15 minutes; phone recipients pending. Distinct from finished washing. |
| Washing finished | `event.washer_notification`, `event_type: washing_is_complete`; event state is the occurrence timestamp. | Immediate, both people home-only starting profile; resolves after dispatch receipts or explicit suppression, no arrival backlog. Lighting unchanged. |
| Washer cleaning | `sensor.washer_cycles >= 30`; a later valid value below 30 clears. | 15 minutes, once per cleaning-needed occurrence after cutover; recipients pending. Legacy messages continue before cutover. |
| Backup failure | `event.backup_automatic_backup`: `failed`, `in_progress`, `completed`; success from `sensor.backup_last_successful_automatic_backup`. | 15 minutes; later successful automatic backup clears. Phone recipients pending. Backup staleness/missed cadence is a separate future rule. |
| Available upgrades | Explicit update list excluding Dad's desk plug firmware. One item with component/installed/latest details; confirmed `off` removes components. Unknown retains last known pending details and incomplete coverage. | Dashboard/TV starting routes; all phone preferences initially off. Six independent controls remain editable. |
| Kiosk | `device_tracker.iphone_8` is mobile-app GPS and last reported six days before inspection; kiosk/charger state does not prove reachability. `sensor.iphone_8_ssid` and `sensor.iphone_8_connection_type` are registered but disabled. | Pending choice of real Wi-Fi/router signal, then verify its freshness. No adapter silently enabled and no GPS/battery outage inference. |
| Lights/groups | Real lights exist, but the curated members and member-versus-group policy remain undecided. | Select devices/groups and persistence before connecting adapters. Saved route: TV only. |
| Switch batteries | Real percentage histories exist. Laundry switch varied roughly 78-87% after an earlier 0%/unavailable period; fridge four-button remote stayed 100% with an unavailable interval. | These samples do not establish reliable rapid drain. Select switches, threshold/window, freshness and recovery; do not treat missing as zero. |
| Auth/credentials | `repairs` is loaded; Spook/Watchman were not in the loaded components. No actionable reauth entity was established by this inventory. | Map a verified supported issue signal before adding an adapter; never inspect credentials to manufacture one. |

Dad's desk plug is `switch.bedroom_dads_desk_plug` (ZHA device
`f92fc38d2e8483ca6b832b09f19c47e6`). Its associated entities, including firmware,
are absent from the handler's source/trigger lists. The handler performs no
whole-instance scan and does not check or create records for that device.

Phone actions verified: `notify.mobile_app_big_lws_iphone_14` (Lachlan) and
`notify.mobile_app_nichola_s_iphone` (Nic), matching the existing washer device IDs.
Presence is `person.lachlan` / `person.nic`, each backed by the corresponding
mobile-app GPS tracker. The draft freshness value is 24 hours; this needs policy
confirmation. Presence-dependent delivery suppresses missing/unknown/stale
observations. Selecting both home and away makes delivery independent of
presence, preserving the fridge's saved route. No SSID value is treated as proof.

Source delays now implement the accepted timing. All phone routing is initially
held behind restored `input_boolean.attention_routing_enabled`, which defaults
off. Dashboard/TV and agreed phone starting values are applied only in the
reviewed first-install setup. Unanswered recipient choices remain phone-off in
that profile. Existing already-captured occurrences are not replayed when the
gate is enabled: review the inbox during setup. Future preference edits change
the six independent destinations without a Git edit.

## Record and consumer contract

`sensor.household_attention_store.attributes.records` is the private bounded
dictionary keyed by reviewed source key. Each record contains:

- `key`, `occurrence_id`, `source_occurrence`, `category`, `kind`, `severity`, `title`;
- `active`, `first_detected`, `last_valid_observation`, `resolved_at` (Unix seconds);
- `quality` (`valid` or `unknown` for currently mapped adapters), `evidence`, `details`;
- backup `failure_at` and one-time `phone_evaluated` / transient `phone_routes`.
- `selected_phone_routes`, `delivered_to`, `delivery_state`, `display_until`
  for bounded one-shot delivery outcome and recent-event display.

Repeated failures update one occurrence. Verified recovery resolves only that
source. A later failure gets a new occurrence. Unknown/missing data does not
resolve an active record. Healthy-to-unknown is a coverage gap, without claiming
physical device failure. Explicit unavailable is valid evidence of HA visibility
loss, not proof of appliance failure. These integration entities are not heartbeat
monitors; an unchanged value is not independently verified fresh telemetry.

One current/last occurrence per row is retained, with no unbounded searchable
history. Trigger-based restoration provides continuity, not guaranteed archival
durability or exactly-once external delivery after a crash. Observation runs on
named entity changes, HA start and each minute, including after template reload.
No `for` wait is used for persisted delivery timing. Startup observations can
capture temporary visibility loss. Fridge delivery is immediate as requested;
other fault phone delays use explicit first-detected timestamps.

`sensor.household_attention_inbox` exposes all active items, confirmed fault count,
coverage gaps, overall and category health. Chores and upgrades never increase
fault counts. Unknown coverage produces `incomplete`, including when zero faults
are confirmed. This is coverage of the curated list, not whole-house assurance.

`sensor.household_attention_dashboard.attributes.items` and
`sensor.household_attention_tv.attributes.items` re-filter active records from
the restored dashboard/TV switches. Resolved washing events can appear briefly
as recent event cards for 15 minutes after the actual event timestamp; they are
not active chores or faults. The TV entity includes `schema_version: 1`.
This only supplies HA-owned data; no TV application integration or screen switch
has been installed. All records and evidence require the normal HA authenticated
API. "Private inbox" is not a separate per-user ACL: HA entities/dashboard data
remain available according to HA's access model. No public endpoint is added.

Phone eligibility is evaluated once when an occurrence reaches its agreed delay.
Disabled destinations, uncertain presence and pauses consume that decision too;
later preference changes/return home/pause expiry do not replay it. A new genuine
occurrence is eligible again. This draft has no recovery message, retries,
escalation or arrival reminder. The decision is stored before the external action;
a crash between them can lose a notification. Fault records remain until source
recovery regardless of delivery result. Internet outages can prevent mobile delivery.

Per-row `input_datetime` pauses suppress every route until their absolute expiry,
leaving source evaluation and evidence active and retaining six previous switch
values. They do not acknowledge or manufacture recovery. Category/channel pause
shortcuts remain UI refinement. There is no washing-attended button or persistent
pending-laundry chore in the latest design.

## Washing cutover and one-shot outcome

Before shared routing is enabled, both washing automations retain their exact
legacy phone actions. Once enabled, those old phone actions are skipped and
shared delivery owns them. Switch the gate while no completion notification is
being processed; verify there are no duplicate messages in the Pi trial.

The completion automation always keeps its original `light.laundry_led_strip`
action: 20%, red RGBW `[255, 0, 0, 0]`, long flash. Phone preferences, handler
pauses, presence and notification failures do not control that lighting action.
The user's latest answer explicitly keeps it separate instead of introducing
another attention light helper.

The starting profile enables only Lachlan-home and Nic-home for washing phones.
Freshness and presence are evaluated individually, then rechecked at actual
dispatch. Away/uncertain recipients are skipped with no return-home replay.
Each successful HA notify action emits an occurrence/recipient receipt. The
event resolves when all selected calls are accepted, without claiming handset
receipt or that someone read the message. It resolves as `suppressed` when
there are no eligible recipients. If a call fails or processing is interrupted,
after five minutes it closes as `unconfirmed`, not as delivered, with its outcome
retained. There are no automatic repeats. The finite 15-minute recent-event
display is independent of resolved lifecycle and can be refined in UI review.

An old completion event more than 15 minutes before observation is retained
without sending a backlog or creating a fresh TV card. Regressing/restored older
event timestamps do not replace the latest processed occurrence identity.

## Checks and acceptance

Use the existing Python 3.13 toolchain and `tests/requirements.txt`:

```powershell
python tools/build_attention_controls.py --check
python tests/validate_yaml.py
python -m unittest discover -s tests -v
git diff --check
```

This laptop's `python` command is a Windows Store alias. A pre-existing ignored
Python 3.13.18 under `.tools/python` and dependencies under `.tools/pydeps` were
used; no separate HA environment was created. The YAML checker now includes
untracked non-ignored YAML, so new files are checked before staging, and skips
sensitive filenames without resolving includes or secrets.

Focused tests call the actual production Jinja functions with boundary inputs;
they do not install HA, register fake entities or send simulated notifications.
They cover duplicate occurrences, concurrent independent recovery, unknown input,
recurrence, serialized record continuity, fridge OR/both recovery, off semantics,
washing occurrence/receipts/timeout and old-event suppression, backup matching, grouped unknown updates,
per-person presence/freshness, delay/pauses/no backlog, excluded devices and
restored helper definitions. Inline template compilation is also checked.
These checks cannot establish HA schema/include loading, actual restore/reload
behaviour, HA state tracking dependencies, UI layout or physical delivery.

Local results on 14 November 2026: YAML syntax passed for 18 repository YAML
files; generated outputs matched; all 22 unit checks passed (3 existing and 19
attention checks); `git diff --check` passed. No HA configuration check, reload,
restart, notification or device action was performed.

Pi acceptance remains pending. Record the exact installed commit and observations
for startup/already-present conditions, independent recoveries, persisted records
and selected helper values after an approved restart, unknown/stale evidence,
dashboard/TV re-filtering, pause expiry, no backlog after enabling a phone route,
real phone/presence behaviour, washing migration and unchanged repair controllers.
Use natural events and separately agreed live checks; do not disconnect devices
to manufacture examples. Relevant pending checks keep the PR open.

## Proposed exact-commit deployment and rollback

This is a runbook, not deployment authorisation. Resolve the pending recipient,
presence-age and kiosk choices and review the washing cutover before proposing
a full delivery trial.

1. Complete policy answers, local checks and review the final diff. Commit locally
   on the feature branch; record `git rev-parse HEAD`. A local commit is not a push.
   Obtain explicit push approval, then push and open a PR with checks/limitations.
2. Ask Lachlan to confirm his Pi backup is complete. Record that confirmation.
   A recent automatic-backup timestamp is not a substitute for his confirmation.
3. Obtain separate explicit approval for the named feature-branch commit, file
   install, HA configuration check and required restart/reloads. No merge is
   included. Prepare a manifest with SHA-256 of only the affected files.
4. Re-read the named live configuration files for drift. Reconcile unrelated
   live changes; never overwrite the Pi's `configuration.yaml` wholesale merely
   because Git differs. Save timestamped copies and hashes of every affected
   existing live file, outside Git; record files that were absent before trial.
   Do not read secrets, runtime storage, credentials or backup contents.
5. Install only the approved commit's `configuration.yaml` edits, the two named
   washing phone cutover edits in `automations.yaml`,
   `packages/household_attention.yaml`, the five `attention/*.yaml` files,
   `custom_templates/household_attention.jinja` and
   `dashboards/household_attention.yaml`. The generator/tests/docs are local-only.
   Recheck live washing trigger/actions for drift before applying those edits.
6. Run HA's configuration validation before any approved restart. Stop and restore
   the affected file copies if validation fails. Initial helper/package loading
   may require a full HA restart; do not assume a template reload is sufficient.
   A template reload affects existing YAML feedback entities too.
7. After the separately approved restart, verify file hashes, the expected
   helper/entity IDs (no collision suffixes), inbox and coverage. Set the agreed
   first-install destinations together using the guarded setup script and inspect
   the values. Only then enable shared routing during the approved cutover,
   while no washing completion notification is being processed. Record real event/device acceptance in
   the open PR; refine on the same feature branch with reviewed, approved trials.
8. Roll back using the recorded pre-trial file copies, preserving later unrelated
   changes. Remove only feature files proven absent before the trial. Validate
   and obtain approval for the required restart/reloads. Keep private rollback
   copies and runtime preferences out of Git. Never restore a whole old config
   over unrelated changes.
9. After relevant live acceptance, request explicit merge approval. Keep the PR
   open until that gate passes. Push, deployment, restart and merge approvals are
   separate under [AGENTS.md](../AGENTS.md).
