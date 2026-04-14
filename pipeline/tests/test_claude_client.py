import pytest
from unittest.mock import MagicMock, patch
from generators.claude_client import call_claude, extract_json


def test_extract_json_from_plain_json():
    raw = '[{"id": 1, "text": "hello"}]'
    result = extract_json(raw)
    assert result == [{"id": 1, "text": "hello"}]


def test_extract_json_strips_markdown_json_fence():
    raw = '```json\n[{"id": 1}]\n```'
    result = extract_json(raw)
    assert result == [{"id": 1}]


def test_extract_json_strips_plain_backtick_fence():
    raw = '```\n{"key": "val"}\n```'
    result = extract_json(raw)
    assert result == {"key": "val"}


def test_extract_json_raises_on_invalid():
    with pytest.raises(ValueError, match="Could not parse JSON"):
        extract_json("This is not JSON at all.")


def test_call_claude_returns_parsed_json():
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='[{"id": 1}]')]
    mock_client.messages.create.return_value = mock_msg

    with patch("generators.claude_client.anthropic.Anthropic", return_value=mock_client):
        result = call_claude("Say hello", model="claude-3-5-sonnet-20241022")

    assert result == [{"id": 1}]
    mock_client.messages.create.assert_called_once()


def test_call_claude_retries_on_rate_limit():
    import httpx
    import anthropic as _anthropic

    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='{"ok": true}')]

    # Build a RateLimitError that matches the installed anthropic SDK version
    # Try the most common constructor patterns
    try:
        rate_err = _anthropic.RateLimitError(
            message="rate limit",
            response=httpx.Response(429, request=httpx.Request("POST", "https://api.anthropic.com")),
            body={"error": {"message": "rate limit"}},
        )
    except TypeError:
        # Fallback for older SDK versions
        rate_err = _anthropic.RateLimitError("rate limit")

    mock_client.messages.create.side_effect = [rate_err, mock_msg]

    with patch("generators.claude_client.anthropic.Anthropic", return_value=mock_client):
        with patch("generators.claude_client.time.sleep"):
            result = call_claude("prompt", max_retries=2)

    assert result == {"ok": True}
    assert mock_client.messages.create.call_count == 2
