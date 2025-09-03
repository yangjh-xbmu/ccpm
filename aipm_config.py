#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM 配置文件
设置默认行为和选项
"""

import os
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    # AI功能默认启用
    'ai_enhance_default': True,
    'ai_decompose_default': True,

    # 批处理模式默认关闭（保持交互性）
    'batch_mode_default': False,

    # 默认输出目录
    'default_output_dir': 'output',

    # API配置
    'google_api_key': os.getenv('GOOGLE_API_KEY', ''),

    # 文件命名模式
    'prd_filename_pattern': '{product_name}_prd_{timestamp}.md',
    'tasks_filename_pattern': '{epic_title}_tasks_{timestamp}.md',

    # 默认作者（可从环境变量获取）
    'default_author': os.getenv('AIPM_DEFAULT_AUTHOR', ''),

    # 默认产品版本
    'default_product_version': '1.0.0',
}


def get_config():
    """获取配置"""
    config = DEFAULT_CONFIG.copy()

    # 尝试从配置文件加载
    config_file = Path.home() / '.aipm_config.py'
    if config_file.exists():
        try:
            # 动态导入用户配置
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "user_config", config_file)
            user_config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_config)

            # 合并用户配置
            if hasattr(user_config, 'USER_CONFIG'):
                config.update(user_config.USER_CONFIG)
        except Exception as e:
            print(f"⚠️  加载用户配置失败: {e}")

    return config


def create_user_config_template():
    """创建用户配置模板"""
    config_file = Path.home() / '.aipm_config.py'
    if config_file.exists():
        print(f"配置文件已存在: {config_file}")
        return

    template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM 用户配置文件
可以覆盖默认设置
"""

# 用户自定义配置
USER_CONFIG = {
    # AI功能默认启用（True/False）
    'ai_enhance_default': True,
    'ai_decompose_default': True,
    
    # 默认作者
    'default_author': '你的名字',
    
    # 默认输出目录
    'default_output_dir': 'my_output',
    
    # 其他配置...
}
'''

    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"✅ 配置模板已创建: {config_file}")
        print("请编辑此文件来自定义您的默认设置")
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")


if __name__ == '__main__':
    # 创建配置模板
    create_user_config_template()

    # 显示当前配置
    config = get_config()
    print("\n当前配置:")
    for key, value in config.items():
        if 'api_key' in key.lower() and value:
            print(f"  {key}: {'*' * 8}")
        else:
            print(f"  {key}: {value}")
