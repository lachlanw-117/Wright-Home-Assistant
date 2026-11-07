# Automation reliability changes

Deployed on 7 November 2026 after local checks and HA configuration validation.
The bathroom remote's existing toggle behaviour is preserved pending a user decision.

## Kiosk phone charging

The 40% on / 80% off thresholds remain. A five-minute check, battery state changes,
charger state changes and HA startup re-evaluate the controller.

A watchdog branch runs before numeric thresholds. It requests charging after
one hour without battery telemetry, or ten minutes with non-numeric feedback.
A missing entity takes the fail-safe path immediately. If the charger is already
on, the branch does nothing and never falls through to turn it off because of a
stale high value. An unavailable charger is left alone and reconsidered on recovery.

Live read-only inspection identifies the battery sensor as `mobile_app`; the
sampled history showed state updates at roughly five-to-ten-minute intervals.
One hour is a conservative initial timeout. `last_reported` tracks HA receiving
reports, including repeated values, while `last_changed` is used only to measure
the duration of invalid feedback. A report is not proof of physical connectivity:
cached updates can conceal a disconnected phone. Startup can reset timestamps,
so recovery from a restored high value may take up to an hour plus the periodic
check. No dedicated app heartbeat sensor was available.

The fail-safe favours keeping the phone powered over strict battery optimisation.
Review the timeout against longer telemetry history after approved deployment.

## Washer-cleaning reminders

The trigger ignores attribute-only updates. The condition requires numeric old
and new counts, with the new value at least 30 and greater than the old value.
It continues reminding on counts 31, 32 and beyond. Recovery from unknown or
unavailable, downward corrections and resets do not notify.

Each notification action uses `continue_on_error` so a runtime delivery failure
for the first recipient does not prevent attempting the second. This does not
hide malformed configuration or establish that either notification was delivered.

The recommendation to skip reconnection/startup reminders is adopted as a local
implementation choice, now deployed, with no change to the existing notification wording.

## Checks

`tests/test_automation_reliability.py` loads the actual YAML and renders its Jinja
templates against synthetic HA state objects. It exercises 13 charging scenarios
and 12 washer transitions, checks independent notification attempts, and verifies
the other 18 automation definitions are identical to `main`.
It is a focused behaviour harness, not a full Home Assistant schema/runtime test.

## Risk and rollback

| Change | Main tradeoff | Reversal |
|---|---|---|
| Charging watchdog | Lost reports can keep the charger on beyond the 80% target. HA receiving cached reports can still conceal a stale phone. Restarted timestamps can delay the watchdog. | Restore automation ID `1789173535286` from its pre-deployment live snapshot. Charger power is a separate physical state; restoring YAML does not restore it. |
| Washer reminders | A count increase while HA is offline is intentionally not notified on reconnection. A jump of several counts produces one reminder. Delivery errors do not prove delivery succeeded. | Restore automation ID `1792576854357` from its pre-deployment live snapshot. Notifications already sent cannot be recalled. |
| Hidden Off label | No intended operational change; the label is hidden. | Restore that one dashboard value and refresh the dashboard. |

Before deployment, save the exact two live definitions and dashboard version,
check for intervening edits, and retain the reviewed diff. Prefer restoring only
the affected automation IDs if anything else has changed. A whole-file restore
is appropriate only when its other contents are still unchanged.

Validate the restored configuration before an approved automation reload.
Reloading automations can interrupt active runs and reset pending trigger timers,
so even a narrow YAML change has a reload impact beyond the two edited definitions.
Avoid deploying during an active recovery sequence or other important automation.
A full HA restart is not part of the intended deployment or rollback.

If a deployed fix misbehaves, disabling just the affected automation is a possible
containment step, followed by restoring its saved definition. Disabling it,
restoring live configuration, reloading and changing charger power all require
explicit approval. No containment or rollback actions have been performed.

```sh
python -m pip install -r tests/requirements.txt
python -m unittest discover -s tests -v
```

Before any deployment, compare the two live definitions for drift, back up the
affected configuration, run HA configuration validation and obtain approval for
the required automation reload. Device actions and notification delivery tests
need their own approval. The dashboard change only quotes a hidden Off label;
it does not change button actions.

## Deployment verification

- Saved the exact two live YAML files in a timestamped, ignored local rollback
  directory before making changes. No backups or runtime snapshots are committed.
- Confirmed the original automation definitions and dashboard matched the reviewed
  baseline, with only the two automation changes and one hidden label in scope.
- Verified live and staged SHA-256 hashes before replacing the files.
- Ran `ha core check` successfully before the separately approved `automation.reload`.
  No active automation runs were reported immediately before the reload; pending
  trigger timers may still have been reset.
- Read back all 20 automation configurations and the served YAML dashboard; they
  match the local source. Both edited automations remain enabled.
- Verified deployed file hashes after activation. No HA restart, manual charger
  command, notification test or other device test was performed.

This verifies configuration and activation, not long-term behaviour or delivery.
Retain the pre-deployment backups for the rollback process above.
