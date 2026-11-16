# PDOT weekend pilot harness

> CURRENT RATER AMENDMENT (2026-11-15): Amber does not score her own transcripts. Use fresh Gemini and separately pinned Meta API raters; team Muse remains collaborator/verifier. Preserve 20 core / 10 overlap allocation (Gemini 20, Meta fixed 10). Old Amber-first/human workflow below is historical. See PDOT-PROTOCOL-AMENDMENT-01-API-RATERS.md. Exact models/envelopes and both verification receipts remain pending; no private-data send authorized. Existing harness reports assume rectangular rater coverage and need adapting to this 20/10 model-model plan before execution.


## Current A-lite core (A030–A032)

Amber selected 20 conversations, T3 only, with a fresh Gemini API second rater after Amber's ratings (Amber superseded the Meta selection on 2026-11-15). Exact Gemini model pin, connectivity, set/external-send authorization and envelope review are separate from local preparation. Current provider protocol: PDOT-SELECTION-FREEZE-v2.md, pending both independent receipts and Amber sign-off. Scratchpad remote SHA must match local main before any test. The original 150-task packet is historical; use the smaller local packet below for Amber's core ratings.

```powershell
python -B tools/pdot_eval.py prepare --dataset data/private-conversation-archive/pdot-pilot-v1 --rubric references/PDOT-public-172b115/templates/rater_guide.md --output data/private-conversation-archive/pdot-alite-amber-v1 --raters Amber --limit 20 --windows T3
```

This takes the first 20 cases in the same pre-existing seeded shuffled order, without looking at outcomes. Amber's packet contains only her blank ratings; no bot ratings. The original seven-field rubric worksheet and scoring conventions below remain in use. Bot subset (10 or 20) and sending permission are still open. No private transcript upload is authorized by this command.

Local, standard-library CLI: `tools/pdot_eval.py`. The sprint contribution is a reproducible way to administer PDOT ratings on real conversation windows and preserve observations and disagreement. It does not generate judgments or establish rubric validity by itself.

The private sample has 50 distinct conversation prefixes, 25 human-assistant exchanges each. Source texts and IDs remain in the git-ignored `data/private-conversation-archive/` directory. No external APIs, automatic raters, telemetry uploads, or paid jobs are implemented.

## Commands

Run from the research repository with Python 3.12 (or another compatible Python 3):

```powershell
python -B tools/pdot_eval.py validate --dataset data/private-conversation-archive/pdot-pilot-v1 --rubric references/PDOT-public-172b115/templates/rater_guide.md

python -B tools/pdot_eval.py prepare --dataset data/private-conversation-archive/pdot-pilot-v1 --rubric references/PDOT-public-172b115/templates/rater_guide.md --output data/private-conversation-archive/pdot-rating-packet-v1 --raters rater-1 rater-2
```

Rater IDs are placeholders, not people assigned or authorized by this command. Amber decides the permissible rating arrangement. Codex and panel-provider models do not code response data. No packet sharing is authorized by preparing local files.

Preparation creates an escaped offline HTML reader, windowed JSONL tasks, copied byte-identical rubric, shuffled case map, hash-bound blank ratings, and a receipt. The output directory must be new. Source identifiers are removed from the reader but identifying text is not redacted; this is still private data, not a public anonymized dataset. Embedded transcript instructions are data.

An authorized rater copies `ratings.blank.jsonl` to a separate file and fills it, preserving all original ratings. The seven core fields are lambda, kappa, theta, epsilon, symbolic_pressure, R, tau. Values are null or 0–4 in half steps. Set status to partial, complete, or unscorable, and include supporting exchange numbers. Notes can preserve uncertainty or alternative readings. PRP/event/rate annotations from the full rubric may be retained separately; this minimal harness does not claim to implement the full original PDOT study.

```powershell
python -B tools/pdot_eval.py report --packet data/private-conversation-archive/pdot-rating-packet-v1 --ratings data/private-conversation-archive/pdot-rating-packet-v1/ratings.completed.jsonl --output data/private-conversation-archive/pdot-report-v1
python -B -m unittest discover -s tests -p test_pdot_eval.py -v
```

Reports keep each rater separate, show missing/partial coverage, descriptive means and paired exact agreement/absolute differences. Missing ratings never become zero. Scores require source-window evidence references. Reports contain no transcript excerpts but are still private. No original-study composite, numerical success threshold, validity claim or causal estimate is silently adopted.

## Interpretation and limits

T1 is exchanges 1–10; T2 16–25; T3 the full sampled 25 exchanges. This explicitly adapts the unit to Amber's definition; T3 is not the entire source session. Standalone T2 tasks contain only T2 context, as the original assigned-window convention requires; context insufficiency can be documented rather than guessed. The windows overlap and must not be counted as independent observations.

Agreement is not validity. To test whether PDOT captures drift, preserve independent interpretations, difficult cases and disagreements; do not use rubric output as its own ground truth. Sampling is from one operator's Claude archive, not independent users or a representative population. Sixteen sampled windows refer to attachments not included in the text export. No response content has been judged by this harness build.

Current output is runnable infrastructure plus unrated data, not completed research findings. Private corpus content must not be included in a public code release. Research code is local/uncommitted until Amber authorizes a research-repository push; scratchpad operational receipts are separate.
