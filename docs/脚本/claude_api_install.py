"""
Claude Code API 配置选择器
允许用户在启动时选择不同的API端点和密钥、
如果发现connect 的问题 记得要要检查DNS，因为某些情况下流量的DNS服务器炸了，未必能够找到claude.ai
的地址，建议使用claude logout去清除以前的所有ANTHROPIC_API_K1EY这个旧的问题，换成auth_api_key就没有任何问题了。
claude code 远程服务器最好不要挂梯子，而且设置对API key就不会需要登录，遇到之前的麻烦事。
OPENAI 本地闲鱼配置，还是bussiness账号，然后本地就是windows好像会自己走转发， 但是linux 必须要命令行带转发设置proxy。网上查了很多关于这个codex如何增加
proxy都是在命令行增加，所以来看比较复杂。不清楚vscode的插件走的什么。
遇到ANTHROPIC_API_KEY无法删除旧的API KEY的问题，挺神奇的，暂时不知道为什么，就是找遍了这个也没有找到来源是什么？果然重启就对了，可能是哪个程序固定写入了。
"""

import json
import os
import sys
import subprocess
from pathlib import Path
if sys.platform.startswith("win"):  # 或者用 os.name == "nt"
    import winreg
# https://status.claude.com/ 当没有反应的时候建议去这个网站查看下是否是服务端的问题

OPENAI_API_CONFIGS = {
# 第一种思路 复制已经登录账号的电脑的auth.json的内容,这个好像要随时刷新，用不了
    # "1":{
    #     "OPENAI_API_KEY": None, # 写到C:\Users\usr_name\.codex\auth.json or ~/.codex/auth.json
    #     "tokens": {
    #         "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIxZGQzZjhmLTlhYWQtNDdmZS1iMGU3LWVkYjAwOTc3N2Q2YiIsInR5cCI6IkpXVCJ9.eyJhdF9oYXNoIjoiVWhoc1NWQlZLc3lZV2w0TVBqTjR0dyIsImF1ZCI6WyJhcHBfRU1vYW1FRVo3M2YwQ2tYYVhwN2hyYW5uIl0sImF1dGhfcHJvdmlkZXIiOiJnb29nbGUiLCJhdXRoX3RpbWUiOjE3NTg4NjM4MTIsImVtYWlsIjoieWFueW9uZ3FpOEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZXhwIjoxNzU4ODY3NDE0LCJodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgiOnsiY2hhdGdwdF9hY2NvdW50X2lkIjoiNDM2OWQ2NTYtY2UxNS00Y2Y1LTg4ODMtMzM0ODQ5ZDAwMjNlIiwiY2hhdGdwdF9wbGFuX3R5cGUiOiJwbHVzIiwiY2hhdGdwdF9zdWJzY3JpcHRpb25fYWN0aXZlX3N0YXJ0IjoiMjAyNS0wOS0yNVQxMTo0MTo0OCswMDowMCIsImNoYXRncHRfc3Vic2NyaXB0aW9uX2FjdGl2ZV91bnRpbCI6IjIwMjUtMTAtMjVUMTE6NDE6NDgrMDA6MDAiLCJjaGF0Z3B0X3N1YnNjcmlwdGlvbl9sYXN0X2NoZWNrZWQiOiIyMDI1LTA5LTI2VDA1OjE2OjUyLjU3MTYyMiswMDowMCIsImNoYXRncHRfdXNlcl9pZCI6InVzZXItQlBWdlcyeHNVdkp0dFFXaFBXT1VzZjl1IiwiZ3JvdXBzIjpbXSwib3JnYW5pemF0aW9ucyI6W3siaWQiOiJvcmctQVI5dWNQZnljWmdYaTVlb2E1S1gwOE9DIiwiaXNfZGVmYXVsdCI6dHJ1ZSwicm9sZSI6Im93bmVyIiwidGl0bGUiOiJQZXJzb25hbCJ9XSwidXNlcl9pZCI6InVzZXItQlBWdlcyeHNVdkp0dFFXaFBXT1VzZjl1In0sImlhdCI6MTc1ODg2MzgxNCwiaXNzIjoiaHR0cHM6Ly9hdXRoLm9wZW5haS5jb20iLCJqdGkiOiI0NDM4YzllOC02OGIxLTQ1YTctOWE2OC01ZDZlN2RiMzllODMiLCJyYXQiOjE3NTg4NjM4MDEsInNpZCI6ImRkY2ViMDVkLWUxMjQtNGI3ZS1hZTgzLTFlOWQwYzdlN2UzNCIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTE1MzExODM5MTEwNjU2Nzk1Nzk4In0.WXwMACNyi2bM0EQFsRYybp_mCRRXZOsD-oOTKnVskaNhodU3YD5aGGOn9AEB_n6vv1_xpsHB26E2FeZs5uYn4sBepa1FppA23KRSHmLE5AG0x-3TI6WyHcESvfimCbwu0iJONdZKgfvKx-97iQyaoaE_S_xR8hee_GraDupssk7-REUxg2Z47J-th-SFtpYQPU8MEHNSEsp1Ogwt4IGa5YiWkFRAUV1jTzn9wooiu6vwW4UAz_7Jew-tEukxatSRJzj90CsSnHwZ6rg05DTl60oJNLomRMiXNGTczGJOcuesJeHSzlBtKW-Y6GnucXOosO4hHL0t7TwPIM8dsflfafr_mJIsKVHVJ39PLrKii5YDkvdxbdJ8ZNRLNgox26TO6zlHJhobdYB7Yh0uSiZmMNKbcD4iF7HezLnl2NUAf4gbMdkHnAMQj9a5DhVhRFAF07Fh6ZuQcA_NzUXLVVFzpeBNnZXiFlhkYuJnTRQU0rR7-MRiITYgTIa2m-jmF1LVwOWX0VbHKNxYmjr8aUEqHopQSFyu68cTGaNUygyx-J-m11p0yhXN89wD9_uJ_-f4UC4atgZu_Y3B8gAS0F28CctjXcNQapVdezYsz7M0wj5kwdjS8jQjK54BnmbSTvOLiWwAgLdJtebxd5_RBDxxbB7uvxXzj63b9eDrmnBp_NM",
    #         "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE5MzQ0ZTY1LWJiYzktNDRkMS1hOWQwLWY5NTdiMDc5YmQwZSIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS92MSJdLCJjbGllbnRfaWQiOiJhcHBfRU1vYW1FRVo3M2YwQ2tYYVhwN2hyYW5uIiwiZXhwIjoxNzU5NzI3ODE1LCJodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgiOnsiY2hhdGdwdF9hY2NvdW50X2lkIjoiNDM2OWQ2NTYtY2UxNS00Y2Y1LTg4ODMtMzM0ODQ5ZDAwMjNlIiwiY2hhdGdwdF9hY2NvdW50X3VzZXJfaWQiOiJ1c2VyLUJQVnZXMnhzVXZKdHRRV2hQV09Vc2Y5dV9fNDM2OWQ2NTYtY2UxNS00Y2Y1LTg4ODMtMzM0ODQ5ZDAwMjNlIiwiY2hhdGdwdF9jb21wdXRlX3Jlc2lkZW5jeSI6Im5vX2NvbnN0cmFpbnQiLCJjaGF0Z3B0X3BsYW5fdHlwZSI6InBsdXMiLCJjaGF0Z3B0X3VzZXJfaWQiOiJ1c2VyLUJQVnZXMnhzVXZKdHRRV2hQV09Vc2Y5dSIsInVzZXJfaWQiOiJ1c2VyLUJQVnZXMnhzVXZKdHRRV2hQV09Vc2Y5dSJ9LCJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJ5YW55b25ncWk4QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwiaWF0IjoxNzU4ODYzODE0LCJpc3MiOiJodHRwczovL2F1dGgub3BlbmFpLmNvbSIsImp0aSI6IjI5ODNkMjZjLWI0NmYtNDMxOC1iOWU0LTY5NzFmYjMzMjY1YSIsIm5iZiI6MTc1ODg2MzgxNCwicHdkX2F1dGhfdGltZSI6MTc1ODg2MzgxMjU3MSwic2NwIjpbIm9wZW5pZCIsInByb2ZpbGUiLCJlbWFpbCIsIm9mZmxpbmVfYWNjZXNzIl0sInNlc3Npb25faWQiOiJhdXRoc2Vzc19TUnpVd3ZPM1lZbkFHMGxzNWJsTVZ4bzUiLCJzdWIiOiJnb29nbGUtb2F1dGgyfDExNTMxMTgzOTExMDY1Njc5NTc5OCJ9.l61n5nNFmVkOHDMO1m7eCtLOF-wTzobjGmyQkFdXhfjwzKfC_S-BJfywVGjDu-HKwf5ILyCilfpfWuuQNPlTtBTE6ywZew6tIRVFvHASqNLRVSGOBK2jLcEPPjKa-dmEnZQ2a20uMU-5_a0TovSd68R2dFQjjRCpzx3J6UJRMRQG3GO2_Dt2vVQaBCMhdTHbbTanD3A5MfZdiux73GfTl1EtmQhShuvb8QI8byAa-Rsh7s-XmHkaJSqdfOHqF8ZzL-vv6IIg9nVVuSMBHOW1w4tENRUhnF_6so_ediRV9oNtmgO2ExYtbgeEHVR6H-lI7hVetHyfjfYv-M-4pRJ_zOB4vyxiVfhRT6T9Bfwlrczl5ptHcmm_SQK-A1h8ydLs98hQxSF_wjOBdDdO6R5-IE2A4rVxV7BlSB5FZDDPixxDpLitfQi-5utRkHocOQj4-fcY1ECyylKnrlvMySClkd8d3apIVYQlLjAnzLajx4yJQRCdUdHdGKup-pTIV_OmsXHLf1XaP51JEnzD4wd9XRZ0_6m2sHfWLnls9z-wocZbEL6uRPOhrvErGKUzf8yStvB1lv1kIBWwqfDtlVGMCu_lp4DHdM6juHfYj8kEejzGbUIxrKbCkvbXqMfW3fy0A8wxDfQQc9eOgTb7FbFZwMZRJ2ScIESpWywresh_token": "rt_hRrubDbgMKppg4Kod0oBVxOx9pUH0AAozQM1fMmRERA.TkxMxx7uRdadHH3Lqe-Jtoa4-y7a_MiNA6kVENHgJXs",
    #         "account_id": "4369d656-ce15-4cf5-8883-334849d0023e"
    #     },
    #     "last_refresh": "2025-09-26T05:16:56.144559200Z"
    # },
#第二种思路，转发 
#~/.codex/config.toml配置下面的：    
# model_provider = "crs"
# model = "gpt-5-codex"
# model_reasoning_effort = "high"
# disable_response_storage = true
# preferred_auth_method = "apikey"
# [model_providers.crs]
# name = "crs"
# base_url = "https://argo0.ai-proxy.4ba.ai/openai"
# wire_api = "responses"
# requires_openai_auth = true
# env_key = "CRS_OAI_KEY"
#~/.codex/auth.json配置下面的：
# {
#   "OPENAI_API_KEY": null,
# }
# 然后永久设置环境变量set CRS_OAI_KEY=cr_xxxxxxxxxx
# 先把windows的配置通过
    "2":{
        "OPENAI_API_KEY": None,
        "env_vars": {
            "CRS_OAI_KEY": "cr_5e336bf379637d65d3be918114510237c088be775a76d10d8bc78e34cfb25a63"  # 需要替换为实际的API密钥
        },
        "config_toml": {
            "model_provider": "crs",
            "model": "gpt-5-codex",
            "model_reasoning_effort": "high",
            "disable_response_storage": True,
            "preferred_auth_method": "apikey",
            "model_providers": {
                "crs": {
                    "name": "crs",
                    "base_url": "https://argo0.ai-proxy.4ba.ai/openai",
                    "wire_api": "responses",
                    "requires_openai_auth": True,
                    "env_key": "CRS_OAI_KEY"
                }
            }
        }
    }
}

# API配置选项 这里如果出现没有login先假假的挂上VPN然后login
API_CONFIGS = {
    "8":{# 88_f7a2da298f9dfb7a5dcfdad20495fef92cb1fc29adac81a6bfdf4fb6bd5e5797
        "name":"闲鱼-88 code API-kiro 逆向 1.7 倍率", 
        "api_url": "https://www.88code.ai/api", 
        "api_key": "88_58e17e881522befb6d1019dcb6b9e666520962c94833b063e1907006facf2364"
    },
    "9":{
        "name": "闲鱼-鸭子code",
        "api_url": "https://jp.duckcoding.com",
        "api_key": "sk-JPqX8PDYXsizlLQEDBJKYtVImdmjoTUGnxWTPHPdVmqgG07b"
    },
   "10":{
        "name":"闲鱼-88 code API-claude max 2.5 倍率", 
        "api_url": "https://www.88code.ai/api", 
        "api_key": "88_1c9a0d1a69899c8ca2cb99bd7278fac04d9bf609b0181885a9b3c753cfc14c6f"
    },
    "11":{
        "name":"闲鱼-augmunt-0.64美金",
        "api_url": "https://hk1.augmunt.com",
        "api_key": "ut_9d611b94821541c58b2891d9"
    },
    "12":{
        "name":"闲鱼-augmunt-kiro-0.2美金",
        "api_url": "https://hk1.augmunt.com",
        "api_key": "ut_b5ad410a81084d4ab10839ae"
    }
}

def get_codex_auth_path():
    """获取Codex认证文件路径"""
    home = Path.home()
    auth_path = home / ".codex" / "auth.json"
    return auth_path

def get_codex_config_path():
    """获取Codex config.toml文件路径"""
    home = Path.home()
    config_path = home / ".codex" / "config.toml"
    return config_path

def get_claude_config_path():
    """获取Claude配置文件路径"""
    home = Path.home()
    config_path = home / ".claude.json"

    # 检查CLAUDE_CONFIG_DIR环境变量
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if config_dir:
        config_path = Path(config_dir) / ".claude.json"

    return config_path

def load_current_config():
    """加载当前Claude配置"""
    config_path = get_claude_config_path()
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"警告：无法读取配置文件 {config_path}: {e}")
        return {}

def save_config(config):
    """保存Claude配置"""
    config_path = get_claude_config_path()
    
    # 确保配置目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"配置已保存到: {config_path}")
        return True
    except IOError as e:
        print(f"错误：无法保存配置文件: {e}")
        return False

def choose_api_type():
    """选择API类型"""
    print("\n" + "="*50)
    print("API 配置选择器")
    print("="*50)
    print()
    print("1. Claude API")
    print("2. OpenAI API")
    print("0. 退出")
    print()

    while True:
        choice = input("请选择要配置的API类型 (0-2): ").strip()

        if choice == "0":
            return None
        elif choice == "1":
            return "claude"
        elif choice == "2":
            return "openai"
        else:
            print("无效选择，请输入 0-2")

def display_claude_menu():
    """显示Claude API选择菜单"""
    print("\n" + "="*50)
    print("Claude Code API 端点选择器")
    print("="*50)
    print()

    for key, config in API_CONFIGS.items():
        print(f"{key}. {config['name']}")
        print(f"   URL: {config['api_url']}")
        print(f"   密钥: {config['api_key'][:20]}...")
        print()

    print("0. 退出不修改")
    print()

def display_openai_menu():
    """显示OpenAI API选择菜单"""
    print("\n" + "="*50)
    print("OpenAI API 配置选择器")
    print("="*50)
    print()

    for key, config in OPENAI_API_CONFIGS.items():
        if config:  # 跳过空配置
            print(f"{key}. 配置 {key}")
            if config.get("OPENAI_API_KEY"):
                print(f"   API Key: {config['OPENAI_API_KEY'][:20]}...")
            if config.get("tokens"):
                print(f"   已配置 tokens")
            print()

    print("0. 退出不修改")
    print()

def get_user_choice(api_type):
    """获取用户选择"""
    configs = API_CONFIGS if api_type == "claude" else OPENAI_API_CONFIGS

    while True:
        choice = input("请选择配置 (0 退出): ").strip()

        if choice == "0":
            return None
        elif choice in configs:
            if api_type == "openai" and not configs[choice]:
                print(f"配置 {choice} 为空，请选择其他配置")
                continue
            return choice
        else:
            print(f"无效选择，请重新输入")

def set_environment_variable_windows(name, value):
    """在Windows系统中设置持久化环境变量"""
    try:
        # 打开当前用户环境变量注册表项
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
        
        # 设置环境变量
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        
        # 关闭注册表项
        winreg.CloseKey(key)
        
        # 通知系统环境变量已更改
        import ctypes
        from ctypes import wintypes
        
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        
        result = ctypes.c_long()
        SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
        SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
        
        return True
    except Exception as e:
        print(f"设置Windows环境变量失败: {e}")
        return False

def set_environment_variable_unix(name, value):
    """在Unix/Linux系统中设置环境变量到shell配置文件"""
    try:
        home = Path.home()
        shell_configs = [
            home / ".bashrc",
            home / ".zshrc", 
            home / ".profile"
        ]
        
        env_line = f'export {name}="{value}"\n'
        
        # 尝试找到存在的shell配置文件
        config_file = None
        for config in shell_configs:
            if config.exists():
                config_file = config
                break
        
        # 如果没有找到，创建.bashrc
        if not config_file:
            config_file = home / ".bashrc"
        
        # 读取现有内容
        existing_lines = []
        if config_file.exists():
            with open(config_file, 'r') as f:
                existing_lines = f.readlines()
        
        # 检查是否已存在该环境变量
        var_exists = False
        for i, line in enumerate(existing_lines):
            if line.strip().startswith(f'export {name}='):
                existing_lines[i] = env_line
                var_exists = True
                break
        
        # 如果不存在，添加到末尾
        if not var_exists:
            existing_lines.append(env_line)
        
        # 写回文件
        with open(config_file, 'w') as f:
            f.writelines(existing_lines)
        
        print(f"已将环境变量添加到: {config_file}")
        print(f"请重新启动终端或运行: source {config_file}")
        
        return True
    except Exception as e:
        print(f"设置Unix环境变量失败: {e}")
        return False

def remove_proxy_variables():
    """检测并移除HTTP_PROXY和HTTPS_PROXY环境变量"""
    proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]
    removed_vars = []
    
    print("\n检测代理环境变量...")
    
    for var_name in proxy_vars:
        if var_name in os.environ:
            removed_vars.append((var_name, os.environ[var_name]))
            del os.environ[var_name]
            print(f"已移除环境变量: {var_name}={os.environ.get(var_name, 'None')}")
    
    if removed_vars:
        print(f"✅ 已移除 {len(removed_vars)} 个代理环境变量")
        for var_name, var_value in removed_vars:
            print(f"   {var_name}: {var_value}")
    else:
        print("✅ 未检测到代理环境变量")
    
    return removed_vars

def check_and_remove_anthropic_api_key():
    """检测并询问是否删除ANTHROPIC_API_KEY环境变量"""
    api_key_name = "ANTHROPIC_API_KEY"
    
    print("\n检测 ANTHROPIC_API_KEY 环境变量...")
    
    if api_key_name in os.environ:
        current_value = os.environ[api_key_name]
        print(f"⚠️ 检测到已存在的 {api_key_name}")
        print(f"当前值: {current_value[:20]}..." if len(current_value) > 20 else f"当前值: {current_value}")
        
        remove_choice = input(f"\n是否删除 {api_key_name} 环境变量? (y/N): ").strip().lower()
        
        if remove_choice in ['y', 'yes', '是']:
            # 从当前会话移除
            del os.environ[api_key_name]
            print(f"✅ 已从当前会话移除 {api_key_name}")
            
            # 尝试从系统永久删除
            try:
                if sys.platform == "win32":
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
                    try:
                        winreg.DeleteValue(key, api_key_name)
                        print(f"✅ 已从系统环境变量永久删除 {api_key_name}")
                        
                        # 通知系统环境变量已更改
                        import ctypes
                        HWND_BROADCAST = 0xFFFF
                        WM_SETTINGCHANGE = 0x001A
                        SMTO_ABORTIFHUNG = 0x0002
                        result = ctypes.c_long()
                        SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
                        SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
                    except FileNotFoundError:
                        print(f"ℹ️ 系统环境变量中未找到 {api_key_name}")
                    finally:
                        winreg.CloseKey(key)
                else:
                    # Unix/Linux 系统 - 自动从shell配置文件删除
                    home = Path.home()
                    shell_configs = [
                        home / ".bashrc",
                        home / ".zshrc",
                        home / ".profile"
                    ]
                    
                    deleted_from_files = []
                    for config_file in shell_configs:
                        if config_file.exists():
                            try:
                                # 读取文件内容
                                with open(config_file, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                
                                # 过滤掉包含该环境变量的行
                                original_count = len(lines)
                                filtered_lines = [line for line in lines if not (
                                    f'export {api_key_name}=' in line or
                                    f'{api_key_name}=' in line
                                )]
                                
                                # 如果有行被删除，写回文件
                                if len(filtered_lines) < original_count:
                                    with open(config_file, 'w', encoding='utf-8') as f:
                                        f.writelines(filtered_lines)
                                    deleted_from_files.append(str(config_file))
                            except Exception as e:
                                print(f"⚠️ 处理 {config_file} 时出错: {e}")
                    
                    if deleted_from_files:
                        print(f"✅ 已从以下文件中删除 {api_key_name}:")
                        for file_path in deleted_from_files:
                            print(f"   - {file_path}")
                        print(f"ℹ️ 请重新启动终端或运行 'source <配置文件>' 使更改生效")
                    else:
                        print(f"ℹ️ 在常见的 shell 配置文件中未找到 {api_key_name}")
            except Exception as e:
                print(f"⚠️ 删除系统环境变量时出错: {e}")
            
            return True
        else:
            print(f"ℹ️ 保留 {api_key_name} 环境变量")
            return False
    else:
        print(f"✅ 未检测到 {api_key_name} 环境变量")
        return False

def set_persistent_environment_variable(name, value):
    """设置持久化环境变量"""
    if sys.platform == "win32":
        return set_environment_variable_windows(name, value)
    else:
        return set_environment_variable_unix(name, value)

def print_anthropic_env_status():
    """Print the current Claude-related environment variables."""
    print(f"Current session ANTHROPIC_AUTH_TOKEN: {os.environ.get('ANTHROPIC_AUTH_TOKEN')}")
    print(f"Current session ANTHROPIC_API_KEY: {os.environ.get('ANTHROPIC_API_KEY')}")
    print(f"Current session ANTHROPIC_BASE_URL: {os.environ.get('ANTHROPIC_BASE_URL')}")

def save_openai_config(config_data):
    """保存OpenAI配置到auth.json"""
    auth_path = get_codex_auth_path()

    # 确保目录存在
    auth_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(auth_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"配置已保存到: {auth_path}")
        return True
    except IOError as e:
        print(f"错误：无法保存配置文件: {e}")
        return False

def save_codex_config_toml(config_data):
    """保存config.toml配置"""
    config_path = get_codex_config_path()

    # 确保目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # 将配置转换为TOML格式
        toml_content = ""

        # 添加顶级配置
        for key, value in config_data.items():
            if key != "model_providers":
                if isinstance(value, bool):
                    toml_content += f'{key} = {str(value).lower()}\n'
                elif isinstance(value, str):
                    toml_content += f'{key} = "{value}"\n'
                else:
                    toml_content += f'{key} = {value}\n'

        toml_content += "\n"

        # 添加model_providers配置
        if "model_providers" in config_data:
            for provider_name, provider_config in config_data["model_providers"].items():
                toml_content += f"[model_providers.{provider_name}]\n"
                for key, value in provider_config.items():
                    if isinstance(value, bool):
                        toml_content += f'{key} = {str(value).lower()}\n'
                    elif isinstance(value, str):
                        toml_content += f'{key} = "{value}"\n'
                    else:
                        toml_content += f'{key} = {value}\n'

        # 写入文件
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(toml_content)

        print(f"config.toml已保存到: {config_path}")
        return True
    except IOError as e:
        print(f"错误：无法保存config.toml文件: {e}")
        return False

def update_openai_config(choice):
    """更新OpenAI配置"""
    if choice is None:
        print("未修改配置，退出。")
        return False

    selected_config = OPENAI_API_CONFIGS[choice]

    print(f"\n正在应用OpenAI配置 {choice}...")

    # 准备auth.json的内容
    auth_config = {}
    if selected_config.get("OPENAI_API_KEY") is not None:
        auth_config["OPENAI_API_KEY"] = selected_config["OPENAI_API_KEY"]
    else:
        auth_config["OPENAI_API_KEY"] = None

    # 如果有tokens，添加到auth.json
    if selected_config.get("tokens"):
        auth_config.update(selected_config["tokens"])
        if selected_config.get("last_refresh"):
            auth_config["last_refresh"] = selected_config["last_refresh"]

    # 保存配置到auth.json
    if save_openai_config(auth_config):
        print(f"\n✅ OpenAI auth.json配置已更新")

        # 如果有环境变量需要设置
        if selected_config.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = selected_config["OPENAI_API_KEY"]
            print(f"当前会话 OPENAI_API_KEY 已设置")

        # 设置额外的环境变量（如CRS_OAI_KEY）
        if selected_config.get("env_vars"):
            print("\n正在设置持久化环境变量...")
            for env_name, env_value in selected_config["env_vars"].items():
                if set_persistent_environment_variable(env_name, env_value):
                    os.environ[env_name] = env_value
                    print(f"✅ {env_name} 已设置")
                else:
                    print(f"⚠️ {env_name} 设置失败")

        # 如果有config.toml配置，自动保存
        if selected_config.get("config_toml"):
            print("\n正在更新 config.toml 文件...")
            if save_codex_config_toml(selected_config["config_toml"]):
                print("✅ config.toml 已自动更新")
            else:
                print("⚠️ config.toml 更新失败，请手动配置")

        return True

    return False

def update_claude_config(choice):
    """更新Claude API配置"""
    if choice is None:
        print("未修改配置，退出。")
        return False

    selected_config = API_CONFIGS[choice]

    # 加载当前配置
    current_config = load_current_config()

    # 更新API URL
    current_config["customApiUrl"] = selected_config["api_url"]

    # 保存配置
    if save_config(current_config):
        print(f"\n✅ 已切换到: {selected_config['name']}")
        print(f"API URL: {selected_config['api_url']}")

        # 设置当前进程环境变量
        os.environ["ANTHROPIC_AUTH_TOKEN"] = selected_config["api_key"]
        os.environ["ANTHROPIC_BASE_URL"] = selected_config["api_url"]

        # 设置持久化环境变量
        print("正在设置持久化环境变量...")
        auth_token_success = set_persistent_environment_variable("ANTHROPIC_AUTH_TOKEN", selected_config["api_key"])
        base_url_success = set_persistent_environment_variable("ANTHROPIC_BASE_URL", selected_config["api_url"])

        print_anthropic_env_status()

        if auth_token_success and base_url_success:
            print("✅ 环境变量已持久化设置")
        else:
            print("⚠️ 部分环境变量设置失败，但当前会话仍可使用")

        return True

    return False

def launch_claude_code():
    """启动Claude Code"""
    print("\n正在启动 Claude Code...")
    
    try:
        # 在Windows上启动Claude Code
        if sys.platform == "win32":
            subprocess.run(["claude"], check=True)
        else:
            subprocess.run(["claude"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"启动Claude Code失败: {e}")
    except FileNotFoundError:
        print("未找到 'claude' 命令，请确保Claude Code已正确安装")

def main():
    """主函数"""
    try:
        # 移除代理环境变量
        remove_proxy_variables()
        
        # 检测并询问是否删除ANTHROPIC_API_KEY
        check_and_remove_anthropic_api_key()

        # 选择API类型
        api_type = choose_api_type()

        if api_type is None:
            print("退出程序。")
            return

        # 根据API类型显示对应菜单
        if api_type == "claude":
            display_claude_menu()
        else:  # openai
            display_openai_menu()

        # 获取用户选择
        choice = get_user_choice(api_type)

        # 更新配置
        config_updated = False
        if api_type == "claude":
            config_updated = update_claude_config(choice)
        else:  # openai
            config_updated = update_openai_config(choice)

        # 如果是Claude配置且成功，询问是否启动Claude Code
        if config_updated and api_type == "claude":
            launch_choice = input("\n是否现在启动 Claude Code? (y/N): ").strip().lower()
            if launch_choice in ['y', 'yes', '是']:
                # 设置API密钥和基础URL环境变量
                if choice:
                    selected_config = API_CONFIGS[choice]
                    os.environ["ANTHROPIC_AUTH_TOKEN"] = selected_config["api_key"]
                    os.environ["ANTHROPIC_BASE_URL"] = selected_config["api_url"]
                    print_anthropic_env_status()

                launch_claude_code()

    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
