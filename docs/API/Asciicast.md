# TermCap Asciicast 格式 API

*asciicast v2 格式详解和处理接口*

## 概览

TermCap 使用 asciicast v2 格式存储终端会话录制数据。该格式是一个基于 JSON 的开放标准，专门用于记录终端会话的输入输出。

## Asciicast v2 格式规范

### 文件结构

一个 asciicast 文件包含：
1. **文件头** - 包含元数据的 JSON 对象（第一行）
2. **事件流** - 每行一个事件的 JSON 数组

```
{"version": 2, "width": 80, "height": 24, "timestamp": 1234567890}
[0.0, "o", "Hello World!\r\n"]
[1.5, "i", "ls"]
[1.6, "o", "file1.txt file2.txt\r\n"]
[3.2, "i", "\r"]
```

### 文件头格式

```json
{
  "version": 2,
  "width": 80,
  "height": 24,
  "timestamp": 1609459200,
  "duration": 10.5,
  "idle_time_limit": 2.0,
  "command": "/bin/bash",
  "title": "Demo Session",
  "env": {
    "SHELL": "/bin/bash",
    "TERM": "xterm-256color"
  },
  "theme": {
    "fg": "#d0d0d0",
    "bg": "#212121",
    "palette": "#000000:#aa0000:#00aa00:..."
  }
}
```

#### 必需字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `version` | integer | 格式版本，必须为 2 |
| `width` | integer | 终端宽度（字符数） |
| `height` | integer | 终端高度（行数） |

#### 可选字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `timestamp` | integer | Unix 时间戳 |
| `duration` | float | 会话总时长（秒） |
| `idle_time_limit` | float | 空闲时间限制（秒） |
| `command` | string | 执行的命令 |
| `title` | string | 会话标题 |
| `env` | object | 环境变量 |
| `theme` | object | 颜色主题 |

### 事件格式

每个事件是一个 JSON 数组：`[timestamp, event_type, event_data]`

| 位置 | 类型 | 描述 |
|------|------|------|
| 0 | float | 相对时间戳（从录制开始的秒数） |
| 1 | string | 事件类型（"o" 输出，"i" 输入，"r" 重置） |
| 2 | string | 事件数据（UTF-8 编码的字符串） |

#### 事件类型

- **"o" (output)** - 终端输出到屏幕的数据
- **"i" (input)** - 用户输入的数据
- **"r" (resize)** - 终端尺寸改变（实验性）

## TermCap Asciicast API

### 基础解析器

```python
import json
from typing import Dict, List, Tuple, Any

class AsciicastParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.header: Dict[str, Any] = {}
        self.events: List[Tuple[float, str, str]] = []
    
    def parse(self) -> Tuple[Dict[str, Any], List[Tuple[float, str, str]]]:
        """解析 asciicast 文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            # 解析文件头
            header_line = f.readline().strip()
            self.header = json.loads(header_line)
            
            # 验证版本
            if self.header.get('version') != 2:
                raise ValueError(f"Unsupported asciicast version: {self.header.get('version')}")
            
            # 解析事件
            for line_num, line in enumerate(f, 2):
                line = line.strip()
                if line:
                    try:
                        event = json.loads(line)
                        if len(event) != 3:
                            raise ValueError(f"Invalid event format at line {line_num}")
                        
                        timestamp, event_type, event_data = event
                        self.events.append((float(timestamp), str(event_type), str(event_data)))
                    
                    except (json.JSONDecodeError, ValueError) as e:
                        raise ValueError(f"Invalid event at line {line_num}: {e}")
        
        return self.header, self.events
    
    def get_duration(self) -> float:
        """计算会话总时长"""
        if 'duration' in self.header:
            return self.header['duration']
        
        if self.events:
            return self.events[-1][0]  # 最后一个事件的时间戳
        
        return 0.0
    
    def get_geometry(self) -> Tuple[int, int]:
        """获取终端几何尺寸"""
        return (self.header['width'], self.header['height'])
    
    def get_output_events(self) -> List[Tuple[float, str]]:
        """获取仅输出事件"""
        return [(timestamp, data) for timestamp, event_type, data in self.events 
                if event_type == 'o']
    
    def get_input_events(self) -> List[Tuple[float, str]]:
        """获取仅输入事件"""
        return [(timestamp, data) for timestamp, event_type, data in self.events 
                if event_type == 'i']
```

### 高级解析功能

```python
class AdvancedAsciicastParser(AsciicastParser):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.statistics = {}
    
    def analyze_events(self) -> Dict[str, Any]:
        """分析事件统计信息"""
        if not hasattr(self, 'events') or not self.events:
            self.parse()
        
        output_events = [e for e in self.events if e[1] == 'o']
        input_events = [e for e in self.events if e[1] == 'i']
        
        total_output_chars = sum(len(data) for _, _, data in output_events)
        total_input_chars = sum(len(data) for _, _, data in input_events)
        
        duration = self.get_duration()
        
        self.statistics = {
            'total_events': len(self.events),
            'output_events': len(output_events),
            'input_events': len(input_events),
            'total_output_chars': total_output_chars,
            'total_input_chars': total_input_chars,
            'duration': duration,
            'chars_per_second': total_output_chars / duration if duration > 0 else 0,
            'events_per_second': len(self.events) / duration if duration > 0 else 0
        }
        
        return self.statistics
    
    def get_time_segments(self, segment_duration: float = 1.0) -> List[Dict[str, Any]]:
        """将会话分段分析"""
        segments = []
        current_segment = {
            'start_time': 0,
            'end_time': segment_duration,
            'events': [],
            'output_chars': 0,
            'input_chars': 0
        }
        
        for timestamp, event_type, data in self.events:
            if timestamp >= current_segment['end_time']:
                # 完成当前段，开始新段
                segments.append(current_segment)
                current_segment = {
                    'start_time': current_segment['end_time'],
                    'end_time': current_segment['end_time'] + segment_duration,
                    'events': [],
                    'output_chars': 0,
                    'input_chars': 0
                }
            
            current_segment['events'].append((timestamp, event_type, data))
            if event_type == 'o':
                current_segment['output_chars'] += len(data)
            elif event_type == 'i':
                current_segment['input_chars'] += len(data)
        
        # 添加最后一段
        if current_segment['events']:
            segments.append(current_segment)
        
        return segments
    
    def find_idle_periods(self, idle_threshold: float = 2.0) -> List[Tuple[float, float]]:
        """查找空闲期间"""
        idle_periods = []
        
        for i in range(1, len(self.events)):
            prev_timestamp = self.events[i-1][0]
            curr_timestamp = self.events[i][0]
            
            gap = curr_timestamp - prev_timestamp
            if gap >= idle_threshold:
                idle_periods.append((prev_timestamp, curr_timestamp))
        
        return idle_periods
```

### Asciicast 生成器

```python
import time
import json
from typing import Optional, Dict, Any

class AsciicastWriter:
    def __init__(self, file_path: str, width: int, height: int, **metadata):
        self.file_path = file_path
        self.width = width
        self.height = height
        self.metadata = metadata
        self.start_time = None
        self.file_handle = None
    
    def start_recording(self):
        """开始录制"""
        self.start_time = time.time()
        self.file_handle = open(self.file_path, 'w', encoding='utf-8')
        
        # 写入文件头
        header = {
            'version': 2,
            'width': self.width,
            'height': self.height,
            'timestamp': int(self.start_time),
            **self.metadata
        }
        
        self.file_handle.write(json.dumps(header) + '\n')
        self.file_handle.flush()
    
    def write_output(self, data: str):
        """写入输出事件"""
        self._write_event('o', data)
    
    def write_input(self, data: str):
        """写入输入事件"""
        self._write_event('i', data)
    
    def write_resize(self, new_width: int, new_height: int):
        """写入尺寸变更事件"""
        resize_data = f"{new_width}x{new_height}"
        self._write_event('r', resize_data)
    
    def _write_event(self, event_type: str, data: str):
        """写入事件"""
        if self.file_handle is None or self.start_time is None:
            raise RuntimeError("Recording not started")
        
        timestamp = time.time() - self.start_time
        event = [timestamp, event_type, data]
        
        self.file_handle.write(json.dumps(event) + '\n')
        self.file_handle.flush()
    
    def stop_recording(self):
        """停止录制"""
        if self.file_handle:
            # 更新文件头中的持续时间
            if self.start_time:
                duration = time.time() - self.start_time
                self._update_duration(duration)
            
            self.file_handle.close()
            self.file_handle = None
    
    def _update_duration(self, duration: float):
        """更新文件头中的持续时间（需要重写文件）"""
        # 读取现有内容
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新头部
        if lines:
            header = json.loads(lines[0].strip())
            header['duration'] = duration
            lines[0] = json.dumps(header) + '\n'
        
        # 重写文件
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
```

### 数据转换工具

```python
class AsciicastConverter:
    @staticmethod
    def merge_casts(cast_files: List[str], output_file: str, 
                   gap_duration: float = 1.0) -> None:
        """合并多个 asciicast 文件"""
        merged_events = []
        current_time = 0.0
        total_width = 0
        total_height = 0
        
        for cast_file in cast_files:
            parser = AsciicastParser(cast_file)
            header, events = parser.parse()
            
            # 使用第一个文件的几何尺寸
            if not merged_events:
                total_width = header['width']
                total_height = header['height']
            
            # 调整事件时间戳
            for timestamp, event_type, data in events:
                adjusted_timestamp = current_time + timestamp
                merged_events.append((adjusted_timestamp, event_type, data))
            
            # 更新当前时间
            if events:
                current_time = merged_events[-1][0] + gap_duration
        
        # 写入合并后的文件
        writer = AsciicastWriter(output_file, total_width, total_height)
        writer.start_recording()
        
        for timestamp, event_type, data in merged_events:
            if event_type == 'o':
                writer.write_output(data)
            elif event_type == 'i':
                writer.write_input(data)
        
        writer.stop_recording()
    
    @staticmethod
    def trim_cast(input_file: str, output_file: str, 
                  start_time: float = 0.0, end_time: Optional[float] = None) -> None:
        """裁剪 asciicast 文件"""
        parser = AsciicastParser(input_file)
        header, events = parser.parse()
        
        # 过滤事件
        filtered_events = []
        for timestamp, event_type, data in events:
            if timestamp >= start_time and (end_time is None or timestamp <= end_time):
                # 调整时间戳
                adjusted_timestamp = timestamp - start_time
                filtered_events.append((adjusted_timestamp, event_type, data))
        
        # 写入裁剪后的文件
        writer = AsciicastWriter(output_file, header['width'], header['height'])
        writer.start_recording()
        
        for timestamp, event_type, data in filtered_events:
            if event_type == 'o':
                writer.write_output(data)
            elif event_type == 'i':
                writer.write_input(data)
        
        writer.stop_recording()
    
    @staticmethod
    def speed_adjust(input_file: str, output_file: str, speed_factor: float) -> None:
        """调整播放速度"""
        parser = AsciicastParser(input_file)
        header, events = parser.parse()
        
        # 调整时间戳
        adjusted_events = []
        for timestamp, event_type, data in events:
            new_timestamp = timestamp / speed_factor
            adjusted_events.append((new_timestamp, event_type, data))
        
        # 写入调整后的文件
        writer = AsciicastWriter(output_file, header['width'], header['height'])
        writer.start_recording()
        
        for timestamp, event_type, data in adjusted_events:
            if event_type == 'o':
                writer.write_output(data)
            elif event_type == 'i':
                writer.write_input(data)
        
        writer.stop_recording()
```

## 实际使用示例

### 基础文件操作

```python
# 解析现有文件
parser = AsciicastParser('session.cast')
header, events = parser.parse()

print(f"Session: {header.get('title', 'Untitled')}")
print(f"Duration: {parser.get_duration():.2f} seconds")
print(f"Geometry: {parser.get_geometry()}")
print(f"Total events: {len(events)}")

# 分析统计信息
advanced_parser = AdvancedAsciicastParser('session.cast')
stats = advanced_parser.analyze_events()
print(f"Characters per second: {stats['chars_per_second']:.2f}")
```

### 创建新录制

```python
# 创建新的录制会话
writer = AsciicastWriter(
    'new_session.cast', 
    width=80, 
    height=24,
    title='Demo Session',
    command='/bin/bash'
)

writer.start_recording()

# 模拟一些输出
writer.write_output('$ echo "Hello World!"\r\n')
time.sleep(0.5)
writer.write_output('Hello World!\r\n')
time.sleep(1.0)
writer.write_output('$ exit\r\n')

writer.stop_recording()
```

### 文件处理工具

```python
# 合并多个会话
AsciicastConverter.merge_casts(
    ['session1.cast', 'session2.cast', 'session3.cast'],
    'merged_session.cast',
    gap_duration=2.0
)

# 裁剪会话（保留 10-60 秒的部分）
AsciicastConverter.trim_cast(
    'long_session.cast',
    'trimmed_session.cast',
    start_time=10.0,
    end_time=60.0
)

# 调整播放速度（2倍速）
AsciicastConverter.speed_adjust(
    'slow_session.cast',
    'fast_session.cast',
    speed_factor=2.0
)
```

## 验证和调试

### 文件验证器

```python
class AsciicastValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path: str) -> bool:
        """验证 asciicast 文件"""
        try:
            parser = AsciicastParser(file_path)
            header, events = parser.parse()
            
            # 验证头部
            self._validate_header(header)
            
            # 验证事件
            self._validate_events(events)
            
            return len(self.errors) == 0
        
        except Exception as e:
            self.errors.append(f"Parse error: {e}")
            return False
    
    def _validate_header(self, header: Dict[str, Any]):
        """验证头部"""
        # 检查必需字段
        required_fields = ['version', 'width', 'height']
        for field in required_fields:
            if field not in header:
                self.errors.append(f"Missing required field: {field}")
        
        # 检查版本
        if header.get('version') != 2:
            self.errors.append(f"Unsupported version: {header.get('version')}")
        
        # 检查几何尺寸
        width = header.get('width', 0)
        height = header.get('height', 0)
        
        if not isinstance(width, int) or width <= 0:
            self.errors.append(f"Invalid width: {width}")
        
        if not isinstance(height, int) or height <= 0:
            self.errors.append(f"Invalid height: {height}")
        
        if width > 1000 or height > 1000:
            self.warnings.append(f"Very large geometry: {width}x{height}")
    
    def _validate_events(self, events: List[Tuple[float, str, str]]):
        """验证事件"""
        prev_timestamp = -1
        
        for i, (timestamp, event_type, data) in enumerate(events):
            # 检查时间戳顺序
            if timestamp < prev_timestamp:
                self.errors.append(f"Event {i}: timestamp goes backward")
            
            # 检查事件类型
            if event_type not in ['o', 'i', 'r']:
                self.warnings.append(f"Event {i}: unknown event type '{event_type}'")
            
            # 检查数据
            if not isinstance(data, str):
                self.errors.append(f"Event {i}: event data must be string")
            
            prev_timestamp = timestamp
    
    def get_report(self) -> str:
        """获取验证报告"""
        report = "Asciicast Validation Report\n"
        report += "=" * 30 + "\n"
        
        if self.errors:
            report += "ERRORS:\n"
            for error in self.errors:
                report += f"  - {error}\n"
        
        if self.warnings:
            report += "WARNINGS:\n"
            for warning in self.warnings:
                report += f"  - {warning}\n"
        
        if not self.errors and not self.warnings:
            report += "File is valid!\n"
        
        return report
```

这个 Asciicast 格式 API 文档提供了处理 asciicast 文件的完整工具集，支持解析、生成、转换和验证等各种操作。
