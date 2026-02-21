import pytest
import json
from io import StringIO
from unittest.mock import patch
from termcap.parser.asciicast import read_records, AsciiCastV2Header, AsciiCastV2Event

def test_header_parsing():
    json_data = json.dumps({
        "version": 2,
        "width": 80,
        "height": 24,
        "timestamp": 1234567890
    })
    
    with patch('builtins.open', return_value=StringIO(json_data)):
        records = read_records("dummy.cast")
        header = next(records)
        
        assert isinstance(header, AsciiCastV2Header)
        assert header.version == 2
        assert header.width == 80
        assert header.height == 24
        assert header.timestamp == 1234567890

def test_event_parsing():
    header_json = json.dumps({"version": 2, "width": 80, "height": 24})
    event1_json = json.dumps([1.0, "o", "hello"])
    event2_json = json.dumps([2.0, "o", "world"])
    
    file_content = f"{header_json}\n{event1_json}\n{event2_json}"
    
    with patch('builtins.open', return_value=StringIO(file_content)):
        records = read_records("dummy.cast")
        next(records)  # Skip header
        
        event1 = next(records)
        assert isinstance(event1, AsciiCastV2Event)
        assert event1.time == 1.0
        assert event1.event_type == "o"
        assert event1.event_data == "hello"
        
        event2 = next(records)
        assert event2.time == 2.0
        assert event2.event_data == "world"

def test_invalid_header():
    with patch('builtins.open', return_value=StringIO("invalid json")):
        with pytest.raises(ValueError, match="Invalid header JSON"):
            next(read_records("dummy.cast"))

def test_unsupported_version():
    with patch('builtins.open', return_value=StringIO('{"version": 1}')):
        with pytest.raises(ValueError, match="Unsupported asciicast version"):
            next(read_records("dummy.cast"))

def test_header_to_json():
    header = AsciiCastV2Header(version=2, width=80, height=24, timestamp=123)
    json_str = header.to_json_line()
    data = json.loads(json_str)
    assert data['version'] == 2
    assert data['width'] == 80
    assert data['timestamp'] == 123

def test_event_to_json():
    event = AsciiCastV2Event(time=1.5, event_type="o", event_data="test")
    json_str = event.to_json_line()
    data = json.loads(json_str)
    assert data == [1.5, "o", "test"]
