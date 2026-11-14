# Household attention feature-branch trial record

Status: **installed for trial; acceptance incomplete; not merged**.
On 14 November 2026 Lachlan accepted the guide, confirmed his Pi backup complete,
then explicitly approved the branch push/PR and the described trial of `6b36c4a`,
including one Core restart, kiosk sensor enablement and starting preferences/
shared-routing setup. These approvals do not include merge, forced outages or
another restart. Keep [PR #11](https://github.com/lachlanw-117/Wright-Home-Assistant/pull/11)
open until relevant acceptance passes.

## Revision and rollback record

| Field | Value |
|---|---|
| Source commit | `6b36c4a9518a4f424582b4a4240aef17809ba6ff`; all ten runtime files match exactly |
| PR | #11 open; pushed head `78528d86b751a5049d7af9f120e9c4ebfcd28a1e` adds documentation only after runtime commit |
| Pi backup confirmed complete by Lachlan | Yes, explicitly before installation |
| Named install/restart/setup approval | Yes, explicitly in chat before installation |
| Live access route | Direct SSH/SCP with existing authentication and strict saved-host verification; no private key viewed/copied or credentials inspected |
| Named live files compared for drift | `configuration.yaml` and `automations.yaml` byte-for-byte equal to baseline `9b65132` before staging and again before installation |
| Timestamped rollback copies and hashes | `/share/household-attention-trials/20261114-6b36c4a/rollback/`; preparation recorded `2026-11-14T05:52:23Z`; directory mode 700; hashes verified |
| Feature files absent before trial | All eight new runtime files; `packages/`, `custom_templates/`, `attention/` directories also absent; existing `dashboards/` preserved |
| Actual installed file hashes | Ten checks passed immediately after installation and again after restart; see table below and Pi `installed.sha256` |
| HA configuration check | `ha core check` completed successfully before restart |
| Restart/reloads performed | One approved Core restart; ready store observed at `2026-11-14T05:54:28Z`; no template reload or additional restart |
| Shared routing/setup state | Starting profile applied once at 16:55:06 AEDT; all 36 active destinations checked; setup flag on; routing enabled at 16:55:36 AEDT with washer `initial` and no dispatch in progress |
| Kiosk enablement | Still disabled by integration; pending manual enablement through HA entity settings; connector has no registry-edit operation |

## Installed hashes

All times below are 14 November 2026. Installation completed at 16:52:41 AEDT
(`05:52:41Z`). No live merge was necessary because both existing files matched the
reviewed baseline exactly. Only the ten allowlisted runtime files were installed.

| File | SHA-256 |
|---|---|
| `configuration.yaml` | `b33a2fe08cca91e625d8fe7288cb4f9446e83f4f087adf4febd49a6d7e44648e` |
| `automations.yaml` | `cc797858b88c2390218d4714264d985139fab9c040f22bc33d1e93143fa06975` |
| `packages/household_attention.yaml` | `9633c71f58dca775fdb26e7fbc20301dae3ae13a49837501e20ca0d23d784949` |
| `custom_templates/household_attention.jinja` | `06980c803f12324e2a6b3ce902e21854dc97f452bc3144b2672c16405664a253` |
| `dashboards/household_attention.yaml` | `9aa377550bad94b434b7f467da51212f4ab0e0546d1d16acc484828f0319e9df` |
| `attention/sources.yaml` | `f3653de910af718f650f5cd3b0f176b35a08ef41f50fa72dc71896a7a4861c57` |
| `attention/delivery_controls.yaml` | `1d251517cbd389cd371fdf96b2d37241f816421c5f5a2a23d8618d417e8dd5ac` |
| `attention/pauses.yaml` | `b8b55809dcdcbb3653f53f2154cbe96f5d7fdecb09a459ebabd2b90d0498a6a8` |
| `attention/watched_entities.yaml` | `8bfb768e1cc3eb2adc5be8144ff935ab8b371270dc7b06a4f414c2522cd43544` |
| `attention/starting_destinations.yaml` | `ca5d201204072a8e2963515744e9c67e1b08535b121cd48e8295136e9e3bc561` |

Pre-trial `configuration.yaml` SHA-256:
`a5ffca427aaee72df1c3381d300cb901102c8c254f5eff1a1d651a9febf7b5bd`.
Pre-trial `automations.yaml` SHA-256:
`e5b6d18afef889d8f2e8a9b1eb53dc9babd47d6105a4305a7a0702ccbdcc0928`.

The earlier browser-terminal attempt was stopped following an unintended
clipboard paste. Execution of that pasted text was not established. The subsequent
SSH preflight verified both named configuration files still matched baseline.
All staging, backups, installation and hash checks used direct SSH/SCP, without
browser terminal input. No new SSH server, credentials or access settings were created.

Never put credentials, private keys, secrets, runtime storage or backup contents
in this record. Record only safe revision/path/hash/results metadata.

## Acceptance evidence

| Check | Local evidence | Pi / real-device evidence |
|---|---|---|
| First-install include/schema/entity loading | YAML/template syntax only | HA check passed; store/inbox/dashboard/TV and delivery automation loaded; 72 row helpers, two flags and nine pauses found at expected IDs |
| Nine real source rows | Registry/state mappings recorded; kiosk registered but disabled | All nine store records loaded with real evidence; kiosk still disabled/unknown; enable/report check pending |
| Duplicate observations | Actual reducer test passes | Upgrade occurrence ID/first-detected timestamp unchanged across periodic observations; no duplicate record; broader fault observations pending |
| Concurrent faults/recovery | Actual reducer tests pass | Pending natural evidence; no forced disconnections |
| Unknown/stale does not clear faults | Actual reducer/adapter tests pass | Pending real observations |
| Already-present conditions reconcile | Startup/periodic paths implemented | Existing Core 2026.11.0 to 2026.11.1 upgrade captured at startup, with incomplete firmware coverage retained |
| Records/preferences survive restart | Serialized continuity and no-initial helper checks | Pending approved restart with before/after evidence |
| New occurrence after recovery | Reducer test passes | Pending natural recurrence |
| Fridge plug OR LG, both recovery | Reducer cases pass | Mapping/status evidence; loss/recovery awaits natural event |
| Other fault delays, no repeats | Boundary/one-time routing tests pass | Pending natural eligible fault |
| Simple per-recipient phones, presence parked | Actual routing/profile tests pass | All 36 active starting switches match guide; routing on; real handset/UI acceptance pending |
| Preference enable/pause expiry does not resend | Reducer tests pass | Enabling starting preferences and routing did not call send script or replay existing washing/upgrade records; pause/expiry checks pending |
| Dashboard/TV filters | Templates/config checked | Authenticated dashboard config returns three expected views; both filtered sensors show selected recent washing and grouped upgrade; visual layout/interactive changes pending; TV app unchanged |
| Upgrades grouped with unknown coverage | Actual adapter/health tests pass | One Core upgrade with installed/latest versions; unknown firmware sources retain incomplete coverage, without extra fault count |
| Backup recovery requires later success | Actual adapter cases pass | Real failure/recovery awaits natural event; attempted backup insufficient |
| Washing one-shot identity and receipts | Actual reducer tests pass | Existing 16:45:57 event retained as suppressed/recent at startup, without phone replay; new natural wash/receipts/handsets pending |
| Washing lighting unchanged/no duplicate phones | Exact original actions/trigger preserved in guard | Cutover while washer `initial`; no handler send calls; actual next wash and red strip pending |
| Operational health excludes chores/updates | Actual aggregate-template test passes | Zero confirmed faults despite grouped upgrade/recent washing; health incomplete due kiosk, coverage gaps kiosk/upgrades |
| Existing internet/kiosk repairs independent | Existing automation checks and preservation pass | Pending real operational observation |
| Dad's desk plug excluded | Static source/trigger exclusion passes | Store contains only the nine reviewed keys, no Dad's desk record/route; its normal HA integration remains outside handler |

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
