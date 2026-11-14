# Add a shared household inbox with grouped devices and editable delivery

Device faults, washing and maintenance currently have separate delivery paths.
This change adds a native HA inbox with independent occurrences, recovery,
coverage and dashboard/TV/phone routing. The candidate now covers 27 sources:
physical light sets, fans, plugs, blinds, FingerBot, appliances, WAN, kiosk Wi-Fi,
backups and grouped upgrades. Dashboard headings use device names while messages
retain useful fault descriptions.

Kitchen lights are grouped four-plus-entrance, ensuite three and bathroom two.
Any unavailable member creates one item; recovery requires every member valid.
New sources start with dashboard/TV only. Existing fridge timing, recipients,
preferences, pauses, washing handover and independent laundry lighting remain.
Home/away splitting is parked. Existing dormant helpers retain their IDs; new
rows receive four active destination controls without forced initial values.

## Validation and limits

31 local tests pass, including production reducer/routing checks, grouped
partial failure, uncertain recovery, recurrence, name migration and legacy
helper preservation. YAML parsing, generated-file consistency and diff checks
pass. No HA instance, fake devices or simulated delivery environment was created.
Local checks do not prove HA restoration, physical availability or handset delivery.

The current recorded Pi runtime remains `3cc4573` (12 sources), following the
separately approved initial and light-pair trials. Its hashes, validation,
restart and preference continuity passed. Lachlan subsequently confirmed a real
phone test and reported the separately updated TV consumer working. Kiosk
Connection Type was observed enabled and reporting Wi-Fi. These outcomes do not
imply unreported lifecycle, duplicate-suppression or washing acceptance.

Runtime candidate `e2f0bbc7adebcfca6a993c36f4ac038f355328d6` has not been pushed
or installed. All three blinds currently
report unknown and will show coverage gaps. Kitchen's physical four-plus-one
split and the new dashboard layout still need acceptance. The additive
`display_name` field retains the v1 descriptive-title contract checked against
Bravia source revision `5941e01`; its actual deployed revision is not established.

## Trial and approval

Keep [PR #11](https://github.com/lachlanw-117/Wright-Home-Assistant/pull/11) open.
Review the exact candidate commit and runtime manifest, obtain separate push
and installation/restart approvals, confirm backup readiness and recheck drift.
Preserve rollback copies and all existing preferences; enable only the 30 new
display controls, with new phones off. Never rerun global starting preferences.

Follow the [candidate trial procedure](household_attention_grouped_trial.md) and
record actual acceptance before requesting separate merge approval. Documentation
and local checks do not pass the physical/visual gate. See the
[documentation index](household_attention_index.md) for the current guide,
coverage catalogue and historical installation evidence.
