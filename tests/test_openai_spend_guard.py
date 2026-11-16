import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import openai_spend_guard as guard


class SpendingStopTests(TestCase):
    def test_stop_blocks_provider_endpoint_and_model_aliases(self):
        with tempfile.TemporaryDirectory() as temporary:
            stop=Path(temporary)/'STOP.json';stop.write_text('malformed',encoding='utf-8')
            with patch.object(guard,'STOP_PATH',stop):
                for args in [('Astra','',''),('alias','https://api.openai.com/v1/responses',''),('alias','','gpt-6-astra')]:
                    with self.assertRaises(guard.OpenAISpendingStopped):guard.assert_openai_allowed(*args)

    def test_other_provider_is_not_implicitly_launched_or_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            stop=Path(temporary)/'STOP.json';stop.write_text('',encoding='utf-8')
            with patch.object(guard,'STOP_PATH',stop):
                guard.assert_openai_allowed('Qwen','https://example.invalid/v1/chat/completions','Qwen/model')

    def test_persistent_actual_stop_is_present(self):
        self.assertTrue(guard.STOP_PATH.exists())
        with self.assertRaises(guard.OpenAISpendingStopped):
            guard.assert_openai_allowed('Astra','https://api.openai.com/v1/responses','gpt-6-astra')

    def test_all_astra_capable_runner_entrypoints_stop_before_setup(self):
        import pdot_additional_raters
        import stk_coordination_sandbox
        import stk_stack_product
        attempts=[lambda:pdot_additional_raters.execute(*([None]*7)),
                  lambda:pdot_additional_raters.call('Astra',None,None,None,None,None,None),
                  lambda:stk_coordination_sandbox.run(None),
                  lambda:stk_stack_product.run(None)]
        for attempt in attempts:
            with self.assertRaises(guard.OpenAISpendingStopped):attempt()


if __name__=='__main__':main()
