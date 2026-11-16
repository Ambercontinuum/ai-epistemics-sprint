"""Honor Amber's persistent spending stop before any OpenAI request."""
from pathlib import Path
from urllib.parse import urlparse

STOP_PATH = Path(__file__).resolve().parents[2] / 'ai-epistemics-sandbox-codex-scratchpad' / 'OPENAI_API_STOP.json'


class OpenAISpendingStopped(RuntimeError):
    pass


def assert_openai_allowed(provider, endpoint='', model=''):
    is_openai = (str(provider).casefold() in {'astra', 'openai'}
                 or urlparse(endpoint).hostname == 'api.openai.com'
                 or str(model).casefold().startswith('gpt-6-astra'))
    # Presence is sufficient. An empty/malformed record must never reopen spend.
    if is_openai and STOP_PATH.exists():
        raise OpenAISpendingStopped(
            'OpenAI/Astra API use is stopped by Amber. No retry or automatic '
            'substitution. Explicit reauthorization and a spending limit are required.')
