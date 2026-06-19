import sys
import os

print("--- [DEBUG] 脚本进入初始化阶段 ---")

try:
    import requests
    import base64
    import re
    import urllib.parse
    import json
    import datetime
    import traceback
    print("--- [DEBUG] 所有核心依赖库加载成功 ---")
except Exception as init_err:
    print(f"❌ [CRITICAL] 依赖库导入失败: {init_err}")
    sys.exit(1)

def get_date_strings(days_ago=0):
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8) - datetime.timedelta(days=days_ago)
    return bj_time.strftime("%Y%m%d"), bj_time.strftime("%Y"), bj_time.strftime("%m")

try:
    d_today, y_today, m_today = get_date_strings(0)
    d_yesterday, y_yesterday, m_yesterday = get_date_strings(1)
    print(f"--- [DEBUG] 动态日期计算成功: 今天={d_today}, 昨天={d_yesterday} ---")
except Exception as date_err:
    print(f"❌ [CRITICAL] 日期计算失败: {date_err}")
    sys.exit(1)

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
    node_pattern = re.compile(r'^(vmess|vless|ss|trojan|hysteria2|hy2)://[^\s]+')
    
    print(f"--- [DEBUG] 开始执行数据源抓取，共 {len(SOURCES)} 个源 ---")
    for url in SOURCES:
        try:
            print(f"👉 正在请求源: {url}")
            res = requests.get(url, timeout=10)
            print(f"   [状态码: {res.status_code}]")
            if res.status_code == 200:
                content = res.text.strip()
                if "<html" in content.lower() or "<doctype" in content.lower():
                    print("   [⚠️ 警告] 检测到 HTML 源码而非订阅，跳过")
                    continue
                    
                if "://" not in content and len(content) > 20:
                    decoded = safe_b64decode(content)
                    lines = decoded.splitlines()
                else:
                    lines = content.splitlines()
                
                valid_count = 0
                for line in lines:
                    line_str = line.strip()
                    if node_pattern.match(line_str):
                        raw_configs.append(line_str)
                        valid_count += 1
                print(f"   [成功] 从该源提取到 {valid_count} 个标准节点行")
        except Exception as e:
            print(f"   [失败] 访问该源发生异常: {e}")
            
    return list(set(raw_configs))

def rename_nodes_all(nodes):
    final_nodes = []
    counter = 1
    
    print(f"--- [DEBUG] 开始解析与重命名，原始合并总数: {len(nodes)} ---")
    
    # 强制注入首行提示死节点
    notice_name = "📢-来自公开的免费节点源 仅作为学习参考"
    notice_node = f"vless://unusable-uuid@127.0.0.1:8888?encryption=none&security=none#{urllib.parse.quote(notice_name)}"
    final_nodes.append(notice_node)

    for idx, node in enumerate(nodes):
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
        except Exception as single_err:
            print(f"❌ [行错误] 第 {idx} 个节点解析失败，跳过。原因: {single_err}")
            continue
            
    return final_nodes

if __name__ == "__main__":
    print("--- [DEBUG] 进入主程序入口 (__main__) ---")
    try:
        raw_nodes = fetch_and_decode()
        print(f"--- [DEBUG] 去重合并完成，共有 {len(raw_nodes)} 个节点准备进行格式化 ---")
        
        processed_nodes = rename_and_filter_nodes_all = rename_nodes_all(raw_nodes)
        
        print("--- [DEBUG] 正在尝试写入 nodes.txt ---")
        joined_nodes = "\n".join(processed_nodes)
        with open("nodes.txt", "w", encoding="utf-8") as f:
            f.write(joined_nodes)
            
        print("--- [DEBUG] 正在尝试写入 sub.txt ---")
        b64_encoded = base64.b64encode(joined_nodes.encode('utf-8')).decode('utf-8')
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(b64_encoded)
            
        print(f"--- [🎉 成功] 全量处理完毕！最终生成了 {len(processed_nodes)} 个节点 ---")
        
    except Exception as fatal_err:
        print("\n💥💥💥 [FATAL CRASH] 主程序捕获到未处理的毁灭性崩溃 💥💥💥")
        print("以下是具体的崩溃调用栈（请提供给 AI 分析）：")
        traceback.print_exc()
        sys.exit(1)
