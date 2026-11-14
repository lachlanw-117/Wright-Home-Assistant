# Grouped-device extension: review and trial

Status: **installed for trial; physical and visual acceptance remain open**.
PR #11 remains open. The Pi now runs exact runtime
`e2f0bbc7adebcfca6a993c36f4ac038f355328d6`, replacing recorded `3cc4573`.

Installed runtime commit: `e2f0bbc7adebcfca6a993c36f4ac038f355328d6`.
The separately prepared documentation commit does not alter runtime files.
The ignored local trial ZIP contains ten reference payloads with SHA-256 hashes,
a seven-file delta against installed `3cc4573`, and exactly 30 new display-only
starting controls. All payload hashes and these delta/setup limits were verified.

## Changes to review

- Extend 12 sources to 27: kitchen four-plus-entrance, ensuite three, bathroom
  two, bedroom pairs, laundry strip, black fan, three blinds, three plugs and FingerBot.
- Add `display_name` to v1 records. Dashboard/control headings use this name;
  descriptive `title` stays unchanged for existing phone and TV messages.
- Preserve the 98 existing booleans and 12 pause IDs. Add 60 destination
  booleans and 15 pauses: 158 booleans and 27 pauses overall. No forced initial
  values, new presence controls, reset of preferences or source-key migration.
- New-source dashboard/TV routes are the starting policy; phones start off.
  Enable only the 30 new display switches during approved setup. Never rerun
  the global starting-preferences script on this existing installation.
- Generate the exact [coverage catalogue](household_attention_coverage.md).

Kitchen membership is verified in HA, but the physical four-plus-one switch split
still needs confirmation. All three blind motors exist and report `unknown` at
inspection: report incomplete coverage, not invented failures. Entity existence
does not establish useful real-world availability reporting for each integration.

## Existing acceptance and companion evidence

On 14 November 2026, after the TV-light wall-switch test instructions, Lachlan
reported “ok it works” for the phone test. Record successful handset delivery;
exact latency, recovery, duplicate suppression and all other pair tests were not
separately reported. The earlier inspection showed phone routes off and no send
attempt: that was the starting policy, not an established delivery defect.

Lachlan also reported the updated TV consumer working. Read-only source inspection
of Bravia-Ambient-Display at local commit
`5941e01bac8b214e993b6499831e2449d2d5f268` found its `server/notices.mjs`
accepts v1 numeric/string schema identifiers, reads `title`, ignores extra fields,
and allows 64 items. The candidate has 27 sources and keeps existing v1 fields.
This is a source-contract check, not proof of the TV's deployed commit. That
repository's unrelated working-tree file was not edited.

The existing companion sanitiser also accepted all 27 records produced by the
candidate's actual reducer in a local contract check (15,589-byte feed, below
its 262,144-byte bound). This exercised pure functions, not a notification server
or live TV deployment.

Kiosk Connection Type was observed enabled with a fresh Wi-Fi report during the
earlier trial. Phone SSID sensors were also enabled, but home/away routing remains
parked. No SSID/BSSID values are stored here. Reporting cadence still limits coverage.

## Local checks

Run with Python 3.13 and the pinned dependencies in `tests/requirements.txt`:

```sh
python tests/validate_yaml.py
python tools/build_attention_controls.py --check
python -m unittest discover -s tests -v
git diff --check
```

Results: **31 tests passed**, **19 tracked YAML files parsed**, generated outputs
matched and whitespace checks passed. The companion contract check also passed.
GitHub Actions Local checks run 28 passed for review head
`1c2c0228754f4b7119bdf5a4ea908ed2869ac7b2` (documentation on top of this runtime).

Checks cover the actual production reducers: partial/all-member loss, unknown
recovery, off states, independent groups, recurrence, once-only routing and
display-name migration without losing occurrence identity. Generated checks
cover catalogue/control consistency and preservation of legacy helper IDs.
They create no HA instance, fake devices or notification environment.

Security review is scoped to this change: explicit source lists, native HA auth,
no new external service/input boundary or dependencies, no private telemetry
values, and unchanged read-only/pinned CI permissions. This is not an advisory
scan, whole-repository audit or certification of the live host.

## Deployment after explicit approval

1. Review the candidate diff and generated exact-commit package. Obtain separate
   approval to push and update the open PR, then approval for that runtime commit's
   installation and required Core restart. Confirm the Pi backup is ready.
2. Compare all ten runtime files with the last installed manifest. Stop on drift
   and reconcile the named files; do not assume GitHub equals the Pi.
3. Save fresh affected-file rollback copies and hashes. Snapshot all 98 existing
   booleans, 12 pauses and occurrence/delivery summaries through read-only checks.
4. Install only the seven changed runtime files: the custom template, source list,
   dashboard and four generated helper/watchlist/starting-route files. Root
   configuration, automations and package are unchanged reference files.
5. Validate HA configuration. Perform only the approved restart, verify hashes
   and check 27 records, 158 booleans and 27 pause definitions loaded. Compare old
   preferences and occurrences; renaming must not replay an old phone notice.
6. Enable only the 30 new dashboard/TV switches. Confirm all 30 new phone switches
   remain off and old preferences are preserved. Do not apply global defaults.
7. Inspect short headings and useful descriptions on phone-sized and wider
   dashboards. Check the actual TV still accepts the v1 feed.
8. With separately approved/user-operated physical testing, confirm kitchen
   four-plus-one, ensuite three and bathroom two. A lost member gives one item;
   valid full recovery clears it. Two groups must recover independently. Keep
   integration detection latency separate from the configured phone delay.
9. Record observed outcomes, pending natural-event checks and privacy-reviewed
   screenshots. Refine and retest failures before seeking separate merge approval.

Rollback restores only affected pre-trial copies, validates HA configuration and
uses a separately approved restart/reload. Preserve subsequent unrelated changes
and restored preferences; never restore runtime storage from a source archive.

## Installation receipt — 14 November 2026

Lachlan separately approved pushing the two reviewed commits and updating PR #11.
After that completed and CI passed, he confirmed “back up done” and approved
the named seven-file installation, validation, one Core restart and new display
control setup. No forced outages, device actions or merge were performed.

Direct SSH/SCP used existing authentication and saved-host verification; no keys
or credentials were read. All ten old runtime hashes matched `3cc4573` before
installation. Fresh rollback copies of the seven changed files, with verified
hashes, are in:

`/share/household-attention-trials/20261114T0957-e2f0bbc/rollback/`

The parent directory retains the exact trial archive, staging manifest,
`previous.sha256`, `installed.sha256`, `rollback.sha256`, `validated-at.txt` and
the three bounded preference/occurrence snapshots. All ten installed hashes
matched `e2f0bbc` before and after the single approved restart. `ha core check`
passed at **20:57:31 AEDT** (`09:57:31Z`). The restart completed successfully.

At **20:58:28 AEDT**, the store was ready with 27 records, 158 booleans and 27
pauses. All **98 existing switch values, 12 pauses and 12 record summaries**
matched the 20:56:34 pre-install snapshot. Compared record fields were occurrence
ID, first detection, active status, phone-evaluated flag, selected routes,
accepted recipients, delivery state and observation quality. The 60 new switches
were all off, and the 15 new pauses expired. The existing phone-send timestamp
did not change: the TV-light occurrence retained its earlier accepted Lachlan
receipt without replaying delivery.

At **20:58:53 AEDT**, only the approved **30 new dashboard/TV controls** were
enabled. At **20:59:06**, all old preferences still matched and all **30 new phone
controls stayed off**. Shared routing and the configured flag remained on. The
global starting-preferences script was not rerun.

Read-only API checks confirmed the short names on all 27 records, authenticated
three-view dashboard configuration and all intended control headings. The v1 TV
sensor was ready. Dashboard API retrieval required one retry after a closed
WebSocket; this did not cause another restart or configuration change.

The three blind records remain inactive with unknown quality, correctly
contributing coverage gaps. The grouped upgrade record also has incomplete
coverage. Other new sources were valid and healthy at this check. The existing
TV-light fault was still active; its phone receipt and occurrence were preserved.

| Acceptance | Result |
|---|---|
| Exact files, rollback, HA validation and one restart | Passed as above |
| Existing preferences and occurrence continuity | Passed for all compared values |
| New display routes on; new phone routes off | Passed: 30 on / 30 off |
| Short names and dashboard configuration loaded | Passed by read-only API; rendered layout still needs visual acceptance |
| Prior handset push / prior TV operation | User-confirmed before this extension; not retested by forcing an event |
| Kitchen four-plus-one physical split | Pending user wall-switch test |
| Ensuite/bathroom loss, recovery and independent groups | Pending physical observations |
| Blinds' useful physical availability reporting | Incomplete: currently unknown; no fault invented |
| Updated TV rendering and screenshots | Pending visual acceptance |
| Merge approval | Not requested |
