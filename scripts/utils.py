import json
import ssl
import urllib.request

# 世界杯关键词库（严格围绕世界杯，移除易误匹配的国家名单个词）
WORLD_CUP_KEYWORDS = [
    # 中文核心词（必须包含这些才认为是世界杯相关）
    "世界杯", "世预赛", "美加墨", "国足", "中国男足", "国足世预赛",
    "中国vs", "vs中国", "出线", "晋级", "淘汰", "小组赛", "淘汰赛",
    "1/8决赛", "1/4决赛", "半决赛", "决赛", "冠军", "金球奖", "金靴奖",
    "VAR", "点球", "红牌", "黄牌", "越位", "进球", "绝杀", "扳平",
    "逆转", "爆冷", "黑马", "死亡之组", "射手榜", "积分榜", "赛程",
    "直播", "转播", "解说", "预测", "竞猜", "帽子戏法", "梅开二度",
    "伤停补时", "加时赛", "点球大战", "揭幕战", "开幕", "闭幕式",
    "大力神杯", "足联", "FIFA", "国际足联",
    # 球星（知名世界杯球星，避免普通球员名误匹配）
    "梅西", "姆巴佩", "C罗", "内马尔", "哈兰德", "贝林厄姆", "维尼修斯",
    "德布劳内", "莱万", "凯恩", "孙兴慜", "三笘薰", "久保建英",
    "莫德里奇", "亚马尔", "拉什福德", "萨卡", "贝林", "恩德里克",
    "佩德里", "加维", "罗德里", "范戴克", "萨拉赫", "卢卡库",
    "格列兹曼", "登贝莱", "萨利巴", "赖斯", "贝林厄姆",
    "马丁内斯", "大马丁", "迪马利亚", "阿尔瓦雷斯", "恩佐",
    "琼阿梅尼", "卡马文加", "孔德", "于帕", "科纳特",
    "穆西亚拉", "维尔茨", "哈弗茨", "基米希", "诺伊尔",
    "罗德里戈", "米利唐", "马尔基尼奥斯", "阿利松", "埃德森",
    "奥塔门迪", "罗梅罗", "麦卡利斯特", "帕雷德斯", "德保罗",
    "B费", "B席", "菲利克斯", "莱奥", "努诺", "门德斯",
    "孙兴慜", "李刚仁", "金玟哉", "黄喜灿",
    "久保建英", "三笘薰", "富安健洋", "远藤航",
    "塔雷米", "阿兹蒙", "贾汉巴赫什",
    # 英文核心词
    "world cup", "worldcup", "wc2026", "fifa world cup", "group stage", "knockout",
    "round of 16", "quarter final", "semi final", "final", "champion",
    "golden ball", "golden boot", "var", "penalty", "red card", "yellow card",
    "offside", "goal", "hat trick", "brace", "injury time", "extra time",
    "penalty shootout", "opening match", "opening ceremony", "closing ceremony",
    # 英文球星
    "messi", "mbappe", "mbappé", "neymar", "ronaldo", "haaland", "bellingham", "vinicius",
    "de bruyne", "lewandowski", "kane", "son heung-min", "mitoma", "kubo",
    "modric", "lamine yamal", "rashford", "saka", "endrick",
    "pedri", "gavi", "rodri", "van dijk", "salah", "lukaku",
    "griezmann", "dembele", "saliba", "rice", "musiala",
    "wirtz", "havertz", "kimmich", "neuer", "alisson", "ederson",
]


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
