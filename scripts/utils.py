import json
import ssl
import urllib.request

# ============================================================
# 世界杯关键词库（严格过滤，只保留核心词 + 顶级球星名）
# ============================================================
# 核心词：单独出现即认为是世界杯相关
CORE_KEYWORDS = [
    "世界杯", "世预赛", "美加墨", "国足", "中国男足", "国足世预赛",
    "中国vs", "vs中国", "fifa world cup", "wc2026", "world cup 2026",
    "2026 world cup", "大力神杯", "足联", "国际足联", "揭幕战",
    "开幕式", "闭幕式", "诸神黄昏",
]

# 顶级球星名：单独出现即匹配（已确认参加2026世界杯或极大概率参加的顶级球星）
STAR_KEYWORDS = [
    "梅西", "姆巴佩", "C罗", "内马尔", "莫德里奇", "亚马尔",
    "贝林厄姆", "维尼修斯", "德布劳内", "凯恩", "孙兴慜", "莱万",
    "马丁内斯", "大马丁", "迪马利亚", "阿尔瓦雷斯", "恩佐",
    "佩德里", "加维", "罗德里", "萨卡", "拉什福德",
    "穆西亚拉", "维尔茨", "哈弗茨", "基米希", "诺伊尔",
    "罗德里戈", "米利唐", "马尔基尼奥斯", "阿利松", "埃德森",
    "奥塔门迪", "罗梅罗", "麦卡利斯特", "帕雷德斯", "德保罗",
    "B费", "B席", "菲利克斯", "莱奥", "李刚仁", "金玟哉",
    "富安健洋", "远藤航", "塔雷米", "阿兹蒙",
    "messi", "mbappe", "mbappé", "neymar", "ronaldo", "modric",
    "lamine yamal", "bellingham", "vinicius", "de bruyne", "kane",
    "son heung-min", "lewandowski", "martinez", "di maria", "alvarez",
    "enzo", "pedri", "gavi", "rodri", "saka", "rashford",
    "musiala", "wirtz", "havertz", "kimmich", "neuer", "alisson", "ederson",
]

WORLD_CUP_KEYWORDS = CORE_KEYWORDS + STAR_KEYWORDS


def is_world_cup_related(text):
    """判断文本是否与世界杯相关"""
    if not text or not isinstance(text, str):
        return False
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in WORLD_CUP_KEYWORDS)


def fetch_json(url, headers=None, timeout=15):
    """通用 JSON 请求"""
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        return {"_error": str(e)}


def fetch_html(url, headers=None, timeout=15):
    """通用 HTML 请求"""
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return ""


def save_data(data, filepath):
    """保存 JSON 数据"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
