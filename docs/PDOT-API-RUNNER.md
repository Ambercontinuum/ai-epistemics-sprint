# Two-API-rater execution bundle

Prepared per A036. This code prepares requests locally; it does not launch itself or assign scientific ratings. The API model produces the ratings; Codex performs byte/schema validation only. No independent-review clear or Amber private-send authorization is implied.

Pinned candidate settings for reviewer inspection: Gemini `gemini-3.8-flash`, temperature 0, thinkingLevel LOW, maxOutputTokens 4096; Meta `muse-wonder-1.0`, temperature 0, reasoning_effort low, max_completion_tokens 4096. Reasoning token budgets/levels are provider-specific, not asserted equivalent. Actual returned model/version and usage are logged. Non-complete/truncated output is a failure; no silent fallback or retry. Final parameters need the exact-bundle receipts before use; successful default-setting smoke calls do not validate these parameters.

```powershell
python -B tools/pdot_api_raters.py prepare --packet data/private-conversation-archive/pdot-alite-amber-v1 --rubric references/PDOT-public-172b115/templates/rater_guide.md --output data/private-conversation-archive/pdot-api-bundle-v1
```

Preparation revalidates source/rubric hashes and exact task/source text equality. Gemini gets the existing 20; Meta the existing fixed 10. No scoring output, private case map, condition, team discussion, prior model messages or hypotheses enters either request. The byte-identical rubric string and exact message text are wrapped in a fixed administrative envelope asking for seven fields, evidence refs and notes. Each provider gets a fresh stateless request; tools/retrieval and redirects are disabled. This limits context leakage but does not prove immunity to prompt injection in transcripts.

Every request is stored with a SHA-256 and only the two official endpoints are allowed. No credentials enter payloads or manifests. Raw provider output is stored locally; scores are not printed. The syntax parser does not strip fences, fix malformed JSON or retry. Missing failures are never zero. Existing reporting preserves separate rater scores and 20/10 coverage; agreement is computed only on matched nonmissing cases and is model-model agreement, not validity.

Reviewers must issue exact-bundle JSON receipts with reviewer (`claude` or `muse`), status `CLEAR`, scope `execution`, bundle_sha256, receipt_reference and limitations. These are coordination assertions, not authenticated signatures; inspect the referenced authored receipts before materializing them. Amber's separate private authorization file must contain decision_owner `amber`, bundle_sha256, providers `["Google Gemini API", "Meta API"]`, max_requests 30, authorize_private_send_and_launch true, and exact_user_wording. Do not manufacture either receipt or authorization.

```powershell
python -B tools/pdot_api_raters.py execute --bundle data/private-conversation-archive/pdot-api-bundle-v1 --output data/private-conversation-archive/pdot-api-results-v1 --scratchpad ../ai-epistemics-scratchpad --claude-receipt CLAUDE.json --muse-receipt MUSE.json --authorization AMBER.json --env .env
```

Execution checks these records, unchanged runner/harness/envelope/payload hashes, scratchpad origin/main and live remote SHA before reading keys or sending anything. A bundle execution marker prevents automatic replay even with another output directory. Attempt records precede each request, raw output is local, progress stdout contains counts only. Failures are retained. Network timeout 600 seconds per request (Amber-approved timeout-only amendment, 2026-11-15); no retry/fallback. On interruption, do not rerun a partially used bundle without a prospective amendment. Caller must hold the coordination run/output leases and post run logs; the script's exclusive marker is an additional protection, not a substitute for the scratchpad protocol.

The output contains sensitive data and must remain local/git-ignored. Neither reports nor high model agreement establish that PDOT captures intent correctly. Preserve unscorable cases and disagreements. No original composites or numerical success threshold added. This is code and a review bundle, not finished findings.
