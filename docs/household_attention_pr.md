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

Runtime `5fe488ccbf67b7d41d2f92a11be6192fe93fcad9` is installed for trial.
The user confirmed backup readiness and approved push/install. All ten previous
hashes matched, fresh rollback copies were verified, the nine-file delta was
installed, HA configuration validation passed and one Core restart completed.
All eleven installed hashes match. CI run 29 passed on documentation tip `f5af27e`.

The one-time migration preserved all 48 recipient choices across 96 home/away
switches. Other preferences, 24 pauses and 24 compared occurrence/delivery
summaries were unchanged; the phone-send timestamp did not advance. The served
dashboard has 24 cards with six switches each and no blind cards. HA retains
15 inactive registry placeholders for removed blind helpers; cleanup is pending.
Rollback evidence is in `/share/household-attention-trials/20261114T1129-5fe488c/`.

Both presence sensors initially reported unknown, rejecting restored samples.
Normal background departure/arrival, conditional push delivery, visual acceptance
and kitchen four-plus-one physical grouping remain open. Nic's Always permission
is an agreed setup assumption. Earlier real phone/TV success does not establish
acceptance of this new conditional-routing trial. The v1 TV contract is unchanged.

Diagnostic adapters are a separate draft plan; no new diagnostic monitoring has
been installed. Historical trial receipts remain preserved.

## Trial and approval

Keep [PR #11](https://github.com/lachlanw-117/Wright-Home-Assistant/pull/11) open.
The approved exact-commit installation and preserving migration are complete.
Continue normal household observation and record acceptance; any additional
deployment, restart, physical action or merge needs its applicable approval.

Follow the [conditional-routing trial procedure](household_attention_presence_trial.md).
Record actual acceptance before requesting separate merge approval. See the
[documentation index](household_attention_index.md) for the guide, coverage
catalogue and historical receipts.
