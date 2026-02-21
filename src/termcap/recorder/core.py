"""Core recording logic"""
import os
import pty
import select
import time
import fcntl
import termios
import struct
import codecs
from typing import Iterator, List, Union

from termcap.parser.asciicast import AsciiCastV2Header, AsciiCastV2Event

def record_session(
    process_args: List[str],
    columns: int,
    lines: int,
    input_fileno: int,
    output_fileno: int
) -> Iterator[Union[AsciiCastV2Header, AsciiCastV2Event]]:
    """Record a terminal session"""
    
    # Yield the header first
    yield AsciiCastV2Header(
        version=2,
        width=columns,
        height=lines,
        timestamp=int(time.time())
    )

    pid, master_fd = pty.fork()
    
    if pid == 0:
        # Child process
        os.execvp(process_args[0], process_args)
        
    # Parent process
    # Set terminal size for the PTY
    winsize = struct.pack("HHHH", lines, columns, 0, 0)
    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
    
    # Use incremental decoder to handle multi-byte characters split across chunks
    decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
    
    start_time = time.time()
    
    try:
        while True:
            rlist = [input_fileno, master_fd]
            rfds, _, _ = select.select(rlist, [], [])
            
            for fd in rfds:
                if fd == input_fileno:
                    # User input -> Child process
                    try:
                        data = os.read(input_fileno, 1024)
                    except OSError:
                        break
                        
                    if not data:
                        break
                        
                    os.write(master_fd, data)
                    
                elif fd == master_fd:
                    # Child output -> User terminal + Recording
                    try:
                        data = os.read(master_fd, 1024)
                    except OSError:
                        break
                        
                    if not data:
                        break
                    
                    # Write to user terminal
                    os.write(output_fileno, data)
                    
                    # Record event
                    elapsed = time.time() - start_time
                    decoded_data = decoder.decode(data, final=False)
                    if decoded_data:
                        yield AsciiCastV2Event(
                            time=elapsed,
                            event_type="o",
                            event_data=decoded_data
                        )
                        
            # Check if child process is still alive
            if os.waitpid(pid, os.WNOHANG)[0] == pid:
                break
                
    except OSError:
        pass
    finally:
        os.close(master_fd)
        # Flush decoder
        remaining = decoder.decode(b"", final=True)
        if remaining:
            yield AsciiCastV2Event(
                time=time.time() - start_time,
                event_type="o",
                event_data=remaining
            )
