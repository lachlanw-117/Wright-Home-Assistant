# Add a shared household attention inbox and editable destinations

Household faults, washing messages and available upgrades currently have separate
delivery paths. This change adds a native HA-owned typed inbox with independent
source occurrences, recovery, monitoring coverage and dashboard/TV/phone routing.
Fridge visibility loss notifies both people immediately; other configured faults
notify Lachlan once after 15 minutes. Updates form one summary. Washing is a
one-shot notice with its existing red laundry-light action preserved.
Three separate living-room light-pair records cover TV, dining table and
basketball hoop. Each watches both physical bulbs and resolves only when both
are reachable; dashboard/TV routes start on and phones off.

The latest scope parks home/away phone splitting. Four active switches per row
control dashboard, TV, Lachlan phone and Nic phone. Earlier home/away helper IDs
remain dormant without resets. Everyday values restore in HA and are never
overwritten by deployment. The legacy washing phone actions remain available
until an explicit shared-routing cutover avoids duplicate delivery.

Validation: 27 local tests, YAML syntax, generated-file consistency and diff checks
pass. Tests use the actual production templates/reducers without a separate HA
installation, fake devices or simulated delivery service. Local tests do not prove
HA schema/include loading, restoration or physical behaviour.

Trial status: exact runtime commit `3cc4573` installed on 14 November 2026, after
the initial `6b36c4a` trial and separate approval for the light-pair extension,
push, installation and one additional restart. Direct SSH/SCP checked drift and
saved fresh six-file rollback copies. All ten installed hashes match. HA config
validation, CI and the approved restart passed. Twelve source records and expected
controls loaded. All 74 original preferences, nine original pauses and nine record
summaries survived the restart. Only the six new pair dashboard/TV routes were
enabled; their phones stay off. Shared routing remains on, with no handler
phone-send calls observed.
Keep this PR open. Kiosk Connection Type is still disabled and needs manual HA
entity-setting enablement and real report verification. Phone/light, visual UI,
fault lifecycle and physical wall-switch pair tests remain pending.
No TV application changes or third-party router integration are included. Other
lights, rapid battery drain and auth sources remain outside this slice.

Follow `docs/household_attention.md` and record actual acceptance/rollback metadata
in `docs/household_attention_trial.md` and `docs/household_attention_living_room_trial.md`.
Merge requires relevant live acceptance
and separate explicit approval.
