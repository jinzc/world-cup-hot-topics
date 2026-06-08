import json
import ssl
import urllib.request

# 世界杯关键词库（中英文覆盖）
WORLD_CUP_KEYWORDS = [
    "世界杯", "世预赛", "美加墨", "国足", "中国男足", "国足世预赛",
    "中国vs", "vs中国", "出线", "晋级", "淘汰", "小组赛", "淘汰赛",
    "1/8决赛", "1/4决赛", "半决赛", "决赛", "冠军", "金球奖", "金靴奖",
    "VAR", "点球", "红牌", "黄牌", "越位", "进球", "绝杀", "扳平",
    "逆转", "爆冷", "黑马", "死亡之组", "射手榜", "积分榜", "赛程",
    "直播", "转播", "解说", "预测", "竞猜", "帽子戏法", "梅开二度",
    "伤停补时", "加时赛", "点球大战",
    "梅西", "姆巴佩", "C罗", "内马尔", "哈兰德", "贝林厄姆", "维尼修斯",
    "德布劳内", "莱万", "凯恩", "孙兴慜", "三笘薰", "久保建英",
    "阿根廷", "巴西", "德国", "法国", "西班牙", "英格兰", "意大利",
    "荷兰", "葡萄牙", "比利时", "克罗地亚", "摩洛哥", "日本", "韩国",
    "伊朗", "沙特", "澳大利亚", "加拿大", "墨西哥", "美国", "哥伦比亚",
    "乌拉圭", "智利", "厄瓜多尔", "秘鲁", "巴拉圭", "玻利维亚", "委内瑞拉",
    "洪都拉斯", "哥斯达黎加", "巴拿马", "牙买加", "海地", "危地马拉",
    "萨尔瓦多", "尼加拉瓜", "多米尼加", "古巴", "波多黎各", "特立尼达",
    "巴巴多斯", "格林纳达", "圣卢西亚", "圣文森特", "安提瓜", "多米尼克",
    "圣基茨", "巴哈马", "百慕大", "开曼", "特克斯", "凯科斯", "安圭拉",
    "蒙特塞拉特", "瓜德罗普", "马提尼克", "法属圭亚那", "圣马丁",
    "荷属圣马丁", "圣巴泰勒米", "圣尤斯特歇斯", "萨巴", "博奈尔",
    "库拉索", "阿鲁巴",
    "world cup", "worldcup", "wc2026", "fifa", "group stage", "knockout",
    "round of 16", "quarter final", "semi final", "final", "champion",
    "golden ball", "golden boot", "var", "penalty", "red card", "yellow card",
    "offside", "goal", "hat trick", "brace", "injury time", "extra time",
    "penalty shootout",
    "messi", "mbappe", "neymar", "ronaldo", "haaland", "bellingham", "vinicius",
    "de bruyne", "lewandowski", "kane", "son heung-min", "mitoma", "kubo",
    "argentina", "brazil", "germany", "france", "spain", "england", "italy",
    "netherlands", "portugal", "belgium", "croatia", "morocco", "japan",
    "korea", "iran", "saudi", "australia", "canada", "mexico", "usa",
    "colombia", "uruguay", "chile", "ecuador", "peru", "paraguay", "bolivia",
    "venezuela", "honduras", "costa rica", "panama", "jamaica", "haiti",
    "guatemala", "el salvador", "nicaragua", "dominican", "cuba", "puerto rico",
    "trinidad", "barbados", "grenada", "saint lucia", "saint vincent",
    "antigua", "dominica", "saint kitts", "bahamas", "bermuda", "cayman",
    "turks", "caicos", "anguilla", "montserrat", "guadeloupe", "martinique",
    "french guiana", "saint martin", "sint maarten", "saint barthelemy",
    "sint eustatius", "saba", "bonaire", "curacao", "aruba",
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
