# Conditional phone delivery and blind removal

Status: local candidate, not pushed or installed. Exact runtime candidate:
`5fe488ccbf67b7d41d2f92a11be6192fe93fcad9`. The Pi's last verified runtime
remains `e2f0bbc7adebcfca6a993c36f4ac038f355328d6`. Its installation receipt is
preserved in [the grouped-device trial](household_attention_grouped_trial.md).
PR #11 remains open; neither this trial nor merge is approved yet.

## Accepted behaviour

Remove the three blind availability rows, leaving 24 sources. Their cards,
destination definitions, pauses, physical-cover triggers and stored records go
away. Physical blind controls, ZHA support and the three firmware entries in
grouped Updates stay intact. Other source keys, detection, delays, occurrence
history, display names and the v1 TV contract remain unchanged.

Each row shows Dashboard, TV, Lachlan home/away and Nic home/away. For each person:
both on means always, including unknown presence; both off means no phone alert;
one selected requires matching fresh presence. **No alert is automatically changed
to home-only**, including washing. The date format is already fixed; leave it alone.

Before migration the existing plain phone switches remain authoritative. A
guarded one-time script copies each current phone value to both of its home/away
switches, verifies the copy against the still-current original values, then
activates the new model. A failed or interrupted copy leaves old routing active;
the script can safely retry before activation. Once activated it cannot overwrite
later opt-in changes. The hidden plain phone values remain for rollback.

## Presence and privacy

`attention/policy.yaml` contains only the verified tracker/SSID entity references
for Lachlan and Nic, the stationary kiosk's SSID/Connection Type references, and
the accepted 900-second age limit. No network values or coordinates are committed.

- Fresh GPS home-zone evidence establishes home; fresh GPS outside home establishes away.
- Matching fresh phone/kiosk SSID evidence, with a fresh kiosk Wi-Fi report,
  independently supports home. A non-match or no Wi-Fi never proves away.
- Fresh GPS-away conflicting with matching home Wi-Fi produces unknown.
- Missing, stale, future-dated or pre-start observations cannot establish presence.
- If kiosk reports are absent/stale, GPS can still establish home or away.
- Two diagnostic sensors expose only status, a fixed reason and report ages.
  These are local diagnostics, not additional household fault sources or TV data.
- Nic's Always permission is an agreed setup assumption, not an app permission
  this change can grant. iOS reporting remains variable; HA receipt freshness
  is not a guarantee of physical location or a fixed GPS heartbeat.

The boot-ready flag deliberately has `initial: false`; unlike preferences it
must never restore as ready. On HA start, an internal datetime marker is set
to the next whole second before readiness is enabled. This rejects restored
samples even if they were loaded in the same second. All user destinations,
pauses and the persistent migration flag have no forced initial value.

Presence is recomputed for eligibility and again at dispatch, so cached display
status cannot extend a report beyond 15 minutes. Existing pause/cutover guards,
once-per-occurrence decisions, no retry/recovery pushes and no backlog remain.
Arriving home does not replay an already-consumed notice.

## Local checks and limitations

Completed locally: **47 tests passed**, YAML syntax passed for **19 repository
files**, generated-file consistency passed and `git diff --check` passed.

The tests use production reducers and the actual migration/dispatch templates.
They do not create an HA instance, fake devices or simulated notifications.
Run Python 3.13 with the pinned dependencies in `tests/requirements.txt`:

```sh
python tests/validate_yaml.py
python tools/build_attention_controls.py --check
python -m unittest discover -s tests -v
git diff --check
```

Coverage includes all home/away combinations, independent people, the exact
15-minute boundary, conflicts, missing kiosk data, GPS source validation, boot
restoration, preservation of 48 recipient choices, concurrent/missing-helper
migration failures, dispatch rechecks, no arrival backlog and removal of blind
records without resetting remaining occurrences. Local checks do not prove HA
loading/restoration or reliable iOS background departures and arrivals.

The exact-commit bundle was verified locally: 11 payload hashes, nine changed
runtime files, ten previous-install hashes and only `attention/policy.yaml` new
to the installed allowlist. Its setup action is the preserving migration, with
an empty new-starting-destinations list. Local review artifacts are ignored by
Git: `.tools/household_attention_presence_trial.zip`,
`.tools/household_attention_presence_manifest.json` and
`.tools/household_attention_presence_runtime.diff`.

## Approved-trial procedure to use later

1. Review the exact candidate commit, diff and manifest. Obtain separate push/PR
   and exact-runtime install/restart/migration approvals. Confirm backup readiness.
2. Check the ten files in the actual installed `e2f0bbc` allowlist for drift.
   `attention/policy.yaml` existed in Git but was not part of that installed
   runtime: treat it as a new live file, inspect any existing live copy for drift
   before proceeding, and back it up if present. Do not assume Git equals the Pi.
3. Save fresh rollback copies/hashes. Snapshot all existing values, including the
   dormant home/away switches, 48 remaining plain recipient choices, 24 retained
   pauses and all occurrence/delivery summaries. Retain the removed blind values
   separately for rollback. Do not export network values or location coordinates.
4. Install the nine-file runtime delta from the eleven-file reference manifest.
   Root configuration and existing household automations remain unchanged.
   Validate HA and perform only the approved Core restart. Verify hashes.
5. Check 24 records, 196 boolean definitions and 25 datetime definitions loaded:
   24 row pauses plus one internal session marker. Apart from the three removed
   blind rows, existing IDs and values must match; 48 new home/away helpers start
   off. The two new booleans are the persistent migration flag and per-boot guard.
6. Check current routing is still on the plain-phone fallback. Do not rerun global
   starting preferences or bulk-enable the manifest's fresh-install defaults.
   Run `script.household_attention_migrate_presence_routes` once, then verify
   every retained person's home and away values equal the pre-migration phone
   value, including current opt-ins made since the earlier installation.
7. Verify the migration flag committed, all prior effective phone choices remain
   always/off, retained pauses and occurrences survived, and no old event replayed.
   The package's boot-session automation is part of this approved restart; no
   additional device or notification action is implied by setup.
8. Inspect six switches per card, readiness and privacy-safe presence diagnostics.
   Confirm the blind availability rows/gaps are absent and TV still consumes v1.
9. After user opt-in, observe normal background departure/arrival on both phones
   with Nic's permission changed. Confirm conditional delivery, unknown suppression,
   both-on bypass and no arrival backlog using normal household events. Do not
   force outages or send diagnostic pushes without separate approval.
10. Record actual acceptance before requesting merge approval. Keep the PR open.

For rollback, restore only affected saved files and validate before an approved
restart. Preserve subsequent unrelated changes and the home/away preferences.
An immediate pre-opt-in rollback can use unchanged legacy phone choices. Once
conditional choices have been made, the old runtime cannot represent them:
agree a fallback before rollback rather than silently converting home-only to
always. The old runtime does not use the new migration/session flags.

## Diagnostic monitoring is a separate recommendation

Use standard reauthentication Repairs plus integration state for credentials;
integration/required-add-on health for dependency failures; filtered, deduplicated
`system_log_event` errors for software exceptions; and explicit physical feedback
for silent command failures. Repairs already has a live change event, but a
complete adapter must reconcile existing issues and removals, not just future
events. Persistent errors must not clear merely because logs went quiet.

Raw logs, issue payloads or credentials must not be forwarded to TV/phones.
Prefer bounded source/count/time summaries and local diagnostic links. This
candidate enables no log events, installs no Spook or diagnostic adapter and does
not declare optional SSH a required dependency.

Sources: [HA 2026.11 reauthentication Repairs](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/config_entries.py#L1367),
[System Log events](https://www.home-assistant.io/integrations/system_log/),
[script exception handling](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/helpers/script.py#L574).
