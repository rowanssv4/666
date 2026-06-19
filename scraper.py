import sys
import os
import datetime
import traceback
import requests
import base64
import re
import urllib.parse
import json

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

print("==================================================")
print(f"📋 运行报告生成时间: {(datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
print("==================================================")

def get_date_strings(days_ago=0):
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8) - datetime.timedelta(days=days_ago)
    return {
        "ymd": bj_time.strftime("%Y%m%d"),
        "y": bj_time.strftime("%Y"),
        "m": bj_time.strftime("%m"),
        "d": bj_time.strftime("%d"),
        "slash_ym": bj_time.strftime("%Y/%m")
    }

t0 = get_date_strings(0)
t1 = get_date_strings(1)

SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha.txt",
    f"https://freenode.yoyapai.com/{t0['slash_ym']}/{t0['d']}-yoyapai.com-ssr-v2ray-vpn-mianfei-jiedian.txt",
    f"https://freenode.yoyapai.com/{t1['slash_ym']}/{t1['d']}-yoyapai.com-ssr-v2ray-vpn-mianfei-jiedian.txt",
    f"https://oss.oneclash.cc/{t0['slash_ym']}/{t0['ymd']}.txt",
    f"https://oss.oneclash.cc/{t1['slash_ym']}/{t1['ymd']}.txt"
]

# === 超大规模国家/地区指纹识别矩阵 ===
# 只要备注中包含任何一个关键词(中文、英文、简写、Emoji)，就会被精准拦截归类
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
    'CN': ['中国', 'CHINA', '🇨🇳', 'CN', '回国', '回国']
}

def detect_country_advanced(raw_name):
    """进阶指纹匹配引擎"""
    if not raw_name:
        return "UNK"
        
    upper_name = str(raw_name).upper().strip()
    
    # 1. 遍历大规模关键字词典进行匹配
    for code, keywords in COUNTRY_KEYWORDS.items():
        for kw in keywords:
            # 加强匹配边界，防止类似 "VLESS" 触发 "ES" 的情况
            if kw.isalpha() and len(kw) <= 2:
                # 如果是2位英文字符简写，必须形成独立的单词边界或特殊标记
                if re.search(r'\b' + kw + r'\b', upper_name) or f"-{kw}" in upper_name or f"{kw}-" in upper_name:
                    return code
            elif kw in upper_name:
                return code
                
    # 2. 高智能分析兜底：如果完全没匹配到，提取节点前4个有效字符作为前缀，绝不盲目归类
    # 清洗掉干扰字符
    clean_name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-7]', '', upper_name)
    if clean_name:
        return clean_name[:4]
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
    node_pattern = re.compile(r'^(vmess|vless|ss|trojan|hysteria2|hy2)://[^\s]+')
    
    print(f"[INFO] 正在对 {len(SOURCES)} 个筛选过的高质量源发起全自动多路由并发爬取...")
    for index, url in enumerate(SOURCES, 1):
        try:
            res = requests.get(url, timeout=10)
            print(f" -> [{index:02d}] 探测源: {url} | 状态码: {res.status_code}")
            if res.status_code == 200:
                content = res.text.strip()
                if "<html" in content.lower() or "<doctype" in content.lower():
                    continue
                    
                if "://" not in content and len(content) > 20:
                    decoded = safe_b64decode(content)
                    lines = decoded.splitlines()
                else:
                    lines = content.splitlines()
                
                sub_counter = 0
                for line in lines:
                    line_str = line.strip()
                    if node_pattern.match(line_str):
                        raw_configs.append(line_str)
                        sub_counter += 1
                print(f"    └── 成功解析到有效节点: {sub_counter} 条")
        except Exception as e:
            print(f"    └── 连接超时或未更新，已自动跳过: {e}")
            
    return list(set(raw_configs))

def process_and_rename(nodes):
    final_nodes = []
    counter = 1
    
    print(f"[INFO] 正在注入置顶公告，并规范化重命名 {len(nodes)} 个去重节点...")
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
                    country = detect_country_advanced(old_ps)
                    config["ps"] = f"{country}-Rowanss节点分享-{counter:03d}"
                    new_b64 = base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8')
                    final_nodes.append(f"vmess://{new_b64}")
                    counter += 1
                    
            elif node.startswith(("vless://", "trojan://", "ss://", "hysteria2://", "hy2://")):
                if "#" in node:
                    base_url, old_ps_encoded = node.split("#", 1)
                    old_ps = urllib.parse.unquote(old_ps_encoded)
                    country = detect_country_advanced(old_ps)
                else:
                    base_url = node
                    country = "🚀"
                
                new_ps = f"{country}-Rowanss节点分享-{counter:03d}"
                final_nodes.append(f"{base_url}#{urllib.parse.quote(new_ps)}")
                counter += 1
        except Exception:
            continue
            
    return final_nodes

if __name__ == "__main__":
    try:
        raw_list = fetch_and_decode()
        print(f"[INFO] 交叉去重过滤结束，全池留存净节点: {len(raw_list)} 条。")
        
        output_list = process_and_rename(raw_list)
        
        print("[INFO] 正在打包同步输出 sub.txt 与 nodes.txt...")
        joined_data = "\n".join(output_list)
        with open("nodes.txt", "w", encoding="utf-8") as f:
            f.write(joined_data)
            
        b64_data = base64.b64encode(joined_data.encode('utf-8')).decode('utf-8')
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(b64_data)
            
        print(f"[🎉 SUCCESS] 核心清洗管道全部跑通。最终可用节点总数: {len(output_list)} 个。")
        
    except Exception as fatal_err:
        print("\n💥💥💥 [FATAL ERROR] 遭遇未捕捉的主流级系统崩溃 💥💥💥")
        traceback.print_exc()
        sys.exit(1)
