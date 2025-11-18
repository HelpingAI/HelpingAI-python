import os
import sys
import pytest

# Ensure we import the local version of the HelpingAI package for tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from HelpingAI.client.main import HAI


class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data

    def json(self):
        return self._json


def _dummy_response():
    return DummyResponse({
        "id": "1",
        "created": 0,
        "model": "gpt-4",
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": "hi"}}
        ],
        "usage": {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
    })


def test_create_without_tools_does_not_include_tools_keys():
    client = HAI(api_key="testkey")

    captured = {}

    def fake_request(method, path, json_data=None, stream=False, auth_required=True):
        captured['json_data'] = json_data
        return _dummy_response().json()

    client._request = fake_request

    # Call without tools
    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": "Hi"}])
    assert isinstance(response, dict) or hasattr(response, 'id') or response is not None
    assert 'json_data' in captured
    assert 'tools' not in captured['json_data']
    assert 'tool_choice' not in captured['json_data']


def test_create_with_tools_includes_tools_and_tool_choice():
    client = HAI(api_key="testkey")

    captured = {}

    def fake_request(method, path, json_data=None, stream=False, auth_required=True):
        captured['json_data'] = json_data
        return _dummy_response().json()

    client._request = fake_request

    # Minimal standard tool definition
    tools = [{
        "type": "function",
        "function": {
            "name": "dummy_tool",
            "description": "Dummy tool",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }]

    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": "Hi"}], tools=tools, tool_choice="auto")
    # We expect 'tools' to be present and 'tool_choice' to be included
    assert 'json_data' in captured
    assert 'tools' in captured['json_data']
    assert 'tool_choice' in captured['json_data']
    assert captured['json_data']['tool_choice'] == 'auto'


def test_create_tool_choice_and_tools_none_are_not_sent():
    client = HAI(api_key="testkey")
    captured = {}

    def fake_request(method, path, json_data=None, stream=False, auth_required=True):
        captured['json_data'] = json_data
        return _dummy_response().json()

    client._request = fake_request

    # Explicitly set tool_choice to None and do not pass tools
    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": "Hi"}], tool_choice=None)
    assert 'tools' not in captured['json_data']
    assert 'tool_choice' not in captured['json_data']


def test_create_with_explicit_empty_tools_list_includes_tools_key():
    client = HAI(api_key="testkey")
    captured = {}

    def fake_request(method, path, json_data=None, stream=False, auth_required=True):
        captured['json_data'] = json_data
        return _dummy_response().json()

    client._request = fake_request

    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": "Hi"}], tools=[], tool_choice="auto")
    # When user explicitly passes an empty list for tools, we include the tools key and the tool_choice as provided
    assert 'tools' in captured['json_data']
    assert captured['json_data']['tools'] == []
    assert 'tool_choice' in captured['json_data']


def test_invalid_tool_choice_is_normalized_to_auto():
    client = HAI(api_key="testkey")
    captured = {}

    def fake_request(method, path, json_data=None, stream=False, auth_required=True):
        captured['json_data'] = json_data
        return _dummy_response().json()

    client._request = fake_request
    tools = [{
        "type": "function",
        "function": {
            "name": "dummy_tool",
            "description": "Dummy tool",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }]

    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": "Hi"}], tools=tools, tool_choice="INVALID")
    assert 'tool_choice' in captured['json_data']
    assert captured['json_data']['tool_choice'] == 'auto'
