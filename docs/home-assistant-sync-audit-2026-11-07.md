# Home Assistant sync audit — 7 November 2026

## Verified scope and result

Read-only live API inspection covered all 20 automation configurations, their enabled
states and last-triggered values, the two new automations' sensor/switch states,
limited sensor history, and script/scene/dashboard inventories.
No services were called, notifications sent, devices controlled, files uploaded,
automations updated, reloads or restarts performed.

Fetched GitHub's default-branch automations.yaml through the GitHub connector.
Its blob SHA was 220bc2cd1377629b695bc99ed41cd152ad8a8fc3, identical to the
local file before this audit. This is direct GitHub evidence, not a cached ref.

The local automations.yaml now contains a behaviour-preserving import of the live
definitions. GitHub and Home Assistant were not changed.
This records current behaviour, including the quality issues below.

## Exact drift found

| Automation | Difference from GitHub |
|---|---|
| Toggle Bathroom Lights — 1776408030042 | Added turn_on and turn_off short-press triggers for remote b9f33cdb3a257210cf3bf8d51e051f55 |
| Notify Washing Done — 1776926001082 | State trigger for end/refreshing is disabled live; completion-event trigger remains enabled |
| Manage Living Room Kiosk Phone Charging — 1789173535286 | Entire automation absent from GitHub |
| Notify Washer Cycles ready for clean — 1792576854357 | Entire automation absent from GitHub |

The other 16 definitions matched structurally. No repository-only automation IDs
were found. All 20 were enabled at inspection time.
The automation API does not establish who edited each definition or when.

## Quality review

### Kiosk phone charging — medium priority

The normal hysteresis is sensible: integer battery levels at 40% or below turn
charging on, 80% or above turn it off, and 41–79% retain the current plug state.
Startup, battery updates and five-minute checks provide recovery opportunities.
At inspection the battery was 70% and the charger on, consistent with this logic.

The description promises charging when the phone stops reporting, but the fallback
only handles unknown/unavailable. A stale numeric reading of 80 with the charger
off can remain there indefinitely while the actual battery discharges.
This is a logical gap, not evidence that this failure has occurred.

Recommendation: define a freshness limit using evidence about the phone's reporting
cadence, and give stale/unavailable feedback priority over numeric thresholds.
Do not use last_changed as a heartbeat: an unchanged battery value can still be
reported. Verify what actually updates last_reported before relying on it; an
integration can republish cached data. Guard a missing entity before dereferencing
timestamps. Keep the fail-safe and normal control branches mutually exclusive so
stale high readings cannot cause alternating on/off decisions.

The current unknown/unavailable delay is ten minutes plus up to five minutes until
the periodic check; a restart can reset state timestamps. The exact missing-entity
case was not tested against the live system.

### Washer cleaning reminder — medium priority

The threshold correctly includes integer count 30 and every greater count.
However, a state trigger with no from/to also reacts to attribute-only updates.
Recovery from unknown/unavailable to a count above 29 can send another reminder,
and a downward correction that remains above 29 can also send one.
At inspection the count was 23, so no cleaning reminder was currently due.

Recommendation: use to: null to ignore attribute-only updates, and require numeric
previous/new states with the new count greater than the previous count and at
least 30. This preserves reminders on each subsequent wash; using only a numeric
threshold crossing would lose reminders at 31, 32, etc.
That policy would deliberately skip reconnect/startup reminders and should be
confirmed before changing live behaviour.

The two notifications run sequentially. If the first action errors, the second
may not run. Consider independent delivery if both recipients must be attempted.
No notification delivery was tested.

### Bathroom remote change — behaviour to confirm

Both added buttons run the same toggle logic. Thus pressing the on-labelled button
when lights are on turns them off; pressing the off-labelled button when lights
are off can turn a lighting preset on. This may be intentional, given the alias
Toggle Bathroom Lights. Preserve it unless dedicated on/off behaviour is desired.
Hardware event delivery was not tested.

### Washing completion change — preserve

The disabled state trigger leaves the explicit washing_is_complete event as the
active trigger. This may prevent duplicate completion notifications, but the
reason is not established by configuration alone. Replacing the live file with
the old GitHub version would reactivate that state trigger.

## Validation

- YAML parsed locally with the yaml Node package installed in a temporary folder.
- All 20 resulting definitions equal the live API snapshot structurally, including
  value types, disabled triggers, IDs, conditions and actions.
- IDs are unique.
- git diff --check passed.
- Diff: automations.yaml has 82 added lines, no deletions; 10 bathroom trigger
  lines, one disabled-trigger flag, and 71 lines for the two missing automations.
- This is configuration comparison and static review, not a Home Assistant schema
  validation, execution trace review, or physical/device test.

## Remaining sync work

- Live script inventory has 20 entries; local scripts.yaml has 20 definitions.
  Counts alone do not establish matching contents. Full live script definitions
  were not accessible through the available script inventory tool.
- Eight live fan scenes exist (six speeds and swing on/off). Local scenes.yaml
  parses as null (no definitions). These might be integration-provided scenes;
  do not assume they can or should be recreated as YAML scenes.
- Live dashboards include YAML Our Home V2 and UI-storage Our Home and Fridge.
  UI-storage dashboards are not covered by the YAML dashboard file. Export and
  compare their configurations explicitly.
- Existing local changes in templates.yaml and dashboards/our_home_v2.yaml,
  .vscode/settings.json, .codex/, AGENTS.md and the fan notes were left untouched.
  They must be reviewed separately before any broad commit or sync.
- Live direct file reads failed because the connector's SSH file access is not
  configured. No credentials or secret files were read or requested.
- Helpers, integration settings, custom components, blueprints and other files
  have not been exhaustively compared. “Everything synced” is not yet established.

## Suggested sequence

1. Review this behaviour-preserving automation import and commit it locally as a
   baseline. Push only with explicit approval. No HA deployment is needed for
   this baseline: it already represents the live automation configurations.
2. Prepare and validate the agreed charging/reminder improvements separately.
   Show their exact diff and obtain explicit approval before applying live.
3. Export UI dashboards and inspect how the fan scenes and helpers are supplied.
   Compare accessible YAML files individually; exclude secrets, authentication,
   runtime databases and other machine state from version control.
4. Choose Git as the reviewed configuration baseline. After manual UI edits,
   export and review the affected configuration before the next deployment.
   Recheck live drift immediately before any approved write.
