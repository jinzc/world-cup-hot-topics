#!/usr/bin/env python3
"""
2026 世界杯话题热榜爬虫
聚合微博、百度、B站、知乎、抖音、虎扑、懂球帝、小红书、咪咕、网易、腾讯等平台
"""
import sys
import os
import urllib.parse
import re
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import fetch_json, fetch_html, is_world_cup_related, save_data

# 数据文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "world_cup_topics.json")

# 小红书 Cookie 配置（支持 GitHub Secrets）
XIAOHONGSHU_COOKIE = os.environ.get("XIAOHONGSHU_COOKIE", "")

# 获取北京时间
def get_beijing_time():
    return datetime.now(timezone(timedelta(hours=8)))


# ============================================================
# 各平台抓取函数
# ============================================================

def fetch_weibo():
    """微博热搜"""
    topics = []
    try:
        data = fetch_json("https://weibo.com/ajax/side/hotSearch", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://weibo.com/",
        })
        if isinstance(data, dict) and data.get("data", {}).get("realtime"):
            for item in data["data"]["realtime"]:
                title = item.get("word", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": f"https://s.weibo.com/weibo?q={urllib.parse.quote(title)}",
                        "hot": item.get("raw_hot", 0),
                        "label": item.get("label", ""),
                    })
    except Exception as e:
        return {"_error": str(e)}
    return topics


def fetch_baidu():
    """百度热搜（全站 + 体育榜备用）"""
    topics = []
    
    # 方式1：全站实时榜
    try:
        data = fetch_json("https://top.baidu.com/api/board?platform=wise&tab=realtime")
        if isinstance(data, dict) and data.get("data", {}).get("cards"):
            for card in data["data"]["cards"]:
                for item in card.get("content", []):
                    title = item.get("word", "")
                    if is_world_cup_related(title):
                        topics.append({
                            "title": title,
                            "url": item.get("url", ""),
                            "hot": item.get("hotScore", ""),
                            "desc": item.get("desc", ""),
                        })
    except Exception as e:
        print(f"  百度全站榜失败: {e}")
    
    # 方式2：体育榜
    if not topics:
        try:
            data = fetch_json("https://top.baidu.com/api/board?platform=wise&tab=sport")
            if isinstance(data, dict) and data.get("data", {}).get("cards"):
                for card in data["data"]["cards"]:
                    for item in card.get("content", []):
                        title = item.get("word", "")
                        if is_world_cup_related(title):
                            topics.append({
                                "title": title,
                                "url": item.get("url", ""),
                                "hot": item.get("hotScore", ""),
                                "desc": item.get("desc", ""),
                            })
        except Exception as e:
            print(f"  百度体育榜失败: {e}")
    
    return topics


def fetch_bilibili():
    """B站热搜"""
    topics = []
    try:
        data = fetch_json("https://api.bilibili.com/x/web-interface/search/square?limit=30", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://search.bilibili.com/",
        })
        if isinstance(data, dict) and data.get("data", {}).get("trending"):
            for item in data["data"]["trending"].get("list", []):
                title = item.get("keyword", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": f"https://search.bilibili.com/all?keyword={urllib.parse.quote(title)}",
                        "hot": item.get("hot", 0),
                    })
    except Exception as e:
        return {"_error": str(e)}
    return topics


def fetch_zhihu():
    """知乎热榜（多接口尝试）"""
    topics = []
    
    # 方式1：标准热榜接口
    try:
        data = fetch_json("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.zhihu.com/",
            "Accept": "application/json",
            "x-requested-with": "fetch",
        })
        if isinstance(data, dict) and data.get("data"):
            for item in data["data"]:
                target = item.get("target", {})
                title = target.get("title", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": target.get("url", ""),
                        "hot": item.get("detail_text", ""),
                    })
            if topics:
                return topics
    except Exception as e:
        print(f"  知乎接口1失败: {e}")
    
    # 方式2：备用接口
    try:
        data = fetch_json("https://www.zhihu.com/api/v3/feed/topstory/hot-lists?limit=50", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.zhihu.com/",
        })
        if isinstance(data, dict) and data.get("data"):
            for item in data["data"]:
                target = item.get("target", {})
                title = target.get("title", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": target.get("url", ""),
                        "hot": item.get("detail_text", ""),
                    })
    except Exception as e:
        print(f"  知乎接口2失败: {e}")
    
    return topics


def fetch_douyin():
    """抖音热搜（多备用接口）"""
    topics = []
    
    # 方式1：官方接口
    try:
        data = fetch_json("https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.douyin.com/",
        })
        if isinstance(data, dict) and data.get("data"):
            for item in data["data"]:
                title = item.get("word", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": f"https://www.douyin.com/search/{urllib.parse.quote(title)}",
                        "hot": item.get("hot_value", 0),
                    })
            if topics:
                return topics
    except Exception as e:
        print(f"  抖音官方接口失败: {e}")
    
    # 方式2：备用第三方接口1
    try:
        data = fetch_json("https://dabenshi.cn/other/api/hot.php?type=douyinhot", timeout=10)
        if isinstance(data, dict) and data.get("data"):
            for item in data["data"]:
                title = item.get("title", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": item.get("url", ""),
                        "hot": item.get("hot", ""),
                    })
            if topics:
                return topics
    except Exception as e:
        print(f"  抖音备用接口1失败: {e}")
    
    # 方式3：备用第三方接口2
    try:
        data = fetch_json("https://api-hot.imsyy.top/douyin", timeout=10)
        if isinstance(data, dict) and data.get("data"):
            for item in data["data"]:
                title = item.get("title", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": item.get("url", ""),
                        "hot": item.get("hot", ""),
                    })
    except Exception as e:
        print(f"  抖音备用接口2失败: {e}")
    
    return topics


def fetch_hupu():
    """虎扑热帖（API + 网页端多尝试）"""
    topics = []
    
    # 方式1：原API
    try:
        data = fetch_json("https://bbs.hupu.com/api/v1/all-gambia?limit=50", headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://bbs.hupu.com/",
        })
        if isinstance(data, dict) and data.get("data"):
            for item in data["data"]:
                title = item.get("title", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": item.get("url", ""),
                        "hot": item.get("replies", 0),
                        "author": item.get("user", {}).get("name", ""),
                    })
            if topics:
                return topics
    except Exception as e:
        print(f"  虎扑API1失败: {e}")
    
    # 方式2：topic-web API
    try:
        data = fetch_json("https://bbs.hupu.com/api/v1/topic-web?limit=50", headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://bbs.hupu.com/",
        })
        if isinstance(data, dict) and data.get("data"):
            for item in data["data"]:
                title = item.get("title", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": item.get("url", ""),
                        "hot": item.get("replies", 0),
                    })
            if topics:
                return topics
    except Exception as e:
        print(f"  虎扑API2失败: {e}")
    
    # 方式3：足球专区网页抓取
    try:
        html = fetch_html("https://bbs.hupu.com/soccer", timeout=10)
        if html:
            matches = re.findall(r'<a[^>]*class="post-title"[^>]*>([^<<]+)</a>', html)
            for title in matches[:20]:
                clean = title.strip()
                if is_world_cup_related(clean):
                    topics.append({
                        "title": clean,
                        "url": "https://bbs.hupu.com/soccer",
                        "hot": "",
                    })
            if topics:
                return topics
    except Exception as e:
        print(f"  虎扑足球专区失败: {e}")
    
    # 方式4：步行街网页抓取
    try:
        html = fetch_html("https://bbs.hupu.com/all-gambia", timeout=10)
        if html:
            matches = re.findall(r'<a[^>]*class="post-title"[^>]*>([^<<]+)</a>', html)
            for title in matches[:20]:
                clean = title.strip()
                if is_world_cup_related(clean):
                    topics.append({
                        "title": clean,
                        "url": "https://bbs.hupu.com/all-gambia",
                        "hot": "",
                    })
    except Exception as e:
        print(f"  虎扑步行街失败: {e}")
    
    return topics


def fetch_dongqiudi():
    """懂球帝热帖（多接口 + 网页端）"""
    topics = []
    
    # 方式1：原接口
    try:
        data = fetch_json("https://www.dongqiudi.com/api/app/tabs/web/56", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.dongqiudi.com/",
        })
        if isinstance(data, dict) and data.get("articles"):
            for item in data["articles"]:
                title = item.get("title", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": item.get("url", ""),
                        "hot": item.get("total_replies", 0),
                    })
            if topics:
                return topics
    except Exception as e:
        print(f"  懂球帝接口1失败: {e}")
    
    # 方式2：推荐文章接口
    try:
        data = fetch_json("https://www.dongqiudi.com/api/v2/article/recommend?page=1", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.dongqiudi.com/",
        })
        if isinstance(data, dict) and data.get("data"):
            for item in data["data"]:
                title = item.get("title", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": item.get("share_url", ""),
                        "hot": item.get("total_replies", 0),
                    })
            if topics:
                return topics
    except Exception as e:
        print(f"  懂球帝接口2失败: {e}")
    
    # 方式3：首页网页抓取
    try:
        html = fetch_html("https://www.dongqiudi.com/", timeout=10)
        if html:
            matches = re.findall(r'<a[^>]*href="/article/[^"]*"[^>]*>([^<<]{10,100})</a>', html)
            for title in matches[:20]:
                clean = re.sub(r'<[^>]+>', '', title).strip()
                if clean and is_world_cup_related(clean):
                    topics.append({
                        "title": clean,
                        "url": "https://www.dongqiudi.com/",
                        "hot": "",
                    })
    except Exception as e:
        print(f"  懂球帝首页失败: {e}")
    
    return topics


def fetch_xiaohongshu():
    """小红书热搜/热门笔记（需要 Cookie）"""
    topics = []
    if not XIAOHONGSHU_COOKIE:
        print("  小红书: 未配置 Cookie，跳过")
        return topics

    # 方式1：搜索热词
    try:
        data = fetch_json("https://www.xiaohongshu.com/api/sns/web/v1/search/hot", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": XIAOHONGSHU_COOKIE,
            "Referer": "https://www.xiaohongshu.com/search_result",
            "Accept": "application/json",
        }, timeout=10)
        if isinstance(data, dict) and data.get("data", {}).get("items"):
            for item in data["data"]["items"]:
                title = item.get("query", "")
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": f"https://www.xiaohongshu.com/search_result?keyword={urllib.parse.quote(title)}",
                        "hot": item.get("hot_score", 0),
                    })
    except Exception as e:
        print(f"  小红书搜索热词失败: {e}")

    # 方式2：发现页热门笔记
    try:
        data = fetch_json("https://www.xiaohongshu.com/api/sns/web/v1/homefeed", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": XIAOHONGSHU_COOKIE,
            "Referer": "https://www.xiaohongshu.com/explore",
            "Accept": "application/json",
        }, timeout=10)
        if isinstance(data, dict) and data.get("data", {}).get("items"):
            for item in data["data"]["items"]:
                note = item.get("note_card", {})
                title = note.get("title", "") or note.get("desc", "")[:50]
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": f"https://www.xiaohongshu.com/explore/{note.get('note_id', '')}",
                        "hot": note.get("interact_info", {}).get("liked_count", 0),
                    })
    except Exception as e:
        print(f"  小红书发现页失败: {e}")

    # 去重
    seen = set()
    unique = []
    for t in topics:
        if t["title"] and t["title"] not in seen:
            seen.add(t["title"])
            unique.append(t)
    return unique


def fetch_migu():
    """咪咕体育推荐内容（网页端抓取）"""
    topics = []
    wc_keywords = "世界杯|世预赛|足球|体育|梅西|姆巴佩|C罗|内马尔|阿根廷|巴西|德国|法国|西班牙|英格兰"
    try:
        html = fetch_html("https://www.miguvideo.com/p/home", timeout=10)
        if html:
            patterns = [
                r"title=[\"\\']([^\"\\']*?(?:" + wc_keywords + r")[^\"\\']*)[\"\\']",
                r"alt=[\"\\']([^\"\\']*?(?:" + wc_keywords + r")[^\"\\']*)[\"\\']",
                r"<h[1-6][^>]*>([^<<]*?(?:" + wc_keywords + r")[^<<]*)</h[1-6]>",
            ]
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for title in matches[:15]:
                    clean_title = re.sub(r'<[^>]+>', '', title).strip()
                    if clean_title and len(clean_title) > 5 and is_world_cup_related(clean_title):
                        topics.append({
                            "title": clean_title,
                            "url": "https://www.miguvideo.com/p/home",
                            "hot": "",
                        })
    except Exception as e:
        print(f"  咪咕首页抓取失败: {e}")

    try:
        html = fetch_html("https://www.miguvideo.com/p/channel/10010000008", timeout=10)
        if html:
            titles = re.findall(r'<[^>]*title=[\"\\']([^\"\\']+)[\"\\'][^>]*>', html)
            for title in titles[:15]:
                if is_world_cup_related(title):
                    topics.append({
                        "title": title,
                        "url": "https://www.miguvideo.com/p/channel/10010000008",
                        "hot": "",
                    })
    except Exception as e:
        print(f"  咪咕体育频道抓取失败: {e}")

    seen = set()
    unique = []
    for t in topics:
        if t["title"] and t["title"] not in seen:
            seen.add(t["title"])
            unique.append(t)
    return unique


def fetch_netease():
    """网易体育世界杯内容"""
    topics = []
    try:
        html = fetch_html("https://sports.163.com/", timeout=10)
        if html:
            matches = re.findall(r'<a[^>]*href=["\'][^"\']*["\'][^>]*>([^<<]{10,80})</a>', html)
            for title in matches[:30]:
                clean = re.sub(r'<[^>]+>', '', title).strip()
                if clean and is_world_cup_related(clean):
                    topics.append({
                        "title": clean,
                        "url": "https://sports.163.com/",
                        "hot": "",
                    })
            if not topics:
                matches = re.findall(r'title=["\']([^"\']*?(?:世界杯|世预赛|梅西|姆巴佩|C罗|内马尔)[^"\']*)["\']', html, re.IGNORECASE)
                for title in matches[:15]:
                    if is_world_cup_related(title):
                        topics.append({
                            "title": title,
                            "url": "https://sports.163.com/",
                            "hot": "",
                        })
    except Exception as e:
        print(f"  网易体育抓取失败: {e}")
    
    seen = set()
    unique = []
    for t in topics:
        if t["title"] and t["title"] not in seen:
            seen.add(t["title"])
            unique.append(t)
    return unique


def fetch_tencent():
    """腾讯新闻体育内容（多URL尝试）"""
    topics = []
    
    urls = [
        "https://new.qq.com/ch/sports/",
        "https://sports.qq.com/",
    ]
    
    for url in urls:
        try:
            html = fetch_html(url, timeout=10)
            if html:
                matches = re.findall(r'<a[^>]*href=["\'][^"\']*["\'][^>]*>([^<<]{10,80})</a>', html)
                for title in matches[:30]:
                    clean = re.sub(r'<[^>]+>', '', title).strip()
                    if clean and is_world_cup_related(clean):
                        topics.append({
                            "title": clean,
                            "url": url,
                            "hot": "",
                        })
                if topics:
                    break
        except Exception as e:
            print(f"  腾讯 {url} 失败: {e}")
    
    seen = set()
    unique = []
    for t in topics:
        if t["title"] and t["title"] not in seen:
            seen.add(t["title"])
            unique.append(t)
    return unique


def main():
    """主入口"""
    beijing_now = get_beijing_time()
    print(f"开始抓取世界杯话题... {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")

    all_data = {
        "update_time": beijing_now.strftime("%Y-%m-%d %H:%M:%S"),
        "sources": {}
    }

    fetchers = {
        "微博": fetch_weibo,
        "百度": fetch_baidu,
        "B站": fetch_bilibili,
        "知乎": fetch_zhihu,
        "抖音": fetch_douyin,
        "虎扑": fetch_hupu,
        "懂球帝": fetch_dongqiudi,
        "小红书": fetch_xiaohongshu,
        "咪咕": fetch_migu,
        "网易": fetch_netease,
        "腾讯": fetch_tencent,
    }

    for name, fetcher in fetchers.items():
        print(f"正在抓取 {name}...")
        try:
            result = fetcher()
            if isinstance(result, dict) and "_error" in result:
                all_data["sources"][name] = {
                    "topics": [],
                    "count": 0,
                    "status": f"error: {result['_error']}"
                }
                print(f"  {name}: 抓取失败 - {result['_error']}")
            else:
                all_data["sources"][name] = {
                    "topics": result,
                    "count": len(result),
                    "status": "success" if result else "empty"
                }
                print(f"  {name}: 抓到 {len(result)} 条世界杯话题")
        except Exception as e:
            all_data["sources"][name] = {
                "topics": [],
                "count": 0,
                "status": f"error: {str(e)}"
            }
            print(f"  {name}: 抓取失败 - {e}")
        time.sleep(1)

    save_data(all_data, DATA_FILE)
    total = sum(s["count"] for s in all_data["sources"].values())
    print(f"数据已保存到 {DATA_FILE}")
    print(f"抓取完成！共 {total} 条世界杯话题")


if __name__ == "__main__":
    main()
