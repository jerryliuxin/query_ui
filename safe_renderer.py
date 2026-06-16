#!/usr/bin/env python3
"""
Safe context processor for Jinja2 templates
提供安全的环境配置和上下文处理
"""

def make_safe_context(context_dict):
    """
    将嵌套字典扁平化，确保所有嵌套值可通过点号访问
    例如: {"profile": {"funding_stage": "A轮"}} → 增加 {"profile_funding_stage": "A轮"}
    """
    flat = {}
    for key, value in context_dict.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                flat_key = f"{key}_{subkey}"
                if flat_key not in context_dict:
                    flat[flat_key] = subvalue
        # 保持原键值
        flat[key] = value
    return {**context_dict, **flat}
