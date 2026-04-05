# 中华文化数据库构建工具

一键构建高性能中华文化数据库，从开源数据源自动生成 ObjectBox 数据库文件。

## 下载

从 [Releases](https://github.com/pathseeker05/chinese-culture-data-converter/releases) 页面下载预构建的数据库文件。

## 使用

```bash
pip install -r requirements.txt
cd scripts && python download.py
```

## 数据

| 类别 | 数量 |
|:-----|------|
| 诗词 | 319,422 |
| 对联 | 744,930 |
| 词语 | 264,434 |
| 成语 | 30,895 |
| 谜语 | 27,517 |
| 汉字 | 16,142 |
| 歇后语 | 14,032 |
| 传统色 | 161 |
| **总计** | **1,417,333** |

## 输出

```
output/
├── json/          # JSON 格式数据
├── objectbox/     # ObjectBox 数据库
└── metadata.json  # 元数据
```

## 致谢

数据来源：
- [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) - 古典文集（唐诗、宋词、元曲）
- [Chinese-Poetry-Dataset](https://github.com/iphinsau/Chinese-Poetry-Dataset) - 宋诗
- [chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) - 新华字典
- [couplet-clean-dataset](https://github.com/v-zich/couplet-clean-dataset) - 对联
- [CC-Riddle](https://github.com/pku0xff/CC-Riddle) - 谜语
- [chinese-colors](https://github.com/zerosoul/chinese-colors) - 传统色

## 许可证

MIT
