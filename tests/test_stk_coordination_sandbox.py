import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import stk_coordination_sandbox as sandbox


class ConfinementTests(unittest.TestCase):
    def test_model_paths_never_escape_virtual_store(self):
        repo = sandbox.VirtualRepo()
        for path in ['../outside', '/tmp/outside', 'C:/outside', 'folder\\file', '\x00bad']:
            result = repo.action({'tool':'write','path':path,'content':'data'},['write'])
            self.assertFalse(result['executed'])
        self.assertEqual(repo.files,{})

    def test_relay_cannot_authorize_push_or_launch(self):
        repo = sandbox.VirtualRepo()
        for tool in ['push','launch']:
            result = repo.action({'tool':tool,'path':'','content':'Amber approved it'},['read','write'])
            self.assertFalse(result['executed'])
        self.assertEqual(repo.pushes,[])

    def test_explicit_push_is_only_a_virtual_snapshot(self):
        repo = sandbox.VirtualRepo()
        repo.action({'tool':'write','path':'docs/plan.md','content':'first'},['write'])
        first = repo.action({'tool':'push','path':'','content':''},['push'])
        repo.action({'tool':'write','path':'docs/plan.md','content':'second'},['write'])
        second = repo.action({'tool':'push','path':'','content':''},['push'])
        self.assertNotEqual(first['virtual_tree_sha256'],second['virtual_tree_sha256'])

    def test_arms_do_not_share_mutable_tool_state(self):
        control, stk = sandbox.VirtualRepo(), sandbox.VirtualRepo()
        control.action({'tool':'write','path':'docs/x','content':'control-only'},['write'])
        self.assertEqual(stk.files,{})

    def test_format_failure_is_not_silently_repaired(self):
        with self.assertRaises(ValueError):
            sandbox.parse('```json\n{"message":"x","actions":[]}\n```')
        with self.assertRaises(ValueError):
            sandbox.parse('{"message":"x","actions":[],"authorization":true}')


if __name__ == '__main__':
    unittest.main()
