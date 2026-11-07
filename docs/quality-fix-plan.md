# Quality fixes after baseline sync

Keep baseline capture separate from behavioural improvements. No deployment,
reload, device test, push or merge is authorised by this plan.

1. Kiosk charging: inspect reporting cadence and identify a timestamp that reflects
   actual phone updates. Agree a stale timeout. Prioritise stale/missing feedback
   over thresholds, safely handle a missing entity, and preserve 40/80 hysteresis.
   Validate low/middle/high levels, stale high readings, missing/unavailable input,
   startup and plug recovery without operating live devices.
2. Washer cleaning: ignore attribute-only changes and require a numeric increase
   reaching at least 30. Preserve reminders at 31, 32 and beyond. Confirm whether
   startup/reconnection should notify; recommended default is no. Attempt each
   recipient independently. Validate 29→30, 30→31, unchanged values, attributes,
   unknown→30, downward corrections and reset-to-zero.
3. Bathroom remote: confirm whether both buttons should toggle or whether on/off
   should have dedicated meanings. Preserve current behaviour until decided.
4. Dashboard metadata: quote the hidden Off button name; HA currently reads the
   unquoted YAML value as boolean false. It has show_name disabled, so this is a
   metadata cleanup rather than an observed layout problem.

For each fix, prepare the local diff and meaningful non-live checks, obtain
approval for its deployment, recheck live drift, back up affected files, apply
only the approved change, and perform only the approved validation/reload.

## Baseline checkpoint — 7 November 2026

All 20 automations were rechecked against the live API after the other chat
finished. Their definitions match. Exported on/off state strings are explicitly
quoted for Home Assistant YAML compatibility.

The final local dashboard matches the served dashboard when parsed with YAML 1.1
boolean handling (the hidden Off label becomes false). The black-fan notes record
the other chat's live template hash comparison and approved deployment. This
chat could not independently read the live template file through the connector.

The original sync audit describes an earlier snapshot. Its outstanding items
about scripts, UI dashboards, helpers and integration-provided scenes still need
an inventory and comparison before claiming the entire installation is synced.

Commit the reviewed baseline locally, then request explicit push approval.
Merge approval is separate. Editor settings and machine-specific .codex files
remain outside the baseline commit.
