# Living-room light pairs — extension and wall-switch trial

Status: **prepared locally; not installed**. The Pi still runs runtime commit
`6b36c4a`. This extension adds three independent pair records to that handler;
it does not replace the room's lighting controls. Deployment, another Core
restart and pushing this revision require approval after review. PR #11 remains
open; no merge is approved.

## Verified mapping and rules

Read-only inspection on 14 November 2026 showed the Living Room Lights group
contains three pair groups. Each pair contains the following two Matter bulbs,
all currently reachable with state `off`:

| Inbox/control row | Source key | Physical bulbs watched |
|---|---|---|
| HA cannot reach one or both living-room TV lights | `living_room_tv_lights_unavailable` | `light.living_room_tv_light_1`, `light.living_room_tv_light_2` |
| HA cannot reach one or both dining-table lights | `living_room_dining_lights_unavailable` | `light.living_room_dining_table_light_1`, `light.living_room_dining_table_light_2` |
| HA cannot reach one or both basketball-hoop lights | `living_room_hoop_lights_unavailable` | `light.living_room_basketball_hoop_light_1`, `light.living_room_basketball_hoop_light_2` |

Lachlan specifically requested monitoring the pairs rather than one room-wide
item. Each pair watches its two physical bulbs because a group entity can remain
available when only one member is unavailable. Aggregate room/pair entity states
are not used to mask a member fault. `light.living_room_tradfri` is actually named
Main Bedroom Light 2, is not a member of these pairs and is excluded.

- Either bulb `unavailable`: capture one fault for that pair immediately when HA
  reports it, retaining both member statuses.
- Both bulbs valid again (`on` or `off` in normal operation): resolve that pair.
- Unknown or missing evidence: report incomplete coverage; retain any existing
  fault until valid recovery. Do not invent power loss from unknown data.
- Pair records, recovery, occurrence identity, destination controls and pauses
  are independent. Losing both bulbs of a pair remains one item; losing bulbs
  in two pairs creates two items.
- Saved light destinations are dashboard and TV data only. Both phone controls
  start off. If a phone destination is later selected, the normal 15-minute delay
  and once-per-occurrence policy apply. No repeat or recovery phone message.
- A wall switch removing mains power can produce an availability fault. Turning
  a reachable bulb off through HA is normal and must not produce a fault.
- Matter's detection/recovery latency is separate from handler capture. There
  is no guaranteed number of seconds from the physical switch to an HA state
  change. Inspect the bulb states while waiting; do not manufacture HA states.

## Local diff and checks

Six runtime files change: `attention/sources.yaml`, generated delivery controls,
pause helpers, watched entities, starting destinations and the attention dashboard.
The existing availability reducer handles the new rows without code changes.
The existing package, washing automations and root configuration are unchanged.

The resulting source list has twelve rows. There are four active controls and
one absolute pause per pair. Existing helper definitions still have no forced
initial values. The generator keeps its dormant home/away definitions, while
the runtime continues to use only plain per-person phone controls.

27 local tests pass, including both-member loss, incomplete recovery, recurrence
and independent pair recovery using the actual production functions. Generated
files and YAML syntax checks pass. These checks create no HA instance, fake
devices or notification environment. Physical acceptance is pending installation.

## Proposed installation

1. Identify the exact new feature commit from its generated ten-file bundle
   manifest. Review its six-file runtime delta from installed `6b36c4a`.
2. Obtain approval to push this revision and install that delta with one further
   Core restart. Keep the existing PR open. Backup confirmation is already
   recorded for the current trial; save fresh affected-file rollback copies.
3. Check all ten installed files still match the recorded `6b36c4a` manifest.
   Check the new helper IDs are absent, and preserve existing restored values.
4. Back up the six affected files and hashes to a new dated trial directory.
   Install only the six verified changed files. Check all ten runtime hashes
   against the new manifest. Run HA configuration validation before restart.
5. Perform the approved restart. Verify all twelve records and each pair's
   controls/pause loaded. Compare the existing preferences and prior occurrence
   IDs before/after; do not rerun/reset the whole starting profile.
6. Enable only the six new pair dashboard/TV switches. Confirm all six new phone
   switches remain off, existing destinations are unchanged and shared routing
   remains on. New rows restore their values normally thereafter.
7. Observe the checks below. Record exact revision, times, source states and
   outcomes. Another restart or merge remains separately gated.

## Wall-switch acceptance

After installation is confirmed:

1. With all six bulbs reachable, check there are no active light-pair faults.
   They may be normally on or off.
2. Turn off the physical wall switch for one fitting. Wait until HA reports one
   or both of its bulbs `unavailable`. Expect one matching pair item in Inbox
   and Dashboard, with both member statuses, and no phone alert by default.
3. While it remains unavailable, inspect repeated observations. There should
   still be one pair record, with the same occurrence ID/first-detected time.
4. Turn that pair's **HA dashboard** control off and on: hide/show its Dashboard
   item while Inbox retains it. An expiring pair pause should similarly hide it
   from routed views and then let it return if still unavailable.
5. Restore mains power. Once both bulbs report valid states, expect that pair's
   item to clear. A remaining unknown/unavailable member must keep it active.
6. Repeat for the other fittings. If two pair faults coexist, restoring one must
   leave the other active. A later loss after recovery gets a new occurrence.

The TV switch filters HA data; it does not add a visible TV card. Fault recovery
does not itself send a phone message or change the physical light state.

| Acceptance | Result |
|---|---|
| Local checks | Passed as above |
| New exact revision installed / hashes | Pending |
| Existing records/preferences survive restart | Pending |
| All three pair rows/controls loaded | Pending |
| Wall-switch member loss/recovery and no duplicates | Pending |
| Two pair faults recover independently | Pending |
| Pair routing/pause behaviour | Pending |
| Merge approval | Not requested |
