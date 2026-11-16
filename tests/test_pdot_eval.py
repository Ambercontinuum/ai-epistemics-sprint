import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('pdot_eval', Path(__file__).parents[1] / 'tools/pdot_eval.py')
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.binding = {'case_map': {'CASE-001': 'synthetic'}, 'raters': ['A','B'], 'rubric_sha256': 'rubric'}
        self.row = {'case_id':'CASE-001','window':'T1','rater_id':'A','packet_sha256':'packet','rubric_sha256':'rubric','status':'complete','scores':dict.fromkeys(ev.SCORES,2),'evidence_exchange_refs':[1]}

    def test_missing_is_not_zero(self):
        report=ev.summarize([],self.binding,'packet')
        self.assertEqual(report['missing_rating_rows'],6)
        self.assertIsNone(report['descriptive_scores']['A']['T1']['epsilon']['mean'])

    def test_t3_only_coverage(self):
        self.binding['windows']={'T3':(1,25)}
        report=ev.summarize([],self.binding,'packet')
        self.assertEqual(report['expected_rating_rows'],2)
        self.assertEqual(set(report['descriptive_scores']['A']),{'T3'})
        with self.assertRaises(ValueError):ev.summarize([self.row],self.binding,'packet')

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):ev.summarize([self.row,self.row],self.binding,'packet')

    def test_score_ranges_and_types(self):
        for bad in [-1,5,1.2,True,float('nan'),float('inf'),'2']:
            row=copy.deepcopy(self.row);row['scores']['epsilon']=bad
            with self.assertRaises(ValueError):ev.summarize([row],self.binding,'packet')

    def test_missing_complete_rejected(self):
        self.row['scores']['epsilon']=None
        with self.assertRaises(ValueError):ev.summarize([self.row],self.binding,'packet')

    def test_evidence_window_enforced(self):
        self.row['evidence_exchange_refs']=[16]
        with self.assertRaises(ValueError):ev.summarize([self.row],self.binding,'packet')

    def test_empty_evidence_rejected(self):
        self.row['evidence_exchange_refs']=[]
        with self.assertRaises(ValueError):ev.summarize([self.row],self.binding,'packet')

    def test_binding_enforced(self):
        self.row['packet_sha256']='wrong'
        with self.assertRaises(ValueError):ev.summarize([self.row],self.binding,'packet')

    def test_unrated_not_scored(self):
        self.row['status']='unrated'
        with self.assertRaises(ValueError):ev.summarize([self.row],self.binding,'packet')

    def test_agreement_keeps_raters_separate(self):
        b=copy.deepcopy(self.row);b['rater_id']='B';b['scores']['epsilon']=3
        report=ev.summarize([self.row,b],self.binding,'packet')
        entry=next(r for r in report['descriptive_rater_agreement'] if r['window']=='T1' and r['variable']=='epsilon')
        self.assertEqual(entry['paired_n'],1)
        self.assertEqual(entry['mean_absolute_difference'],1)
        self.assertEqual(entry['exact_agreement_fraction'],0)

    def test_packet_roundtrip_and_escaped_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);dataset=root/'dataset';dataset.mkdir();rubric=root/'rubric.md';rubric.write_text('Synthetic rubric')
            messages=[{'exchange_index':i//2+1,'role':'human' if i%2==0 else 'assistant','text':'<script>example</script>'} for i in range(50)]
            ev.write_rows(dataset/'conversations.jsonl',[{'sample_id':'S1','exchange_count':25,'messages':messages}])
            ev.write_rows(dataset/'source_map.jsonl',[{'sample_id':'S1','source_conversation_uuid':'C1','source_message_text_sha256':[ev.hashlib.sha256(m['text'].encode()).hexdigest() for m in messages]}])
            ev.write_json(dataset/'manifest.json',{'selected_conversations':1,'rubric_sha256':ev.sha(rubric),'file_sha256':{n:ev.sha(dataset/n) for n in ('conversations.jsonl','source_map.jsonl')}})
            out=root/'packet';ev.prepare(dataset,rubric,out,['A'],'seed')
            self.assertEqual([len(t['messages']) for t in ev.read_rows(out/'tasks.private.jsonl')],[20,20,50])
            page=(out/'reader.private.html').read_text(encoding='utf-8')
            self.assertNotIn('<script>',page);self.assertIn('&lt;script&gt;',page)
            report=ev.summarize(ev.read_rows(out/'ratings.blank.jsonl'),ev.read_json(out/'packet_manifest.private.json'),ev.sha(out/'packet_manifest.private.json'))
            self.assertEqual(report['status_counts']['unrated'],3)
            lite=root/'lite';receipt=ev.prepare(dataset,rubric,lite,['Amber'],'seed',limit=1,windows=['T3'])
            self.assertEqual(receipt['tasks'],1)
            self.assertEqual(receipt['cases'],1)
            self.assertEqual(len(ev.read_rows(lite/'tasks.private.jsonl')[0]['messages']),50)
            with self.assertRaises(FileExistsError):ev.prepare(dataset,rubric,out,['A'],'seed')
            (dataset/'conversations.jsonl').write_text('tamper')
            with self.assertRaises(ValueError):ev.validate_dataset(dataset,rubric)


if __name__=='__main__':unittest.main()
