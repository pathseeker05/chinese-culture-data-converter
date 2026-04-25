# -*- coding: utf-8 -*-
import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests

try:
    from objectbox import Store, Model, Entity, Id, String, Int32
    OBJECTBOX_AVAILABLE = True
except ImportError:
    OBJECTBOX_AVAILABLE = False

OUTPUT_DIR = Path(__file__).parent.parent / "output"
JSON_DIR = OUTPUT_DIR / "json"
OBJECTBOX_DIR = OUTPUT_DIR / "objectbox"

DATA_SOURCES = {
    "chinese_xinhua": "https://raw.githubusercontent.com/pwxcoo/chinese-xinhua/master/data",
    "chinese_poetry": "https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master",
    "chinese_colors": "https://raw.githubusercontent.com/zerosoul/chinese-colors/master/src/assets",
    "jingmo_data": "https://raw.githubusercontent.com/hefengbao/jingmo-data/gh-pages/api",
}

DATA_FILES = {
    "歇后语": "xiehouyu.json",
    "成语": "idiom.json",
    "汉字": "word.json",
    "词语": "ci.json",
    "谜语": "riddles.json",
    "传统色": "chinese_colors.json",
    "诗词": "poems.json",
    "对联": "couplets.json",
    "谚语": "proverbs.json",
    "绕口令": "tongue_twisters.json",
    "知识卡片": "knowledge.json",
    "世界文化遗产": "world_heritage.json",
    "经典诗文": "classic_poems.json",
    "诗文名句": "sentences.json",
}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "chinese-culture-data-converter/1.0"})


# ============================================================
# 下载
# ============================================================

def ensure_dirs():
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    OBJECTBOX_DIR.mkdir(parents=True, exist_ok=True)


def download(url: str, max_retries: int = 3, timeout: int = 30) -> requests.Response | None:
    for attempt in range(max_retries):
        try:
            response = SESSION.get(url, timeout=timeout)
            if response.status_code == 200:
                return response
            if response.status_code == 404:
                return None
        except requests.RequestException:
            if attempt < max_retries - 1:
                time.sleep(attempt + 1)
    return None


def download_batch(urls: list) -> list:
    results = [None] * len(urls)
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {executor.submit(download, url): i for i, url in enumerate(urls)}
        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                results[idx] = future.result()
            except Exception:
                pass
    return results


def save_json(data: list, filename: str):
    filepath = JSON_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"  {filename}: {len(data):,} 条 ({size_mb:.2f} MB)")


def download_xinhua_data(filename: str, result_fields: list, field_aliases: dict | None = None) -> list:
    url = f"{DATA_SOURCES['chinese_xinhua']}/{filename}"
    response = download(url, timeout=120)
    if not response:
        print(f"  [错误] 下载失败: {url}")
        return []
    data = response.json()
    if field_aliases is None:
        field_aliases = {}
    result = []
    for i, item in enumerate(data):
        row = {"id": i + 1}
        for field in result_fields:
            src_field = field_aliases.get(field, field)
            row[field] = item.get(src_field, "")
            if not row[field] and src_field != field:
                row[field] = item.get(field, "")
        result.append(row)
    save_json(result, filename)
    return result


def download_jingmo_data(filename: str) -> list:
    url = f"{DATA_SOURCES['jingmo_data']}/{filename}"
    response = download(url, timeout=120)
    if not response:
        return []
    data = response.json()
    if isinstance(data, dict):
        items = data.get("data", [])
    elif isinstance(data, list):
        items = data
    else:
        items = []
    return items


def download_riddles() -> list:
    print("\n[谜语]")
    items = download_jingmo_data("chinese_riddle_v2_1.json")
    if not items:
        print("  [错误] 谜语数据下载失败")
        return []
    result = []
    for i, item in enumerate(items):
        result.append({
            "id": i + 1,
            "question": item.get("puzzle", ""),
            "answer": item.get("answer", ""),
        })
    save_json(result, "riddles.json")
    return result


def download_proverbs() -> list:
    print("\n[谚语]")
    items = download_jingmo_data("chinese_proverb_v3_1.json")
    if not items:
        print("  [错误] 谚语数据下载失败")
        return []
    result = []
    for i, item in enumerate(items):
        result.append({
            "id": i + 1,
            "content": item.get("content", ""),
            "tags": ",".join(item.get("tags", [])) if isinstance(item.get("tags"), list) else item.get("tags", ""),
        })
    save_json(result, "proverbs.json")
    return result


def download_tongue_twisters() -> list:
    print("\n[绕口令]")
    items = download_jingmo_data("chinese_tonguetwister_v2_1.json")
    if not items:
        print("  [错误] 绕口令数据下载失败")
        return []
    result = []
    for i, item in enumerate(items):
        result.append({
            "id": i + 1,
            "title": item.get("title", ""),
            "content": item.get("content", ""),
        })
    save_json(result, "tongue_twisters.json")
    return result


def download_knowledge() -> list:
    print("\n[知识卡片]")
    items = download_jingmo_data("chinese_knowledge_v2_1.json")
    if not items:
        print("  [错误] 知识卡片数据下载失败")
        return []
    result = []
    for i, item in enumerate(items):
        result.append({
            "id": i + 1,
            "content": item.get("content", ""),
            "label": item.get("label", ""),
        })
    save_json(result, "knowledge.json")
    return result


def download_world_heritage() -> list:
    print("\n[世界文化遗产]")
    items = download_jingmo_data("china_worldcultureheritage_v4_1.json")
    if not items:
        print("  [错误] 世界文化遗产数据下载失败")
        return []
    result = []
    for i, item in enumerate(items):
        result.append({
            "id": i + 1,
            "name": item.get("name", ""),
            "year": item.get("year", ""),
            "type": item.get("type", ""),
            "address": item.get("address", ""),
            "content": item.get("content", ""),
        })
    save_json(result, "world_heritage.json")
    return result


def download_classic_poems() -> list:
    print("\n[经典诗文]")
    items = download_jingmo_data("classicalliterature_classicpoem_v3_1.json")
    if not items:
        print("  [错误] 经典诗文数据下载失败")
        return []
    result = []
    for i, item in enumerate(items):
        content = item.get("content", [])
        if isinstance(content, list):
            content = "\n".join(content)
        result.append({
            "id": i + 1,
            "title": item.get("title", ""),
            "dynasty": item.get("dynasty", ""),
            "author": item.get("writer", ""),
            "content": content,
            "translate": item.get("translation", "") or "",
            "comment": item.get("comment", "") or "",
            "collection": item.get("collection", "") or "",
            "category": item.get("category", "") or "",
        })
    save_json(result, "classic_poems.json")
    return result


def download_sentences() -> list:
    print("\n[诗文名句]")
    items = download_jingmo_data("classicalliterature_sentence_v3_1.json")
    if not items:
        print("  [错误] 诗文名句数据下载失败")
        return []
    result = []
    for i, item in enumerate(items):
        result.append({
            "id": i + 1,
            "content": item.get("content", ""),
            "from": item.get("from", ""),
        })
    save_json(result, "sentences.json")
    return result


def download_chinese_colors() -> list:
    print("\n[传统色]")
    urls_to_try = [
        f"{DATA_SOURCES['chinese_colors']}/colors.json",
        f"{DATA_SOURCES['chinese_colors']}/chinese-colors.json",
    ]
    for url in urls_to_try:
        response = download(url)
        if response:
            try:
                data = response.json()
                result = []
                color_id = 1
                if isinstance(data, list) and len(data) > 0 and "colors" in data[0]:
                    for group in data:
                        for color in group.get("colors", []):
                            result.append({
                                "id": color_id,
                                "name": color.get("name", ""),
                                "hex": color.get("hex", ""),
                                "intro": color.get("intro", ""),
                            })
                            color_id += 1
                else:
                    for i, item in enumerate(data):
                        result.append({
                            "id": i + 1,
                            "name": item.get("name", ""),
                            "hex": item.get("hex", ""),
                            "intro": item.get("intro", ""),
                        })
                if result:
                    save_json(result, "chinese_colors.json")
                    return result
            except Exception as e:
                print(f"  解析传统色数据时出错: {e}")
    print("  [错误] 传统色数据下载失败")
    return []


def _add_poem(poems: list, item: dict, dynasty: str, poem_id: int,
              default_author: str = "") -> int:
    content = item.get("paragraphs") or item.get("para") or item.get("content", [])
    if isinstance(content, list):
        content = "\n".join(content)
    title = item.get("title") or item.get("rhythmic", "") or item.get("name", "")
    author = item.get("author", "") or default_author
    poems.append({
        "id": poem_id,
        "title": title,
        "author": author,
        "dynasty": dynasty,
        "content": content,
    })
    return poem_id + 1


def _download_poem_batch(base_url, dynasty: str, poems: list, poem_id: int,
                         label: str, default_author: str = "") -> int:
    print(f"  {label}...")
    count = len(poems)
    responses = download_batch(base_url) if isinstance(base_url, list) else [download(base_url)]
    for resp in responses:
        if resp:
            try:
                items = resp.json()
                for item in items:
                    poem_id = _add_poem(poems, item, dynasty, poem_id, default_author)
            except Exception as e:
                print(f"    解析出错: {e}")
    print(f"    +{len(poems) - count:,} 首")
    return poem_id


def download_poems() -> list:
    print("\n[诗词]")
    poems = []
    poem_id = 1

    poem_id = _download_poem_batch(
        [f"{DATA_SOURCES['chinese_poetry']}/全唐诗/poet.tang.{i}.json"
         for i in range(0, 58000, 1000)],
        "唐", poems, poem_id, "全唐诗")

    poem_id = _download_poem_batch(
        [f"{DATA_SOURCES['chinese_poetry']}/御定全唐詩/json/{i:03d}.json"
         for i in range(1, 901)],
        "唐", poems, poem_id, "御定全唐诗")

    poem_id = _download_poem_batch(
        [f"{DATA_SOURCES['chinese_poetry']}/全唐诗/poet.song.{i}.json"
         for i in range(0, 255000, 1000)],
        "宋", poems, poem_id, "全宋诗")

    poem_id = _download_poem_batch(
        [f"{DATA_SOURCES['chinese_poetry']}/宋词/ci.song.{i}.json"
         for i in range(0, 22000, 1000)] +
        [f"{DATA_SOURCES['chinese_poetry']}/宋词/ci.song.2019y.json"],
        "宋", poems, poem_id, "宋词")

    poem_id = _download_poem_batch(
        f"{DATA_SOURCES['chinese_poetry']}/元曲/yuanqu.json",
        "元", poems, poem_id, "元曲")

    poem_id = _download_poem_batch(
        [f"{DATA_SOURCES['chinese_poetry']}/五代诗词/huajianji/huajianji-{i}-juan.json"
         for i in range(1, 10)] +
        [f"{DATA_SOURCES['chinese_poetry']}/五代诗词/huajianji/huajianji-0-preface.json",
         f"{DATA_SOURCES['chinese_poetry']}/五代诗词/huajianji/huajianji-x-juan.json"],
        "五代", poems, poem_id, "花间集")

    poem_id = _download_poem_batch(
        f"{DATA_SOURCES['chinese_poetry']}/五代诗词/nantang/poetrys.json",
        "五代", poems, poem_id, "南唐二主词")

    poem_id = _download_poem_batch(
        f"{DATA_SOURCES['chinese_poetry']}/楚辞/chuci.json",
        "先秦", poems, poem_id, "楚辞")

    poem_id = _download_poem_batch(
        f"{DATA_SOURCES['chinese_poetry']}/诗经/shijing.json",
        "先秦", poems, poem_id, "诗经")

    poem_id = _download_poem_batch(
        f"{DATA_SOURCES['chinese_poetry']}/纳兰性德/纳兰性德诗集.json",
        "清", poems, poem_id, "纳兰性德诗集")

    poem_id = _download_poem_batch(
        f"{DATA_SOURCES['chinese_poetry']}/曹操诗集/caocao.json",
        "汉", poems, poem_id, "曹操诗集", default_author="曹操")

    print(f"  总计: {len(poems):,} 首")
    if poems:
        save_json(poems, "poems.json")
        return poems
    print("  [错误] 诗词数据下载失败")
    return []


def download_couplets() -> list:
    print("\n[对联]")
    items = download_jingmo_data("chinese_antitheticalcouplet_v2_1.json")
    if not items:
        print("  [错误] 对联数据下载失败")
        return []
    result = []
    for i, item in enumerate(items):
        body = item.get("body", "")
        parts = body.split("\n\n") if "\n\n" in body else body.split("\n")
        first = parts[0].strip() if len(parts) >= 1 else ""
        second = parts[1].strip() if len(parts) >= 2 else ""
        if not first and not second:
            first = body.strip()
        result.append({
            "id": i + 1,
            "first_line": first,
            "second_line": second,
        })
    print(f"  总计: {len(result):,} 条")
    save_json(result, "couplets.json")
    return result


def download_all() -> dict:
    all_data = {}

    print("\n[歇后语]")
    all_data["allegorical_sayings"] = download_xinhua_data(
        "xiehouyu.json", ["riddle", "answer"])

    print("\n[成语]")
    all_data["idioms"] = download_xinhua_data(
        "idiom.json", ["word", "pinyin", "explanation", "derivation", "example", "abbreviation"])

    print("\n[汉字]")
    all_data["characters"] = download_xinhua_data(
        "word.json",
        ["character", "pinyin", "strokes", "radical", "explanation"],
        field_aliases={"character": "word", "radical": "radicals"})

    print("\n[词语]")
    all_data["words"] = download_xinhua_data(
        "ci.json", ["ci", "explanation"])

    all_data["riddles"] = download_riddles()
    all_data["chinese_colors"] = download_chinese_colors()
    all_data["proverbs"] = download_proverbs()
    all_data["tongue_twisters"] = download_tongue_twisters()
    all_data["knowledge"] = download_knowledge()
    all_data["world_heritage"] = download_world_heritage()
    all_data["classic_poems"] = download_classic_poems()
    all_data["sentences"] = download_sentences()
    all_data["poems"] = download_poems()
    all_data["couplets"] = download_couplets()

    return all_data


# ============================================================
# 校验
# ============================================================

def check_poems():
    filepath = JSON_DIR / "poems.json"
    if not filepath.exists():
        print("  诗词文件不存在")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        poems = json.load(f)

    dynasty_count = {}
    for p in poems:
        d = p.get("dynasty", "未知")
        dynasty_count[d] = dynasty_count.get(d, 0) + 1

    print("  朝代分布:", " | ".join(f"{d}:{c:,}" for d, c in
          sorted(dynasty_count.items(), key=lambda x: -x[1])))

    empty_title = sum(1 for p in poems if not p.get("title"))
    empty_content = sum(1 for p in poems if not p.get("content"))
    empty_author = sum(1 for p in poems if not p.get("author"))
    print(f"  空标题: {empty_title:,} | 空内容: {empty_content:,} | 空作者: {empty_author:,}")


def check_characters():
    filepath = JSON_DIR / "word.json"
    if not filepath.exists():
        print("  汉字文件不存在")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    empty = sum(1 for d in data if not d.get("pinyin") or not d.get("explanation"))
    print(f"  空字段: {empty} / {len(data)}")


def check_all():
    print("\n[校验] 数据完整性检查")
    check_poems()
    check_characters()

    print("  各类别空字段统计:")
    for name, filename in DATA_FILES.items():
        filepath = JSON_DIR / filename
        if not filepath.exists():
            print(f"    {name}: 文件不存在!")
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        empty = sum(
            1 for item in data
            if any(not v for v in item.values() if isinstance(v, str))
        )
        status = "OK" if empty == 0 else f"空字段 {empty}"
        print(f"    {name}: {len(data):,} 条 [{status}]")


def _count_xinhua_source(filename: str) -> int | None:
    url = f"{DATA_SOURCES['chinese_xinhua']}/{filename}"
    resp = download(url, timeout=120)
    if not resp:
        return None
    data = resp.json()
    return len(data) if isinstance(data, list) else None


def _count_jingmo_source(filename: str) -> int | None:
    url = f"{DATA_SOURCES['jingmo_data']}/{filename}"
    resp = download(url, timeout=120)
    if not resp:
        return None
    data = resp.json()
    if isinstance(data, dict):
        items = data.get("data", [])
        return len(items)
    if isinstance(data, list):
        return len(data)
    return None


def _count_poetry_source(url_pattern: str, start: int, end: int, step: int) -> int:
    urls = [url_pattern.format(i=i) for i in range(start, end, step)]
    total = 0
    responses = download_batch(urls)
    for resp in responses:
        if resp:
            try:
                items = resp.json()
                total += len(items)
            except Exception:
                pass
    return total


def _count_single_poetry_source(url: str) -> int:
    resp = download(url, timeout=60)
    if not resp:
        return 0
    try:
        items = resp.json()
        return len(items)
    except Exception:
        return 0


def verify_source_integrity():
    print("\n[对比] 原始数据源 vs 整理数据源")
    print("-" * 70)
    print(f"{'数据源':<14} {'原始条数':>10} {'整理条数':>10} {'差异':>10} {'状态':<8}")
    print("-" * 70)

    results = []

    def _report(name: str, original: int | None, processed: int):
        if original is None:
            print(f"{name:<14} {'N/A':>10} {processed:>10,} {'N/A':>10} [?]")
            return
        diff = processed - original
        if diff == 0:
            status = "[OK]"
        elif diff > 0:
            status = f"+{diff}"
        else:
            status = f"{diff}"
        print(f"{name:<14} {original:>10,} {processed:>10,} {diff:>+10} {status}")
        results.append((name, original, processed, diff))

    xinhua_base = DATA_SOURCES['chinese_xinhua']
    poetry_base = DATA_SOURCES['chinese_poetry']

    _report("歇后语", _count_xinhua_source("xiehouyu.json"),
            len(json.load(open(JSON_DIR / "xiehouyu.json", encoding="utf-8")))
            if (JSON_DIR / "xiehouyu.json").exists() else 0)

    _report("成语", _count_xinhua_source("idiom.json"),
            len(json.load(open(JSON_DIR / "idiom.json", encoding="utf-8")))
            if (JSON_DIR / "idiom.json").exists() else 0)

    _report("汉字", _count_xinhua_source("word.json"),
            len(json.load(open(JSON_DIR / "word.json", encoding="utf-8")))
            if (JSON_DIR / "word.json").exists() else 0)

    _report("词语", _count_xinhua_source("ci.json"),
            len(json.load(open(JSON_DIR / "ci.json", encoding="utf-8")))
            if (JSON_DIR / "ci.json").exists() else 0)

    _report("谜语", _count_jingmo_source("chinese_riddle_v2_1.json"),
            len(json.load(open(JSON_DIR / "riddles.json", encoding="utf-8")))
            if (JSON_DIR / "riddles.json").exists() else 0)

    _report("谚语", _count_jingmo_source("chinese_proverb_v3_1.json"),
            len(json.load(open(JSON_DIR / "proverbs.json", encoding="utf-8")))
            if (JSON_DIR / "proverbs.json").exists() else 0)

    _report("绕口令", _count_jingmo_source("chinese_tonguetwister_v2_1.json"),
            len(json.load(open(JSON_DIR / "tongue_twisters.json", encoding="utf-8")))
            if (JSON_DIR / "tongue_twisters.json").exists() else 0)

    _report("知识卡片", _count_jingmo_source("chinese_knowledge_v2_1.json"),
            len(json.load(open(JSON_DIR / "knowledge.json", encoding="utf-8")))
            if (JSON_DIR / "knowledge.json").exists() else 0)

    _report("世界遗产", _count_jingmo_source("china_worldcultureheritage_v4_1.json"),
            len(json.load(open(JSON_DIR / "world_heritage.json", encoding="utf-8")))
            if (JSON_DIR / "world_heritage.json").exists() else 0)

    _report("经典诗文", _count_jingmo_source("classicalliterature_classicpoem_v3_1.json"),
            len(json.load(open(JSON_DIR / "classic_poems.json", encoding="utf-8")))
            if (JSON_DIR / "classic_poems.json").exists() else 0)

    _report("诗文名句", _count_jingmo_source("classicalliterature_sentence_v3_1.json"),
            len(json.load(open(JSON_DIR / "sentences.json", encoding="utf-8")))
            if (JSON_DIR / "sentences.json").exists() else 0)

    _report("对联", _count_jingmo_source("chinese_antitheticalcouplet_v2_1.json"),
            len(json.load(open(JSON_DIR / "couplets.json", encoding="utf-8")))
            if (JSON_DIR / "couplets.json").exists() else 0)

    colors_url = f"{DATA_SOURCES['chinese_colors']}/colors.json"
    resp = download(colors_url)
    original_colors = 0
    if resp:
        try:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0 and "colors" in data[0]:
                for group in data:
                    original_colors += len(group.get("colors", []))
            else:
                original_colors = len(data)
        except Exception:
            original_colors = None
    else:
        original_colors = None
    _report("传统色", original_colors,
            len(json.load(open(JSON_DIR / "chinese_colors.json", encoding="utf-8")))
            if (JSON_DIR / "chinese_colors.json").exists() else 0)

    print("-" * 70)
    print("\n[对比] 诗词分来源对比")
    print("-" * 70)
    print(f"{'来源':<16} {'原始条数':>10} {'整理条数':>10} {'差异':>10} {'状态':<8}")
    print("-" * 70)

    poems = json.load(open(JSON_DIR / "poems.json", encoding="utf-8")) \
        if (JSON_DIR / "poems.json").exists() else []

    tang_poems = [p for p in poems if p.get("dynasty") == "唐"]
    song_poems = [p for p in poems if p.get("dynasty") == "宋"]
    yuan_poems = [p for p in poems if p.get("dynasty") == "元"]
    wudai_poems = [p for p in poems if p.get("dynasty") == "五代"]
    xianqin_poems = [p for p in poems if p.get("dynasty") == "先秦"]
    qing_poems = [p for p in poems if p.get("dynasty") == "清"]
    han_poems = [p for p in poems if p.get("dynasty") == "汉"]

    tang_original = _count_poetry_source(
        f"{poetry_base}/全唐诗/poet.tang.{{i}}.json", 0, 58000, 1000)
    yuding_original = _count_poetry_source(
        f"{poetry_base}/御定全唐詩/json/{{i:03d}}.json", 1, 901, 1)
    tang_original += yuding_original

    _report("全唐诗+御定", tang_original, len(tang_poems))

    song_shi_original = _count_poetry_source(
        f"{poetry_base}/全唐诗/poet.song.{{i}}.json", 0, 255000, 1000)
    song_ci_original = _count_poetry_source(
        f"{poetry_base}/宋词/ci.song.{{i}}.json", 0, 22000, 1000)
    song_ci_original += _count_single_poetry_source(f"{poetry_base}/宋词/ci.song.2019y.json")
    song_original = song_shi_original + song_ci_original

    _report("全宋诗+宋词", song_original, len(song_poems))

    yuan_original = _count_single_poetry_source(f"{poetry_base}/元曲/yuanqu.json")
    _report("元曲", yuan_original, len(yuan_poems))

    huajianji_original = 0
    for i in range(1, 10):
        huajianji_original += _count_single_poetry_source(
            f"{poetry_base}/五代诗词/huajianji/huajianji-{i}-juan.json")
    huajianji_original += _count_single_poetry_source(
        f"{poetry_base}/五代诗词/huajianji/huajianji-0-preface.json")
    huajianji_original += _count_single_poetry_source(
        f"{poetry_base}/五代诗词/huajianji/huajianji-x-juan.json")
    nantang_original = _count_single_poetry_source(
        f"{poetry_base}/五代诗词/nantang/poetrys.json")
    wudai_original = huajianji_original + nantang_original

    _report("五代诗词", wudai_original, len(wudai_poems))

    chuci_original = _count_single_poetry_source(f"{poetry_base}/楚辞/chuci.json")
    shijing_original = _count_single_poetry_source(f"{poetry_base}/诗经/shijing.json")
    xianqin_original = chuci_original + shijing_original

    _report("楚辞+诗经", xianqin_original, len(xianqin_poems))

    nalan_original = _count_single_poetry_source(f"{poetry_base}/纳兰性德/纳兰性德诗集.json")
    _report("纳兰性德", nalan_original, len(qing_poems))

    caocao_original = _count_single_poetry_source(f"{poetry_base}/曹操诗集/caocao.json")
    _report("曹操诗集", caocao_original, len(han_poems))

    _report("诗词总计",
            tang_original + song_original + yuan_original + wudai_original + xianqin_original + nalan_original + caocao_original,
            len(poems))

    print("-" * 70)

    mismatch_count = sum(1 for r in results if r[3] != 0)
    if mismatch_count == 0:
        print("\n[OK] 所有数据源与原始仓库完全一致")
    else:
        print(f"\n[!!] {mismatch_count} 个数据源与原始仓库存在差异，请检查")


# ============================================================
# ObjectBox 数据库生成
# ============================================================

def create_objectbox_database(data: dict):
    if not OBJECTBOX_AVAILABLE:
        print("\n[ObjectBox] 未安装，跳过数据库生成")
        print("  安装命令: pip install objectbox")
        return

    print("\n[ObjectBox] 生成数据库...")

    @Entity(uid=5138689974812837194)
    class Poem:
        id = Id(uid=2092154132757188441)
        title = String(uid=8672563413047427982)
        author = String(uid=5466912638969577328)
        dynasty = String(uid=1579315928936075485)
        content = String(uid=8555457517754422605)

    @Entity(uid=3835404907815727800)
    class Idiom:
        id = Id(uid=3968121255767916431)
        word = String(uid=8553329578059715463)
        pinyin = String(uid=4332491910449251933)
        explanation = String(uid=6921009637449458400)
        derivation = String(uid=261158313601471568)
        example = String(uid=1000000000000000061)
        abbreviation = String(uid=1000000000000000062)

    @Entity(uid=8459453139415417600)
    class AllegoricalSaying:
        id = Id(uid=2148276261068406532)
        riddle = String(uid=8066095940029803981)
        answer = String(uid=4120252874179261267)

    @Entity(uid=6733639669014313072)
    class Couplet:
        id = Id(uid=6699522448716242168)
        firstLine = String(uid=1816942533708551130)
        secondLine = String(uid=267558228280783991)

    @Entity(uid=8829709278046343028)
    class Riddle:
        id = Id(uid=5350698984327621257)
        question = String(uid=8365546854183537471)
        answer = String(uid=7064020760632626022)

    @Entity(uid=2457973436130635545)
    class Character:
        id = Id(uid=5398421242281898217)
        character = String(uid=5731950547804103849)
        pinyin = String(uid=7777249884059871139)
        strokes = Int32(uid=501311208075614740)
        radical = String(uid=7025245699339300924)
        explanation = String(uid=3365472651526989353)

    @Entity(uid=2979839035019917214)
    class Word:
        id = Id(uid=5506157397098358099)
        ci = String(uid=4080862617523690944)
        explanation = String(uid=1238575630192955858)

    @Entity(uid=2317813331518468214)
    class ChineseColor:
        id = Id(uid=3180020349576209163)
        name = String(uid=406963024289964779)
        hex = String(uid=4057588086824924305)
        intro = String(uid=1158706618833912945)

    @Entity(uid=1000000000000000001)
    class Proverb:
        id = Id(uid=1000000000000000002)
        content = String(uid=1000000000000000003)
        tags = String(uid=1000000000000000004)

    @Entity(uid=1000000000000000011)
    class TongueTwister:
        id = Id(uid=1000000000000000012)
        title = String(uid=1000000000000000013)
        content = String(uid=1000000000000000014)

    @Entity(uid=1000000000000000021)
    class Knowledge:
        id = Id(uid=1000000000000000022)
        content = String(uid=1000000000000000023)
        label = String(uid=1000000000000000024)

    @Entity(uid=1000000000000000031)
    class WorldHeritage:
        id = Id(uid=1000000000000000032)
        name = String(uid=1000000000000000033)
        year = String(uid=1000000000000000034)
        type = String(uid=1000000000000000035)
        address = String(uid=1000000000000000036)
        content = String(uid=1000000000000000037)

    @Entity(uid=1000000000000000041)
    class ClassicPoem:
        id = Id(uid=1000000000000000042)
        title = String(uid=1000000000000000043)
        dynasty = String(uid=1000000000000000044)
        author = String(uid=1000000000000000045)
        content = String(uid=1000000000000000046)
        translate = String(uid=1000000000000000047)
        comment = String(uid=1000000000000000048)
        collection = String(uid=1000000000000000049)
        category = String(uid=1000000000000000050)

    @Entity(uid=1000000000000000051)
    class Sentence:
        id = Id(uid=1000000000000000052)
        content = String(uid=1000000000000000053)
        from_ = String(uid=1000000000000000054)

    all_entities = [
        Poem, Idiom, AllegoricalSaying, Couplet, Riddle, Character, Word,
        ChineseColor, Proverb, TongueTwister, Knowledge, WorldHeritage,
        ClassicPoem, Sentence,
    ]

    model = Model()
    for entity in all_entities:
        model.entity(entity)

    if OBJECTBOX_DIR.exists():
        shutil.rmtree(OBJECTBOX_DIR)
    OBJECTBOX_DIR.mkdir(parents=True, exist_ok=True)

    store = Store(model=model, directory=str(OBJECTBOX_DIR))

    def insert(entity_class, items: list, field_map: dict):
        if not items:
            return
        box = store.box(entity_class)
        entities = []
        for item in items:
            entity = entity_class()
            for src, dst in field_map.items():
                value = item.get(src)
                if dst == "strokes" and value is not None:
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        value = 0
                setattr(entity, dst, value if value is not None else "")
            entities.append(entity)
        batch_size = 10000
        for i in range(0, len(entities), batch_size):
            box.put(*entities[i:i + batch_size])
        print(f"  {entity_class._name}: {len(entities):,} 条")

    insert(Poem, data.get("poems", []),
           {"title": "title", "author": "author", "dynasty": "dynasty", "content": "content"})
    insert(Idiom, data.get("idioms", []),
           {"word": "word", "pinyin": "pinyin", "explanation": "explanation", "derivation": "derivation",
            "example": "example", "abbreviation": "abbreviation"})
    insert(AllegoricalSaying, data.get("allegorical_sayings", []),
           {"riddle": "riddle", "answer": "answer"})
    insert(Couplet, data.get("couplets", []),
           {"first_line": "firstLine", "second_line": "secondLine"})
    insert(Riddle, data.get("riddles", []),
           {"question": "question", "answer": "answer"})
    insert(Character, data.get("characters", []),
           {"character": "character", "pinyin": "pinyin", "strokes": "strokes", "radical": "radical", "explanation": "explanation"})
    insert(Word, data.get("words", []),
           {"ci": "ci", "explanation": "explanation"})
    insert(ChineseColor, data.get("chinese_colors", []),
           {"name": "name", "hex": "hex", "intro": "intro"})
    insert(Proverb, data.get("proverbs", []),
           {"content": "content", "tags": "tags"})
    insert(TongueTwister, data.get("tongue_twisters", []),
           {"title": "title", "content": "content"})
    insert(Knowledge, data.get("knowledge", []),
           {"content": "content", "label": "label"})
    insert(WorldHeritage, data.get("world_heritage", []),
           {"name": "name", "year": "year", "type": "type", "address": "address", "content": "content"})
    insert(ClassicPoem, data.get("classic_poems", []),
           {"title": "title", "dynasty": "dynasty", "author": "author", "content": "content",
            "translate": "translate", "comment": "comment", "collection": "collection", "category": "category"})
    insert(Sentence, data.get("sentences", []),
           {"content": "content", "from": "from_"})

    store.close()

    db_size = sum(f.stat().st_size for f in OBJECTBOX_DIR.glob("*"))
    print(f"  数据库大小: {db_size / (1024 * 1024):.2f} MB")


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("中华文化数据库构建工具")
    print("=" * 60)

    ensure_dirs()

    all_data = download_all()

    metadata = {
        "version": "1.0.0",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": {k: len(v) for k, v in all_data.items()},
        "data_sources": {
            "poems": "https://github.com/chinese-poetry/chinese-poetry (MIT)",
            "allegorical_sayings": "https://github.com/pwxcoo/chinese-xinhua (MIT)",
            "idioms": "https://github.com/pwxcoo/chinese-xinhua (MIT)",
            "characters": "https://github.com/pwxcoo/chinese-xinhua (MIT)",
            "words": "https://github.com/pwxcoo/chinese-xinhua (MIT)",
            "couplets": "https://github.com/hefengbao/jingmo-data (MIT)",
            "chinese_colors": "https://github.com/zerosoul/chinese-colors (ISC)",
            "riddles": "https://github.com/hefengbao/jingmo-data (MIT)",
            "proverbs": "https://github.com/hefengbao/jingmo-data (MIT)",
            "tongue_twisters": "https://github.com/hefengbao/jingmo-data (MIT)",
            "knowledge": "https://github.com/hefengbao/jingmo-data (MIT)",
            "world_heritage": "https://github.com/hefengbao/jingmo-data (MIT)",
            "classic_poems": "https://github.com/hefengbao/jingmo-data (MIT)",
            "sentences": "https://github.com/hefengbao/jingmo-data (MIT)",
        }
    }

    with open(OUTPUT_DIR / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    create_objectbox_database(all_data)

    check_all()

    verify_source_integrity()

    print("\n" + "=" * 60)
    print("构建完成")
    print("=" * 60)
    for name, count in metadata["total_count"].items():
        print(f"  {name}: {count:,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
