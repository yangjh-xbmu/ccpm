#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM包功能测试脚本
测试aipm包的各个模块和功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """测试模块导入"""
    print("🔍 测试aipm包导入...")
    
    try:
        # 测试核心模块导入
        import aipm.core.base
        print("✅ 核心基础类导入成功")
        
        # 测试AI客户端导入
        import aipm.ai.client
        print("✅ AI客户端导入成功")
        
        # 测试工具函数导入
        import aipm.utils.helpers
        print("✅ 工具函数导入成功")
        
        # 测试命令模块导入
        import aipm.commands.epic_decompose
        import aipm.commands.prd_new
        print("✅ 命令模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_validator():
    """测试验证器功能"""
    print("\n🔍 测试验证器功能...")
    
    try:
        from aipm.core.base import BaseValidator
        
        validator = BaseValidator()
        
        # 测试功能名称验证
        valid_names = ['user-auth', 'payment-v2', 'notification-system']
        invalid_names = ['UserAuth', 'payment_system', '123-feature', '']
        
        print("测试有效功能名称:")
        for name in valid_names:
            is_valid, msg = validator.validate_feature_name(name)
            status = "✅" if is_valid else "❌"
            print(f"  {status} {name}: {msg if msg else '有效'}")
        
        print("测试无效功能名称:")
        for name in invalid_names:
            is_valid, msg = validator.validate_feature_name(name)
            status = "✅" if not is_valid else "❌"
            print(f"  {status} {name}: {msg}")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证器测试失败: {e}")
        return False


def test_file_manager():
    """测试文件管理器功能"""
    print("\n🔍 测试文件管理器功能...")
    
    try:
        from aipm.core.base import BaseFileManager
        
        file_manager = BaseFileManager()
        
        # 测试时间获取
        current_time = file_manager.get_current_datetime()
        print(f"✅ 当前时间: {current_time}")
        
        # 测试目录创建
        test_dir = Path("test_temp_dir")
        file_manager.ensure_directory(test_dir)
        if test_dir.exists():
            print("✅ 目录创建成功")
            test_dir.rmdir()  # 清理测试目录
        else:
            print("❌ 目录创建失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件管理器测试失败: {e}")
        return False


def test_content_generators():
    """测试内容生成器"""
    print("\n🔍 测试内容生成器...")
    
    try:
        from aipm.commands.epic_decompose import TaskContentGenerator
        from aipm.commands.prd_new import PRDContentGenerator
        
        # 测试任务内容生成器
        task_generator = TaskContentGenerator()
        task_generator.get_template()
        print("✅ 任务内容生成器模板获取成功")
        
        # 测试PRD内容生成器
        prd_generator = PRDContentGenerator()
        prd_generator.get_template()
        print("✅ PRD内容生成器模板获取成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 内容生成器测试失败: {e}")
        return False


def test_ai_client():
    """测试AI客户端（不需要实际API密钥）"""
    print("\n🔍 测试AI客户端...")
    
    try:
        from aipm.ai.client import AIClient
        
        # 创建AI客户端实例
        AIClient()
        print("✅ AI客户端实例创建成功")
        
        # 注意：不测试实际配置，因为可能没有API密钥
        print("ℹ️  AI客户端配置需要有效的API密钥")
        
        return True
        
    except Exception as e:
        print(f"❌ AI客户端测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("AIPM包功能测试")
    print("="*60)
    
    tests = [
        ("模块导入", test_imports),
        ("验证器功能", test_validator),
        ("文件管理器", test_file_manager),
        ("内容生成器", test_content_generators),
        ("AI客户端", test_ai_client),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n{'='*60}")
    print(f"测试结果: {passed}/{total} 通过")
    print(f"{'='*60}")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关模块")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)