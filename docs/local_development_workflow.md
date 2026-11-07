# Development workflow

This is a live household installation. Changes should make it easier to use
without surprising anyone using the house.

Git records the reviewed configuration. Home Assistant is where it runs.
Manual UI edits need to come back into Git, and repository changes need an
explicit deployment. Neither side automatically proves what is on the other.
[AGENTS.md](../AGENTS.md) contains the working rules.

## Make and review changes

1. Inspect the existing configuration and its device and integration dependencies.
2. Make a small change on a branch, preserving unrelated work.
3. Parse the YAML and check the relevant logic locally. Test unavailable inputs,
   stale state and repeated triggers where they matter.
4. Review the diff and document behaviour, validation and limitations.
5. Push for review and merge separately from deployment.

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
