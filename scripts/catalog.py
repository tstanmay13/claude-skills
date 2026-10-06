#!/usr/bin/env python3
"""Build both runtime catalogs and submission ZIPs from separate source checkouts."""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

CATALOG_ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def sources(root):
    catalog = json.loads((CATALOG_ROOT / 'catalog.json').read_text())
    result = []
    for entry in catalog['plugins']:
        repo = root / entry['name']
        if not (repo / '.git').exists():
            raise ValueError(f'Missing source checkout: {repo}')
        manifest = json.loads((repo / 'plugin.json').read_text())
        assert manifest['name'] == entry['name'], repo
        assert manifest['repository'] == f"https://github.com/{entry['repo']}", repo
        result.append((entry, repo, manifest))
    return catalog, result


def generated(root):
    catalog, repos = sources(root)
    claude = dict(name=catalog['name'], owner=catalog['owner'],
                  metadata={'description': "Tanmay Singh's skills for Claude Code and Codex.", 'version': '0.2.0'}, plugins=[])
    codex = dict(name=catalog['name'], interface={'displayName': "Tanmay Singh's Skills"}, plugins=[])
    for entry, repo, manifest in repos:
        source = dict(source='url', url=f"https://github.com/{entry['repo']}.git", sha=git(repo, 'rev-parse', 'HEAD'))
        claude['plugins'].append(dict(name=entry['name'], source=source, description=manifest['description'], category=entry['category']))
        codex['plugins'].append(dict(name=entry['name'], source=source,
                                    policy={'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, category='Productivity'))
    releases = {entry['name']: {'version': manifest['version'], 'sha': git(repo, 'rev-parse', 'HEAD')}
                for entry, repo, manifest in repos}
    return {'.claude-plugin/marketplace.json': claude, '.agents/plugins/marketplace.json': codex, 'releases.json': releases}


def validate(root):
    _, repos = sources(root)
    for entry, repo, manifest in repos:
        name = entry['name']
        for relative in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json']:
            other = json.loads((repo / relative).read_text())
            for key in ['name', 'version', 'description', 'author', 'license', 'repository']:
                assert other[key] == manifest[key], f'{repo}/{relative}: {key} differs'
        interface = manifest['extensions']['com.openai']['interface']
        for key in ['displayName', 'shortDescription']:
            assert 0 < len(interface[key]) <= 30, f'{name}: {key} exceeds listing limit'
        assert 0 < len(interface['longDescription']) <= 4000
        assert json.loads((repo / '.codex-plugin/plugin.json').read_text())['skills'] == './skills/'
        for key in ['logo', 'composerIcon']:
            asset = repo / interface[key]
            assert asset.is_file() and asset.resolve().is_relative_to(repo.resolve()), asset
        assert (repo / 'LICENSE').is_file()
        for skill in (repo / 'skills').iterdir():
            if not skill.is_dir():
                continue
            content = (skill / 'SKILL.md').read_text()
            assert content.startswith('---\n') and '\n---\n' in content, skill
            assert re.search(r'^name: ' + re.escape(skill.name) + r'$', content, re.M), skill
            assert 'description:' in content.split('\n---\n')[0], skill
            assert (skill / 'agents/openai.yaml').is_file(), skill
            for document in skill.rglob('*.md'):
                for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', document.read_text()):
                    if '://' in target or target.startswith('#'):
                        continue
                    assert (document.parent / target.split('#')[0]).exists(), f'{document}: {target}'
        print(f"validated {name} {manifest['version']}")


def package(root, output):
    validate(root)
    output.mkdir(parents=True, exist_ok=True)
    checksums = []
    for entry, repo, manifest in sources(root)[1]:
        if git(repo, 'status', '--porcelain'):
            raise ValueError(f'Commit source changes before packaging: {repo}')
        archive = output / f"{entry['name']}-{manifest['version']}.zip"
        # Allowlist distributable files. Never include .git, private profiles, eval output, or local config.
        files = [repo / p for p in ['plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'LICENSE']]
        for optional in ['NOTICE.md', 'THIRD_PARTY_NOTICES.md']:
            if (repo / optional).exists():
                files.append(repo / optional)
        files += [p for p in (repo / 'skills').rglob('*') if p.is_file()]
        interface = manifest['extensions']['com.openai']['interface']
        files += [repo / interface[key] for key in ['logo', 'composerIcon']]
        files += [repo / p for p in interface.get('screenshots', [])]
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for path in sorted(set(files)):
                assert not path.is_symlink() and path.resolve().is_relative_to(repo.resolve()), path
                relative = path.relative_to(repo).as_posix()
                assert not any(part.startswith('.') for part in path.relative_to(repo).parts) or relative in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json'], path
                z.write(path, relative)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        checksums.append(f'{digest}  {archive.name}')
        print(f'packaged {archive}')
    (output / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['generate', 'check', 'package'])
    parser.add_argument('--source-root', type=Path, default=CATALOG_ROOT.parent)
    parser.add_argument('--output', type=Path, default=CATALOG_ROOT / 'dist')
    args = parser.parse_args()
    try:
        if args.command == 'generate':
            validate(args.source_root)
            for relative, value in generated(args.source_root).items():
                path = CATALOG_ROOT / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(value, indent=2) + '\n')
        elif args.command == 'check':
            validate(args.source_root)
            for relative, value in generated(args.source_root).items():
                assert json.loads((CATALOG_ROOT / relative).read_text()) == value, f'{relative} is stale; run generate'
        else:
            package(args.source_root, args.output)
    except (AssertionError, ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'catalog: {exc}\n')


if __name__ == '__main__':
    main()
