"""Terminal state management"""
import os
import tty
import termios
import struct
import fcntl
import signal
from typing import Tuple

class TerminalMode:
    """Context manager to save and restore terminal attributes"""
    def __init__(self, fd: int):
        self.fd = fd
        self.original_attrs = None
        self.original_winsize = None

    def __enter__(self):
        try:
            self.original_attrs = termios.tcgetattr(self.fd)
            self.original_winsize = get_terminal_size(self.fd)
            tty.setraw(self.fd)
        except termios.error:
            # Not a TTY
            pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_attrs:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.original_attrs)
        
        # Restore window size if it changed (though usually we don't change it back,
        # but capturing it might be useful if we want to enforce a size during recording)
        if self.original_winsize:
            set_terminal_size(self.fd, self.original_winsize)

def get_terminal_size(fd: int) -> Tuple[int, int]:
    """Get (cols, rows) of the terminal"""
    try:
        size = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        return size[1], size[0]
    except (struct.error, OSError):
        return 80, 24

def set_terminal_size(fd: int, size: Tuple[int, int]):
    """Set (cols, rows) of the terminal"""
    cols, rows = size
    try:
        winsize = struct.pack('hh', rows, cols)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
    except OSError:
        pass
