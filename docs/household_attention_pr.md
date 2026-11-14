# Shared household inbox with grouped devices and editable delivery

Device faults, washing and maintenance previously had separate delivery paths.
This change adds a native HA inbox with independent occurrences, recovery,
coverage and dashboard/TV/phone routing. The latest candidate covers 24 sources,
with concise device headings and descriptive notification messages.

Light sets monitor individual bulbs: any unavailable member creates one item;
recovery requires every member valid. Three blind availability rows are removed,
including their controls, pauses and coverage records. Physical blind controls
and their firmware entries in Updates remain.

Each card has Dashboard, TV, Lachlan home/away and Nic home/away controls. Both
phone switches on means always; one requires matching presence; both off means
no phone alert. A guarded one-time migration copies each current phone choice
to both switches before activating conditional routing. It preserves all current
always/off choices, including washing, pauses and occurrence identities. Hidden
plain phone helpers remain for rollback; global starting preferences are not rerun.

Presence uses post-start GPS and matching phone/kiosk Wi-Fi reports, expiring
after 15 minutes. Missing Wi-Fi never proves away; conflicting evidence is unknown.
Unknown suppresses conditional routes while both-on bypasses it. Eligibility is
rechecked at dispatch; arrival does not replay consumed notices. Local diagnostics
show status, reason and ages without network identifiers or coordinates.

## Validation and limits

47 local tests pass, including grouped failure/recovery, route combinations,
fresh/stale/conflicting evidence, startup restoration, migration preservation,
dispatch-time changes, deduplication and no arrival backlog. YAML parsing of 19
repository files, generated-file consistency and diff checks pass. No isolated
HA instance, fake devices or simulated notification environment was created.

The Pi's last verified runtime remains
`e2f0bbc7adebcfca6a993c36f4ac038f355328d6` (27 sources). Its ten hashes,
HA validation, approved restart and preference continuity passed; the historical
[installation receipt](household_attention_grouped_trial.md) is preserved.
Lachlan confirmed a real phone test and reported the updated TV consumer working.
These outcomes do not establish acceptance of this conditional-routing candidate.
The additive display-name field retains the v1 TV contract checked against
Bravia source `5941e01`; its actual deployed revision is not established.

The new runtime candidate `5fe488ccbf67b7d41d2f92a11be6192fe93fcad9` is local only. HA loading/restoration, background iOS reports,
conditional delivery, visual layout and kitchen four-plus-one physical grouping
still require live acceptance. Nic's Always permission is an agreed setup assumption.
Diagnostic adapters for Repairs, integration/add-on health and software errors
are documented recommendations for a separate change; none is installed here.

## Trial and approval

Keep [PR #11](https://github.com/lachlanw-117/Wright-Home-Assistant/pull/11) open.
Review the exact candidate and nine-file delta (eleven-file reference manifest),
obtain separate push and installation/restart/migration approvals, confirm backup
readiness, check live drift and save rollback copies. Run only the guarded
migration; compare all retained preferences, pauses and occurrences before/after.

Follow the [conditional-routing trial procedure](household_attention_presence_trial.md).
Record actual acceptance before requesting separate merge approval. See the
[documentation index](household_attention_index.md) for the guide, coverage
catalogue and historical receipts.
