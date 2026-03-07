import sys
import time
from typing import Optional

from termcap.parser.asciicast import read_records, AsciiCastV2Header, AsciiCastV2Event


def play(filename: str, speed: float = 1.0, idle_time_limit: Optional[float] = None):
    """Replay a terminal session from a cast file"""
    if speed <= 0:
        print("Error: speed must be greater than 0.", file=sys.stderr)
        return

    try:
        records = read_records(filename)
        header = next(records)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        return
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return
    except StopIteration:
        print("Error: Empty file.", file=sys.stderr)
        return
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return

    if not isinstance(header, AsciiCastV2Header):
        print("Error: Invalid file format (missing header).", file=sys.stderr)
        return

    sys.stdout.write("\x1b[2J\x1b[H")
    sys.stdout.flush()

    current_time = 0.0

    try:
        for record in records:
            if not isinstance(record, AsciiCastV2Event) or record.event_type != "o":
                continue

            delay = (record.time - current_time) / speed

            if idle_time_limit is not None and delay > idle_time_limit:
                delay = idle_time_limit

            if delay > 0:
                time.sleep(delay)

            sys.stdout.write(record.event_data)
            sys.stdout.flush()
            current_time = record.time
    except KeyboardInterrupt:
        pass
    finally:
        print()
