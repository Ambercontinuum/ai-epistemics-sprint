# Preserving Human Intent in AI-Assisted Research

Submission repository for the paper *Preserving Human Intent in AI-Assisted Research: Human Corrections and the Limits of Model-Based Verification*. Author: Amber Anson (AmberContinuum Research), AI x Epistemics Research Sprint, November 2026.

- **Paper:** [`paper/preserving-human-intent.pdf`](paper/preserving-human-intent.pdf)
- **LaTeX source:** [`paper/source/`](paper/source/)

## What is new in this sprint, and what is pre-existing

| Material | Status |
| --- | --- |
| PDOT, STK-Flux, STK-Teams, SERAPH frameworks | **Pre-existing** (the researcher's prior work). Not included here; cited at pinned public commits: PDOT `172b115`, STK-Flux `73cfa6b`, STK-Teams `21afd36`, SERAPH `4ee7d30`. |
| The researcher's private conversation archive | **Pre-existing** private data. **Not included**, and not released. |
| `tools/pdot_eval.py`, `tools/pdot_api_raters.py`, `tools/pdot_qwen_pass.py`, `tools/pdot_additional_raters.py` | **Sprint-new.** Archive-pilot harness: frozen packets, exact-bundle gated API raters, strict parsing, and descriptive aggregation. |
| `tools/stk_coordination_sandbox.py`, `tools/stk_sandbox_evaluate.py`, `tools/stk_stack_product.py` | **Sprint-new.** Constructed multi-agent sandbox, evaluator, and the adapter linking the pinned frameworks with a virtual action gate. |
| `tools/openai_spend_guard.py` | **Sprint-new**, written *after* the sandbox runs (spending stop). It was not part of the tested intervention. |
| `tests/`, `docs/` (frozen protocol and amendments), `paper/` | **Sprint-new.** |

The paper's Appendix B gives the same boundary in more detail.

## Running the tests

From the repository root:

```
python -m unittest discover -s tests -p "test_*.py"
```

On a clean checkout, expect 22 tests to pass and 7 to be skipped:

- The five `test_stk_stack_product` integration tests need `STK_STACK_PILOT_DIR` to point at local vendored snapshots of the pinned framework sources. Those snapshots are not redistributed here.
- Two `test_openai_spend_guard` tests need the persistent OpenAI stop file, which lives outside this repo.

## What this repository does not let you do

- **Re-run the archive pilot.** The runners read `data/private-conversation-archive/`, which is private and not included. They also require exact-bundle reviewer receipts and the researcher's per-bundle authorization. The code is published for inspection, not for replay.
- **Reach the original Qwen endpoint.** `tools/pdot_qwen_pass.py` and `tools/stk_sandbox_evaluate.py` hard-coded a private live endpoint when they ran. In the published copies, the endpoint is read from `PDOT_QWEN_ENDPOINT` instead.
- **Match the executed source hashes.** Several published files differ from the executed bytes: two endpoint redactions, three spend-guard additions made after the runs, and test-skip edits. `MANIFEST.json` lists every published file's hash, the executed hashes from before these edits, and each edit.

## Privacy

This repository contains none of the following:

- raw conversations, case identifiers, or source mappings;
- model responses or case-level ratings;
- credentials or `.env` files.

Aggregate agreement tables appear only in the paper.

## Use of AI systems

AI systems assisted with planning, code, and drafting, as described in the paper's LLM usage statement (Appendix D). No AI system is an author.

## License

No license has been granted yet; all rights are reserved pending the author's decision. The pinned framework repositories keep their own licenses and contributor attribution.
