import pytest
import termios
from unittest.mock import patch, MagicMock
from termcap.recorder import core, terminal

def test_get_terminal_size():
    # Mock fcntl.ioctl
    with patch('fcntl.ioctl') as mock_ioctl:
        # struct.pack('hh', rows, cols) -> bytes
        # struct.unpack('hh', bytes) -> (rows, cols)
        # get_terminal_size returns (cols, rows)
        
        # Mock return value for 24 rows, 80 cols
        # In the code: size = struct.unpack('hh', ...) -> returns (rows, cols)
        # The function returns size[1], size[0] -> (cols, rows)
        
        mock_ioctl.return_value = b'\x18\x00\x50\x00' # 24, 80 in little endian short
        
        cols, rows = terminal.get_terminal_size(0)
        assert cols == 80
        assert rows == 24

def test_set_terminal_size():
    with patch('fcntl.ioctl') as mock_ioctl:
        terminal.set_terminal_size(0, (80, 24))
        mock_ioctl.assert_called()

def test_terminal_mode_context():
    with patch('termios.tcgetattr') as mock_getattr, \
         patch('termios.tcsetattr') as mock_setattr, \
         patch('tty.setraw') as mock_setraw, \
         patch('termcap.recorder.terminal.get_terminal_size'), \
         patch('termcap.recorder.terminal.set_terminal_size'):
             
        fd = 0
        with terminal.TerminalMode(fd):
            mock_getattr.assert_called_with(fd)
            mock_setraw.assert_called_with(fd)
            
        mock_setattr.assert_called_with(fd, termios.TCSADRAIN, mock_getattr.return_value)

def test_record_session_header():
    # We can't easily test the full loop with forks/pty in unit tests without complex mocking
    # But we can test that it yields a header first
    
    with patch('pty.fork', return_value=(123, 456)), \
         patch('os.close'), \
         patch('os.waitpid', return_value=(123, 0)):
        
        gen = core.record_session(['bash'], 80, 24, 0, 1)
        header = next(gen)
        
        assert header.width == 80
        assert header.height == 24
        assert header.version == 2
