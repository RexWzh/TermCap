# TermCap 终端模块 API

*基于源码分析的终端处理模块详解*

## 概览

TermCap 的终端模块（`termcap.term`）负责处理终端会话的创建、管理和数据捕获。该模块是录制功能的核心组件。

## 主要组件

### 终端会话管理

#### 类和方法概述

```python
from termcap.term import TerminalSession

# 创建终端会话
session = TerminalSession(
    command='/bin/bash',
    geometry=(80, 24),
    env=None
)

# 开始录制
session.start_recording(output_file='session.cast')

# 停止录制
session.stop_recording()
```

### 几何配置

终端几何配置控制终端窗口的尺寸：

```python
# 几何格式：(width, height)
geometry_small = (60, 15)    # 小窗口
geometry_standard = (80, 24) # 标准尺寸
geometry_large = (120, 40)   # 大窗口
```

#### 常用几何尺寸

| 用途 | 尺寸 | 描述 |
|------|------|------|
| 演示 | 120x40 | 大屏幕，适合投影 |
| 标准 | 80x24 | 传统终端尺寸 |
| 紧凑 | 60x15 | 节省空间 |
| 宽屏 | 100x30 | 现代宽屏显示器 |

### 环境变量处理

```python
# 自定义环境变量
custom_env = {
    'TERM': 'xterm-256color',
    'SHELL': '/bin/zsh',
    'PATH': '/usr/local/bin:/usr/bin:/bin'
}

session = TerminalSession(
    command='/bin/zsh',
    geometry=(80, 24),
    env=custom_env
)
```

### 录制数据格式

TermCap 使用 asciicast v2 格式存储录制数据：

```json
{"version": 2, "width": 80, "height": 24}
[时间戳, "o", "输出数据"]
[时间戳, "i", "输入数据"]
```

#### 数据类型

- `"o"` - 终端输出（显示在屏幕上的内容）
- `"i"` - 用户输入（键盘输入）
- `"r"` - 终端重置或特殊事件

## 核心功能

### 1. 伪终端 (PTY) 管理

```python
import pty
import os

class PTYManager:
    def __init__(self, command, geometry):
        self.command = command
        self.width, self.height = geometry
        
    def spawn_pty(self):
        """创建伪终端进程"""
        master_fd, slave_fd = pty.openpty()
        
        # 设置终端尺寸
        self._set_winsize(slave_fd, self.width, self.height)
        
        return master_fd, slave_fd
    
    def _set_winsize(self, fd, width, height):
        """设置终端窗口尺寸"""
        import struct
        import fcntl
        import termios
        
        winsize = struct.pack('HHHH', height, width, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
```

### 2. 数据流处理

```python
class DataStreamHandler:
    def __init__(self, output_file):
        self.output_file = output_file
        self.start_time = None
        
    def handle_output(self, data):
        """处理终端输出数据"""
        timestamp = self._get_timestamp()
        self._write_event(timestamp, 'o', data)
    
    def handle_input(self, data):
        """处理用户输入数据"""
        timestamp = self._get_timestamp()
        self._write_event(timestamp, 'i', data)
    
    def _get_timestamp(self):
        """获取相对时间戳"""
        import time
        current_time = time.time()
        if self.start_time is None:
            self.start_time = current_time
            return 0.0
        return current_time - self.start_time
    
    def _write_event(self, timestamp, event_type, data):
        """写入事件到文件"""
        import json
        event = [timestamp, event_type, data.decode('utf-8', errors='replace')]
        self.output_file.write(json.dumps(event) + '\n')
```

### 3. 信号处理

```python
import signal

class SignalHandler:
    def __init__(self, session):
        self.session = session
        self._setup_signals()
    
    def _setup_signals(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_terminate)
        signal.signal(signal.SIGWINCH, self._handle_winch)
    
    def _handle_interrupt(self, signum, frame):
        """处理中断信号 (Ctrl+C)"""
        self.session.stop_recording()
    
    def _handle_terminate(self, signum, frame):
        """处理终止信号"""
        self.session.cleanup()
    
    def _handle_winch(self, signum, frame):
        """处理窗口大小变化信号"""
        self.session.update_geometry()
```

## 实际使用示例

### 基础录制

```python
from termcap.term import TerminalRecorder

# 创建录制器
recorder = TerminalRecorder(
    output_file='demo.cast',
    command='/bin/bash',
    geometry=(100, 30)
)

# 开始录制
try:
    recorder.start()
    recorder.wait()  # 等待用户退出
except KeyboardInterrupt:
    recorder.stop()
finally:
    recorder.cleanup()
```

### 程序化录制

```python
import time
from termcap.term import TerminalAutomator

# 自动化录制脚本
automator = TerminalAutomator('auto_demo.cast')

# 模拟用户输入
automator.start()
automator.send_command('echo "Hello, TermCap!"')
time.sleep(1)
automator.send_command('ls -la')
time.sleep(2)
automator.send_command('date')
time.sleep(1)
automator.send_command('exit')
automator.wait_for_completion()
```

### 多会话管理

```python
class MultiSessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, session_id, command, geometry):
        """创建新会话"""
        session = TerminalSession(
            command=command,
            geometry=geometry,
            output_file=f'{session_id}.cast'
        )
        self.sessions[session_id] = session
        return session
    
    def start_all(self):
        """启动所有会话"""
        for session in self.sessions.values():
            session.start()
    
    def stop_all(self):
        """停止所有会话"""
        for session in self.sessions.values():
            session.stop()
```

## 高级功能

### 自定义输入/输出过滤

```python
class DataFilter:
    def __init__(self):
        self.filters = []
    
    def add_filter(self, filter_func):
        """添加数据过滤器"""
        self.filters.append(filter_func)
    
    def apply_filters(self, data, event_type):
        """应用所有过滤器"""
        filtered_data = data
        for filter_func in self.filters:
            filtered_data = filter_func(filtered_data, event_type)
        return filtered_data

# 使用示例
def sensitive_data_filter(data, event_type):
    """过滤敏感数据"""
    if 'password' in data.lower():
        return data.replace(data, '[FILTERED]')
    return data

filter_manager = DataFilter()
filter_manager.add_filter(sensitive_data_filter)
```

### 会话元数据

```python
class SessionMetadata:
    def __init__(self):
        self.metadata = {
            'version': 2,
            'timestamp': time.time(),
            'command': None,
            'title': None,
            'env': {},
            'geometry': None
        }
    
    def set_command(self, command):
        self.metadata['command'] = command
    
    def set_title(self, title):
        self.metadata['title'] = title
    
    def set_geometry(self, width, height):
        self.metadata['geometry'] = {'width': width, 'height': height}
    
    def to_header(self):
        """生成 asciicast 文件头"""
        return json.dumps(self.metadata)
```

## 错误处理

### 常见异常

```python
class TermCapException(Exception):
    """TermCap 基础异常"""
    pass

class PTYError(TermCapException):
    """伪终端错误"""
    pass

class RecordingError(TermCapException):
    """录制错误"""
    pass

class GeometryError(TermCapException):
    """几何配置错误"""
    pass

# 使用示例
try:
    session = TerminalSession(command='invalid_command', geometry=(80, 24))
    session.start()
except PTYError as e:
    print(f"无法创建伪终端: {e}")
except RecordingError as e:
    print(f"录制失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

### 资源清理

```python
class ResourceManager:
    def __init__(self):
        self.resources = []
    
    def register_resource(self, resource):
        """注册需要清理的资源"""
        self.resources.append(resource)
    
    def cleanup_all(self):
        """清理所有资源"""
        for resource in reversed(self.resources):
            try:
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
            except Exception as e:
                print(f"清理资源时出错: {e}")
        self.resources.clear()
```

## 性能优化

### 缓冲区管理

```python
class BufferedWriter:
    def __init__(self, file_handle, buffer_size=8192):
        self.file_handle = file_handle
        self.buffer = []
        self.buffer_size = buffer_size
    
    def write_event(self, event):
        """写入事件到缓冲区"""
        self.buffer.append(event)
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self):
        """刷新缓冲区到文件"""
        if self.buffer:
            for event in self.buffer:
                self.file_handle.write(json.dumps(event) + '\n')
            self.file_handle.flush()
            self.buffer.clear()
```

### 异步处理

```python
import asyncio

class AsyncTerminalSession:
    def __init__(self, command, geometry):
        self.command = command
        self.geometry = geometry
        self.running = False
    
    async def start_recording(self):
        """异步开始录制"""
        self.running = True
        
        # 创建子进程
        process = await asyncio.create_subprocess_exec(
            self.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 异步读取输出
        await asyncio.gather(
            self._read_stdout(process.stdout),
            self._read_stderr(process.stderr)
        )
    
    async def _read_stdout(self, stdout):
        """异步读取标准输出"""
        while self.running:
            data = await stdout.read(1024)
            if not data:
                break
            self._process_output(data)
```

## 配置和调试

### 调试模式

```python
import logging

class DebugTerminal:
    def __init__(self, debug=False):
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging.getLogger('termcap.term')
    
    def log_event(self, event_type, data):
        """记录调试事件"""
        if self.debug:
            self.logger.debug(f"{event_type}: {repr(data)}")
```

### 性能监控

```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.stats = {
            'events_processed': 0,
            'bytes_processed': 0,
            'start_time': None,
            'last_event_time': None
        }
    
    def record_event(self, data_size):
        """记录事件统计"""
        current_time = time.time()
        
        if self.stats['start_time'] is None:
            self.stats['start_time'] = current_time
        
        self.stats['events_processed'] += 1
        self.stats['bytes_processed'] += data_size
        self.stats['last_event_time'] = current_time
    
    def get_stats(self):
        """获取性能统计"""
        duration = self.stats['last_event_time'] - self.stats['start_time']
        return {
            'duration': duration,
            'events_per_second': self.stats['events_processed'] / duration,
            'bytes_per_second': self.stats['bytes_processed'] / duration
        }
```

这个终端模块 API 文档提供了 TermCap 终端处理的完整技术细节，帮助开发者理解和扩展终端录制功能。
