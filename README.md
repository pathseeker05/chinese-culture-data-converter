# 中华文化数据库构建工具

从开源数据源自动下载、清洗并生成 ObjectBox 数据库文件。

## 数据内容

| 类别 | 数据源 | 数量 | 许可证 |
|------|--------|------|--------|
| 诗词 | [chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) | 388,265 | MIT |
| 词语 | [pwxcoo/chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) | 264,434 | MIT |
| 成语 | [pwxcoo/chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) | 30,895 | MIT |
| 谜语 | [hefengbao/jingmo-data](https://github.com/hefengbao/jingmo-data) | 42,446 | MIT |
| 歇后语 | [pwxcoo/chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) | 14,032 | MIT |
| 汉字 | [pwxcoo/chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) | 16,142 | MIT |
| 诗文名句 | [hefengbao/jingmo-data](https://github.com/hefengbao/jingmo-data) | 10,000 | MIT |
| 经典诗文 | [hefengbao/jingmo-data](https://github.com/hefengbao/jingmo-data) | 955 | MIT |
| 谚语 | [hefengbao/jingmo-data](https://github.com/hefengbao/jingmo-data) | 964 | MIT |
| 对联 | [hefengbao/jingmo-data](https://github.com/hefengbao/jingmo-data) | 490 | MIT |
| 知识卡片 | [hefengbao/jingmo-data](https://github.com/hefengbao/jingmo-data) | 465 | MIT |
| 世界文化遗产 | [hefengbao/jingmo-data](https://github.com/hefengbao/jingmo-data) | 60 | MIT |
| 传统色 | [zerosoul/chinese-colors](https://github.com/zerosoul/chinese-colors) | 161 | ISC |
| 绕口令 | [hefengbao/jingmo-data](https://github.com/hefengbao/jingmo-data) | 45 | MIT |

## 快速开始

```bash
# 1. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # Linux / macOS

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行构建
python scripts/download.py
```

脚本自动完成：下载数据 → 生成 ObjectBox 数据库 → 校验完整性 → 对比原始数据源

## 项目结构

```
chinese-culture-data-converter/
├── scripts/
│   └── download.py          # 构建脚本
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 输出结构

```
output/
├── json/                    # JSON 格式中间数据
├── objectbox/               # ObjectBox 数据库文件
│   ├── data.mdb
│   └── lock.mdb
└── metadata.json            # 构建元信息
```

## 许可证

[MIT](LICENSE)
