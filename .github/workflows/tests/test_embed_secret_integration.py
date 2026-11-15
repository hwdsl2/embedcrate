"""Reranker source selection and active Hugging Face helper handoff."""
import os
from pathlib import Path
import shlex
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_secret_files as common


class EmbeddingSecretTests(unittest.TestCase):
    def setUp(self):
        self.fixture = common.LauncherTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_reranker_sources_and_rerank_only_keep_their_existing_meaning(self):
        f = self.fixture
        rerank = f.base / 'rerank secret'
        rerank.write_bytes(b'synthetic-reranker-key\n')
        cases = [
            ({'EMBED_API_KEY_FILE': str(f.external)},
             [b'synthetic-file-key', b'synthetic-file-key']),
            ({'EMBED_API_KEY_FILE': str(f.external), 'RERANK_API_KEY': ''},
             [b'synthetic-file-key', b'']),
            ({'EMBED_API_KEY': 'synthetic-direct-key', 'RERANK_API_KEY_FILE': str(rerank)},
             [b'synthetic-direct-key', b'synthetic-reranker-key']),
            ({'EMBED_API_KEY': '', 'RERANK_API_KEY_FILE': str(rerank),
              'EMBED_ENABLED': 'false', 'RERANK_ENABLED': 'true'},
             [b'', b'synthetic-reranker-key']),
            ({'EMBED_API_KEY': 'synthetic-unused-key', 'RERANK_API_KEY_FILE': str(rerank),
              'EMBED_ENABLED': 'false', 'RERANK_ENABLED': 'true'},
             [b'synthetic-unused-key', b'synthetic-reranker-key']),
        ]
        for values, expected in cases:
            result = f.launch(values, extra_keys=('RERANK_API_KEY',))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.split(b'\0')[:-1], expected)
        # A separate reranker key must not make the helper report an old saved
        # embeddings key as active when embeddings auth was explicitly disabled.
        result = subprocess.run(['bash', '-c', f.remap(common.source('manage.sh')),
                                 'helper', '--getkey'], capture_output=True,
                                env={'PATH': os.environ['PATH'],
                                     'KUBERNETES_SERVICE_HOST': 'fixture'}, timeout=5)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b'')

    def test_hf_token_reaches_model_helper_after_source_removal(self):
        f = self.fixture
        f.envfile.write_text('EMBED_HF_TOKEN_FILE=' + shlex.quote(str(f.external)) + '\n')
        self.assertEqual(f.launch().returncode, 0)
        f.external.unlink()
        stub = f.base / 'python-stub'
        stub.mkdir()
        (stub / 'huggingface_hub.py').write_text(
            'import os\nfrom pathlib import Path\n'
            'def snapshot_download(**kwargs):\n'
            '    Path(os.environ["TEST_TOKEN_CAPTURE"]).write_text(kwargs["token"])\n')
        capture = f.base / 'token-result'
        result = subprocess.run(['bash', '-c', f.remap(common.source('manage.sh')),
                                 'helper', '--pullmodel', 'synthetic/model'],
                                capture_output=True, timeout=5,
                                env={'PATH': os.environ['PATH'],
                                     'KUBERNETES_SERVICE_HOST': 'fixture',
                                     'PYTHONPATH': str(stub), 'TEST_TOKEN_CAPTURE': str(capture)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(capture.read_bytes(), b'synthetic-file-key')
        self.assertFalse(any(b'synthetic-file-key' in p.read_bytes()
                             for p in f.data.iterdir() if p.is_file()))


if __name__ == '__main__':
    unittest.main()
