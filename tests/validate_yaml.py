"""Parse tracked YAML syntax without loading HA includes, secrets or runtime files."""
import pathlib
import subprocess

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    tracked = subprocess.check_output(
        ['git', 'ls-files', '-z', '--', '*.yaml', '*.yml'], cwd=ROOT,
    ).decode('utf8').split('\0')
    files = [name for name in tracked if name]
    for name in files:
        # BaseLoader treats scalars as text and does not resolve !include,
        # !secret or !input; it parses syntax without interpreting HA config.
        with (ROOT / name).open(encoding='utf8') as stream:
            list(yaml.load_all(stream, Loader=yaml.BaseLoader))
    print(f'PASS YAML syntax: {len(files)} tracked files; no includes/secrets resolved')


if __name__ == '__main__':
    main()
