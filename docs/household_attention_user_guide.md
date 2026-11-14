# Household attention — user guide

**Status: built locally, not installed on the Pi.**

This guide describes runtime code at commit
`6b36c4a9518a4f424582b4a4240aef17809ba6ff` on
`feature/household-attention-handler`. The dashboard and controls described below
would become available after an approved installation. They are not live now.
Nothing has been pushed, no PR has been opened, and no deployment or restart has
been approved. The requested review comes first.

## What has been built

The handler gives Home Assistant one place to keep household issues and notices.
It watches a selected list of real sources, keeps separate records for separate
issues, and decides which records belong on the dashboard, in the TV data or on
each person's phone.

The local implementation includes:

- A shared inbox for nine source rules, including faults, washing and upgrades.
- A dashboard with an Inbox tab and editable Delivery controls.
- Four active destination switches per row: dashboard, TV, Lachlan phone and Nic phone.
- An expiry time for pausing all handler destinations for a row.
- One phone-delivery decision per issue occurrence, rather than repeated messages.
- Separate operational health and monitoring coverage, so a washing notice or
  available upgrade is not counted as a household fault.
- A controlled handover from the existing washing phone messages, preserving
  the original laundry light action.

Home/away splitting is parked. An enabled phone destination applies wherever
that person is. No GPS, router presence or location-report age is used for delivery.
The previous home/away settings are retained in configuration but are hidden and
unused by the current handler.

## Starting rules

These are the settings the first-install setup applies. You can later change
destinations without changing code. The inbox keeps tracking an active issue
even when every destination for that row is off.

**Dashboard and TV data are enabled for all nine rows in the starting profile.**
The phone delay below does not delay initial capture in the inbox or filtering
into the dashboard/TV data.

| Row | What creates the item | Starting phone recipients | Phone timing | What clears it |
|---|---|---|---|---|
| Fridge visibility loss | The fridge plug or LG fridge entity is unavailable | Lachlan and Nic | Immediately | Both channels must be valid again |
| Dyson unavailable | The configured Dyson fan becomes unavailable; simply being off is normal | Lachlan | After 15 minutes | Valid fan availability returns |
| Internet disconnected | The router reports WAN disconnected, or the WAN entity is unavailable | Lachlan | After 15 minutes | Valid connected WAN status returns |
| Washer unavailable | The washer status entity is unavailable | Lachlan | After 15 minutes | A valid washer status returns |
| Kiosk off Wi-Fi | A fresh phone connection report says Cellular or No Connection | Lachlan | After 15 minutes | A fresh Wi-Fi report returns |
| Washing finished | The existing washer completion event arrives | Lachlan and Nic | Immediately | One-shot delivery handling finishes |
| Washer cleaning needed | The wash count is 30 or more | Lachlan | After 15 minutes, once for that cleaning-needed occurrence | A valid count below 30 |
| Backup failure | A backup failure is observed | Lachlan | After 15 minutes | A later successful automatic backup |
| Available upgrades | One or more listed update entities report an upgrade | Neither | No starting phone alert | Confirmed updates clear from the group; the item resolves when all coverage is valid and none remain |

"Immediately" means no configured waiting period; it does not guarantee instant
handset receipt. Fault timing is measured from when the handler first detects
the occurrence. There are no repeat, escalation or recovery phone messages.

The fridge notice means **Home Assistant has lost visibility through one or more
channels**. It does not claim the fridge has stopped cooling. A successful backup
attempt is not enough to clear a backup failure: the successful automatic-backup
timestamp must be later than the failure.

**Kiosk coverage is not ready yet.** Its existing Connection Type sensor is
registered but disabled. It must be enabled and its real reporting behaviour
checked during the separately approved setup. A report older than 15 minutes is
treated as uncertain. The code cannot reliably infer that a powered-off phone is
offline from an old Wi-Fi value.

## Finding your way around

After installation, open **Household Attention** in the Home Assistant sidebar.
It has three tabs:

| Tab | What it shows |
|---|---|
| Dashboard | The active items selected by their HA dashboard switches, plus short-lived washing event cards |
| Inbox | All active items, their source evidence, upgrade details, health, coverage gaps and recent washing outcomes |
| Delivery controls | Four destination switches and a pause-until time for each row; setup controls appear at the top |

A blank Dashboard does not necessarily mean there are no issues. A row may be
switched off for that destination. Check **Inbox** for the underlying active records.

The inbox uses normal signed-in Home Assistant access. It does not add separate
private access rules for Lachlan and Nic or a public inbox website.

## Changing where an item goes

In **Delivery controls**, find the row and change its switches independently:

| Control | Effect |
|---|---|
| HA dashboard | Includes or excludes the row from the filtered Dashboard tab |
| TV screensaver | Includes or excludes the row from the HA data prepared for a TV consumer |
| Lachlan phone | Allows or prevents that row's new eligible phone notice to Lachlan |
| Nic phone | Allows or prevents that row's new eligible phone notice to Nic |

Dashboard and TV data re-filter existing items when you change their controls.
Phone controls do not replay old notices whose delivery decision has already
been made. For example, turning a phone switch on after an issue's phone decision
was skipped will not send that old issue. A later genuine recurrence gets a new
decision. If an issue is still inside its waiting period, the settings in effect
when it becomes eligible determine its phone routes.

Switching every destination off does not delete or resolve an active fault.
Recovery must come from valid source evidence. There is no manual fault-resolve
or acknowledgement button in this version.

### What the TV switch currently does

**The TV display application has not been changed.** The switch filters data held
in Home Assistant, ready for a compatible TV consumer. It does not itself put a
card on the television, change the TV screen or interrupt photos. Visible TV
delivery still needs the companion application to consume that data.

### Pausing one row

Set **Pause all routes until** to a future date and time. Until that time, the
handler hides the row from its routed dashboard/TV data and suppresses its phone
delivery. The inbox continues to track the source. The four switch values are
preserved.

When the pause expires, active dashboard/TV items can reappear. A phone decision
skipped while paused is not sent afterwards. To end a pause early, set its date
and time to the past. There are no quick one-hour buttons or category-wide pause
controls yet.

The row pause does not stop the independent washing light action or existing
device-repair automations.

## Washing behaviour

Washing finished is a notice, not a fault or a chore waiting to be acknowledged.
With the starting profile, it sends one notice to each person's phone regardless
of location. The new phone message is **Washing finished**, under the title
**Household attention**. Tapping the notice is configured to open the HA inbox.

The event resolves once Home Assistant has accepted all selected notification
calls. This is not proof that a phone received the push or that someone read it.
With no eligible phone destinations it resolves as suppressed. If dispatch is
interrupted or fails, it closes after five minutes as unconfirmed, with that
outcome retained. It is not automatically retried.

A recent washing card remains eligible for dashboard/TV data for 15 minutes after
the actual event, even after delivery handling has resolved the event. It then
expires. An old completion event discovered after restart does not cause a fresh
phone backlog or a new 15-minute display window. You do not need to mark laundry
attended, and there is no arrival-home reminder.

The existing laundry light action remains red RGBW `[255, 0, 0, 0]`, at 20%, with
a long flash. Handler destination switches and row pauses do not control it.
No new code restores the light's previous settings.

### Shared routing is a handover switch

**Enable shared phone routing is not an "all notifications off" switch.**

| Shared routing setting | Washing and washer-cleaning phone path |
|---|---|
| Off | The existing washing automations retain their original phone messages, outside the new row controls |
| On | Those original phone actions are skipped; the shared handler owns the phone notices |

For everyday muting after handover, leave shared routing on and use the row's
phone switches or pause time. Turning shared routing off returns washing to its
old behaviour, including its original messages and recipients. Perform the initial
handover while no washing completion notification is being processed.

## Understanding health and coverage

Health and coverage answer different questions:

| Display | Meaning |
|---|---|
| Confirmed faults | Number of active fault records in the monitored list |
| Health: faults | At least one monitored fault is active |
| Health: incomplete | Fault monitoring lacks valid evidence, so healthy cannot be established |
| Health: healthy | No active faults and the configured fault sources have valid observations |
| Coverage: incomplete | At least one monitored source has unknown or stale evidence, including update/event sources |
| Coverage gaps | Names of the sources whose observations are uncertain |

A washing event, cleaning reminder or available upgrade does not increase the
fault count. You can have healthy operational sources with incomplete update
coverage; the inbox displays both. This applies to the selected source list,
not every device or condition in the house.

If a fault is active and its evidence becomes unknown or stale, it stays active
with uncertain quality. If a previously healthy source becomes unknown, the
handler reports a monitoring gap rather than inventing a physical failure.

## First setup — after separate installation approval

1. Check that the new entities and dashboard loaded successfully and review the
   inbox, including any issues already present.
2. Run **Household attention - apply starting preferences once** during setup.
   Inspect each row's resulting destinations.
3. Leave **Attention starting preferences applied** on. It is a setup completion
   flag, not an everyday delivery switch. Clearing it and rerunning the setup
   action can re-enable starting destinations you had turned off.
4. Enable/report/verify the existing kiosk Connection Type sensor as separately
   approved. Missing evidence remains visible as incomplete coverage.
5. With no washing completion being processed, enable shared routing for the
   reviewed handover. Check actual phone and laundry-light behaviour using normal
   household events or separately approved real checks.

The setup action does not enable shared routing. The helper definitions omit
forced initial values so selected settings can restore across normal restarts.
Actual restart continuity still needs to be checked on the Pi. Deployments do not
run a preference-reset action.

## What this version does not provide

- Automatic TV display behaviour or screen switching.
- Home/away phone splitting or router-based people tracking.
- Lights/group availability rules, rapid battery-drop alerts or authentication
  alerts: their exact source rules have not been connected in this slice.
- The second Dyson, which is not in HA, or Dad's desk plug, which is deliberately excluded.
- Backup overdue/staleness detection, reminders, critical-alert bypass or escalation.
- Automatic fixes beyond the existing unchanged repair automations.
- Reliable reporting of a complete HA/Pi/power outage from within HA itself.
- A searchable long-term incident archive: only the current/last occurrence per
  row is retained by the handler, with a short recent-washing display.

## What has actually been checked

The local code passed 25 tests, YAML syntax checks, generated-file checks and diff
checks. The exact-commit trial archive's ten payload files matched its SHA-256
manifest. These checks used no separate HA installation, fake devices or simulated
notification service.

The real entity map was inspected read-only, but the local configuration has not
been installed or validated by the live HA configuration checker. Phone delivery,
dashboard layout, restart behaviour, kiosk reporting and normal household events
still need the Pi trial. Live-file drift has not been checked because the file
connector has no SSH transport configured.

The next step is your review of this guide and the [as-built document](household_attention.md).
Push, PR and trial remain on hold. Backup confirmation and the relevant approvals
will be revisited after that review, with the PR kept open through live acceptance.
