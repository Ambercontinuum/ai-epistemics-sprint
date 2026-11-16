# Protocol amendment 02: timeout only

2026-11-15. Amber approved Claude's recommendation to increase per-request timeout from180 to600seconds, replying "approved" to the specific timeout-amendment proposal. Codex executor/recorder.

Frozen sampling, case ordering, Gemini20/Wonder10 allocation, models, envelope, settings, token/thinking limits, no retries/fallback and response parser remain unchanged. Only runner source change is timeout=180 to timeout=600. Timeout is a transport wait, not an increase to requested model tokens. Each attempt may now wait up to600seconds; provider behavior and billing cannot be guaranteed by that setting.

Original bundle `d0e768b4dfa98bc20b9846736690c8cbf93db64458103e997e9bf37ab923bc80` retained. New exact bundle `91154036ce0dd59652398ec763678f40fa230bc3fcef3a38ff6f2496c508d86b`. Rebuilt locally, 30/30 serialized request bytes and hashes identical in order and content. Bundle comparison: only runner_sha256 differs. All other bundle values identical. No test/API call, study attempt or execution marker created for this amendment. No private payloads uploaded.

Claude and Muse must each issue exact-new-bundle execution receipts after verifying the timeout-only diff and identical payloads. Earlier clears do not automatically transfer. A037 authorization was scoped to old hash. Amber approved the timeout amendment; final exact-new-bundle send/launch confirmation remains to be recorded before execution, after this concrete bundle is reviewable. Remote sync gate remains mandatory. No rating results exist from Codex runs.
