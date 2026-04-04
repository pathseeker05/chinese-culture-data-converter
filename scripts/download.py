# -*- coding: utf-8 -*-
import json
import time
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
    "chinese_xinhua": "https://cdn.jsdelivr.net/gh/pwxcoo/chinese-xinhua@master/data",
    "chinese_poetry": "https://cdn.jsdelivr.net/gh/chinese-poetry/chinese-poetry@master",
    "couplet": "https://cdn.jsdelivr.net/gh/wb14123/couplet-dataset@master",
    "riddles": "https://cdn.jsdelivr.net/gh/pku0xff/CC-Riddle@master",
    "chinese_colors": "https://cdn.jsdelivr.net/gh/zerosoul/chinese-colors@master",
}

def ensure_dirs():
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    OBJECTBOX_DIR.mkdir(parents=True, exist_ok=True)

def download(url: str, max_retries: int = 3) -> requests.Response | None:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                return response
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
    return None

def save_json(data: list, filename: str):
    filepath = JSON_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"  {filename}: {len(data):,} 条 ({size_mb:.2f} MB)")

def download_xinhua_data(filename: str, result_fields: list) -> list:
    url = f"{DATA_SOURCES['chinese_xinhua']}/{filename}"
    response = download(url)
    if not response:
        return []
    data = response.json()
    result = []
    for i, item in enumerate(data):
        row = {"id": i + 1}
        for field in result_fields:
            row[field] = item.get(field, "")
        result.append(row)
    save_json(result, filename)
    return result

def download_riddles() -> list:
    url = f"{DATA_SOURCES['riddles']}/riddles.json"
    response = download(url)
    if not response:
        return []
    data = response.json()
    result = [{
        "id": i + 1,
        "question": item.get("question", ""),
        "answer": item.get("answer", ""),
        "source": item.get("source", ""),
    } for i, item in enumerate(data)]
    save_json(result, "riddles.json")
    return result

def download_chinese_colors() -> list:
    url = f"{DATA_SOURCES['chinese_colors']}/colors.json"
    response = download(url)
    if not response:
        return []
    data = response.json()
    result = [{
        "id": i + 1,
        "name": item.get("name", ""),
        "hex": item.get("hex", ""),
        "intro": item.get("intro", ""),
    } for i, item in enumerate(data)]
    save_json(result, "chinese_colors.json")
    return result

def download_poems() -> list:
    print("\n[诗词]")
    poems = []
    poem_id = 1
    
    def add_poem(item, dynasty):
        nonlocal poem_id
        content = item.get("paragraphs", [])
        if isinstance(content, list):
            content = "\n".join(content)
        poems.append({
            "id": poem_id,
            "title": item.get("title") or item.get("name") or item.get("rhythmic", ""),
            "author": item.get("author", ""),
            "dynasty": dynasty,
            "content": content,
        })
        poem_id += 1
    
    print("  全唐诗...")
    for i in range(0, 26000, 1000):
        url = f"{DATA_SOURCES['chinese_poetry']}/全唐诗/poet.tang.{i}.json"
        response = download(url)
        if response:
            for item in response.json():
                add_poem(item, "唐")
    print(f"    {len(poems):,} 首")
    
    print("  御定全唐诗...")
    count = len(poems)
    for i in range(1, 170):
        url = f"{DATA_SOURCES['chinese_poetry']}/御定全唐詩/json/{i:03d}.json"
        response = download(url)
        if response:
            for item in response.json():
                add_poem(item, "唐")
    print(f"    +{len(poems) - count:,} 首")
    
    print("  全宋诗...")
    count = len(poems)
    for i in range(0, 26000, 1000):
        url = f"{DATA_SOURCES['chinese_poetry']}/全宋诗/poet.song.{i}.json"
        response = download(url)
        if response:
            for item in response.json():
                add_poem(item, "宋")
    print(f"    +{len(poems) - count:,} 首")
    
    print("  宋词...")
    count = len(poems)
    for i in range(0, 21000, 1000):
        url = f"{DATA_SOURCES['chinese_poetry']}/宋词/ci.song.{i}.json"
        response = download(url)
        if response:
            for item in response.json():
                add_poem(item, "宋")
    print(f"    +{len(poems) - count:,} 首")
    
    print("  元曲...")
    url = f"{DATA_SOURCES['chinese_poetry']}/元曲/yuanqu.json"
    response = download(url)
    if response:
        for item in response.json():
            add_poem(item, "元")
    
    print(f"  总计: {len(poems):,} 首")
    save_json(poems, "poems.json")
    return poems

def download_couplets() -> list:
    print("\n[对联]")
    couplets = []
    couplet_id = 1
    
    for dataset in ["train", "test"]:
        in_url = f"{DATA_SOURCES['couplet']}/{dataset}/in.txt"
        out_url = f"{DATA_SOURCES['couplet']}/{dataset}/out.txt"
        
        in_resp = download(in_url)
        out_resp = download(out_url)
        
        if in_resp and out_resp:
            in_lines = in_resp.content.decode('utf-8').strip().split('\n')
            out_lines = out_resp.content.decode('utf-8').strip().split('\n')
            
            for in_line, out_line in zip(in_lines, out_lines):
                first = in_line.strip().replace(" ", "")
                second = out_line.strip().replace(" ", "")
                if first and second:
                    couplets.append({
                        "id": couplet_id,
                        "firstLine": first,
                        "secondLine": second,
                    })
                    couplet_id += 1
    
    print(f"  总计: {len(couplets):,} 条")
    save_json(couplets, "couplets.json")
    return couplets

def create_objectbox_database(data: dict):
    if not OBJECTBOX_AVAILABLE:
        print("\n[ObjectBox] 未安装，跳过数据库生成")
        print("  安装命令: pip install objectbox")
        return
    
    print("\n[ObjectBox] 生成数据库...")
    
    @Entity
    class Poem:
        id = Id()
        title = String()
        author = String()
        dynasty = String()
        content = String()
    
    @Entity
    class Idiom:
        id = Id()
        word = String()
        pinyin = String()
        explanation = String()
        derivation = String()
    
    @Entity
    class AllegoricalSaying:
        id = Id()
        riddle = String()
        answer = String()
    
    @Entity
    class Couplet:
        id = Id()
        firstLine = String()
        secondLine = String()
    
    @Entity
    class Riddle:
        id = Id()
        question = String()
        answer = String()
        source = String()
    
    @Entity
    class Character:
        id = Id()
        character = String()
        pinyin = String()
        strokes = Int32()
        radical = String()
        explanation = String()
    
    @Entity
    class Word:
        id = Id()
        ci = String()
        explanation = String()
    
    @Entity
    class ChineseColor:
        id = Id()
        name = String()
        hex = String()
        intro = String()
    
    model = Model()
    entities = [Poem, Idiom, AllegoricalSaying, Couplet, Riddle, Character, Word, ChineseColor]
    for entity in entities:
        model.add_entity(entity)
    
    if OBJECTBOX_DIR.exists():
        import shutil
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
                setattr(entity, dst, value if value is not None else "")
            entities.append(entity)
        box.put(*entities)
        print(f"  {entity_class.__name__}: {len(entities):,} 条")
    
    insert(Poem, data.get("poems", []), 
           {"title": "title", "author": "author", "dynasty": "dynasty", "content": "content"})
    insert(Idiom, data.get("idioms", []), 
           {"word": "word", "pinyin": "pinyin", "explanation": "explanation", "derivation": "derivation"})
    insert(AllegoricalSaying, data.get("allegorical_sayings", []), 
           {"riddle": "riddle", "answer": "answer"})
    insert(Couplet, data.get("couplets", []), 
           {"firstLine": "firstLine", "secondLine": "secondLine"})
    insert(Riddle, data.get("riddles", []), 
           {"question": "question", "answer": "answer", "source": "source"})
    insert(Character, data.get("characters", []), 
           {"character": "character", "pinyin": "pinyin", "strokes": "strokes", "radical": "radical", "explanation": "explanation"})
    insert(Word, data.get("words", []), 
           {"ci": "ci", "explanation": "explanation"})
    insert(ChineseColor, data.get("chinese_colors", []), 
           {"name": "name", "hex": "hex", "intro": "intro"})
    
    store.close()
    
    db_size = sum(f.stat().st_size for f in OBJECTBOX_DIR.glob("*"))
    print(f"  数据库大小: {db_size / (1024*1024):.2f} MB")

def main():
    print("=" * 60)
    print("中华文化数据库构建工具")
    print("=" * 60)
    
    ensure_dirs()
    all_data = {}
    
    print("\n[歇后语]")
    all_data["allegorical_sayings"] = download_xinhua_data(
        "xiehouyu.json", ["riddle", "answer"])
    
    print("\n[成语]")
    all_data["idioms"] = download_xinhua_data(
        "idiom.json", ["word", "pinyin", "explanation", "derivation"])
    
    print("\n[汉字]")
    all_data["characters"] = download_xinhua_data(
        "char.json", ["word", "pinyin", "strokes", "radical", "explanation"])
    
    print("\n[词语]")
    all_data["words"] = download_xinhua_data(
        "word.json", ["ci", "explanation"])
    
    print("\n[谜语]")
    all_data["riddles"] = download_riddles()
    
    print("\n[传统色]")
    all_data["chinese_colors"] = download_chinese_colors()
    
    all_data["poems"] = download_poems()
    all_data["couplets"] = download_couplets()
    
    metadata = {
        "version": "1.0.0",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": {k: len(v) for k, v in all_data.items()},
        "data_sources": {
            "poems": "https://github.com/chinese-poetry/chinese-poetry",
            "allegorical_sayings": "https://github.com/pwxcoo/chinese-xinhua",
            "idioms": "https://github.com/pwxcoo/chinese-xinhua",
            "characters": "https://github.com/pwxcoo/chinese-xinhua",
            "words": "https://github.com/pwxcoo/chinese-xinhua",
            "couplets": "https://github.com/wb14123/couplet-dataset",
            "riddles": "https://github.com/pku0xff/CC-Riddle",
            "chinese_colors": "https://github.com/zerosoul/chinese-colors",
        }
    }
    
    with open(OUTPUT_DIR / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    create_objectbox_database(all_data)
    
    print("\n" + "=" * 60)
    print("构建完成")
    print("=" * 60)
    for name, count in metadata["total_count"].items():
        print(f"  {name}: {count:,}")
    print("=" * 60)

if __name__ == "__main__":
    main()
