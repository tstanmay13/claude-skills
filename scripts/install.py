#!/usr/bin/env python3
"""Install or verify released public plugins in Claude and Codex profiles."""
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = 'tstanmay13-skills'
REPOSITORY = 'tstanmay13/claude-skills'


def run(command, env, capture=False):
    return subprocess.check_output(command, env=env, text=True) if capture else subprocess.check_call(command, env=env)


def installed(agent, env):
    result = json.loads(run([agent, 'plugin', 'list', '--json'], env, capture=True))
    if agent == 'codex':
        return {p['pluginId']: p for p in result['installed']}
    return {p['id']: p for p in result}


def sync(agent, profile, releases, verify):
    env = os.environ.copy()
    env['CLAUDE_CONFIG_DIR' if agent == 'claude' else 'CODEX_HOME'] = str(profile)
    if not verify:
        profile.mkdir(parents=True, exist_ok=True)
    print(f'{agent}: {profile}', flush=True)
    if not verify:
        known = json.loads(run([agent, 'plugin', 'marketplace', 'list', '--json'], env, capture=True))
        if agent == 'claude':
            found = any(p['name'] == MARKETPLACE for p in known)
            refresh = True
        else:
            # Codex has used both list and object envelopes across versions.
            entries = known if isinstance(known, list) else known.get('marketplaces', [])
            match = next((p for p in entries if p.get('name') == MARKETPLACE), None)
            found = match is not None
            refresh = not match or match.get('marketplaceSource', {}).get('sourceType') != 'local'
        if not found:
            run([agent, 'plugin', 'marketplace', 'add', REPOSITORY], env)
        if refresh:
            run([agent, 'plugin', 'marketplace', 'update' if agent == 'claude' else 'upgrade', MARKETPLACE], env)
        have = installed(agent, env)
        for name, release in releases.items():
            selector = f'{name}@{MARKETPLACE}'
            current = have.get(selector)
            if current and current.get('version') == release['version'] and current.get('enabled'):
                continue
            action = 'update' if agent == 'claude' and current else 'install' if agent == 'claude' else 'add'
            run([agent, 'plugin', action, selector], env)
            if agent == 'claude' and current and not current.get('enabled'):
                run([agent, 'plugin', 'enable', selector, '--scope', 'user'], env)
    have = installed(agent, env)
    for name, release in releases.items():
        selector = f'{name}@{MARKETPLACE}'
        current = have.get(selector)
        if not current or current.get('version') != release['version'] or not current.get('enabled'):
            raise ValueError(f'{profile}: {selector} is missing, disabled, or not at {release["version"]}')
        print(f'  {selector} {release["version"]}: enabled', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--claude-home', type=Path, action='append')
    parser.add_argument('--codex-home', type=Path, action='append')
    args = parser.parse_args()
    profiles = {
        'claude': args.claude_home or [Path.home()/'.claude', Path.home()/'.claude-personal'],
        'codex': args.codex_home or [Path.home()/'.codex', Path.home()/'.codex-personal']
    }
    releases = json.loads((ROOT / 'releases.json').read_text())
    failures = []
    for agent, homes in profiles.items():
        if not shutil.which(agent):
            failures.append(f'{agent} CLI is not installed')
            continue
        for profile in dict.fromkeys(homes):
            try:
                sync(agent, profile, releases, args.verify)
            except (subprocess.CalledProcessError, ValueError, KeyError) as exc:
                failures.append(f'{agent} {profile}: {exc}')
    if failures:
        parser.exit(1, '\n'.join(failures) + '\n')


if __name__ == '__main__':
    main()
