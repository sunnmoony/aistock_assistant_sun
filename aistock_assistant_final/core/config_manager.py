import yaml
import json
import os
from typing import Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class ConfigManager(QObject):
    """配置管理器 - 管理应用配置文件"""
    
    config_changed = pyqtSignal(str, object)
    
    def __init__(self, config_file: str = "config.yaml"):
        super().__init__()
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._default_config = self._get_default_config()
        self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "app": {
                "name": "A股智能助手",
                "version": "1.0.0",
                "language": "zh-CN",
                "theme": "light",
                "font_size": "normal"
            },
            "data": {
                "auto_refresh": True,
                "refresh_interval": 30,
                "cache_enabled": True,
                "cache_ttl": 300,
                "use_mock_data": False,
                "network": {
                    "enabled": True,
                    "max_retries": 3,
                    "retry_delay": 2,
                    "timeout": 30
                }
            },
            "data_sources": {
                "tushare_token": ""
            },
            "search": {
                "tavily_api_keys": [],
                "serpapi_keys": [],
                "bocha_api_keys": [],
                "brave_api_keys": []
            },
            "ai": {
                "api_key": "",
                "api_url": "",
                "model": "default",
                "timeout": 30,
                "max_retries": 3
            },
            "notification": {
                "enabled": True,
                "sound": True,
                "desktop": True,
                "types": ["price_alert", "news", "system"]
            },
            "market": {
                "default_market": "SH",
                "watchlist": [],
                "show_pre_market": True,
                "show_after_market": True
            },
            "ui": {
                "window_width": 1400,
                "window_height": 900,
                "sidebar_width": 240,
                "info_panel_width": 300,
                "show_info_panel": True
            },
            "advanced": {
                "debug_mode": False,
                "log_level": "INFO",
                "data_path": "./data",
                "backup_enabled": True,
                "backup_interval": 3600
            }
        }
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            是否加载成功
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        loaded_config = yaml.safe_load(f)
                    else:
                        loaded_config = json.load(f)
                    
                    self._config = self._merge_config(self._default_config, loaded_config)
                    logger.info(f"配置文件加载成功: {self.config_file}")
                    return True
            else:
                self._config = self._default_config.copy()
                self.save_config()
                logger.info("使用默认配置")
                return True
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._config = self._default_config.copy()
            return False
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并配置
        
        Args:
            default: 默认配置
            loaded: 加载的配置
            
        Returns:
            合并后的配置
        """
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self) -> bool:
        """
        保存配置文件
        
        Returns:
            是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
                else:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置文件保存成功: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径（如 "app.theme"）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any, auto_save: bool = True) -> bool:
        """
        设置配置值
        
        Args:
            key_path: 配置键路径（如 "app.theme"）
            value: 配置值
            auto_save: 是否自动保存
            
        Returns:
            是否设置成功
        """
        try:
            keys = key_path.split('.')
            config = self._config
            
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            config[keys[-1]] = value
            
            self.config_changed.emit(key_path, value)
            
            if auto_save:
                self.save_config()
            
            logger.info(f"配置更新: {key_path} = {value}")
            return True
        except Exception as e:
            logger.error(f"设置配置失败 {key_path}: {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置段
        
        Args:
            section: 配置段名称
            
        Returns:
            配置段字典
        """
        return self._config.get(section, {}).copy()
    
    def set_section(self, section: str, config: Dict[str, Any], 
                   auto_save: bool = True) -> bool:
        """
        设置配置段
        
        Args:
            section: 配置段名称
            config: 配置字典
            auto_save: 是否自动保存
            
        Returns:
            是否设置成功
        """
        try:
            self._config[section] = config
            self.config_changed.emit(section, config)
            
            if auto_save:
                self.save_config()
            
            logger.info(f"配置段更新: {section}")
            return True
        except Exception as e:
            logger.error(f"设置配置段失败 {section}: {e}")
            return False
    
    def reset_to_default(self, section: str = None) -> bool:
        """
        重置为默认配置
        
        Args:
            section: 配置段名称，None表示重置全部
            
        Returns:
            是否重置成功
        """
        try:
            if section:
                if section in self._default_config:
                    self._config[section] = self._default_config[section].copy()
                    self.config_changed.emit(section, self._config[section])
                    logger.info(f"重置配置段: {section}")
            else:
                self._config = self._default_config.copy()
                self.config_changed.emit("*", self._config)
                logger.info("重置所有配置")
            
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"重置配置失败: {e}")
            return False
    
    def export_config(self, export_file: str) -> bool:
        """
        导出配置
        
        Args:
            export_file: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                if export_file.endswith('.yaml') or export_file.endswith('.yml'):
                    yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
                else:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置导出成功: {export_file}")
            return True
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_file: str) -> bool:
        """
        导入配置
        
        Args:
            import_file: 导入文件路径
            
        Returns:
            是否导入成功
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                if import_file.endswith('.yaml') or import_file.endswith('.yml'):
                    loaded_config = yaml.safe_load(f)
                else:
                    loaded_config = json.load(f)
                
                self._config = self._merge_config(self._default_config, loaded_config)
                self.config_changed.emit("*", self._config)
                self.save_config()
            
            logger.info(f"配置导入成功: {import_file}")
            return True
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        获取所有配置

        Returns:
            所有配置字典
        """
        return self._config.copy()
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        配置属性(兼容性访问)

        Returns:
            所有配置字典
        """
        return self._config.copy()
    
    @config.setter
    def config(self, value: Dict[str, Any]):
        """
        设置配置属性(兼容性设置)

        Args:
            value: 配置字典
        """
        self._config = value
        self.save_config()
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置
        
        Returns:
            验证结果字典
        """
        issues = []
        warnings = []
        
        required_sections = ["app", "data", "ai", "notification", "market", "ui"]
        for section in required_sections:
            if section not in self._config:
                issues.append(f"缺少必需的配置段: {section}")
        
        if not self.get("ai.api_key"):
            warnings.append("未设置AI API密钥")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
