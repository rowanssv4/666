import requests
import base64
import re
import urllib.parse
import json
import datetime

def get_date_strings(days_ago=0):
    """获取北京时间及过去几天的日期字符串"""
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8) - datetime.timedelta(days=days_ago)
    return bj_time.strftime("%Y%m%d"), bj_time.strftime("%Y"), bj_time.strftime("%m")

# 获取今天和昨天的日期，防止动态源 404
d_today, y_today, m_today = get_date_strings(0)
d_yesterday, y_yesterday, m_yesterday = get_date_strings(1)

SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    f"https://wanzhuanmi.cczzuu.top/node/{d_today}.txt",
    f"https://oss.oneclash.cc/{y_today}/{m_today}/{d_today}.txt",
    f"https://wanzhuanmi.cczzuu.top/node/{d_yesterday}.txt",
    f"https://oss.oneclash.cc/{y_yesterday}/{m_yesterday}/{d_yesterday}.txt",
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
    # 严格匹配标准节点链接前缀
    node_pattern = re.compile(r'^(vmess|vless|ss|trojan|hysteria2|hy2)://[^\s]+')
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                content = res.text.strip()
                if "<html" in content.lower() or "<doctype" in content.lower():
                    continue
                    
                if "://" not in content and len(content) > 20:
                    decoded = safe_b64decode(content)
                    lines = decoded.splitlines()
                else:
                    lines = content.splitlines()
                
                for line in lines:
                    line_str = line.strip()
                    if node_pattern.match(line_str):
                        raw_configs.append(line_str)
        except Exception:
            pass
    return list(set(raw_configs))

def rename_nodes_all(nodes):
    final_nodes = []
    counter = 1
    
    # 强制注入首行提示死节点
    notice_name = "📢-来自公开的免费节点源 仅作为学习参考"
    notice_node = f"vless://unusable-uuid@127.0.0.1:8888?encryption=none&security=none#{urllib.parse.quote(notice_name)}"
    final_nodes.append(notice_node)

    for node in nodes:
        try:
            if node.startswith("vmess://"):
                b64_data = node.replace("vmess://", "")
                json_str = safe_b64decode(b64_data)
                if json_str:
                    config = json.loads(json_str)
                    old_ps = config.get("ps", "")
                    country = detect_country(old_ps)
                    config["ps"] = f"{country}-Rowanss节点分享-{counter:03d}"
                    new_b64 = base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8')
                    final_nodes.append(f"vmess://{new_b64}")
                    counter += 1
                    
            elif node.startswith(("vless://", "trojan://", "ss://", "hysteria2://", "hy2://")):
                if "#" in node:
                    base_url, old_ps_encoded = node.split("#", 1)
                    old_ps = urllib.parse.unquote(old_ps_encoded)
                    country = detect_country(old_ps)
                else:
                    base_url = node
                    country = "🚀"
                
                new_ps = f"{country}-Rowanss节点分享-{counter:03d}"
                final_nodes.append(f"{base_url}#{urllib.parse.quote(new_ps)}")
                counter += 1
        except Exception:
            # 极个别单条格式奇怪的直接丢弃，不影响大部队
            continue
            
    return final_nodes

if __name__ == "__main__":
    try:
        raw_nodes = fetch_and_decode()
        processed_nodes = rename_nodes_all(raw_nodes)
        
        joined_nodes = "\n".join(processed_nodes)
        with open("nodes.txt", "w", encoding="utf-8") as f:
            f.write(joined_nodes)
            
        b64_encoded = base64.b64encode(joined_nodes.encode('utf-8')).decode('utf-8')
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(b64_encoded)
            
        print(f"全量处理完毕！共导出 {len(processed_nodes)} 个节点（含公告）。")
    except Exception as e:
        print(f"保活拦截: {e}")
