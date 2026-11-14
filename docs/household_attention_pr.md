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

Trial status: installed from exact runtime commit `6b36c4a` on 14 November 2026,
following explicit backup confirmation and installation/restart/setup approval.
Direct SSH/SCP verified both existing files against baseline and saved rollback
copies before installation. All ten installed hashes match; HA configuration
validation and one Core restart passed. Nine source records, expected controls,
three-view dashboard configuration and starting preferences loaded. Shared
routing is on, with no existing-notice replay or phone-send calls observed.
Keep this PR open. Kiosk Connection Type is still disabled and needs manual HA
entity-setting enablement and real report verification. Phone/light, visual UI,
fault lifecycle and continuity across a later approved restart remain pending.
No TV application changes or third-party router integration are included. Lights,
rapid battery drain and auth sources have no reviewed adapters in this slice.

Follow `docs/household_attention.md` and record actual acceptance/rollback metadata
in `docs/household_attention_trial.md`. Merge requires relevant live acceptance
and separate explicit approval.
