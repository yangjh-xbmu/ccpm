#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIPM包安装配置文件
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements
requirements = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="aipm",
    version="1.0.0",
    author="AIPM Team",
    author_email="team@aipm.dev",
    description="AI-Powered Project Management - 基于AI的产品管理工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/aipm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Groupware",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "ai": ["google-generativeai>=0.3.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "all": [
            "google-generativeai>=0.3.0",
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "aipm=aipm.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "aipm": ["*.md", "*.txt"],
    },
    keywords=[
        "project management",
        "product management",
        "prd",
        "epic",
        "task management",
        "ai",
        "automation",
        "documentation",
        "workflow",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-org/aipm/issues",
        "Source": "https://github.com/your-org/aipm",
        "Documentation": "https://github.com/your-org/aipm/blob/main/README.md",
    },
)