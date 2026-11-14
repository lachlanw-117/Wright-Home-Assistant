# Household attention — user guide

**Status: the Pi runs the 27-source `e2f0bbc` trial. The 24-source, six-switch
update described below is a local candidate and has not been installed.**

The [grouped-device receipt](household_attention_grouped_trial.md) records the
existing installation, hashes, restart and preservation of preferences. Lachlan
confirmed a real phone notification and reported the separately updated TV
consumer working. Other physical/visual acceptance remains explicit.
[PR #11](https://github.com/lachlanw-117/Wright-Home-Assistant/pull/11) stays open.

The candidate removes the three blind availability rows and restores conditional
phone routing. Existing phone choices stay unchanged during setup: enabled
becomes both home and away on; disabled becomes both off. **No alert becomes
home-only automatically.** See the [candidate trial](household_attention_presence_trial.md)
and [exact coverage catalogue](household_attention_coverage.md).

## What it watches

One shared inbox keeps faults, washing and maintenance separate. The candidate
has 24 sources, including fridge visibility, Dyson, grouped lights, black fan,
plugs, FingerBot, WAN, washer availability, kiosk Wi-Fi, completed washing,
washer cleaning, backup failures and grouped updates.

Light sets watch their physical members: one unavailable bulb creates one item;
every member must be valid to clear it. An ordinary off state is healthy.
Kitchen lights are four bulbs plus the separate entrance; the physical switch
split still needs acceptance. Fridge visibility loss is not proof cooling stopped.
Unknown data indicates incomplete coverage and does not clear an existing fault.
Blind availability is excluded; blind firmware remains in grouped Updates.

## Finding your way around

Open **Household Attention** in the Home Assistant sidebar:

| Tab | What it shows |
|---|---|
| Dashboard | Active items selected for dashboard delivery, grouped by kind/category |
| Inbox | All active items, source evidence, coverage gaps and recent washing outcomes |
| Delivery controls | Six destination switches and a pause per device, plus phone presence |

Card headings use device names; the condition is underneath. A blank Dashboard
can mean its switches are off: check Inbox. The inbox uses normal signed-in HA
access; it is not a separate public website or a new per-person access boundary.

## Six destination switches

Each device has **Dashboard**, **TV**, **Lachlan home**, **Lachlan away**,
**Nic home** and **Nic away**. Each person's phone choices are independent:

| Home | Away | Result |
|---|---|---|
| On | On | Always, even if presence is unknown |
| On | Off | Only when known home |
| Off | On | Only when known away |
| Off | Off | No phone alert |

To opt a currently enabled alert into home-only delivery, leave its home switch
on and turn its away switch off. To mute it, turn both off. Setup preserves your
current always/off choices, including washing; it does not select conditional
delivery for you. Before setup finishes the card says setup pending and current
phone delivery remains active. The old plain phone helpers are retained but hidden.

Dashboard and TV switches re-filter existing items immediately. Phone decisions
happen once per occurrence. Enabling a route, arriving home or ending a pause
does not replay an already-consumed notice. Before its waiting period expires,
the settings and presence in effect at eligibility determine delivery; they are
checked again just before sending.

## How home and away are determined

Phone presence shows **home**, **away** or **unknown**, with an explanation and
location/Wi-Fi report ages. Reports must be no older than **15 minutes**:

- A fresh GPS home-zone report means home; a fresh GPS report outside home means away.
- Matching fresh phone and stationary-kiosk Wi-Fi reports can also confirm home.
- No Wi-Fi or another network alone does not prove away.
- Fresh GPS-away conflicting with home Wi-Fi means unknown.
- With no usable evidence, a conditional alert is skipped. Both switches on still means always.
- After a restart, wait for post-start reports: restored readings do not count as fresh.

Nic's Always permission is an agreed setup assumption. iOS decides background
report timing, so a phone staying silent can produce unknown even while physically
home. Missing kiosk data removes the Wi-Fi hint; fresh GPS can still be used.
Network identifiers and coordinates are not shown in these diagnostics or sent
to TV/phones. These statuses describe reported evidence, not guaranteed location.

## Timing and clearing

Capture in the inbox is immediate when HA reports the condition. Phone timing is
separate: **fridge visibility loss and completed washing have no configured
delay**; other configured availability, cleaning and backup-failure notices use
**15 minutes**. Grouped updates start with phones off. All existing phone choices
are preserved; consult the catalogue for the fresh-install profile rather than
assuming it describes your current switches.

There are no automatic repeats, escalation or recovery pushes. A genuine new
failure after recovery gets a new occurrence. Pausing or changing destinations
does not resolve a fault; source evidence must establish recovery. A successful
automatic backup later than the failure clears the backup item; starting a
backup does not. Invalid washer counts are not zero; unknown update components
remain coverage gaps rather than being treated as up to date.

Kiosk Connection Type is enabled and has reported Wi-Fi. Reports older than 15
minutes are uncertain; an old Wi-Fi value cannot prove a powered-off phone is alive.

## Pausing a device

Set **Pause all routes until** to a future date/time. Until expiry, handler
dashboard/TV/phone delivery is suppressed, while the underlying inbox continues
tracking the issue. Destination switches are preserved. An existing item can
reappear on dashboard/TV when the pause expires, but a skipped phone decision is
not replayed. Set the date/time into the past to end a pause early.

The date picker follows your HA profile's date format; Lachlan has set day/month/year.
The pause does not affect the independent laundry lighting or operate a device.

## Washing and the TV

Completed washing is a one-shot event, not a chore that persists until someone
acknowledges it. Once selected notify calls are accepted, it resolves; unavailable
routes are suppressed and an unconfirmed dispatch times out after five minutes.
HA accepting a notify call is distinct from a handset receiving or reading it.
Recent events display for 15 minutes from the actual completion event, without
creating a later arrival reminder or replaying old completion timestamps.

The existing red laundry-light flash at 20% remains independent. To mute new
washing phone delivery, leave shared routing enabled and turn that person's
home and away switches off. **Turning shared routing off restores the legacy
washing phone path; it is not an all-notifications mute.**

The TV switch filters HA's v1 feed for the separate Bravia app. The existing
descriptive notification title remains compatible; this repository does not
deploy or force a screen change on the television.

## Limits and acceptance

This candidate does not add a generic software-error handler, credential/Repairs
adapter, overdue-backup detector, battery alarms or independent HA/Pi outage
monitor. Diagnostic recommendations and implementation boundaries are in the
[candidate trial](household_attention_presence_trial.md).

Local tests exercise production reducers and migration/dispatch templates without
an HA instance, fake devices or notification environment. HA loading, preference
restoration, normal background departures/arrivals and actual conditional handset
delivery still need the separately approved exact-commit Pi trial. Keep the PR
open through acceptance; merging requires separate approval.
