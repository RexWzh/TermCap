# TermCap 配置系统 API

*配置管理模块的完整技术参考*

## 概览

TermCap 的配置系统基于 TOML 格式，使用 `platformdirs` 进行跨平台目录管理。配置系统提供了灵活的设置管理、默认值处理和运行时配置更新功能。

## 核心组件

### 配置管理器

```python
from termcap.config_manager import ConfigManager
from termcap.config import Config

# 创建配置管理器实例
config_manager = ConfigManager()

# 加载配置
config = config_manager.load_config()

# 获取配置值
default_template = config.get('general', 'default_template')

# 设置配置值
config.set('general', 'default_template', 'dracula')

# 保存配置
config_manager.save_config(config)
```

## 配置管理器类

### ConfigManager 主要接口

```python
import toml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from platformdirs import user_config_dir

class ConfigManager:
    def __init__(self, app_name: str = 'termcap'):
        self.app_name = app_name
        self.config_dir = Path(user_config_dir(app_name))
        self.config_file = self.config_dir / 'config.toml'
        self.templates_dir = self.config_dir / 'templates'
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> 'Config':
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = toml.load(f)
                return Config(config_data)
            except (toml.TomlDecodeError, IOError) as e:
                print(f"Warning: Failed to load config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def save_config(self, config: 'Config') -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                toml.dump(config.data, f)
        except IOError as e:
            raise RuntimeError(f"Failed to save config: {e}")
    
    def reset_config(self) -> 'Config':
        """重置配置为默认值"""
        config = self._create_default_config()
        self.save_config(config)
        return config
    
    def _create_default_config(self) -> 'Config':
        """创建默认配置"""
        default_data = {
            'general': {
                'default_template': 'gjm8',
                'default_geometry': '82x19',
                'default_min_duration': 17,
                'default_max_duration': 3000,
                'default_loop_delay': 1000
            },
            'templates': {
                'custom_templates_enabled': True,
                'builtin_templates_enabled': True
            },
            'output': {
                'default_output_dir': '~/termcap_recordings',
                'auto_timestamp': True
            }
        }
        return Config(default_data)
    
    def get_config_path(self) -> Path:
        """获取配置文件路径"""
        return self.config_file
    
    def get_templates_dir(self) -> Path:
        """获取模板目录路径"""
        return self.templates_dir
```

### Config 数据类

```python
class Config:
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.data.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """设置配置值"""
        if section not in self.data:
            self.data[section] = {}
        self.data[section][key] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取整个配置段"""
        return self.data.get(section, {})
    
    def set_section(self, section: str, section_data: Dict[str, Any]) -> None:
        """设置整个配置段"""
        self.data[section] = section_data.copy()
    
    def has_section(self, section: str) -> bool:
        """检查配置段是否存在"""
        return section in self.data
    
    def has_key(self, section: str, key: str) -> bool:
        """检查配置键是否存在"""
        return section in self.data and key in self.data[section]
    
    def remove_key(self, section: str, key: str) -> bool:
        """删除配置键"""
        if self.has_key(section, key):
            del self.data[section][key]
            return True
        return False
    
    def remove_section(self, section: str) -> bool:
        """删除配置段"""
        if section in self.data:
            del self.data[section]
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.data.copy()
    
    def __repr__(self) -> str:
        return f"Config({self.data})"
```

## 配置验证系统

### 配置验证器

```python
from typing import List, Tuple, Union
import re

class ConfigValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_config(self, config: Config) -> bool:
        """验证完整配置"""
        self.errors.clear()
        self.warnings.clear()
        
        # 验证各个配置段
        self._validate_general_section(config)
        self._validate_templates_section(config)
        self._validate_output_section(config)
        
        return len(self.errors) == 0
    
    def _validate_general_section(self, config: Config):
        """验证 general 段"""
        general = config.get_section('general')
        
        # 验证 default_template
        template = general.get('default_template')
        if template and not isinstance(template, str):
            self.errors.append("general.default_template must be a string")
        
        # 验证 default_geometry
        geometry = general.get('default_geometry')
        if geometry:
            if not self._validate_geometry_format(geometry):
                self.errors.append(f"Invalid geometry format: {geometry}")
        
        # 验证时间参数
        time_params = ['default_min_duration', 'default_max_duration', 'default_loop_delay']
        for param in time_params:
            value = general.get(param)
            if value is not None:
                if not isinstance(value, (int, float)) or value < 0:
                    self.errors.append(f"general.{param} must be a non-negative number")
        
        # 检查时间参数逻辑关系
        min_dur = general.get('default_min_duration', 0)
        max_dur = general.get('default_max_duration', float('inf'))
        if min_dur > max_dur:
            self.errors.append("default_min_duration cannot be greater than default_max_duration")
    
    def _validate_templates_section(self, config: Config):
        """验证 templates 段"""
        templates = config.get_section('templates')
        
        # 验证布尔值
        bool_params = ['custom_templates_enabled', 'builtin_templates_enabled']
        for param in bool_params:
            value = templates.get(param)
            if value is not None and not isinstance(value, bool):
                self.errors.append(f"templates.{param} must be a boolean")
    
    def _validate_output_section(self, config: Config):
        """验证 output 段"""
        output = config.get_section('output')
        
        # 验证输出目录
        output_dir = output.get('default_output_dir')
        if output_dir and not isinstance(output_dir, str):
            self.errors.append("output.default_output_dir must be a string")
        
        # 验证自动时间戳
        auto_timestamp = output.get('auto_timestamp')
        if auto_timestamp is not None and not isinstance(auto_timestamp, bool):
            self.errors.append("output.auto_timestamp must be a boolean")
    
    def _validate_geometry_format(self, geometry: str) -> bool:
        """验证几何格式 (WIDTHxHEIGHT)"""
        pattern = r'^\d+x\d+$'
        if not re.match(pattern, geometry):
            return False
        
        try:
            width, height = geometry.split('x')
            width, height = int(width), int(height)
            
            # 检查合理范围
            if width < 10 or width > 1000 or height < 5 or height > 1000:
                self.warnings.append(f"Unusual geometry size: {geometry}")
            
            return True
        except ValueError:
            return False
    
    def get_validation_report(self) -> str:
        """获取验证报告"""
        report = "Configuration Validation Report\n"
        report += "=" * 35 + "\n"
        
        if self.errors:
            report += "ERRORS:\n"
            for error in self.errors:
                report += f"  - {error}\n"
        
        if self.warnings:
            report += "WARNINGS:\n"
            for warning in self.warnings:
                report += f"  - {warning}\n"
        
        if not self.errors and not self.warnings:
            report += "Configuration is valid!\n"
        
        return report
```

## 实用工具示例

### 基础配置操作

```python
# 创建配置管理器
config_manager = ConfigManager()

# 加载配置
config = config_manager.load_config()

# 读取配置值
template = config.get('general', 'default_template', 'gjm8')
geometry = config.get('general', 'default_geometry', '80x24')

# 修改配置
config.set('general', 'default_template', 'dracula')
config.set('general', 'default_geometry', '120x40')

# 保存配置
config_manager.save_config(config)

# 验证配置
validator = ConfigValidator()
if not validator.validate_config(config):
    print(validator.get_validation_report())
```

这个配置系统 API 提供了完整的配置管理功能，支持验证、环境变量和备份等高级特性。
