# Household attention — as built and trial status

**Review status:** installed on the Pi for trial; live acceptance is incomplete.
This document describes runtime commit
`6b36c4a9518a4f424582b4a4240aef17809ba6ff`. The companion
[user guide](household_attention_user_guide.md) explains everyday operation and
the differences between the new handler and existing washing delivery.

After reviewing these documents, Lachlan confirmed his Pi backup complete and
explicitly approved the push/PR and named `6b36c4a` trial, including one Core
restart and setup. That installation and restart are complete; shared routing is
on. Kiosk enablement, actual phones/light/UI and restoration checks remain pending.
See the [trial record](household_attention_trial.md) for hashes, times and evidence.

Branch: `feature/household-attention-handler`, based on
`9b6513203ac89764d8669aaaf998b1878e2199ba`. The supplied
[accepted handoff](household_attention_accepted_handoff.txt) is a historical
requirements record. The decisions below supersede its earlier proposals.
The branch is pushed through documentation commit `78528d8`, and
[PR #11](https://github.com/lachlanw-117/Wright-Home-Assistant/pull/11) is open.
Installed runtime files match `6b36c4a` exactly. No merge has occurred.

## Prepared living-room extension — not yet installed

The latest request adds separate availability records for the TV, dining-table
and basketball-hoop light pairs, each watching its two verified physical bulbs.
The [extension and wall-switch trial](household_attention_living_room_trial.md)
documents the member map, twelve-row candidate, six-file delta, checks and proposed
installation. Existing installed nine-row results below remain historical trial
evidence for `6b36c4a`; the new revision has no live acceptance yet.

## Implementation status at a glance

| Capability | Actual implementation | Verification status |
|---|---|---|
| Shared attention store | One native trigger-based sensor, one current/last record per source | Loaded with nine records on Pi; later restart restoration pending |
| Nine source rules | Fridge, Dyson, WAN, washer availability, kiosk Wi-Fi, wash completion, cleaning, backup failure, upgrades | Real mappings inspected; kiosk is registered but disabled |
| Everyday controls | Four active destinations per row plus an absolute row pause | Expected helpers and all starting values checked live; visual UI pending |
| Presence split | Parked; old home/away helpers dormant | Routing test proves they do not control current delivery |
| Phone delivery | Once per occurrence; current destination/pause rechecked before sending | Local selection/receipt checks; real push receipt not tested |
| Washing migration | Legacy phone branches kept behind shared-routing handover; light action preserved | Exact original triggers/actions checked locally; real wash pending |
| Dashboard/inbox | YAML views and HA sensors | Sensors and three-view authenticated configuration loaded; visual layout pending |
| TV delivery | HA-owned filtered data contract only | No TV app consumer implementation or visible TV delivery in this change |
| Health/coverage | Fault-only operational health; separate source uncertainty | Actual inline template test passes |
| Trial materials | Exact-commit ten-file ZIP, hashes, review diff, rollback and acceptance record | Installed ten-file hashes match; rollback copies saved; acceptance incomplete |

## Current decisions - 14 November 2026

Lachlan parked the phone home/away split and asked to proceed with everything
else. The current UI has four independent destinations per row: HA dashboard,
TV screensaver, Lachlan phone and Nic phone. Phone routing does not read Person,
GPS, router presence or presence freshness. Washing can therefore notify both
selected people wherever they are. Router/Companion presence research and
unknown-presence fallback decisions are deferred, not trial blockers.

The earlier six helper IDs per row are preserved without resetting their restored
values. Their home/away controls are hidden and unused. Two new plain phone
controls are active instead; dashboard/TV controls retain their existing IDs.
`attention/policy.yaml` is parked research configuration, not a runtime include
or deployment file. Resuming presence routing requires a reviewed migration.

| Source | Starting destinations | Phone delay and lifecycle |
|---|---|---|
| Fridge visibility loss | Dashboard, TV, Lachlan, Nic | Immediate; one item; clear only when both channels recover |
| Dyson unavailable | Dashboard, TV, Lachlan | 15 minutes; clear on valid recovery |
| Internet WAN disconnected | Dashboard, TV, Lachlan | 15 minutes; clear on valid recovery |
| Washer unavailable | Dashboard, TV, Lachlan | 15 minutes; separate from washing finished |
| Kiosk reports off Wi-Fi | Dashboard, TV, Lachlan | 15 minutes; fresh connection evidence required |
| Washing finished | Dashboard, TV, Lachlan, Nic | Immediate one-shot event; close after dispatch outcome |
| Washer cleaning needed | Dashboard, TV, Lachlan | 15 minutes; one occurrence until valid count falls below 30 |
| Backup failure | Dashboard, TV, Lachlan | 15 minutes; later successful automatic backup clears |
| Grouped upgrades | Dashboard, TV | Phone switches off initially; no per-component alerts |

All faults capture immediately, independently of repair actions. There are no
automatic repeats, escalations or recovery messages. Expiring per-row routing
pauses preserve destination values and do not manufacture source recovery.
The second Dyson is not in HA and was explicitly removed from scope. Dad's desk
plug is excluded from every handler source/trigger list, including firmware.

## Verified real source map

Read-only inventory on 14 November established HA Core **2026.11.0**. It does not
prove live configuration files match Git. No credentials, secrets, private keys,
runtime storage or backup contents were read or copied.

| Source | Entity and interpretation |
|---|---|
| Fridge plug | `switch.kitchen_fridge_power_plug`, ZHA |
| LG fridge | `number.refrigerator_fridge_temperature`, LG ThinQ; a setpoint, not measured cooling proof |
| Dyson | `fan.purifier_hot_cool_de_nox`, Matter; `off` is normal |
| Internet | `binary_sensor.archer_ax73_wan_status`, UPnP connectivity; `off` is disconnected; registry ID matches existing repair trigger |
| Washer availability | `sensor.washer_current_status`, LG ThinQ; `initial` is normal |
| Washing event | `event.washer_notification`, `event_type: washing_is_complete`; state is occurrence timestamp |
| Washer cleaning | `sensor.washer_cycles >= 30`; invalid/missing is not zero |
| Backup | `event.backup_automatic_backup` and `sensor.backup_last_successful_automatic_backup` |
| Upgrades | Explicit verified entity list in `attention/sources.yaml`, excluding Dad's desk plug |
| Kiosk Wi-Fi | Registered `sensor.iphone_8_connection_type`, currently disabled; enable and verify reports during separately approved setup |

Fridge unavailability is plug OR LG, retaining both channels' evidence. One good
channel cannot clear the other bad/unknown channel. Wording says HA has lost
visibility, not that cooling stopped. Existing repair automations are unchanged
and cannot suppress capture or resolve a record merely by attempting a repair.

Kiosk `Wi-Fi` is connected; `Cellular`/`No Connection` are explicit off-Wi-Fi
reports. Draft sample freshness is 15 minutes. Old reports become `stale` /
uncertain, never proof the phone powered off. GPS, charger state and stale battery
alone are not outage detectors. This adapter is prepared against a real registered
entity, but runtime coverage remains pending enabling and verifying that sensor.

Phone actions were verified as `notify.mobile_app_big_lws_iphone_14` (Lachlan)
and `notify.mobile_app_nichola_s_iphone` (Nic), matching existing washer device IDs.
Source rules remain reviewed Git configuration; daily destination values live
in restored HA state.

The first draft covers backup failures, washing, grouped upgrades and curated
availability. Lights/group membership, rapid battery-drop thresholds and actionable
authentication sources have not been agreed/verified and are not silently enabled.
Real battery histories were inspected but do not establish reliable rapid-drain
rules. Backup staleness, external HA/Pi outage monitoring and causal dependency
grouping remain outside this slice. The inbox is not whole-house assurance.

## Implementation and contract

| File | Responsibility |
|---|---|
| `attention/sources.yaml` | Source meanings, timing and starting profile |
| `custom_templates/household_attention.jinja` | Actual observation/lifecycle/routing functions |
| `packages/household_attention.yaml` | Restored store, derived views/health, delivery and guarded setup |
| `attention/delivery_controls.yaml` | Restored active/dormant helper definitions; no `initial` values |
| `attention/pauses.yaml` | Restored absolute pause deadlines |
| `attention/watched_entities.yaml` | Targeted source triggers, no whole-instance scans |
| `attention/starting_destinations.yaml` | Explicit first-install profile; no automatic reset |
| `dashboards/household_attention.yaml` | Inbox, routed dashboard and four active controls per row |
| `tools/build_attention_controls.py` | Local static-file generator with `--check` |
| `tools/package_attention_trial.py` | Exact-commit trial ZIP, manifest and diff; no live actions |

`configuration.yaml` adds one explicit package include and one YAML dashboard.
`automations.yaml` changes only phone cutover in the two washing automations.
The completion trigger and red laundry light action are preserved. Other repair
automations, `scripts.yaml` and `templates.yaml` are unchanged.

The store is `sensor.household_attention_store.attributes.records`, a dictionary
with one current/last occurrence per source key. Records contain stable occurrence
identity, category/kind/severity, active/resolved lifecycle, first-detected /
last-valid-observation / resolved timestamps, source evidence, observation quality
and grouped details. Phone selection, accepted recipients and bounded dispatch
outcomes are also retained. There is no unbounded archival inbox.

Duplicate observations keep occurrence identity and first detection. Verified
recovery clears only that source; recurrence gets a new occurrence. Unknown or
stale input cannot resolve active faults. Healthy-to-unknown is a coverage gap,
not an invented physical failure. Explicit unavailable is evidence of HA visibility
loss. Cached entity availability is not independent proof of fresh physical telemetry.
Backup attempts/in-progress never clear failure; only a later successful automatic
backup satisfies the accepted matching rule. Unknown update components retain
last-confirmed pending details until confirmed off.

Observation runs on named changes, HA start and every minute, including after
reload. Delivery durations use explicit timestamps, not `for` waits. Trigger-based
restoration provides continuity, not guaranteed archival durability or exactly-once
external delivery after a crash. Startup/reload/restart behaviour still needs Pi
acceptance. Immediate fridge delivery can report real startup visibility loss.

`sensor.household_attention_inbox` exposes active items, recent one-shot events,
confirmed fault count, operational/category health, and separate coverage gaps.
Operational health uses fault sources only; washing and updates never count as
faults. Unknown fault coverage prevents an unqualified healthy result. Unknown
update/event coverage is reported separately rather than inventing operational
failure. Categories containing no fault sources report `not_applicable` health.

`sensor.household_attention_dashboard.attributes.items` and
`sensor.household_attention_tv.attributes.items` re-filter the active records and
finite recent event cards using current helper values. TV data has schema version
1. No TV app changes or screen-switch actions are included. "Private inbox" uses
normal authenticated HA access, not a new public endpoint or separate per-user ACL.

Phone eligibility is consumed once per occurrence at its delay, even if disabled
or paused. Enabling a destination or shared routing later does not replay backlog.
At dispatch, destination and pause are checked again. Delivery failure cannot
clear an active fault. A crash between recording selection and sending can lose
a notice; there are no automatic retries. Internet outages can block phone delivery.

## Setup and washing cutover

Helpers start off on first installation and restore thereafter. The explicit
`script.household_attention_apply_starting_preferences` applies the profile once,
guarded by a restored completion flag. It never runs on restart or deployment and
does not enable routing. Inspect the chosen controls before switching shared
routing on. Preserve source keys/helper IDs in later configuration changes.

Before `input_boolean.attention_routing_enabled` is on, the two washing automations
keep their original phone actions. After cutover, those phone actions are skipped
and shared delivery owns them. Perform cutover while no washing completion is
being processed. Existing already-captured issues remain in the inbox without a
surprise resend. The completion light action remains independent: red RGBW
`[255, 0, 0, 0]`, 20%, long flash on `light.laundry_led_strip`. No extra light helper
is introduced, as requested.

This gate is a handover control, not a global notification mute. Setting it off
returns washing and cleaning to their original direct phone actions, which ignore
the new row switches/pauses. The original completion light action also remains
outside handler routing. After handover, everyday suppression should use the
row's recipient controls or pause, with shared routing left on.

Washing is a one-shot event. Each selected successful HA notify call emits an
occurrence/recipient receipt. After all selected calls are accepted the event
resolves; this is not proof of handset receipt or reading. With no eligible routes
it resolves as suppressed. Interrupted/failed dispatch closes after five minutes
as `unconfirmed`, not delivered, with outcome retained. Recent washing cards
expire 15 minutes after the actual event. Historical events older than that cannot
create a fresh card or phone backlog. Older restored event timestamps cannot
replace the latest processed identity. No attendance button or arrival reminder
is needed.

Per-row pauses suppress all handler routes until their absolute expiry, retaining
the previous controls while source evaluation continues. They do not affect the
independent laundry lighting. Category/channel pause shortcuts remain UI refinement.

## Validation and remaining runtime gates

```powershell
python tools/build_attention_controls.py --check
python tests/validate_yaml.py
python -m unittest discover -s tests -v
git diff --check
```

Local results: **25 tests passed**, generated-file checks passed, YAML syntax
passed for 19 repository files, and diff whitespace checks passed. Python
3.13.18 and the pre-existing ignored `.tools/pydeps` were used because `python`
on this laptop points to the Windows Store alias. No separate HA installation,
fake device inventory or simulated-notification service was created.

Tests exercise the actual production Jinja and inline health templates:
duplicates, independent recovery, recurrence, serialized record continuity,
unknown/stale evidence, source off semantics, grouped updates, backup recovery,
one-shot receipts/timeout, old event suppression, pauses/no backlog, explicit
recipient controls independent of presence, exclusions and helper preservation.
The original automation guard additionally verifies preserved triggers, original
legacy phone branches and exact laundry lighting action.

Local checks do not resolve HA includes/secrets, validate HA's complete schema,
prove actual restoration or check physical delivery/UI layout. The [trial record](household_attention_trial.md)
must record what was actually observed and what remains pending natural events.
Relevant pending acceptance keeps the PR open; local/CI tests alone do not pass it.

The file connector lacks SSH configuration, but direct SSH/SCP with existing
authentication and strict saved-host verification succeeded during the approved
trial. Live `configuration.yaml` and `automations.yaml` matched baseline `9b65132`
byte for byte before staging and installation. All eight new files were absent.
Rollback copies were saved before installation; all ten installed hashes matched
`6b36c4a` both before and after the approved restart. No new access method/add-on
was installed and no credentials were inspected. HA's configuration check passed;
the store and dashboard configuration loaded. Kiosk is still disabled and actual
phones/light/UI/restoration acceptance remains pending in the trial record.

## Exact-commit trial and rollback

1. Review the diff/checks, commit on the feature branch, then package that exact
   SHA with `python tools/package_attention_trial.py --revision SHA --output PATH`.
   The ZIP contains only ten allowlisted runtime files, a SHA-256 manifest,
   comparison diff and runbook; it reads committed blobs, not working-tree files.
   Dormant `attention/policy.yaml`, tests/tools/docs and runtime values are not
   deployment payload. Do not extract payload blindly over `/config`.
2. Obtain explicit push approval, push and open the prepared PR. Keep it open
   throughout trial and refinement. Prepare a new exact-commit bundle after any
   runtime change; do not silently deploy branch HEAD.
3. Confirm Lachlan's Pi backup is complete. An automatic-backup timestamp is not
   a substitute. Obtain named approval for this SHA, affected-file installation,
   HA configuration validation, required restart/reloads, kiosk sensor enablement,
   and first-install helper setup/routing cutover. Merge is a separate approval.
4. Before installation, compare the named live files for drift and save timestamped
   rollback copies/hashes outside Git. Record which feature files were absent.
   Reconcile `configuration.yaml` and the two washing phone changes against any
   unrelated live edits; do not overwrite them wholesale. If a reviewed live merge
   changes payload content, record its deployed hash and reconcile that exact
   content to Git before continuing the trial. Never read secrets/runtime storage.
5. Install only approved files/merges. Validate HA configuration before the approved
   restart; stop/restore affected copies if validation fails. New helper/package
   loading can require a full restart. Template reload also affects existing YAML
   feedback sensors, so do not substitute an unapproved reload.
6. Verify installed hashes, expected entity IDs without collision suffixes, inbox,
   health/coverage and controls. Enable the existing kiosk Connection Type sensor
   in the app/registry as approved; verify real ID/value/update cadence before
   accepting that adapter. Apply first-install preferences once, inspect them,
   then perform the approved shared-routing cutover while the washer is idle.
7. Use natural household events and explicitly approved real checks. Do not
   disconnect devices or manufacture fake entities to create acceptance examples.
   Record faults/recovery independently, unknown/stale handling, grouping, no
   backlog, real phones/light behaviour and restored preferences/records after
   an approved restart. Refine on the feature branch and repeat relevant checks.
8. Rollback restores only affected pre-trial copies, preserving later unrelated
   edits; remove only feature files known absent before trial. Validate and obtain
   approval for required restart/reloads. No secret/runtime state is in the bundle.
9. Request merge approval only after relevant live acceptance. Deployment,
   restart, push and merge approvals remain separate under [AGENTS.md](../AGENTS.md).

## Parked architecture research

Native template records/helpers were selected for this bounded slice on installed
HA 2026.11.0. They satisfy restored preferences and typed record/consumer needs
without a runtime AI or new custom integration. Alert2 offers condition/event
lifecycle and reminders, but would still need household-specific routing/contract
work and has periodic-restoration limitations. Native Alert is simpler but does
not supply this typed shared inbox. Supernotify routing is not needed for the
current plain per-person switches. See [template restoration](https://www.home-assistant.io/integrations/template/),
[helper restoration](https://www.home-assistant.io/integrations/input_boolean/),
[Alert2](https://github.com/redstone99/hass-alert2), and
[Supernotify](https://supernotify.rhizomatics.org.uk/latest/configuration/deliveries/).

If presence splitting resumes: HA currently exposes only three mobile-app
trackers; the AX73's existing [UPnP integration](https://www.home-assistant.io/integrations/upnp/)
does not expose clients. The [third-party router integration](https://github.com/AlexandrErohin/home-assistant-tplink-router)
lists AX73 V1/V2.0 tracking, with firmware/admin-session caveats; this household's
hardware/firmware compatibility has not been verified and nothing was installed.
[Companion background timing](https://companion.home-assistant.io/docs/core/sensors/)
is iOS-controlled; Local Push may improve sensor updates but is not a guaranteed
GPS heartbeat. These are parked research findings, not current routing dependencies.
