# Development workflow

This is a live household installation. Changes should make it easier to use
without surprising anyone using the house.

Git records the reviewed configuration. Home Assistant is where it runs.
Manual UI edits need to come back into Git, and repository changes need an
explicit deployment. Neither side automatically proves what is on the other.
[AGENTS.md](../AGENTS.md) contains the working rules.

Distinguish configuration edits from ordinary runtime preferences. For the planned
Bravia notice controls, Git will own helper definitions and routing logic, while
the restored helper values will be changed in HA. Toggling a destination will not
require a Git edit or later source reconciliation. The feature-branch
[household attention implementation](household_attention.md) defines these
controls; deployment and live acceptance remain separate. Installed `e2f0bbc` uses one phone control per recipient. The
[conditional-routing candidate](household_attention_presence_trial.md) restores
home/away controls with a guarded migration that preserves current always/off
choices. The candidate is not installed yet.
See also the [companion host notes](bravia_ambient_host.md).

## Make and review changes

`main` is the accepted configuration baseline, not a declaration of current live
state. Start one short-lived branch per coherent change, open a PR with the
problem/result/checks/limitations, review it, trial runtime changes with approval,
record relevant live/device acceptance, then merge with approval and retire
the incorporated branch. A project phase may need several PRs. No permanent
development or staging branch is needed. Preserve published history.

1. Inspect the existing configuration and its device and integration dependencies.
2. Make a small change on a branch, preserving unrelated work.
3. Parse the YAML and check the relevant logic locally. Test unavailable inputs,
   stale state and repeated triggers where they matter.
4. Review the diff and document behaviour, validation and limitations.
5. Push/open the PR and keep it open during an approved trial deployment of its
   exact feature-branch commit. Preserve rollback copies and record deployed hashes.
6. Pass relevant live/device acceptance, document results/limitations and close
   the testing session. Fix and retest on the branch if acceptance fails; relevant
   pending checks keep the gate open. Runtime edits need appropriate retesting.
7. Only then request merge approval and retire the incorporated branch after merge.

This acceptance-before-main order was selected on 8 November 2026. CI success is
not physical acceptance. Documentation-only changes need review/local checks,
not a live deployment. Approval for a trial does not authorise merging it.

GitHub Actions runs tracked-YAML syntax parsing and the synthetic automation
reliability harness on PRs and pushes to `main`. It resolves no `!secret`,
`!include` or blueprint inputs and performs no HA connection or deployment. The
workflow has read-only repository permissions and commit-pinned action versions.
The checks do not replace HA's own configuration validation or physical tests.

To repeat the checks locally with Python 3.13:

```sh
python -m pip install -r tests/requirements.txt
python tests/validate_yaml.py
python -m unittest discover -s tests -v
```

The reliability harness uses `main` as its default comparison baseline; CI sets
`HA_AUTOMATION_BASE_REF=origin/main` for detached PR checkouts. Its unrelated-change
guard covers the original charging/washer fix. Deliberate future changes to other
automations need corresponding test/guard review, not a blanket bypass.

Reusable Bravia source and app/host checks stay in its companion repository;
household configuration and deployment records stay here. Link related PRs when
both repositories change. Software milestone tags/releases belong in Bravia;
HA deployment notes identify the exact source revision actually installed.

### Branch audit - 8 November 2026

`feature/codex-ha-setup` is incorporated through PR #3, and
`feature/ha-automation-reliability` points at the existing reviewed baseline.
`docs/bravia-host-trial` is included in the repository-consolidation PR. These
branches can be retired once consolidation is merged.

`feature/black-fan-dashboard` contains the earlier Glance-card/UI-helper proposal,
superseded by the deployed native-button layout and tracked templates captured
in PR #3. Do not merge the older implementation over the current one. Its exact
tip `2f43c59021ee9b34ced52c19fa7fb56fe3359a40` is preserved by the annotated tag
`archive/black-fan-dashboard-2026-11-08` before branch retirement. The archive is
a historical reference, not a software release or deployment marker.

VS Code settings and Codex connection configuration are machine-specific and
ignored. Shared line endings are defined in `.editorconfig`.

## Compare with Home Assistant

Use read-only API inspection for entity states and exposed configuration.
Compare named YAML files or their hashes when file access is available.
Entity existence does not prove the underlying definition matches the repository.

AI tools help with inspection and implementation. Their access can include write
operations, so an instruction to inspect is not permission to operate devices.
Keep credentials, private keys, runtime storage and backups outside Git.

## Deploy and roll back

1. Review the exact diff and obtain approval for the named deployment, reloads
   and any device tests.
2. Recheck affected live files for drift and save timestamped backups.
3. Upload only approved files. Validate the HA configuration before reloading
   changed template entities.
4. Compare deployed files with the reviewed versions and inspect the resulting
   entities and dashboard. Check phone layout and physical behaviour when relevant.

Dashboard-only YAML changes need a dashboard refresh. Template reloads affect
all YAML template entities, including existing feedback sensors.
Restarts, device actions, pushes and merges are separate approval decisions.

For rollback, restore the affected live backup, validate it and perform the
approved reload or refresh. Do not overwrite unrelated live changes or assume
the current GitHub version is the right rollback target.

See the [black-fan notes](arlec_black_fan_dashboard_notes.md) for implementation
tradeoffs and validation, and [TODO](../TODO.md) for remaining work.
