# Household diagnostic monitoring — draft implementation plan

Status: draft for review, 14 November 2026. This is a separate change after the
conditional-phone trial; no diagnostic adapter or additional alert is installed.

## Outcome

Extend the shared inbox with actionable software and dependency incidents.
Device availability remains useful symptom evidence, but cannot reliably detect
expired credentials, a partially working integration or a command that never
produced its intended result. There is no universal error event that proves both
failure and recovery. Repairs, integration state, required-service health and
selected outcome checks should complement a bounded software-error feed.

## Evidence and coverage

Read-only inspection on 14 November found these existing Supervisor entities,
all disabled by the integration:

| Dependency | Existing running sensor | Proposed treatment |
|---|---|---|
| Matter Server | `binary_sensor.matter_server_running` | Required for Matter devices |
| OpenThread Border Router | `binary_sensor.openthread_border_router_running` | Required for the household Thread path; verify topology before attributing all device faults |
| Bravia host | `binary_sensor.bravia_ambient_photo_host_running` | Required for the TV delivery destination |
| File editor | `binary_sensor.file_editor_running` | Optional administration; exclude from required-service alerts |
| Terminal & SSH | `binary_sensor.terminal_ssh_running` | Optional administration; exclude from required-service alerts |

All five add-ons reported started through the Supervisor CLI. The connector's
add-on REST endpoint returned 401; this is an inspection-access limitation, not
an add-on failure. Use the native running sensors in runtime monitoring after
separately approved enabling; no SSH polling or embedded token is needed.
Running proves process state, not end-to-end service health. Native Supervisor
running entities are disabled by default. [Supervisor integration](https://www.home-assistant.io/integrations/hassio/)

The existing fan notes establish that speed feedback is the device-reported
percentage, while swing is inferred from the last scene request. Neither swing
nor the FingerBot's switch state proves the physical appliance moved/responded.
Do not promise physical-outcome monitoring for those actions without an
independent signal. See [black-fan feedback limits](arlec_black_fan_dashboard_notes.md).

## Implementation sequence

### 1. Add required-service health

Enable only the three named required running sensors during approved setup.
Add a source per dependency with the existing six delivery controls and pause.
Use a five-minute startup grace and a two-minute continuous explicit stopped
state before creating a fault. Missing/unavailable signals mean uncertain
coverage, not stopped or recovered. Require a valid running observation after
the fault to clear it. Restarting and maintenance pauses preserve occurrences;
an operator pause should be explicit and expire.

Label the Bravia row **TV service** so the meaning is clear. Its TV route cannot
report its own failed consumer; the HA inbox and independently enabled phone
route are the useful destinations. Keep device faults visible as linked symptoms.
Do not assume every unavailable Matter device is caused by the server or border
router, and do not hide genuine device faults during an infrastructure incident.

### 2. Add Repairs and integration-state adapters

Use a small, repository-owned HA integration for in-process read-only observation
of Repairs and config-entry state. This avoids an external credential-bearing
poller and can take a complete startup snapshot. Keep the first implementation
small: a normalised sensor/export, bounded incident store and version-compatibility
checks, with routing still owned by the existing household-attention layer.
Do not install Spook or perform automatic repairs, reauthentication or reloads.

At startup, subscribe before taking the initial snapshot, then reconcile queued
changes. Reconcile periodically as protection against missed events. The issue
registry event carries identity and action, so event-only monitoring misses
pre-existing problems. The installed-version Repairs API exposes active visible
issues; ignored/hidden issues need distinct treatment rather than being declared
fixed. [Repairs API](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/repairs/websocket_api.py)
[Issue registry](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/helpers/issue_registry.py)

For expired credentials, join a reauthentication Repair to its integration entry.
Show one incident such as **LG ThinQ — Sign-in required**, with a local Repairs
link. Supplement this with setup/authentication state where supported. Standard
pending reauthentication creates a Repair in installed HA 2026.11.0, but not every
integration reports failures identically. Do not infer authentication failure
from any unavailable entity or from arbitrary log text.
[Installed-version config entries](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/config_entries.py#L1367)

For required integrations, use an explicit allowlist derived from the monitored
entities: verify the exact config-entry mappings for Matter/Thread, ZHA, TP-Link,
LG ThinQ, Dyson and Tuya during implementation. Observe setup error/retry and
unload states, with startup grace; intentional disabling/unloading must be
recorded as excluded or maintenance, not silently considered healthy. Loaded
means setup completed, not proof that every device works. Clear a combined
incident only after the relevant Repair is actually resolved and the applicable
integration state is healthy. A failed snapshot retains prior faults and marks
coverage uncertain. [Config-entry API](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/config/config_entries.py)

### 3. Add automation/script and other software errors

Enable `system_log.fire_event` in a separately reviewed change. Start with ERROR
and CRITICAL events. Handle automation/script logger families explicitly; group
other errors by a sanitised integration/logger and error class. Warnings remain
excluded unless a particular actionable warning is reviewed. The native log
buffer is bounded and event emission is off by default.
[System Log](https://www.home-assistant.io/integrations/system_log/)

Store only a fixed safe summary, component, opaque incident key, first/last time,
count and local diagnostic link. Do not persist or forward raw message bodies,
tracebacks, URLs, account identifiers, device payloads or credentials. Raw text
may be examined transiently for reviewed classification; unknown patterns become
**Software error — Review Home Assistant logs**, with no raw interpolation.
Exclude the adapter's own logger from its event feed to prevent feedback loops;
expose adapter health separately.

Deduplicate repeated events into one incident. Proposed bounds: 100 active
incidents, 200 recent summaries, seven-day recent-history retention; overflow
gets an explicit coverage counter, never a silent all-clear. Count repeats while
paused without sending catch-up pushes on expiry. Use a five-minute aggregation
window and at most one software-summary push per recipient per 30 minutes after
opt-in. This diagnostic rate limit is additional to existing per-occurrence rules.

An exception is an event, not a continuously observed fault. Provide **Acknowledge**
for review; it does not mean the automation is fixed. Log silence or clearing the
HA log buffer must never mean verified recovery. A later successful run can prove
recovery only for explicitly instrumented flows with the same operation and a
reliable success signal; `last_triggered` alone is insufficient. Acknowledged
recurrences reopen on a new event, subject to the notification rate limit.

### 4. Add selected command outcome checks

Start with one useful flow whose real feedback is reliable, then extend:

- Black-fan speed/off: wrap the existing command, record intended state and a
  command generation, wait up to 30 seconds for fresh device-reported feedback.
  A newer command supersedes the prior expectation. Name failures **Fan did not
  report the requested state**, not physical motor failure.
- Charging controls: inspect whether the existing plug telemetry measures real
  power/charging. A switch echo alone cannot prove the phone is charging.
- FingerBot/air conditioner and fan swing: leave outcome coverage explicitly
  unavailable until an independent appliance/position/power signal is selected.

A timeout with healthy, contradictory feedback creates an outcome incident;
missing/stale feedback creates uncertain verification. Do not retry physical
actions automatically. Verify wrappers preserve existing command behaviour and
handle manual overrides, cancellations and rapid successive requests.

## Inbox and delivery design

Use concise headings: **Sign-in required**, **Integration health**, **Matter
service**, **Thread service**, **TV service**, **Software errors**, and specific
outcome rows. Dynamic Repairs/log incidents sit beneath stable category controls;
each child has its own occurrence identity, count and lifecycle. This requires
an explicit diagnostic-child model rather than squeezing changing incidents
into one existing occurrence and accidentally losing later alerts.

Reuse Dashboard, TV, Lachlan home/away, Nic home/away and expiring pauses. Proposed
new-source defaults are dashboard on, TV and phones off during observation;
existing 24-source preferences remain intact. After quiet observation, approve
recipient/category opt-ins. Conditional routing uses the existing 15-minute
presence policy. A shared diagnostic parent groups known related evidence to
avoid duplicate software pushes, while retaining individual device symptoms.

Keep the v1 TV contract stable; export only safe device/category names and fixed
summaries. Show current faults, reviewable exception events and uncertain coverage
separately, with counts and direct local links to Repairs, Integrations or Logs.
Acknowledgement, pause and verified recovery must have distinct labels.

The adapter must expose its own last successful reconciliation and coverage.
HA cannot reliably notify about its own complete shutdown or a failed internet
push path. An external HA heartbeat would be a separate proposal, not an implied
capability of this plan.

## Checks and rollout

Implement in small reviewable stages: native service sensors first; Repairs and
integration health next; software errors next; one outcome check last. Each stage
gets its own manifest and exact feature-branch trial approval. Keep PR #11's
current live acceptance separate from these future diagnostic changes.

Local tests use pure reducers and captured schema shapes with private data
removed: initial snapshot/event races, duplicate and reordered events, missing
sources, ignored issues, explicit resolution, restart persistence, bounds,
redaction, grace, maintenance, conditional delivery and rate limits. Test child
incidents independently, including a second error while another is active.
Outcome tests cover stale feedback, cancellation and a newer command winning.
No isolated HA instance, fake devices, forced credential expiry or simulated
notification environment is required.

For each approved trial: confirm backup readiness, check live drift, save rollback
copies, validate HA before any approved restart, preserve preferences and inspect
privacy-safe readbacks. Observe normal household errors and successful runs;
record only actual results. Any deliberate service stop, physical action or
notification test requires separate approval. Merge only after relevant acceptance.

Implementation-time confirmations remain: exact required-integration mapping,
actual current Repair/config-entry states through a supported read-only access
path, and which independent signals can prove the first physical outcome. These
are evidence to gather before coding the corresponding stage, not reasons to
invent sensors or treat admin tools as essential services.
