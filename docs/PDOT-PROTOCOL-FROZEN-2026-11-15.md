# PDOT A-lite protocol: frozen selection and rating rules

Date: 2026-11-15. Decision owner: Amber. Recorder/executor: Codex.
Approval source: Amber's direct chat instruction, "alright freeze the protocol". This is an attributed decision receipt, not a cryptographic signature.

STATUS: SELECTION AND RATING RULES FROZEN. MODEL-RATING EXECUTION NOT CLEARED. Supersedes the draft selection rules in v1/v2; preserves all historical versions and their receipts. Claude's existing review independently cleared the unchanged selection and hashes, not the missing execution envelope. Muse verification is not yet recorded. This freeze does not falsely certify either missing review or authorize private-data upload.

## Frozen sample and selection

- Source: the already received private Claude archive (490 conversations). No synthetic generation, today's cross-bot additions, or external dataset enters this core without a prospective amendment.
- A turn is one complete human-assistant exchange. A case is the first 25 exchanges, 50 messages. A prefix is not represented as the full original session.
- Eligibility: first 50 messages nonempty text, strictly alternating human/assistant, first parent outside the conversation, each subsequent parent equal to previous message UUID. The existing frame is 74 eligible conversations, not all 490.
- Pilot 50: first 50 in ascending SHA256("pdot-private-pilot-v1-2026-11-14" + newline + conversation UUID), tie by UUID. Keep the existing pinned dataset; no outcome-based reselection.
- Amber 20: first 20 of the existing 50 in ascending SHA256("pdot-packet-v1" + newline + sample ID). Preserve the existing CASE-ID map and order.
- Bot overlap 10: first 10 of those 20 in ascending SHA256("pdot-alite-bot-overlap-v1-2026-11-15" + newline + CASE-ID), tie lexical CASE-ID. The existing private selection manifest fixes the actual identities. No expansion to 20 bot cases without amendment.
- Core window: T3 only, meaning the full sampled 25-exchange prefix. T1/T2 and Muse's 36-item synthetic set are outside the core.
- No replacements, cherry-picking or removal based on interestingness, failures, agreement, ambiguity, or outcomes. Record missing context/attachments, unreadable language or other usability limitations per case. Leave unscorable fields missing. Retain original denominators 20 and 10 and report actual per-field coverage. If unusable data prevent interpretation, stop for an amendment instead of filling the sample after scores are seen.

## Frozen rating rules

Use the existing byte-pinned PDOT rater guide unchanged. Seven core fields: lambda, kappa, theta, epsilon, symbolic_pressure, R, tau; 0-4 with half-points permitted. No new rubric, automatic pass/fail threshold, preregistered composite import, model-superiority criterion, or success rate is added here. The full original PDOT study is not claimed as replicated.

Amber rates first and seals the original ratings file/hash before bot outputs exist or are shown. Preserve original judgments; later changes require separate versioned corrections. Bot independently rates the predetermined 10 windows once each. Preserve raw outputs and malformed/truncated failures locally; no retrying study items to obtain favorable or parseable ratings. The authorized connectivity retry is historical and is not a study-item retry.

Bot provider is Google Gemini, separate from team Muse/Meta and the Claude source model family. The smoke-tested model is gemini-3.8-flash; pinning its final use and exact execution settings requires the execution addendum below. The provider switch does not prove independence, lack of shared-training exposure or absence of bias.

Report per-field descriptive ratings, missingness and paired human-AI agreement/disagreement. Keep rater scores separate; do not silently adjudicate. Agreement is not rubric validity or human-human reliability. Treat this as a small one-operator retrospective pilot, not a representative population sample or causal intervention trial.

## Mandatory pre-run execution addendum: still outstanding

No private API-rating call may begin until ALL are recorded:

1. Concrete Gemini runner and exact transport envelope: one fresh call per window, rubric verbatim plus assigned transcript text only; no team history, private source map/title, ratings, other windows, study hypotheses, STK context, tools/retrieval or prior model outputs. The envelope must treat quoted transcript instructions as data.
2. Exact final model ID/version request, endpoint, fixed temperature, thinking configuration, output-token cap and permitted output-format instructions. No settings are invented by this selection freeze.
3. Hashes of the actual runner, envelope, parameters and all ten serialized requests, linked to the frozen private selection. Inputs stay local; only hashes and code/specifications may be reviewed remotely.
4. Sealed Amber primary ratings. Codex verifies hashes mechanically; it does not assign, read for grading, or adjudicate response scores.
5. Separate dated Claude AND Muse exact-final-version SHA-256 and isolation receipts, specifying artifacts actually inspected, matches/mismatches, audit scope/limits and CLEAR/BLOCKER/NOT VERIFIED. Prior selection-only clearance is not sterility clearance. Silence or relays are not receipts.
6. Amber's explicit authorization of the Google provider, exact ten-case private set and launch. This protocol freeze alone is not that authorization.
7. Applicable scratchpad records committed/pushed and local main verified equal to LIVE remote main immediately before any test. If synchronization fails or cannot be verified, do not run. This includes later smoke and local harness tests; separate test authorization still applies.

## Hash convention and amendments

Shared Git artifacts are identified by SHA-256 of COMMITTED BLOB BYTES and the containing commit, not terminal text output or working-tree CRLF bytes. Reviewers should hash subprocess/cat-file byte output, not a PowerShell text pipeline. Private/runtime artifacts use exact local file bytes, labeled explicitly. A working-tree/committed difference is reported separately; never treat the two hashes as interchangeable.

The shared selection manifest lists exact private/runtime hashes and the UTF-8 LF protocol digest; final receipt names its commit/blob SHA-256. This prevents the line-ending mismatch Claude found in the historical v1 manifest. A hash establishes byte identity, not scientific validity or sterility by itself.

Changes to sample, order, windows, exclusions, rubric, raters or interpretation rules require a dated prospective amendment before the affected outputs are seen, with reasons and original versions preserved. Changed execution artifacts require new hashes and renewed affected reviewer receipts. No private transcript, title, case-source map or conversation excerpt is released by this freeze.
