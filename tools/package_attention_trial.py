"""Package only the exact committed household-attention runtime files for review.

Does not connect to HA, deploy, restart, read credentials or include working-tree
content. Configuration/automation snapshots require reviewed merges against live
files, not blind replacement. Runtime preferences are never exported.
"""
import argparse
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
)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def build(revision, output):
    commit = git('rev-parse', '--verify', f'{revision}^{{commit}}').decode().strip()
    if git('status', '--porcelain', '--', *FILES).strip():
        raise SystemExit('Commit the runtime files before packaging the trial.')
    contents = {name: git('show', f'{commit}:{name}') for name in FILES}
    manifest = {
        'source_commit': commit,
        'comparison_base': BASE,
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
    patch = git('diff', '--binary', BASE, commit, '--', *FILES)
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
        'Inspect controls and apply starting preferences once; enable shared routing\n'
        'only after verifying the store and while no washer completion is processing.\n'
        'Enable/report/verify the existing kiosk Connection Type sensor only as approved.\n'
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
    args = parser.parse_args()
    build(args.revision, args.output)
