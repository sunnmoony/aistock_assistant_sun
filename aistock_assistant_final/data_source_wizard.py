# -*- coding: utf-8 -*-
"""
===================================
数据源配置向导
===================================

帮助新手轻松配置数据源
"""

import os
import sys
import json
import yaml

DATA_SOURCES = {
    "pytdx": {
        "name": "通达信(Pytdx)",
        "description": "免费、稳定、实时行情数据源",
        "required_config": [],
        "recommended": True,
        "priority": 0
    },
    "akshare": {
        "name": "AkShare",
        "description": "免费、功能全面的金融数据接口",
        "required_config": [],
        "recommended": True,
        "priority": 1
    },
    "tushare": {
        "name": "Tushare",
        "description": "专业金融数据接口，需要注册获取Token",
        "required_config": ["token"],
        "recommended": False,
        "priority": 2,
        "register_url": "https://tushare.pro/register"
    },
    "baostock": {
        "name": "Baostock",
        "description": "免费证券宝数据接口，支持复权数据",
        "required_config": [],
        "recommended": False,
        "priority": 3
    }
}


def check_data_source_available(source_name):
    """检查数据源是否可用"""
    try:
        if source_name == "pytdx":
            import pytdx
            return True
        elif source_name == "akshare":
            import akshare
            return True
        elif source_name == "tushare":
            import tushare
            return True
        elif source_name == "baostock":
            import baostock
            return True
    except ImportError:
        return False
    return False


def install_data_source(source_name):
    """安装数据源依赖"""
    import subprocess
    
    package_map = {
        "pytdx": "pytdx",
        "akshare": "akshare",
        "tushare": "tushare",
        "baostock": "baostock"
    }
    
    package = package_map.get(source_name)
    if package:
        print(f"正在安装 {source_name}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package, "-q"])
        print(f"{source_name} 安装完成")


def test_data_source_connection(source_name, config=None):
    """测试数据源连接"""
    config = config or {}
    
    try:
        if source_name == "pytdx":
            from pytdx.hq import TdxHq_API
            api = TdxHq_API()
            result = api.connect('119.147.212.81', 7709)
            if result:
                data = api.get_security_quotes([(1, '600000')])
                api.disconnect()
                return True, "连接成功"
            return False, "连接失败"
            
        elif source_name == "akshare":
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            if df is not None and len(df) > 0:
                return True, f"获取到 {len(df)} 只股票数据"
            return False, "未获取到数据"
            
        elif source_name == "tushare":
            import tushare as ts
            token = config.get('token', '')
            if not token:
                return False, "需要配置Token"
            ts.set_token(token)
            pro = ts.pro_api()
            df = pro.trade_cal(exchange='SSE', limit=1)
            if df is not None:
                return True, "Token验证成功"
            return False, "Token验证失败"
            
        elif source_name == "baostock":
            import baostock as bs
            lg = bs.login()
            if lg.error_code == '0':
                bs.logout()
                return True, "登录成功"
            return False, f"登录失败: {lg.error_msg}"
            
    except Exception as e:
        return False, f"测试失败: {str(e)}"
    
    return False, "未知数据源"


def save_config(config):
    """保存配置到config.yaml"""
    config_path = "config.yaml"
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            existing_config = yaml.safe_load(f) or {}
    else:
        existing_config = {}
    
    if 'data_sources' not in existing_config:
        existing_config['data_sources'] = {}
    
    existing_config['data_sources'].update(config)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(existing_config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"配置已保存到 {config_path}")


def run_wizard():
    """运行配置向导"""
    print("=" * 50)
    print("    A股智能助手 - 数据源配置向导")
    print("=" * 50)
    print()
    
    print("可用数据源：")
    print()
    
    for key, info in sorted(DATA_SOURCES.items(), key=lambda x: x[1]['priority']):
        available = "✓" if check_data_source_available(key) else "✗"
        recommended = " [推荐]" if info['recommended'] else ""
        print(f"  [{available}] {info['name']}{recommended}")
        print(f"      {info['description']}")
        if info.get('register_url'):
            print(f"      注册地址: {info['register_url']}")
        print()
    
    print("-" * 50)
    print()
    
    config = {}
    
    for source_name, info in sorted(DATA_SOURCES.items(), key=lambda x: x[1]['priority']):
        if info['recommended']:
            default = 'y'
        else:
            default = 'n'
        
        enable = input(f"启用 {info['name']}? (y/n) [{default}]: ").strip().lower()
        enable = enable if enable else default
        
        if enable == 'y':
            if not check_data_source_available(source_name):
                install = input(f"  {info['name']} 未安装，是否安装? (y/n) [y]: ").strip().lower()
                if install != 'n':
                    install_data_source(source_name)
            
            source_config = {"enabled": True}
            
            for req in info.get('required_config', []):
                value = input(f"  请输入 {req}: ").strip()
                if value:
                    source_config[req] = value
            
            success, msg = test_data_source_connection(source_name, source_config)
            if success:
                print(f"  ✓ 测试成功: {msg}")
            else:
                print(f"  ✗ 测试失败: {msg}")
                continue
            
            config[source_name] = source_config
        else:
            config[source_name] = {"enabled": False}
    
    print()
    print("-" * 50)
    
    if config:
        save_config(config)
        print()
        print("配置完成！现在可以启动程序了。")
    else:
        print("未配置任何数据源。")


if __name__ == "__main__":
    run_wizard()
