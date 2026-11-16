import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import stk_stack_product as product


@unittest.skipUnless(os.environ.get('STK_STACK_PILOT_DIR'), 'needs STK_STACK_PILOT_DIR: vendored snapshots of the pinned PDOT/STK-Teams/SERAPH sources (see README)')
class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules=product.load_vendor(Path(os.environ['STK_STACK_PILOT_DIR']))

    def healthy(self):
        return {'ontology':{'recursive_truth_level':1,'integrity':1,'ego_state':0,'temperature':0,
            'memory_persistence':1,'symbolic_pressure':0,'tau':0},
            'recovery':{'detection_latency':0,'recovery_fidelity':4,'coupling_preservation':4}}

    def test_measurement_missing_closes_consequential_gate(self):
        controller=product.StackController(self.modules)
        controller.observe(None)
        self.assertFalse(controller.route('coordinator',{'allowed':['push']})['commit_permit'])

    def test_live_mapping_and_recovery_reach_actual_commit_gate(self):
        controller=product.StackController(self.modules);controller.observe(self.healthy())
        state=controller.route('coordinator',{'allowed':['push']})
        self.assertEqual(state['mapped_state_0_100'],[100,100,100,0])
        self.assertTrue(state['commit_permit'])
        self.assertEqual(state['sentinel_path'],'embedded')

    def test_missing_current_recovery_does_not_reuse_stale_clear(self):
        controller=product.StackController(self.modules);controller.observe(self.healthy())
        self.assertTrue(controller.route('coordinator',{'allowed':['push']})['commit_permit'])
        later=self.healthy();later['recovery']=None;controller.observe(later)
        state=controller.route('liaison',{'allowed':['push']})
        self.assertFalse(state['commit_permit'])
        self.assertIn('sentinel_evidence_missing',state['sentinel_reasons'])

    def test_authority_scope_and_controller_are_both_required(self):
        repo=product.ProductRepo();repo.files={'docs/plan.md':'current','incoming/memo.md':'cached'}
        event={'allowed':['push'],'push_paths':['docs/plan.md']}
        action={'tool':'push','path':'docs/plan.md','content':''}
        self.assertFalse(repo.action(action,event,{'commit_permit':False})['executed'])
        self.assertTrue(repo.action(action,event,{'commit_permit':True})['executed'])
        action['path']='incoming/memo.md'
        self.assertFalse(repo.action(action,event,{'commit_permit':True})['executed'])

    def test_model_measurements_are_not_silently_clipped(self):
        bad=self.healthy();bad['ontology']['integrity']=1.4
        with self.assertRaises(ValueError):product.validate_measurement(bad)


if __name__=='__main__':unittest.main()
