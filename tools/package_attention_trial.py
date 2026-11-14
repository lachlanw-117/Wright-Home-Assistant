"""Package only the exact committed household-attention runtime files for review.

Does not connect to HA, deploy, restart, read credentials or include working-tree
content. Configuration/automation snapshots require reviewed merges against live
files, not blind replacement. Runtime preferences are never exported.
"""
import argparse
import ast
import hashlib
import json
import pathlib
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = '9b6513203ac89764d8669aaaf998b1878e2199ba'
FILES = (
    'configuration.yaml', 'automations.yaml',
    'packages/household_attention.yaml',
    'custom_templates/household_attention.jinja',
    'dashboards/household_attention.yaml',
    'attention/sources.yaml', 'attention/delivery_controls.yaml',
    'attention/pauses.yaml', 'attention/watched_entities.yaml',
    'attention/starting_destinations.yaml',
    'attention/policy.yaml',
)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def build(revision, output, installed_revision=None):
    commit = git('rev-parse', '--verify', f'{revision}^{{commit}}').decode().strip()
    if git('status', '--porcelain', '--', *FILES).strip():
        raise SystemExit('Commit the runtime files before packaging the trial.')
    contents = {name: git('show', f'{commit}:{name}') for name in FILES}
    installed = git('rev-parse', '--verify', f'{installed_revision}^{{commit}}').decode().strip() if installed_revision else None
    previous_paths = ()
    if installed:
        # A tracked file at the old SHA was not necessarily installed. Recover
        # that revision's explicit runtime allowlist, without executing its code.
        old_builder = ast.parse(git('show', f'{installed}:tools/package_attention_trial.py'))
        previous_paths = next(ast.literal_eval(node.value) for node in old_builder.body
                              if isinstance(node, ast.Assign)
                              and any(isinstance(target, ast.Name) and target.id == 'FILES' for target in node.targets))
        if not set(previous_paths) <= set(FILES):
            raise SystemExit('Previous runtime file removal requires explicit packaging support.')
    previous = {name: git('show', f'{installed}:{name}') for name in previous_paths}
    changed = [name for name in FILES if contents[name] != previous.get(name)]
    def starting_routes(data):
        return {line[2:].strip() for line in data.decode().splitlines()
                if line.startswith('- input_boolean.')}
    new_starting = sorted(starting_routes(contents['attention/starting_destinations.yaml']) -
                          starting_routes(previous.get('attention/starting_destinations.yaml', b'')))
    needs_migration = installed is not None and b'household_attention_migrate_presence_routes:' in contents['packages/household_attention.yaml']
    manifest = {
        'source_commit': commit,
        'comparison_base': installed or BASE,
        'installed_revision': installed,
        'changed_runtime_files': changed,
        'new_runtime_files': sorted(set(FILES) - set(previous_paths)) if installed else list(FILES),
        'previous_file_hashes': {name: hashlib.sha256(data).hexdigest() for name, data in previous.items()},
        'new_starting_destinations': [] if needs_migration else new_starting,
        'setup_action': 'script.household_attention_migrate_presence_routes' if needs_migration else None,
        'branch': 'feature/household-attention-handler',
        'files': [{
            'path': name, 'sha256': hashlib.sha256(data).hexdigest(),
            'bytes': len(data),
            'install': 'reviewed_merge' if name in ['configuration.yaml', 'automations.yaml']
                       else 'install_after_live_drift_check',
        } for name, data in contents.items()],
        'required_gates': [
            'User confirms Pi backup complete',
            'Explicit approval for this exact commit, install and required restart/reloads',
            'Compare named live files for drift and save rollback copies',
            'HA configuration validation passes before restart',
            'Verify installed hashes and actual runtime/device acceptance with PR open',
            'Separate merge approval after acceptance',
        ],
    }
    patch = git('diff', '--binary', installed or BASE, commit, '--', *FILES)
    readme = (
        f'Source commit: {commit}\n\n'
        'This is a review/trial package, not approval to install.\n'
        'Do not extract payload directly over /config.\n'
        'configuration.yaml and automations.yaml are reference snapshots: merge\n'
        'only approved changes after checking live drift. No runtime state is included.\n'
        'Confirm the Pi backup and obtain named install/restart approval first.\n'
        'Back up each affected existing live file; record files previously absent.\n'
        'Install approved files/merges, validate HA configuration, then perform\n'
        'only the approved restart. Compare actual installed hashes with manifest.\n'
        'If a reviewed live merge differs from this payload, record its deployed hash\n'
        'and reconcile that exact content to Git before proceeding with the trial.\n'
        'On an existing installation, preserve all restored preferences and pauses.\n'
        'Never rerun global starting preferences: enable only the separately approved\n'
        'new_starting_destinations listed in the manifest. If setup_action names the\n'
        'presence migration, run that guarded preserving copy instead of defaults.\n'
        'Compare effective old/new delivery and old preferences before/after.\n'
        'For a fresh install only, apply starting preferences once and enable shared\n'
        'routing after inspecting the store while no washer completion is processing.\n'
        'Kiosk Connection Type was enabled during the earlier trial; verify reporting\n'
        'rather than changing entity settings without a separate need and approval.\n'
        'Keep the PR open. Record acceptance before requesting merge approval.\n\n'
        'Rollback: restore only affected pre-trial copies, preserving later unrelated\n'
        'edits; remove only feature files verified absent before trial. Validate and\n'
        'obtain approval for required restart/reloads. Never restore secrets or\n'
        'runtime preference storage from this package.\n'
    ).encode()
    entries = {f'payload/{name}': data for name, data in contents.items()}
    entries.update({
        'manifest.json': (json.dumps(manifest, indent=2) + '\n').encode(),
        'review.diff': patch,
        'READ-ME-FIRST.txt': readme,
    })
    output = pathlib.Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    print(f'Packaged {len(contents)} runtime files from {commit}: {output.resolve()}')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--output', required=True)
    parser.add_argument('--installed-revision', help='Recorded runtime commit to compare; live drift still requires verification')
    args = parser.parse_args()
    build(args.revision, args.output, args.installed_revision)
