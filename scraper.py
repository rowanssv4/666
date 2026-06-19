import requests
import base64
import re
import urllib.parse
import json

# 你提供的 10 个优质高频更新源
SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://wanzhuanmi.cczzuu.top/node/20260619.txt",
    "https://oss.oneclash.cc/2026/06/20260619.txt",
    "https://raw.githubusercontent.com/shaoyouvip/free/refs/heads/main/base64.txt",
    "https://Nmnb6H.tosslk.xyz/54759c411d85fcfc170e8882ec60b863",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub2.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub3.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub4.txt"
    # 注：网页型源(如freeclashnode)由于每天URL带有日期或动态参数，建议手动定期更新或改用公开的订阅源
]

# 常见国家/地区关键字映射（用于从原始节点名中洗出国家）
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
    """从节点的原始备注名里匹配国家/地区"""
    upper_name = raw_name.upper()
    for kw, code in COUNTRY_MAP.items():
        if kw in upper_name:
            return code
    return "🚀" # 未捕获到时默认的符号或写"未知"

def safe_b64decode(s):
    """安全 Base64 解码"""
    s = s.strip()
    # 补齐等号
    missing_padding = len(s) % 4
    if missing_padding:
        s += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(s).decode('utf-8', errors='ignore')
    except:
        return ""

def fetch_and_decode():
    """抓取源并统一解码为明文行"""
    raw_configs = []
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                content = res.text.strip()
                # 判断是否是 base64 加密订阅
                if "://" not in content and len(content) > 20:
                    decoded = safe_b64decode(content)
                    lines = decoded.splitlines()
                else:
                    lines = content.splitlines()
                
                for line in lines:
                    if "://" in line:
                        raw_configs.append(line.strip())
        except Exception as e:
            print(f"读取源失败 {url}: {e}")
    return list(set(raw_configs))

def rename_nodes(nodes):
    """核心重命名逻辑"""
    renamed_nodes = []
    counter = 1
    
    for node in nodes:
        try:
            if node.startswith("vmess://"):
                # vmess 的后半部分通常是 base64 编码的 json
                b64_data = node.replace("vmess://", "")
                json_str = safe_b64decode(b64_data)
                if json_str:
                    config = json.loads(json_str)
                    old_ps = config.get("ps", "")
                    country = detect_country(old_ps)
                    # 重新命名 ps
                    config["ps"] = f"{country}-Rowanss节点分享-{counter:03d}"
                    new_b64 = base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8')
                    renamed_nodes.append(f"vmess://{new_b64}")
                    counter += 1
                    
            elif node.startswith(("vless://", "trojan://", "ss://")):
                # 这些协议的备注名通常在 URL 末尾的 # 后面
                if "#" in node:
                    base_url, old_ps_encoded = node.split("#", 1)
                    old_ps = urllib.parse.unquote(old_ps_encoded)
                    country = detect_country(old_ps)
                else:
                    base_url = node
                    country = "🚀"
                
                new_ps = f"{country}-Rowanss节点分享-{counter:03d}"
                new_ps_encoded = urllib.parse.quote(new_ps)
                renamed_nodes.append(f"{base_url}#{new_ps_encoded}")
                counter += 1
                
            elif node.startswith("hysteria2://") or node.startswith("hy2://"):
                # Hysteria2 同上，也是在 # 后面
                if "#" in node:
                    base_url, old_ps_encoded = node.split("#", 1)
                    old_ps = urllib.parse.unquote(old_ps_encoded)
                    country = detect_country(old_ps)
                else:
                    base_url = node
                    country = "🚀"
                new_ps = f"{country}-Rowanss节点分享-{counter:03d}"
                renamed_nodes.append(f"{base_url}#{urllib.parse.quote(new_ps)}")
                counter += 1
            else:
                # 其他不支持解析的直接保留原样
                renamed_nodes.append(node)
        except Exception as e:
            # 解析单条失败则保留原节点不崩溃
            renamed_nodes.append(node)
            
    return renamed_nodes

if __name__ == "__main__":
    print("开始从各大 Agent 推荐源抓取免费节点...")
    raw_nodes = fetch_and_decode()
    print(f"共抓取到 {len(raw_nodes)} 个原始节点。开始过滤并规范化重命名...")
    
    final_nodes = rename_nodes(raw_nodes)
    
    # 保存结果
    joined_nodes = "\n".join(final_nodes)
    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write(joined_nodes)
        
    b64_encoded = base64.b64encode(joined_nodes.encode('utf-8')).decode('utf-8')
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(b64_encoded)
        
    print(f"处理完成！最终可用节点数: {len(final_nodes)}。已生成 nodes.txt 和 sub.txt")
