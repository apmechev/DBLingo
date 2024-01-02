import os
from dblingo.sinks.jsonl import JSONLSink

def test_create(mocker):
    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('os.makedirs')
    mocker.patch('os.path.isfile', return_value=False)
    mocker.patch('builtins.open', mocker.mock_open())
    jsonl = JSONLSink('data/test.jsonl')
    os.makedirs.assert_called_once_with('data')
    open.assert_called_once_with('data/test.jsonl', 'w')
    jsonl.create()
    assert os.makedirs.call_count == 2

def test_get_last_timestamp_no_file(mocker):
    mocker.patch('os.path.isfile', return_value=False)
    jsonl = JSONLSink('data/test.jsonl')
    timestamp = jsonl.get_last_timestamp()
    assert timestamp == 0

def test_get_last_timestamp_empty_file(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data=''))
    jsonl = JSONLSink('data/test.jsonl')
    timestamp = jsonl.get_last_timestamp()
    assert timestamp == 0

def test_get_last_timestamp_valid_file(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"datetime": 1628000000}\n'))
    jsonl = JSONLSink('data/test.jsonl')
    timestamp = jsonl.get_last_timestamp()
    assert timestamp == 1628000000
