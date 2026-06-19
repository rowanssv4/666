import sys
import os
import datetime
import traceback
import requests
import base64
import re
import urllib.parse
import json
import socket

class Logger(object):
    def __init__(self, filename="report.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger("report.txt")
sys.stderr = sys.stdout

# 1. 动态计算北京时间
bj_now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
time_str = bj_now.strftime('%Y-%m-%d %H:%M:%S')

print("==================================================")
print(f"📋 混合指纹反查级清洗管道启动: {time_str} (北京时间)")
print("==================================================")

def get_date_strings(days_ago=0):
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8) - datetime.timedelta(days=days_ago)
    return {
        "ymd": bj_time.strftime("%Y%m%d"),
        "slash_ym": bj_time.strftime("%Y/%m"),
        "d": bj_time.strftime("%d")
    }

t0, t1 = get_date_strings(0), get_date_strings(1)

SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha.txt",
    f"https://freenode.yoyapai.com/{t0['slash_ym']}/{t0['d']}-yoyapai.com-ssr-v2ray-vpn-mianfei-jiedian.txt",
    f"https://freenode.yoyapai.com/{t1['slash_ym']}/{t1['d']}-yoyapai.com-ssr-v2ray-vpn-mianfei-jiedian.txt",
    f"https://oss.oneclash.cc/{t0['slash_ym']}/{t0['ymd']}.txt",
    f"https://oss.oneclash.cc/{t1['slash_ym']}/{t1['ymd']}.txt"
]

COUNTRY_KEYWORDS = {
    'HK': ['香港', 'HONGKONG', 'HONG KONG', '🇭🇰', 'HK'],
    'TW': ['台湾', 'TAIWAN', '🇹🇼', 'TW'],
    'JP': ['日本', 'JAPAN', '🇯🇵', 'JP'],
    'US': ['美国', 'UNITED STATES', 'AMERICA', '🇺🇸', 'US', '美'],
    'SG': ['新加坡', 'SINGAPORE', '🇸🇬', 'SG', '新'],
    'KR': ['韩国', 'KOREA', '🇰🇷', 'KR', '韩'],
    'UK': ['英国', 'UNITED KINGDOM', 'BRITAIN', '🇬🇧', 'UK'],
    'DE': ['德国', 'GERMANY', '🇩🇪', 'DE'],
    'FR': ['法国', 'FRANCE', '🇫🇷', 'FR'],
    'NL': ['荷兰', 'NETHERLANDS', '🇳🇱', 'NL'],
    'RU': ['俄罗斯', 'RUSSIA', '🇷🇺', 'RU'],
    'CA': ['加拿大', 'CANADA', '🇨🇦', 'CA'],
    'AU': ['澳大利亚', '澳洲', 'AUSTRALIA', '🇦🇺', 'AU'],
    'IN': ['印度', 'INDIA', '🇮🇳', 'IN'],
    'TR': ['土耳其', 'TURKEY', '🇹🇷', 'TR'],
    'VN': ['越南', 'VIETNAM', '🇻🇳', 'VN'],
    'TH': ['泰国', 'THAILAND', '🇹🇭', 'TH'],
    'PH': ['菲律宾', 'PHILIPPINES', '🇵🇭', 'PH'],
    'MY': ['马来西亚', 'MALAYSIA', '🇲🇾', 'MY'],
    'BR': ['巴西', 'BRAZIL', '🇧🇷', 'BR'],
    'ZA': ['南非', 'SOUTH AFRICA', '🇿🇦', 'ZA'],
    'IT': ['意大利', 'ITALY', '🇮🇹', 'IT'],
    'ES': ['西班牙', 'SPAIN', '🇪🇸', 'ES'],
    'CH': ['瑞士', 'SWITZERLAND', '🇨🇭', 'CH'],
    'SE': ['瑞典', 'SWEDEN', '🇸🇪', 'SE'],
    'CN': ['中国', 'CHINA', '🇨🇳', 'CN', '回国']
}

def detect_country_local(upper_name):
    for code, keywords in COUNTRY_KEYWORDS.items():
        for kw in keywords:
            if kw.isalpha() and len(kw) <= 2:
                if re.search(r'\b' + kw + r'\b', upper_name) or f"-{kw}" in upper_name or f"{kw}-" in upper_name:
                    return code
            elif kw in upper_name:
                return code
    clean_name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', upper_name)
    if clean_name:
        return clean_name[:4]
    return "🚀"

def query_third_party_isp(host):
    try:
        target_ip = socket.gethostbyname(host)
        api_url = f"http://ip-api.com/json/{target_ip}?fields=status,countryCode,org,as,proxy"
        res = requests.get(api_url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                country = data.get("countryCode", "🚀")
                org_raw = data.get("org", "") or data.get("as", "")
                org_clean = org_raw.split(" ")[0].split("-")[0].replace(",", "").upper()
                
                isp_tag = ""
                if any(k in org_clean for k in ["CLOUDFLARE", "DIGITALOCEAN", "LINODE", "AMAZON", "AWS", "OVH", "HETZNER"]):
                    isp_tag = "+商业机房"
                elif any(k in org_clean for k in ["TELECOM", "MOBILE", "UNICOM", "CHINANET"]):
                    isp_tag = "+直连原生"
                elif data.get("proxy") is True or "CHG" in org_clean:
                    isp_tag = "+住宅IP"
                else:
                    isp_tag = f"+{org_clean[:6]}"
                    
                return country, isp_tag
    except:
        pass
    return None, None

def extract_host_from_node(node):
    try:
        if node.startswith("vmess://"):
            b64_data = node.replace("vmess://", "")
            missing_padding = len(b64_data) % 4
            if missing_padding: b64_data += '=' * (4 - missing_padding)
            config = json.loads(base64.b64decode(b64_data).decode('utf-8', errors='ignore'))
            return config.get("add"), "vmess", config, str(config.get("ps", "")).upper()
        else:
            base_part = node.split("#")[0]
            server_part = base_part.split("@")[-1].split("?")[0]
            host = server_part.split(":")[0] if ":" in server_part else server_part
            old_ps = ""
            if "#" in node:
                old_ps = urllib.parse.unquote(node.split("#")[1])
            return host, "uri", node, str(old_ps).upper()
    except:
        return None, None, None, ""

def fetch_and_decode():
    raw_configs = []
    node_pattern = re.compile(r'^(vmess|vless|ss|trojan|hysteria2|hy2)://[^\s]+')
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                content = res.text.strip()
                if "<html" in content.lower() or "<doctype" in content.lower():
                    continue
                lines = base64.b64decode(content + '=' * (4 - len(content) % 4)).decode('utf-8', errors='ignore').splitlines() if "://" not in content and len(content) > 20 else content.splitlines()
                for line in lines:
                    if node_pattern.match(line.strip()):
                        raw_configs.append(line.strip())
        except Exception:
            pass
    return list(set(raw_configs))

if __name__ == "__main__":
    try:
        raw_list = fetch_and_decode()
        print(f"[INFO] 原始去重去重终结。池容量: {len(raw_list)} 条。")
        
        final_nodes = []
        counter = 1
        
        # ==================== 🛠️ 核心修改：注入专属双置顶公告 ====================
        notice_1 = "📢 本订阅节点均来自于公开节点源，仅供学习参考"
        notice_2 = f"🔄 订阅最后更新时间：{time_str} (北京时间)"
        
        node_ann_1 = f"vless://unusable-uuid-1@127.0.0.1:8888?encryption=none&security=none#{urllib.parse.quote(notice_1)}"
        node_ann_2 = f"vless://unusable-uuid-2@127.0.0.1:8889?encryption=none&security=none#{urllib.parse.quote(notice_2)}"
        
        final_nodes.append(node_ann_1)  # 第一条公告：免责声明
        final_nodes.append(node_ann_2)  # 第二条公告：实时动态时间
        # =====================================================================
        
        for idx, node in enumerate(raw_list, 1):
            host, ntype, orig_data, upper_ps = extract_host_from_node(node)
            if not host:
                continue
                
            if idx <= 120:
                real_country, real_isp = query_third_party_isp(host)
                country_prefix = real_country if real_country else detect_country_local(upper_ps)
                isp_suffix = real_isp if real_isp else ""
                new_ps = f"{country_prefix}{isp_suffix}-Rowanss节点分享-{counter:03d}"
            else:
                country_prefix = detect_country_local(upper_ps)
                new_ps = f"{country_prefix}-Rowanss节点分享-{counter:03d}"
            
            try:
                if ntype == "vmess":
                    orig_data["ps"] = new_ps
                    new_b64 = base64.b64encode(json.dumps(orig_data).encode('utf-8')).decode('utf-8')
                    final_nodes.append(f"vmess://{new_b64}")
                    counter += 1
                elif ntype == "uri":
                    base_url = orig_data.split("#")[0]
                    final_nodes.append(f"{base_url}#{urllib.parse.quote(new_ps)}")
                    counter += 1
            except:
                continue

        joined_data = "\n".join(final_nodes)
        with open("nodes.txt", "w", encoding="utf-8") as f: f.write(joined_data)
        with open("sub.txt", "w", encoding="utf-8") as f: f.write(base64.b64encode(joined_data.encode('utf-8')).decode('utf-8'))
        print(f"[🎉 SUCCESS] 双管道全自动清洗完成。最终总下发节点: {len(final_nodes)} 个。")
    except Exception:
        sys.exit(0)
