#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM 工作流程测试脚本
测试重构后的包结构和完整工作流程
"""

import sys
from pathlib import Path
import shutil
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ai_pm import (run_full_workflow, create_prd, parse_prd,
                         decompose_epic)
    import ai_pm
except ImportError as e:
    print(f"❌ 包导入失败: {e}")
    print("请确保ccpm_pm包已正确安装")
    sys.exit(1)


def test_package_import():
    """测试包导入"""
    print("\n🔍 测试包导入...")
    try:
        print(f"✅ 包版本: {ai_pm.__version__}")
        print("✅ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 包导入失败: {e}")
        return False


def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}不存在: {file_path}")
        return False


def test_prd_creation(feature_name, mode):
    """测试PRD创建"""
    print("\n" + "="*50)
    print("第一步: 创建PRD")
    print("="*50)
    
    try:
        # 使用包的函数创建PRD
        result = create_prd(feature_name, mode)
        if result:
            print("✅ PRD创建成功")
            prd_file = f".claude/prds/{feature_name}.md"
            return check_file_exists(prd_file, "PRD文件")
        else:
            print("❌ PRD创建失败")
            return False
    except Exception as e:
        print(f"❌ PRD创建异常: {e}")
        return False


def test_epic_creation(feature_name, mode):
    """测试Epic创建"""
    print("\n" + "="*50)
    print("第二步: 创建Epic")
    print("="*50)
    
    try:
        # 使用包的函数解析PRD
        result = parse_prd(feature_name, mode)
        if result:
            print("✅ Epic创建成功")
            epic_file = f".claude/epics/{feature_name}/epic.md"
            return check_file_exists(epic_file, "Epic文件")
        else:
            print("❌ Epic创建失败")
            return False
    except Exception as e:
        print(f"❌ Epic创建异常: {e}")
        return False


def test_task_decomposition(feature_name, mode):
    """测试任务分解"""
    print("\n" + "="*50)
    print("第三步: 分解任务")
    print("="*50)
    
    try:
        # 使用包的函数分解Epic
        result = decompose_epic(feature_name, mode)
        if result:
            print("✅ 任务分解成功")
            
            # 检查任务目录是否创建
            tasks_dir = f".claude/epics/{feature_name}/tasks"
            if not Path(tasks_dir).exists():
                print(f"❌ 任务目录不存在: {tasks_dir}")
                return False
            
            # 检查是否有任务文件
            task_files = list(Path(tasks_dir).glob("*.md"))
            if not task_files:
                print(f"❌ 任务目录中没有任务文件: {tasks_dir}")
                return False
            
            print(f"✅ 任务目录: {tasks_dir}")
            print(f"✅ 创建了 {len(task_files)} 个任务文件")
            for task_file in task_files:
                print(f"  - {task_file.name}")
            
            return True
        else:
            print("❌ 任务分解失败")
            return False
    except Exception as e:
        print(f"❌ 任务分解异常: {e}")
        return False


def show_workflow_summary(feature_name):
    """显示工作流程摘要"""
    print("\n" + "="*50)
    print("工作流程完成摘要")
    print("="*50)
    
    # 检查所有生成的文件
    prd_file = Path(f".claude/prds/{feature_name}.md")
    epic_file = Path(f".claude/epics/{feature_name}/epic.md")
    tasks_dir = Path(f".claude/epics/{feature_name}/tasks")
    
    print(f"\n📁 为功能 '{feature_name}' 生成的文件:")
    
    if prd_file.exists():
        print(f"✅ PRD: {prd_file}")
    else:
        print(f"❌ PRD: {prd_file} (不存在)")
    
    if epic_file.exists():
        print(f"✅ Epic: {epic_file}")
    else:
        print(f"❌ Epic: {epic_file} (不存在)")
    
    if tasks_dir.exists():
        task_files = list(tasks_dir.glob("*.md"))
        print(f"✅ 任务目录: {tasks_dir} ({len(task_files)} 个任务)")
        for task_file in task_files:
            print(f"  - {task_file}")
    else:
        print(f"❌ 任务目录: {tasks_dir} (不存在)")
    
    print("\n🎉 CCPM PRD工作流程测试完成！")
    print("\n💡 下一步建议:")
    print(f"  - 查看PRD: cat {prd_file}")
    print(f"  - 查看Epic: cat {epic_file}")
    print(f"  - 查看任务: ls {tasks_dir}/")
    print("  - 开始开发工作")


def cleanup_test_files(feature_name):
    """清理测试文件"""
    
    print(f"\n🧹 清理测试文件 '{feature_name}'")
    
    # 删除PRD文件
    prd_file = Path(f".claude/prds/{feature_name}.md")
    if prd_file.exists():
        prd_file.unlink()
        print(f"✅ 删除PRD: {prd_file}")
    
    # 删除Epic目录
    epic_dir = Path(f".claude/epics/{feature_name}")
    if epic_dir.exists():
        shutil.rmtree(epic_dir)
        print(f"✅ 删除Epic目录: {epic_dir}")
    
    print("✅ 清理完成")


def test_full_workflow(feature_name, mode):
    """测试完整工作流程"""
    print(f"\n🔄 测试完整工作流程 - 功能: {feature_name}")
    
    try:
        # 使用包的便捷函数测试完整工作流程
        result = run_full_workflow(feature_name, mode)
        
        if result:
            print("\n✅ 完整工作流程测试成功!")
            if 'prd_result' in result and result['prd_result']:
                prd_file = result['prd_result'].get('prd_file', 'N/A')
                print(f"📄 PRD文件: {prd_file}")
            if 'epic_result' in result and result['epic_result']:
                epic_file = result['epic_result'].get('epic_file', 'N/A')
                print(f"🔧 Epic文件: {epic_file}")
            if 'tasks_result' in result and result['tasks_result']:
                tasks_file = result['tasks_result'].get('tasks_file', 'N/A')
                print(f"📋 任务文件: {tasks_file}")
            return True
        else:
            print("❌ 完整工作流程测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 工作流程执行异常: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='测试重构后的CCPM包结构和工作流程')
    parser.add_argument('feature_name', help='功能名称')
    parser.add_argument(
        '--mode',
        choices=['interactive', 'non-interactive', 'ai'],
        default='non-interactive',
        help='工作模式'
    )
    parser.add_argument(
        '--cleanup', action='store_true', help='测试后清理文件'
    )
    parser.add_argument(
        '--test-import', action='store_true', help='仅测试包导入'
    )
    parser.add_argument(
        '--test-full', action='store_true', help='测试完整工作流程'
    )
    
    args = parser.parse_args()
    feature_name = args.feature_name
    mode = args.mode
    
    print("\n🚀 开始测试CCPM包结构和工作流程")
    print(f"功能名称: {feature_name}")
    print(f"工作模式: {mode}")
    
    # 测试包导入
    if not test_package_import():
        sys.exit(1)
    
    if args.test_import:
        print("\n✅ 包导入测试完成")
        sys.exit(0)
    
    # 执行工作流程
    success = True
    
    if args.test_full:
        # 测试完整工作流程
        success = test_full_workflow(feature_name, mode)
    else:
        # 分步测试
        # 第一步: 创建PRD
        if success:
            success = test_prd_creation(feature_name, mode)
        
        # 第二步: 创建Epic
        if success:
            success = test_epic_creation(feature_name, mode)
        
        # 第三步: 分解任务
        if success:
            success = test_task_decomposition(feature_name, mode)
    
    # 显示摘要
    show_workflow_summary(feature_name)
    
    # 清理文件（如果请求）
    if args.cleanup:
        cleanup_test_files(feature_name)
    
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
