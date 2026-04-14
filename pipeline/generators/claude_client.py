import json
import re
import time
import anthropic
import config


_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
_DEFAULT_MAX_TOKENS = 4096


def extract_json(text: str) -> dict | list:
    """
    Parse JSON from a Claude response, stripping markdown fences if present.
    Raises ValueError if parsing fails.
    """
    text = text.strip()
    fenced = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```$", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from Claude response: {e}\nRaw: {text[:200]}")


def call_claude(
    prompt: str,
    model: str = _DEFAULT_MODEL,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
    max_retries: int = 3,
    retry_delay: float = 10.0,
) -> dict | list:
    """
    Call Claude API with the given prompt and return parsed JSON.
    Retries on RateLimitError with exponential backoff.
    """
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    last_err: Exception | None = None

    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text
            return extract_json(raw)
        except anthropic.RateLimitError as e:
            last_err = e
            delay = retry_delay * (2 ** attempt)
            print(f"Rate limit hit, retrying in {delay:.0f}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        except anthropic.APIError as e:
            raise RuntimeError(f"Claude API error: {e}") from e

    raise RuntimeError(f"Exceeded max retries ({max_retries}): {last_err}") from last_err
