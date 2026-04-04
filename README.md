# 中华文化数据库构建工具

一键构建高性能中华文化数据库，从开源数据源自动生成 ObjectBox 数据库文件。

## 使用

```bash
pip install -r requirements.txt
cd scripts && python download.py
```

## 数据

| 类别 | 数量 |
|:-----|------|
| 诗词 | 380,000+ |
| 对联 | 770,000+ |
| 词语 | 264,000+ |
| 成语 | 30,000+ |
| 谜语 | 27,000+ |
| 汉字 | 16,000+ |
| 歇后语 | 14,000+ |
| 传统色 | 161 |

## 输出

```
output/
├── json/          # JSON 格式数据
├── objectbox/     # ObjectBox 数据库
└── metadata.json  # 元数据
```

## 致谢

数据来源：
- [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) - 古典文集
- [chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) - 新华字典
- [couplet-dataset](https://github.com/wb14123/couplet-dataset) - 对联
- [CC-Riddle](https://github.com/pku0xff/CC-Riddle) - 谜语
- [chinese-colors](https://github.com/zerosoul/chinese-colors) - 传统色

## 许可证

MIT
