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

# 优化源：如果动态源不存在，try 块会自动跳过，不影响整体运行
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
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                content = res.text.strip()
                if "://" not in content and len(content) > 20:
                    decoded = safe_b64decode(content)
                    lines = decoded.splitlines()
                else:
                    lines = content.splitlines()
                
                for line in lines:
                    if "://" in line:
                        raw_configs.append(line.strip())
        except Exception as e:
            print(f"跳过失效或未更新的源 {url}")
    return list(set(raw_configs))

def check_port(host, port, timeout=2):
    try:
        port = int(port)
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
                # 极其宽松的测速：如果由于任何原因测速失败，也可以考虑先不放行，但这里确保测速逻辑不崩
                if check_port(config.get("add"), config.get("port")):
                    return True, {"type": "vmess", "data": config}
        
        elif node.startswith(("vless://", "trojan://", "ss://", "hysteria2://", "hy2://")):
            base_part = node.split("#")[0]
            server_part = base_part.split("@")[-1].split("?")[0]
            if ":" in server_part:
                host, port = server_part.split(":")[:2]
                port = port.split("/")[0]
                if check_port(host, port):
                    return True, {"type": "uri", "data": node}
    except Exception as e:
        pass
    return False, None

def rename_and_filter_nodes(nodes):
    final_nodes = []
    counter = 1
    
    # 【保证第一行绝对存在】强制注入公告节点
    notice_name = "📢-来自公开的免费节点源 仅作为学习参考"
    notice_node = f"vless://unusable-uuid@127.0.0.1:8888?encryption=none&security=none#{urllib.parse.quote(notice_name)}"
    final_nodes.append(notice_node)

    print("开始检测节点可用性...")
    for node in nodes:
        try:
            is_alive, node_info = parse_and_validate_node(node)
            if not is_alive:
                continue  # 过滤死节点
                
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
            # 即使某一条解析爆了，也继续循环，绝不让整个脚本中断
            continue
            
    return final_nodes

if __name__ == "__main__":
    raw_nodes = fetch_and_decode()
    processed_nodes = rename_and_filter_nodes(raw_nodes)
    
    # 最终写入文件
    joined_nodes = "\n".join(processed_nodes)
    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write(joined_nodes)
        
    b64_encoded = base64.b64encode(joined_nodes.encode('utf-8')).decode('utf-8')
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(b64_encoded)
        
    print("写入完毕。")
