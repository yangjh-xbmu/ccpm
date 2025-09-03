#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM CLI - AI-Powered Project Management 命令行接口

提供命令行工具用于产品需求文档(PRD)创建、Epic分解和任务管理。
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# 添加当前包路径到系统路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

try:
    from aipm.commands.prd_new import PRDContentGenerator
    from aipm.commands.epic_decompose import TaskContentGenerator
    from aipm.commands.prd_parse import PRDParser
    from aipm.core.base import BaseFileManager
    from aipm.ai.client import AIClient
    from aipm.utils.helpers import ContentExtractor
except ImportError:
    # 如果作为模块运行失败，尝试直接导入
    from commands.prd_new import PRDContentGenerator
    from commands.epic_decompose import TaskContentGenerator
    from commands.prd_parse import PRDParser
    from core.base import BaseFileManager
    from ai.client import AIClient
    from utils.helpers import ContentExtractor


class AIPMFileManager(BaseFileManager):
    """AIPM文件管理器实现"""
    
    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"文件不存在: {file_path}")
        except Exception as e:
            raise Exception(f"读取文件失败: {e}")
    
    def write_file(self, file_path: str, content: str) -> None:
        """写入文件内容"""
        try:
            if not file_path:
                raise ValueError("文件路径不能为空")
            
            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"写入文件失败: {e}")
    
    def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(file_path)
    
    def get_current_datetime(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class AIPMCLI:
    """AIPM命令行接口主类"""
    
    def __init__(self):
        self.file_manager = AIPMFileManager()
        self.ai_client = None
        
    def _init_ai_client(self) -> Optional[AIClient]:
        """初始化AI客户端"""
        try:
            if not self.ai_client:
                self.ai_client = AIClient()
            return self.ai_client
        except Exception as e:
            print(f"⚠️  AI客户端初始化失败: {e}")
            print("💡 提示: 请设置GOOGLE_API_KEY环境变量以启用AI功能")
            return None
    
    def create_prd(self, args) -> None:
        """创建PRD文档"""
        print("🚀 开始创建PRD文档...")
        
        # 收集PRD信息
        prd_info = self._collect_prd_info(args)
        
        # 生成PRD内容
        generator = PRDContentGenerator()
        content = generator.generate_content(
            prd_info['product_name'],
            prd_info,
            self.file_manager.get_current_datetime()
        )
        
        # 确定输出文件路径
        if args.output:
            output_path = args.output
        else:
            output_path = f"prds/{prd_info['product_name'].lower().replace(' ', '-')}.md"
        
        # 写入文件
        self.file_manager.write_file(output_path, content)
        print(f"✅ PRD文档已创建: {output_path}")
        
        # AI增强功能
        if args.ai_enhance and self._init_ai_client():
            self._enhance_prd_with_ai(output_path, prd_info)
    
    def _collect_prd_info(self, args) -> Dict[str, Any]:
        """收集PRD信息"""
        prd_info = {}
        
        # 从命令行参数获取信息
        if args.product_name:
            prd_info['product_name'] = args.product_name
        else:
            prd_info['product_name'] = input("请输入产品名称: ")
        
        if args.product_version:
            prd_info['version'] = args.product_version
        else:
            prd_info['version'] = input("请输入版本号 (默认: 1.0.0): ") or "1.0.0"
        
        if args.author:
            prd_info['author'] = args.author
        else:
            prd_info['author'] = input("请输入作者姓名: ")
        
        # 收集其他信息
        if not args.batch:
            prd_info['description'] = input("请输入产品描述: ")
            prd_info['target_users'] = input("请输入目标用户 (用逗号分隔): ").split(',')
            prd_info['business_goals'] = input("请输入商业目标 (用逗号分隔): ").split(',')
        else:
            # 批处理模式使用默认值
            prd_info['description'] = "待完善的产品描述"
            prd_info['target_users'] = ["待定义的目标用户"]
            prd_info['business_goals'] = ["待定义的商业目标"]
        
        return prd_info
    
    def _enhance_prd_with_ai(self, prd_path: str, prd_info: Dict[str, Any]) -> None:
        """使用AI增强PRD内容"""
        print("🤖 正在使用AI增强PRD内容...")
        try:
            # 读取当前PRD内容
            current_content = self.file_manager.read_file(prd_path)
            
            # 构建AI提示
            prompt = f"""
请帮助完善以下PRD文档，特别是执行摘要、问题陈述和功能需求部分：

产品名称: {prd_info['product_name']}
产品描述: {prd_info.get('description', '')}

当前PRD内容:
{current_content}

请提供改进建议和具体的内容补充。
"""
            
            # 调用AI生成建议
            response = self.ai_client.generate_content(prompt)
            
            # 保存AI建议到单独文件
            ai_suggestions_path = prd_path.replace('.md', '_ai_suggestions.md')
            self.file_manager.write_file(ai_suggestions_path, response)
            print(f"✅ AI建议已保存: {ai_suggestions_path}")
            
        except Exception as e:
            print(f"⚠️  AI增强功能出错: {e}")
    
    def decompose_epic(self, args) -> None:
        """分解Epic为任务"""
        print("📋 开始Epic分解...")
        
        # 读取Epic文件或收集Epic信息
        if args.epic_file:
            epic_content = self.file_manager.read_file(args.epic_file)
            epic_info = self._parse_epic_from_file(epic_content)
        else:
            epic_info = self._collect_epic_info(args)
        
        # 生成任务分解
        if args.ai_decompose and self._init_ai_client():
            tasks = self._ai_decompose_epic(epic_info)
        elif args.batch:
            # 批处理模式使用默认任务
            tasks = self._get_default_tasks()
            print(f"✅ 使用默认任务模板，共 {len(tasks)} 个任务")
        else:
            tasks = self._manual_decompose_epic(epic_info)
        
        # 生成任务文档
        generator = TaskContentGenerator()
        content = generator.generate_content(
            epic_info['title'],
            epic_info,
            tasks,
            self.file_manager.get_current_datetime()
        )
        
        # 确定输出文件路径
        if args.output:
            output_path = args.output
        else:
            output_path = f"tasks/{epic_info['title'].lower().replace(' ', '-')}.md"
        
        # 写入文件
        self.file_manager.write_file(output_path, content)
        print(f"✅ 任务分解文档已创建: {output_path}")
    
    def _parse_epic_from_file(self, content: str) -> Dict[str, Any]:
        """从文件内容解析Epic信息"""
        # 提取Frontmatter
        frontmatter = ContentExtractor.extract_frontmatter(content)
        
        # 提取各个章节
        description = ContentExtractor.extract_section(content, "## 描述")
        acceptance_criteria = ContentExtractor.extract_section(content, "## 验收标准")
        
        return {
            'title': frontmatter.get('title', '未知Epic'),
            'description': description or '无描述',
            'acceptance_criteria': acceptance_criteria.split('\n') if acceptance_criteria else [],
            'priority': frontmatter.get('priority', 'medium'),
            'estimated_hours': frontmatter.get('estimated_hours', 0)
        }
    
    def _collect_epic_info(self, args) -> Dict[str, Any]:
        """收集Epic信息"""
        epic_info = {}
        
        if args.title:
            epic_info['title'] = args.title
        else:
            epic_info['title'] = input("请输入Epic标题: ")
        
        if not args.batch:
            epic_info['description'] = input("请输入Epic描述: ")
            epic_info['priority'] = input("请输入优先级 (high/medium/low, 默认: medium): ") or "medium"
            
            # 收集验收标准
            print("请输入验收标准 (每行一个，空行结束):")
            criteria = []
            while True:
                criterion = input("- ")
                if not criterion:
                    break
                criteria.append(criterion)
            epic_info['acceptance_criteria'] = criteria
        else:
            epic_info['description'] = "待完善的Epic描述"
            epic_info['priority'] = "medium"
            epic_info['acceptance_criteria'] = ["待定义的验收标准"]
        
        return epic_info
    
    def _ai_decompose_epic(self, epic_info: Dict[str, Any]) -> list:
        """使用AI分解Epic"""
        print("🤖 正在使用AI分解Epic...")
        try:
            prompt = f"""
请将以下Epic分解为具体的开发任务：

Epic标题: {epic_info['title']}
Epic描述: {epic_info['description']}
验收标准: {', '.join(epic_info['acceptance_criteria'])}

请按照以下格式输出任务列表：
1. 任务名称 - 任务描述 - 预估工时(小时) - 优先级(high/medium/low)
2. ...

每个任务应该是可独立完成的开发工作项。
"""
            
            response = self.ai_client.generate_content(prompt)
            
            # 解析AI响应为任务列表
            tasks = self._parse_ai_tasks_response(response)
            print(f"✅ AI已生成 {len(tasks)} 个任务")
            return tasks
            
        except Exception as e:
            print(f"⚠️  AI分解失败: {e}")
            print("🔄 切换到手动分解模式...")
            return self._manual_decompose_epic(epic_info)
    
    def _parse_ai_tasks_response(self, response: str) -> list:
        """解析AI任务响应"""
        tasks = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # 解析任务行
                parts = line.split(' - ')
                if len(parts) >= 2:
                    # 提取任务名称（去掉序号）
                    title = parts[0]
                    if '. ' in title:
                        title = title.split('. ', 1)[1]
                    
                    task = {
                        'title': title,
                        'description': parts[1] if len(parts) > 1 else '',
                        'estimated_hours': 4,  # 默认值
                        'priority': 'medium',  # 默认值
                        'status': 'pending'
                    }
                    
                    # 尝试解析工时和优先级
                    if len(parts) > 2:
                        for part in parts[2:]:
                            if '小时' in part or 'hour' in part.lower():
                                try:
                                    hours = int(''.join(filter(str.isdigit, part)))
                                    task['estimated_hours'] = hours
                                except:
                                    pass
                            elif part.lower() in ['high', 'medium', 'low']:
                                task['priority'] = part.lower()
                    
                    tasks.append(task)
        
        return tasks if tasks else self._get_default_tasks()
    
    def _manual_decompose_epic(self, epic_info: Dict[str, Any]) -> list:
        """手动分解Epic"""
        print("📝 请手动输入任务信息:")
        tasks = []
        
        while True:
            print(f"\n任务 #{len(tasks) + 1}:")
            title = input("任务标题 (空行结束): ")
            if not title:
                break
            
            description = input("任务描述: ")
            estimated_hours = input("预估工时 (小时, 默认: 4): ")
            priority = input("优先级 (high/medium/low, 默认: medium): ")
            
            task = {
                'title': title,
                'description': description or '待完善',
                'estimated_hours': int(estimated_hours) if estimated_hours.isdigit() else 4,
                'priority': priority if priority in ['high', 'medium', 'low'] else 'medium',
                'status': 'pending'
            }
            
            tasks.append(task)
        
        return tasks if tasks else self._get_default_tasks()
    
    def _get_default_tasks(self) -> list:
        """获取默认任务列表"""
        return [
            {
                'title': '需求分析',
                'description': '分析和整理详细需求',
                'estimated_hours': 4,
                'priority': 'high',
                'status': 'pending'
            },
            {
                'title': '技术设计',
                'description': '设计技术方案和架构',
                'estimated_hours': 6,
                'priority': 'high',
                'status': 'pending'
            },
            {
                'title': '开发实现',
                'description': '编码实现功能',
                'estimated_hours': 16,
                'priority': 'medium',
                'status': 'pending'
            },
            {
                'title': '测试验证',
                'description': '功能测试和验证',
                'estimated_hours': 4,
                'priority': 'medium',
                'status': 'pending'
            }
        ]
    
    def parse_prd(self, args) -> None:
        """解析PRD文档"""
        print(f"📖 正在解析PRD文档: {args.prd_file}")
        
        if not self.file_manager.file_exists(args.prd_file):
            print(f"❌ 文件不存在: {args.prd_file}")
            return
        
        try:
            # 读取PRD文件
            content = self.file_manager.read_file(args.prd_file)
            
            # 解析PRD
            parser = PRDParser()
            prd_data = parser.parse_content(content)
            
            # 输出解析结果
            print("\n📋 PRD解析结果:")
            print(f"产品名称: {prd_data.get('product_name', 'N/A')}")
            print(f"版本: {prd_data.get('version', 'N/A')}")
            print(f"作者: {prd_data.get('author', 'N/A')}")
            print(f"创建时间: {prd_data.get('created_time', 'N/A')}")
            
            if 'features' in prd_data:
                print(f"\n功能需求 ({len(prd_data['features'])}个):")
                for i, feature in enumerate(prd_data['features'][:5], 1):
                    print(f"  {i}. {feature}")
                if len(prd_data['features']) > 5:
                    print(f"  ... 还有 {len(prd_data['features']) - 5} 个功能")
            
            # 保存解析结果
            if args.output:
                import json
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(prd_data, f, ensure_ascii=False, indent=2)
                print(f"\n✅ 解析结果已保存: {args.output}")
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")
    
    def show_version(self) -> None:
        """显示版本信息"""
        print("AIPM - AI-Powered Project Management")
        print("版本: 1.0.0")
        print("作者: AIPM Team")
        print("描述: 基于AI的产品管理工具包")


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='aipm',
        description='AIPM - AI-Powered Project Management 命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  aipm prd create --product-name "我的产品" --author "张三"
  aipm epic decompose --title "用户认证" --ai-decompose
  aipm prd parse --prd-file prds/my-product.md
  aipm --version

更多信息请访问: https://github.com/your-org/aipm
"""
    )
    
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # PRD命令组
    prd_parser = subparsers.add_parser('prd', help='PRD相关操作')
    prd_subparsers = prd_parser.add_subparsers(dest='prd_action', help='PRD操作')
    
    # PRD创建命令
    prd_create = prd_subparsers.add_parser('create', help='创建PRD文档')
    prd_create.add_argument('--product-name', help='产品名称')
    prd_create.add_argument('--product-version', help='产品版本号', default='1.0.0')
    prd_create.add_argument('--author', help='作者姓名')
    prd_create.add_argument('--output', '-o', help='输出文件路径')
    prd_create.add_argument('--ai-enhance', action='store_true', help='使用AI增强PRD内容')
    prd_create.add_argument('--batch', action='store_true', help='批处理模式（使用默认值）')
    
    # PRD解析命令
    prd_parse = prd_subparsers.add_parser('parse', help='解析PRD文档')
    prd_parse.add_argument('prd_file', help='PRD文件路径')
    prd_parse.add_argument('--output', '-o', help='输出JSON文件路径')
    
    # Epic命令组
    epic_parser = subparsers.add_parser('epic', help='Epic相关操作')
    epic_subparsers = epic_parser.add_subparsers(dest='epic_action', help='Epic操作')
    
    # Epic分解命令
    epic_decompose = epic_subparsers.add_parser('decompose', help='分解Epic为任务')
    epic_decompose.add_argument('--title', help='Epic标题')
    epic_decompose.add_argument('--epic-file', help='Epic文件路径')
    epic_decompose.add_argument('--output', '-o', help='输出文件路径')
    epic_decompose.add_argument('--ai-decompose', action='store_true', help='使用AI自动分解')
    epic_decompose.add_argument('--batch', action='store_true', help='批处理模式')
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 创建CLI实例
    cli = AIPMCLI()
    
    try:
        if args.version:
            cli.show_version()
        elif args.command == 'prd':
            if args.prd_action == 'create':
                cli.create_prd(args)
            elif args.prd_action == 'parse':
                cli.parse_prd(args)
            else:
                parser.print_help()
        elif args.command == 'epic':
            if args.epic_action == 'decompose':
                cli.decompose_epic(args)
            else:
                parser.print_help()
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n👋 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()