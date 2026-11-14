# Household attention feature-branch trial record

Status: **not deployed; no live acceptance claimed**. No Pi backup confirmation,
push, install, restart, sensor enablement or merge approval has been recorded.
Lachlan has explicitly held push, PR creation and trial until the user guide and
as-built explanation have been reviewed. Earlier approval questions are unanswered;
they must not be interpreted as consent.
Use the exact source SHA and manifest from the generated trial bundle. Keep the
PR open until relevant acceptance passes.

## Revision and rollback record

| Field | Value |
|---|---|
| Source commit | Candidate is identified by generated bundle manifest; no deployed SHA yet |
| PR | Not opened; push approval pending |
| Pi backup confirmed complete by Lachlan | Pending |
| Named install/restart/setup approval | Pending |
| Live access route | File connector lacks SSH configuration; existing Pi workflow/user-assisted comparison needed |
| Named live files compared for drift | Not done |
| Timestamped rollback copies and hashes | Not created |
| Feature files absent before trial | Not checked |
| Actual installed file hashes | Not recorded |
| HA configuration check | Not run |
| Restart/reloads performed | None |
| Shared routing/setup state | Not installed |

Never put credentials, private keys, secrets, runtime storage or backup contents
in this record. Record only safe revision/path/hash/results metadata.

## Acceptance evidence

| Check | Local evidence | Pi / real-device evidence |
|---|---|---|
| First-install include/schema/entity loading | YAML/template syntax only | Pending HA config check, restart and expected entity IDs |
| Nine real source rows | Registry/state mappings recorded; kiosk registered but disabled | Reverify; enable/report kiosk sensor as approved |
| Duplicate observations | Actual reducer test passes | Pending natural repeated observations |
| Concurrent faults/recovery | Actual reducer tests pass | Pending natural evidence; no forced disconnections |
| Unknown/stale does not clear faults | Actual reducer/adapter tests pass | Pending real observations |
| Already-present conditions reconcile | Startup/periodic paths implemented | Pending real startup evidence |
| Records/preferences survive restart | Serialized continuity and no-initial helper checks | Pending approved restart with before/after evidence |
| New occurrence after recovery | Reducer test passes | Pending natural recurrence |
| Fridge plug OR LG, both recovery | Reducer cases pass | Mapping/status evidence; loss/recovery awaits natural event |
| Other fault delays, no repeats | Boundary/one-time routing tests pass | Pending natural eligible fault |
| Simple per-recipient phones, presence parked | Actual routing/profile tests pass | Pending real phone/UI acceptance |
| Preference enable/pause expiry does not resend | Reducer tests pass | Pending UI check using existing records |
| Dashboard/TV filters | Templates/config checked | Pending authenticated entity/UI checks; TV app unchanged |
| Upgrades grouped with unknown coverage | Actual adapter/health tests pass | Pending comparison with real update entities/details |
| Backup recovery requires later success | Actual adapter cases pass | Real failure/recovery awaits natural event; attempted backup insufficient |
| Washing one-shot identity and receipts | Actual reducer tests pass | Pending natural wash and actual phone outcomes |
| Washing lighting unchanged/no duplicate phones | Exact original actions/trigger preserved in guard | Pending real wash and red strip; cutover only while idle |
| Operational health excludes chores/updates | Actual aggregate-template test passes | Pending live health/coverage comparison |
| Existing internet/kiosk repairs independent | Existing automation checks and preservation pass | Pending real operational observation |
| Dad's desk plug excluded | Static source/trigger exclusion passes | Confirm no handler record/route; normal HA integration remains outside handler |

Record date/time, exact revision, actual source/occurrence identifiers and observed
results during trial. Mark checks that await natural events explicitly. Do not
substitute artificial HA states, fake devices, simulated notifications or deliberate
household outages. Pending relevant acceptance keeps the merge gate open.

## Closeout

| Gate | Result |
|---|---|
| Relevant live/device acceptance | Pending |
| Material limitations accepted / remaining work recorded | Pending |
| Testing session closed | Pending |
| Explicit merge approval | Not requested |
