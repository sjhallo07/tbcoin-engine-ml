import os
import requests
import pytest

# Test description metadata (informational)
# operation: read
# resource: message


@pytest.mark.parametrize("expected_status", ([200]))
def test_get_messages(expected_status):
    """
    HTTP test that GETs the /messages endpoint and asserts a 200 response and
    that the response body is valid JSON.

    Configure the target URL using the environment variable TEST_MESSAGES_URL.
    Default: http://127.0.0.1:3000/messages
    """
    url = os.getenv("TEST_MESSAGES_URL", "http://127.0.0.1:3000/messages")

    resp = requests.get(url, headers={"Content-Type": "application/json"}, timeout=10)
    assert resp.status_code in expected_status

    # Ensure body is parseable as JSON
    try:
        data = resp.json()
    except Exception as exc:
        pytest.fail(f"Response from {url} not parseable as JSON: {exc}")

    # Optional: perform a minimal shape check if messages list expected
    if isinstance(data, dict) and "messages" in data:
        assert isinstance(data["messages"], (list, tuple))
