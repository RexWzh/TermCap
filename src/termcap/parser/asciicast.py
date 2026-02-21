"""Asciicast V2 parser and data structures"""
import json
import codecs
from typing import NamedTuple, Optional, Union, Iterator, List, Dict, Any

class AsciiCastV2Header(NamedTuple):
    """Asciicast V2 Header"""
    version: int
    width: int
    height: int
    timestamp: Optional[int] = None
    duration: Optional[float] = None
    idle_time_limit: Optional[float] = None
    command: Optional[str] = None
    title: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    theme: Optional[Dict[str, str]] = None

    def to_json_line(self) -> str:
        data = {
            "version": self.version,
            "width": self.width,
            "height": self.height,
        }
        if self.timestamp:
            data["timestamp"] = self.timestamp
        if self.duration:
            data["duration"] = self.duration
        if self.idle_time_limit:
            data["idle_time_limit"] = self.idle_time_limit
        if self.command:
            data["command"] = self.command
        if self.title:
            data["title"] = self.title
        if self.env:
            data["env"] = self.env
        if self.theme:
            data["theme"] = self.theme
        return json.dumps(data)

class AsciiCastV2Event(NamedTuple):
    """Asciicast V2 Event"""
    time: float
    event_type: str
    event_data: str
    duration: Optional[float] = None

    def to_json_line(self) -> str:
        return json.dumps([self.time, self.event_type, self.event_data])

def read_records(filename: str) -> Iterator[Union[AsciiCastV2Header, AsciiCastV2Event]]:
    """Read asciicast records from a file"""
    with open(filename, 'r', encoding='utf-8') as f:
        # Read header
        line = f.readline()
        if not line:
            raise ValueError("Empty file")
        
        try:
            header_data = json.loads(line)
        except json.JSONDecodeError:
            raise ValueError("Invalid header JSON")
            
        if 'version' not in header_data or header_data['version'] != 2:
            raise ValueError("Unsupported asciicast version")
            
        yield AsciiCastV2Header(
            version=header_data.get('version'),
            width=header_data.get('width'),
            height=header_data.get('height'),
            timestamp=header_data.get('timestamp'),
            duration=header_data.get('duration'),
            idle_time_limit=header_data.get('idle_time_limit'),
            command=header_data.get('command'),
            title=header_data.get('title'),
            env=header_data.get('env'),
            theme=header_data.get('theme')
        )
        
        # Read events
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event_data = json.loads(line)
                if len(event_data) >= 3:
                    yield AsciiCastV2Event(
                        time=event_data[0],
                        event_type=event_data[1],
                        event_data=event_data[2]
                    )
            except json.JSONDecodeError:
                continue
