# Add a shared household attention inbox and editable destinations

Household faults, washing messages and available upgrades currently have separate
delivery paths. This change adds a native HA-owned typed inbox with independent
source occurrences, recovery, monitoring coverage and dashboard/TV/phone routing.
Fridge visibility loss notifies both people immediately; other configured faults
notify Lachlan once after 15 minutes. Updates form one summary. Washing is a
one-shot notice with its existing red laundry-light action preserved.

The latest scope parks home/away phone splitting. Four active switches per row
control dashboard, TV, Lachlan phone and Nic phone. Earlier home/away helper IDs
remain dormant without resets. Everyday values restore in HA and are never
overwritten by deployment. The legacy washing phone actions remain available
until an explicit shared-routing cutover avoids duplicate delivery.

Validation: 25 local tests, YAML syntax, generated-file consistency and diff checks
pass. Tests use the actual production templates/reducers without a separate HA
installation, fake devices or simulated delivery service. Local tests do not prove
HA schema/include loading, restoration or physical behaviour.

Trial status: not deployed. Keep this PR open through an approved trial of its
exact feature-branch commit on the backed-up Pi. Live-file drift comparison is
pending because the file connector lacks SSH transport. Kiosk Connection Type
is registered but disabled and needs approved enablement/runtime verification.
No TV application changes or third-party router integration are included. Lights,
rapid battery drain and auth sources have no reviewed adapters in this slice.

Follow `docs/household_attention.md` and record actual acceptance/rollback metadata
in `docs/household_attention_trial.md`. Merge requires relevant live acceptance
and separate explicit approval.
