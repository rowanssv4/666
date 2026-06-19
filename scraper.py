import requests
import base64
import re
import urllib.parse
import json
import datetime
import socket

# 动态生成日期
bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
date_str = bj_time.strftime("%Y%m%d")      
year_str = bj_time.strftime("%Y")          
month_str = bj_time.strftime("%m")         

# 仅保留标准的明文或 Base64 订阅源，剔除纯 YAML 源（避免格式污染）
SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    f"https://wanzhuanmi.cczzuu.top/node/{date_str}.txt",
    f"https://oss.oneclash.cc/{year_str}/{month_str}/{date_str}.txt",
    "https://raw.githubusercontent.com/shaoyouvip/free/refs/heads/main/base64.txt",
    "https://Nmnb6H.tosslk.xyz/54759c411d85fcfc170e8882ec60b863",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub2.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub3.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub4.txt"
]

COUNTRY_MAP = {
    '香港': 'HK', 'HK': 'HK', 'HONG KONG': 'HK',
    '台湾': 'TW', 'TW': 'TW', 'TAIWAN': 'TW',
    '日本': 'JP', 'JP': 'JP', 'JAPAN': 'JP',
    '美国': 'US', 'US': 'US', 'UNITED STATES': 'US',
    '韩国': 'KR', 'KR': 'KR', 'KOREA': 'KR',
    '新加坡': 'SG', 'SG': 'SG', 'SINGAPORE': 'SG',
    '英国': 'UK', 'GB': 'UK', 'UNITED KINGDOM': 'UK',
    '德国': 'DE', 'GERMANY': 'DE',
}

def detect_country(raw_name):
    upper_name = str(raw_name).upper()
    for kw, code in COUNTRY_MAP.items():
        if kw in upper_name:
            return code
    return "🚀"

def safe_b64decode(s):
    s = s.strip()
    missing_padding = len(s) % 4
    if missing_padding:
        s += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(s).decode('utf-8', errors='ignore')
    except:
        return ""

def fetch_and_decode():
    raw_configs = []
    # 定义合法的协议前缀
    valid_protocols = ("vmess://", "vless://", "ss://", "trojan://", "hysteria2://", "hy2://")
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                content = res.text.strip()
                # 如果没有通用协议头且长度很长，尝试进行 base64 解码
                if "://" not in content and len(content) > 20:
                    decoded = safe_b64decode(content)
                    lines = decoded.splitlines()
                else:
                    lines = content.splitlines()
                
                for line in lines:
                    line_str = line.strip()
                    # 极其严格的前置过滤：必须以合法协议开头，彻底干掉 YAML 杂质行
                    if line_str.startswith(valid_protocols):
                        raw_configs.append(line_str)
        except Exception as e:
            print(f"跳过无法访问的源: {url}")
    return list(set(raw_configs))

def check_port(host, port, timeout=2):
    try:
        port = int(port)
        # 排除不合法的端口范围
        if not (0 < port <= 65535):
            return False
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def parse_and_validate_node(node):
    try:
        if node.startswith("vmess://"):
            b64_data = node.replace("vmess://", "")
            json_str = safe_b64decode(b64_data)
            if json_str:
                config = json.loads(json_str)
                # 核心测速过滤
                if check_port(config.get("add"), config.get("port")):
                    return True, {"type": "vmess", "data": config}
        
        elif node.startswith(("vless://", "trojan://", "ss://", "hysteria2://", "hy2://")):
            # 分离配置与备注
            base_part = node.split("#")[0]
            # 提取连接部分
            server_part = base_part.split("@")[-1].split("?")[0]
            if ":" in server_part:
                parts = server_part.split(":")
                host = parts[0]
                port = parts[1].split("/")[0]  # 防止由于残余斜杠引发转换错误
                if check_port(host, port):
                    return True, {"type": "uri", "data": node}
    except Exception as e:
        pass
    return False, None

def rename_and_filter_nodes(nodes):
    final_nodes = []
    counter = 1
    
    # 强制注入首行提示死节点
    notice_name = "📢-来自公开的免费节点源 仅作为学习参考"
    notice_node = f"vless://unusable-uuid@127.0.0.1:8888?encryption=none&security=none#{urllib.parse.quote(notice_name)}"
    final_nodes.append(notice_node)

    print("开始检测节点可用性...")
    for node in nodes:
        try:
            is_alive, node_info = parse_and_validate_node(node)
            if not is_alive:
                continue  
                
            if node_info["type"] == "vmess":
                config = node_info["data"]
                old_ps = config.get("ps", "")
                country = detect_country(old_ps)
                config["ps"] = f"{country}-Rowanss节点分享-{counter:03d}"
                new_b64 = base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8')
                final_nodes.append(f"vmess://{new_b64}")
                counter += 1
                
            elif node_info["type"] == "uri":
                orig_node = node_info["data"]
                if "#" in orig_node:
                    base_url, old_ps_encoded = orig_node.split("#", 1)
                    old_ps = urllib.parse.unquote(old_ps_encoded)
                    country = detect_country(old_ps)
                else:
                    base_url = orig_node
                    country = "🚀"
                
                new_ps = f"{country}-Rowanss节点分享-{counter:03d}"
                final_nodes.append(f"{base_url}#{urllib.parse.quote(new_ps)}")
                counter += 1
        except Exception as e:
            # 内部单条异常时绝不抛出，直接跳过处理下一条
            continue
            
    return final_nodes

if __name__ == "__main__":
    try:
        raw_nodes = fetch_and_decode()
        processed_nodes = rename_and_filter_nodes(raw_nodes)
        
        # 最终写入文件
        joined_nodes = "\n".join(processed_nodes)
        with open("nodes.txt", "w", encoding="utf-8") as f:
            f.write(joined_nodes)
            
        b64_encoded = base64.b64encode(joined_nodes.encode('utf-8')).decode('utf-8')
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(b64_encoded)
            
        print(f"写入完毕。共成功输出 {len(processed_nodes)} 个节点（含公告）。")
    except Exception as main_err:
        print(f"主进程拦截异常，进行兜底保活: {main_err}")
