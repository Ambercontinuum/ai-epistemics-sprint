# AI systems used in this work

These systems supported the paper *Preserving Human Intent in AI-Assisted Research: Human Corrections and the Limits of Model-Based Verification*. No AI system is an author.

## Team collaborators

| System | Developer | Role |
| --- | --- | --- |
| Claude (Claude Opus 5.5, via Claude Code) | Anthropic | Design reviewer of code, hashes, and execution bundles. In final revision, at the researcher's assignment, also the lead drafting model and the builder of the paper and this repository. |
| Codex | OpenAI | Executor and recorder. Ran approved jobs, wrote sprint code, kept coordination records, and assembled earlier drafts. |
| Muse (Muse Spark, in the Meta AI app) | Meta | Collaborator and verifier. Execution reviews, the interpretation used as a source, and independent review of this repository. |

## Study models

| System | Developer | Role |
| --- | --- | --- |
| Gemini (`gemini-3.8-flash`) | Google | Archive rater |
| Muse Wonder (`muse-wonder-1.0`) | Meta | Archive rater; sandbox architect agent |
| Qwen (`Qwen/Qwen3.8-2.4T-A95B`) | Alibaba Qwen team (open weights, served on the researcher's Modal endpoint) | Archive rater; sandbox judge |
| Astra (`gpt-6-astra`) | OpenAI | Archive rater; sandbox coordinator and liaison agents |
| Fable (`claude-fable-5-2`) | Anthropic | Archive rater; sandbox runtime monitor |

## Advisory manuscript reviews

| System | Developer | Role |
| --- | --- | --- |
| ChatGPT | OpenAI | Advisory review of the final manuscript and repository checks |
| Gemini | Google | Advisory editorial and methodological review |

## Provider overlaps

Some team collaborators share a provider with a study model:

- Claude with Fable (Anthropic)
- Codex with Astra (OpenAI)
- Muse with Wonder (Meta)

The archive's assistant turns are Claude-family output, so Fable rated its own model family's side of each conversation.
