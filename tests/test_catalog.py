import importlib.util
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('catalog', Path(__file__).resolve().parents[1] / 'scripts/catalog.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'example'
        self.repo.mkdir()
        self.catalog_root = self.root / 'catalog'
        self.catalog_root.mkdir()
        self.previous = catalog.CATALOG_ROOT
        catalog.CATALOG_ROOT = self.catalog_root
        self.addCleanup(setattr, catalog, 'CATALOG_ROOT', self.previous)
        (self.catalog_root / 'catalog.json').write_text(json.dumps({'name': 'test', 'owner': {'name': 'Test'}, 'plugins': [{'name': 'example', 'repo': 'example/example', 'category': 'workflow'}]}))
        manifest = {'name': 'example', 'version': '1.0.0', 'description': 'Example', 'author': {'name': 'Test'}, 'license': 'MIT', 'repository': 'https://github.com/example/example'}
        interface = {'displayName': 'Example', 'shortDescription': 'Example workflow', 'longDescription': 'An example workflow.', 'logo': './assets/icon.svg', 'composerIcon': './assets/icon.svg'}
        for folder in ['.claude-plugin', '.codex-plugin', 'skills/example/agents', 'assets', 'orchestrate-profiles']:
            (self.repo / folder).mkdir(parents=True, exist_ok=True)
        (self.repo / 'plugin.json').write_text(json.dumps(dict(manifest, extensions={'com.openai': {'interface': interface}})))
        (self.repo / '.claude-plugin/plugin.json').write_text(json.dumps(manifest))
        (self.repo / '.codex-plugin/plugin.json').write_text(json.dumps(dict(manifest, skills='./skills/', interface=interface)))
        (self.repo / 'skills/example/SKILL.md').write_text('---\nname: example\ndescription: Example workflow.\n---\n\nUse the example.\n')
        (self.repo / 'skills/example/agents/openai.yaml').write_text('interface:\n  display_name: "Example"\n')
        (self.repo / 'assets/icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"/>')
        (self.repo / 'LICENSE').write_text('License fixture')
        (self.repo / 'NOTICE.md').write_text('Attribution fixture')
        (self.repo / '.env').write_text('PRIVATE_MARKER=never-publish')
        (self.repo / 'orchestrate-profiles/company.md').write_text('PRIVATE_MARKER')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.com')
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True).strip()

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'commit.gpgsign=false', 'commit', '-qm', 'Fixture')

    def test_archive_preserves_notices_and_excludes_private_files(self):
        catalog.package(self.root, self.root / 'dist')
        with zipfile.ZipFile(self.root / 'dist/example-1.0.0.zip') as archive:
            self.assertIn('NOTICE.md', archive.namelist())
            self.assertIn('LICENSE', archive.namelist())
            self.assertIn('skills/example/SKILL.md', archive.namelist())
            self.assertFalse(any('PRIVATE_MARKER' in archive.read(name).decode() for name in archive.namelist()))
        self.assertTrue((self.root / 'dist/SHA256SUMS').is_file())

    def test_dirty_source_cannot_be_released(self):
        (self.repo / 'skills/example/SKILL.md').write_text('uncommitted edit')
        with self.assertRaises((AssertionError, ValueError)):
            catalog.package(self.root, self.root / 'dist')

    def test_symlink_cannot_smuggle_private_file_into_archive(self):
        (self.repo / 'skills/example/leak.txt').symlink_to(self.repo / '.env')
        self.commit()
        with self.assertRaises(AssertionError):
            catalog.package(self.root, self.root / 'dist')

    def test_both_catalogs_pin_same_source_commit(self):
        outputs = catalog.generated(self.root)
        expected = self.git('rev-parse', 'HEAD')
        for key in ['.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json']:
            self.assertEqual(outputs[key]['plugins'][0]['source']['sha'], expected)
        self.assertEqual(outputs['releases.json']['example']['sha'], expected)


if __name__ == '__main__':
    unittest.main()
