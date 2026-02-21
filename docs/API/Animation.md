# TermCap 动画模块 API

*基于源码分析的 SVG 动画生成系统详解*

## 概览

TermCap 的动画模块（`termcap.anim`）负责将录制的终端会话数据转换为 SVG 动画。这是渲染功能的核心组件，处理帧生成、时间控制和 SVG 输出。

## 主要组件

### 动画渲染器

#### 核心渲染函数

```python
from termcap.anim import render_animation

# 基础渲染
frames = load_cast_file('session.cast')
geometry = (80, 24)
template = load_template('gjm8')
output_path = 'animation.svg'

render_animation(frames, geometry, output_path, template)
```

### 帧数据结构

每个帧包含以下信息：

```python
class Frame:
    def __init__(self, timestamp, content, cursor_pos):
        self.timestamp = timestamp      # 时间戳（秒）
        self.content = content          # 终端内容（二维数组）
        self.cursor_pos = cursor_pos    # 光标位置 (x, y)
        self.duration = 0               # 帧持续时间
```

### 时间控制参数

```python
class TimingConfig:
    def __init__(self):
        self.min_duration = 17      # 最小帧持续时间（毫秒）
        self.max_duration = 3000    # 最大帧持续时间（毫秒）
        self.loop_delay = 1000      # 循环延迟（毫秒）
        self.speed_factor = 1.0     # 速度倍率
```

## 核心功能

### 1. Cast 文件解析

```python
import json

class CastParser:
    def __init__(self, cast_file):
        self.cast_file = cast_file
        self.header = None
        self.events = []
    
    def parse(self):
        """解析 asciicast 文件"""
        with open(self.cast_file, 'r') as f:
            # 读取文件头
            first_line = f.readline().strip()
            self.header = json.loads(first_line)
            
            # 读取事件
            for line in f:
                if line.strip():
                    event = json.loads(line.strip())
                    self.events.append(event)
        
        return self.header, self.events
    
    def get_geometry(self):
        """获取终端几何尺寸"""
        return (self.header['width'], self.header['height'])
    
    def get_events(self):
        """获取事件列表"""
        return [(event[0], event[1], event[2]) for event in self.events]
```

### 2. 终端状态模拟

```python
import pyte

class TerminalSimulator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pyte.Screen(width, height)
        self.stream = pyte.ByteStream(self.screen)
    
    def process_output(self, data):
        """处理终端输出数据"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.stream.feed(data)
    
    def get_display_content(self):
        """获取当前显示内容"""
        lines = []
        for y in range(self.height):
            line = ''
            for x in range(self.width):
                char = self.screen.buffer[y][x]
                line += char.data
            lines.append(line.rstrip())
        return lines
    
    def get_cursor_position(self):
        """获取光标位置"""
        return (self.screen.cursor.x, self.screen.cursor.y)
    
    def get_char_attributes(self, x, y):
        """获取字符属性（颜色、样式等）"""
        if y < len(self.screen.buffer) and x < len(self.screen.buffer[y]):
            char = self.screen.buffer[y][x]
            return {
                'fg': char.fg,
                'bg': char.bg,
                'bold': char.bold,
                'italics': char.italics,
                'underscore': char.underscore,
                'strikethrough': char.strikethrough
            }
        return None
```

### 3. 帧生成器

```python
class FrameGenerator:
    def __init__(self, events, geometry, timing_config):
        self.events = events
        self.geometry = geometry
        self.timing_config = timing_config
        self.simulator = TerminalSimulator(*geometry)
    
    def generate_frames(self):
        """生成动画帧序列"""
        frames = []
        current_time = 0
        
        for timestamp, event_type, data in self.events:
            if event_type == 'o':  # 输出事件
                self.simulator.process_output(data)
                
                # 创建帧
                frame = Frame(
                    timestamp=timestamp,
                    content=self.simulator.get_display_content(),
                    cursor_pos=self.simulator.get_cursor_position()
                )
                
                # 计算帧持续时间
                if frames:
                    duration = (timestamp - current_time) * 1000  # 转换为毫秒
                    duration = max(self.timing_config.min_duration, 
                                 min(duration, self.timing_config.max_duration))
                    frames[-1].duration = duration
                
                frames.append(frame)
                current_time = timestamp
        
        # 设置最后一帧的持续时间
        if frames:
            frames[-1].duration = self.timing_config.loop_delay
        
        return frames
```

### 4. SVG 生成器

```python
from xml.etree import ElementTree as ET

class SVGGenerator:
    def __init__(self, template, geometry):
        self.template = template
        self.width, self.height = geometry
        self.char_width = 8    # 字符宽度（像素）
        self.char_height = 16  # 字符高度（像素）
    
    def create_svg_document(self, frames):
        """创建 SVG 文档"""
        # 解析模板
        root = ET.fromstring(self.template)
        
        # 设置 SVG 尺寸
        svg_width = self.width * self.char_width
        svg_height = self.height * self.char_height
        root.set('width', str(svg_width))
        root.set('height', str(svg_height))
        
        # 生成动画元素
        animation_group = self._create_animation_group(frames)
        root.append(animation_group)
        
        return ET.tostring(root, encoding='unicode')
    
    def _create_animation_group(self, frames):
        """创建动画组"""
        g = ET.Element('g', {'class': 'animation'})
        
        total_duration = sum(frame.duration for frame in frames)
        current_time = 0
        
        for i, frame in enumerate(frames):
            frame_group = self._create_frame_group(frame, i)
            
            # 添加动画时间控制
            if len(frames) > 1:
                self._add_animation_timing(frame_group, current_time, 
                                         frame.duration, total_duration)
            
            g.append(frame_group)
            current_time += frame.duration
        
        return g
    
    def _create_frame_group(self, frame, frame_index):
        """创建单个帧组"""
        g = ET.Element('g', {
            'class': f'frame frame-{frame_index}',
            'opacity': '0' if frame_index > 0 else '1'
        })
        
        # 添加文本内容
        for y, line in enumerate(frame.content):
            if line.strip():  # 跳过空行
                text_elem = self._create_text_element(line, y)
                g.append(text_elem)
        
        # 添加光标
        cursor_elem = self._create_cursor_element(frame.cursor_pos)
        g.append(cursor_elem)
        
        return g
    
    def _create_text_element(self, text, line_num):
        """创建文本元素"""
        return ET.Element('text', {
            'x': '0',
            'y': str((line_num + 1) * self.char_height),
            'class': 'terminal-text'
        })
    
    def _create_cursor_element(self, cursor_pos):
        """创建光标元素"""
        x, y = cursor_pos
        return ET.Element('rect', {
            'x': str(x * self.char_width),
            'y': str(y * self.char_height),
            'width': str(self.char_width),
            'height': str(self.char_height),
            'class': 'cursor'
        })
    
    def _add_animation_timing(self, element, start_time, duration, total_duration):
        """添加动画时间控制"""
        # 计算动画时间（以秒为单位）
        begin = start_time / 1000
        dur = duration / 1000
        
        # 添加透明度动画
        animate_elem = ET.Element('animate', {
            'attributeName': 'opacity',
            'values': '0;1;1;0',
            'dur': f'{total_duration/1000}s',
            'begin': f'{begin}s',
            'repeatCount': 'indefinite'
        })
        
        element.append(animate_elem)
```

## 高级功能

### 样式和主题处理

```python
class StyleProcessor:
    def __init__(self, template):
        self.template = template
        self.color_map = self._extract_color_map()
    
    def _extract_color_map(self):
        """从模板提取颜色映射"""
        # 解析 CSS 样式
        color_map = {
            'black': '#000000',
            'red': '#ff0000',
            'green': '#00ff00',
            'yellow': '#ffff00',
            'blue': '#0000ff',
            'magenta': '#ff00ff',
            'cyan': '#00ffff',
            'white': '#ffffff'
        }
        return color_map
    
    def apply_character_style(self, char_elem, attributes):
        """应用字符样式"""
        style_parts = []
        
        # 前景色
        if attributes.get('fg'):
            fg_color = self.color_map.get(attributes['fg'], attributes['fg'])
            style_parts.append(f'fill: {fg_color}')
        
        # 背景色
        if attributes.get('bg'):
            bg_color = self.color_map.get(attributes['bg'], attributes['bg'])
            style_parts.append(f'background: {bg_color}')
        
        # 文本样式
        if attributes.get('bold'):
            style_parts.append('font-weight: bold')
        if attributes.get('italics'):
            style_parts.append('font-style: italic')
        if attributes.get('underscore'):
            style_parts.append('text-decoration: underline')
        
        if style_parts:
            char_elem.set('style', '; '.join(style_parts))
```

### 性能优化

```python
class OptimizedRenderer:
    def __init__(self):
        self.frame_cache = {}
        self.diff_threshold = 0.1  # 帧差异阈值
    
    def optimize_frames(self, frames):
        """优化帧序列"""
        optimized = []
        prev_frame = None
        
        for frame in frames:
            if prev_frame is None or self._frame_diff(prev_frame, frame) > self.diff_threshold:
                optimized.append(frame)
                prev_frame = frame
            else:
                # 合并相似帧，累加持续时间
                if optimized:
                    optimized[-1].duration += frame.duration
        
        return optimized
    
    def _frame_diff(self, frame1, frame2):
        """计算两帧之间的差异度"""
        diff_count = 0
        total_chars = 0
        
        for y in range(min(len(frame1.content), len(frame2.content))):
            line1 = frame1.content[y] if y < len(frame1.content) else ''
            line2 = frame2.content[y] if y < len(frame2.content) else ''
            
            max_len = max(len(line1), len(line2))
            total_chars += max_len
            
            for x in range(max_len):
                char1 = line1[x] if x < len(line1) else ' '
                char2 = line2[x] if x < len(line2) else ' '
                if char1 != char2:
                    diff_count += 1
        
        return diff_count / total_chars if total_chars > 0 else 0
```

### 模板系统

```python
class TemplateManager:
    def __init__(self, template_dir):
        self.template_dir = template_dir
        self.template_cache = {}
    
    def load_template(self, template_name):
        """加载模板"""
        if template_name in self.template_cache:
            return self.template_cache[template_name]
        
        template_path = self._find_template(template_name)
        if not template_path:
            raise ValueError(f"Template '{template_name}' not found")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        self.template_cache[template_name] = template_content
        return template_content
    
    def _find_template(self, template_name):
        """查找模板文件"""
        import os
        
        # 检查内置模板
        builtin_path = os.path.join(self.template_dir, 'builtin', f'{template_name}.svg')
        if os.path.exists(builtin_path):
            return builtin_path
        
        # 检查自定义模板
        custom_path = os.path.join(self.template_dir, 'custom', f'{template_name}.svg')
        if os.path.exists(custom_path):
            return custom_path
        
        return None
    
    def resize_template(self, template, new_geometry):
        """调整模板尺寸"""
        new_width, new_height = new_geometry
        
        # 解析模板 SVG
        root = ET.fromstring(template)
        
        # 更新 SVG 尺寸
        char_width = 8
        char_height = 16
        svg_width = new_width * char_width
        svg_height = new_height * char_height
        
        root.set('width', str(svg_width))
        root.set('height', str(svg_height))
        root.set('viewBox', f'0 0 {svg_width} {svg_height}')
        
        return ET.tostring(root, encoding='unicode')
```

## 实际使用示例

### 基础动画生成

```python
from termcap.anim import AnimationRenderer

# 创建渲染器
renderer = AnimationRenderer(
    input_file='session.cast',
    output_file='animation.svg',
    template='dracula',
    timing_config={
        'min_duration': 25,
        'max_duration': 2000,
        'loop_delay': 1500
    }
)

# 渲染动画
renderer.render()
```

### 自定义渲染管道

```python
class CustomRenderPipeline:
    def __init__(self):
        self.processors = []
    
    def add_processor(self, processor):
        """添加处理器"""
        self.processors.append(processor)
    
    def process_frames(self, frames):
        """处理帧序列"""
        processed_frames = frames
        
        for processor in self.processors:
            processed_frames = processor.process(processed_frames)
        
        return processed_frames

# 使用示例
pipeline = CustomRenderPipeline()
pipeline.add_processor(FrameOptimizer())
pipeline.add_processor(StyleEnhancer())
pipeline.add_processor(CompressionProcessor())

optimized_frames = pipeline.process_frames(original_frames)
```

### 批量渲染

```python
class BatchRenderer:
    def __init__(self, template_manager):
        self.template_manager = template_manager
    
    def render_multiple_templates(self, cast_file, templates):
        """为多个模板渲染同一个 cast 文件"""
        results = {}
        
        # 解析 cast 文件（只需解析一次）
        parser = CastParser(cast_file)
        header, events = parser.parse()
        geometry = parser.get_geometry()
        
        # 生成帧（只需生成一次）
        frame_generator = FrameGenerator(events, geometry, TimingConfig())
        frames = frame_generator.generate_frames()
        
        # 为每个模板渲染
        for template_name in templates:
            try:
                template = self.template_manager.load_template(template_name)
                svg_generator = SVGGenerator(template, geometry)
                svg_content = svg_generator.create_svg_document(frames)
                
                output_file = f'{cast_file.stem}_{template_name}.svg'
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                
                results[template_name] = output_file
            
            except Exception as e:
                results[template_name] = f'Error: {e}'
        
        return results
```

## 错误处理和调试

### 动画验证

```python
class AnimationValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_frames(self, frames):
        """验证帧序列"""
        if not frames:
            self.errors.append("No frames generated")
            return False
        
        # 检查帧时间
        for i, frame in enumerate(frames):
            if frame.duration <= 0:
                self.warnings.append(f"Frame {i} has invalid duration: {frame.duration}")
            
            if frame.duration > 10000:  # 10秒
                self.warnings.append(f"Frame {i} has very long duration: {frame.duration}ms")
        
        # 检查内容
        for i, frame in enumerate(frames):
            if not frame.content:
                self.warnings.append(f"Frame {i} has no content")
        
        return len(self.errors) == 0
    
    def validate_svg(self, svg_content):
        """验证 SVG 内容"""
        try:
            ET.fromstring(svg_content)
            return True
        except ET.ParseError as e:
            self.errors.append(f"Invalid SVG: {e}")
            return False
```

### 性能监控

```python
import time

class RenderingProfiler:
    def __init__(self):
        self.timings = {}
    
    def time_operation(self, operation_name):
        """计时操作装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                self.timings[operation_name] = end_time - start_time
                return result
            return wrapper
        return decorator
    
    def get_report(self):
        """获取性能报告"""
        report = "Rendering Performance Report:\n"
        report += "=" * 30 + "\n"
        
        for operation, duration in self.timings.items():
            report += f"{operation}: {duration:.3f}s\n"
        
        total_time = sum(self.timings.values())
        report += f"\nTotal time: {total_time:.3f}s"
        
        return report
```

这个动画模块 API 文档详细介绍了 TermCap 如何将终端录制转换为 SVG 动画，为开发者提供了完整的技术参考。
