# 基于能源新闻情绪分析的 WTI 原油价格预测系统课程报告

## 1. 项目背景

WTI 原油价格是国际能源市场中的重要价格指标之一，其变化受到供需关系、库存水平、地缘政治、宏观经济环境、极端天气以及突发事件等多种因素影响。

传统油价预测方法通常依赖历史价格、成交量或宏观经济指标等结构化数据。然而，在实际能源市场中，大量重要信息往往首先以新闻文本形式出现。能源新闻能够反映市场事件、政策变化、供需预期和投资者情绪，因此新闻文本信息可以作为油价预测的重要补充。

本项目围绕“能源新闻文本信息能否辅助 WTI 原油价格预测”这一问题，构建了从新闻数据采集、文本预处理、主题分类、情感分析、新闻摘要、周度特征构建到油价预测和系统展示的完整实验流程。

## 2. 项目目标

本项目主要目标如下：

1. 构建能源新闻文本数据集；
2. 对新闻文本进行清洗、分词和结构化处理；
3. 建立能源新闻主题分类体系；
4. 计算新闻情感指标和情感极性分布；
5. 提取新闻摘要，降低新闻阅读成本；
6. 将新闻文本特征与 WTI 油价数据进行周度对齐；
7. 构建油价预测模型并进行结果评估；
8. 使用 Streamlit 搭建可视化展示系统。

## 3. 数据来源

本项目使用两类数据：

### 3.1 能源新闻数据

能源新闻数据来源于 EIA RSS 信息源。项目通过程序采集新闻标题、摘要、链接、来源等字段，并生成原始新闻数据文件：

```text
data/raw/eia_energy_news.csv
````

新闻数据主要用于后续文本预处理、主题分类、情感分析和摘要提取。

### 3.2 WTI 油价数据

WTI 油价数据保存于本地文件：

```text
data/raw/wti_price.csv
```

数据字段包括日期和 WTI 原油价格，用于后续周度聚合和价格预测建模。

## 4. 项目技术路线

项目整体流程如下：

```text
能源新闻数据采集
→ 文本预处理
→ 新闻主题分类
→ 情感分析
→ 新闻摘要提取
→ 周度特征构建
→ WTI 油价预测
→ Streamlit 可视化展示
```

各阶段输出文件如下：

| 阶段    | 输入文件                               | 输出文件                                                |
| ----- | ---------------------------------- | --------------------------------------------------- |
| 数据采集  | EIA RSS、WTI 油价数据                   | data/raw/eia_energy_news.csv、data/raw/wti_price.csv |
| 文本预处理 | data/raw/eia_energy_news.csv       | data/processed/processed_news.csv                   |
| 主题分类  | data/processed/processed_news.csv  | data/processed/classified_news.csv                  |
| 情感分析  | data/processed/classified_news.csv | data/processed/sentiment_news.csv                   |
| 新闻摘要  | data/processed/sentiment_news.csv  | data/processed/summarized_news.csv                  |
| 特征工程  | summarized_news.csv、wti_price.csv  | data/processed/weekly_features.csv                  |
| 油价预测  | data/processed/weekly_features.csv | results/price_prediction_results.csv                |

## 5. 数据采集模块

数据采集模块位于：

```text
src/data_collection.py
```

该模块主要完成以下任务：

1. 从 EIA RSS 中采集能源相关新闻；
2. 清洗 RSS 中的 HTML 标签和多余空白；
3. 提取新闻标题、摘要、链接、来源等字段；
4. 读取本地 WTI 油价数据；
5. 将原始数据保存到 `data/raw/` 目录。

考虑到网络请求可能存在超时或限流问题，本项目采用“新闻在线采集 + 油价本地读取”的方式，保证实验流程可以稳定运行。

## 6. 文本预处理模块

文本预处理模块位于：

```text
src/text_preprocessing.py
```

该模块对新闻文本进行标准化处理，主要步骤包括：

1. 合并新闻标题和摘要；
2. 转换为小写；
3. 去除 URL、数字和标点符号；
4. 去除停用词；
5. 生成清洗后的文本；
6. 统计词项数量。

输出文件为：

```text
data/processed/processed_news.csv
```

该文件为后续主题分类、情感分析和摘要提取提供基础文本数据。

## 7. 新闻主题分类模块

新闻主题分类模块位于：

```text
src/news_classification.py
```

本项目采用关键词规则匹配的方法对新闻进行主题分类。主题类别包括：

* supply：供给相关
* demand：需求相关
* inventory：库存相关
* geopolitics：地缘政治相关
* financial_market：金融市场相关
* weather_event：天气事件相关
* natural_gas：天然气相关
* energy_transition：能源转型相关
* other：其他类别

模块会根据新闻文本中不同主题关键词的命中次数，计算主题得分，并选择得分最高的主题作为新闻类别。

输出文件为：

```text
data/processed/classified_news.csv
```

该文件包含新闻主题、主题得分和分类置信度等字段。

## 8. 情感分析模块

情感分析模块位于：

```text
src/sentiment_analysis.py
```

本项目采用词典规则方法计算新闻情感。情感词典包括两部分：

1. 通用积极词和消极词；
2. 面向油价影响的领域词，例如 bullish 和 bearish 相关表达。

最终情感分数由通用情感得分和领域情感得分共同构成。根据情感分数，新闻被划分为：

* positive：积极
* negative：消极
* neutral：中立

输出文件包括：

```text
data/processed/sentiment_news.csv
results/sentiment_summary.csv
```

其中 `sentiment_news.csv` 保存每条新闻的情感分析结果，`sentiment_summary.csv` 保存整体情感分布统计。

## 9. 新闻摘要模块

新闻摘要模块位于：

```text
src/summarization.py
```

本项目采用抽取式摘要方法生成新闻摘要。算法主要考虑以下因素：

1. 句子中的高频词；
2. 句子与标题的词项重合度；
3. 句子在原文中的位置。

系统会对新闻中的句子进行打分，选取得分较高的句子作为摘要，并保留原始顺序，以提高摘要的可读性。

输出文件包括：

```text
data/processed/summarized_news.csv
results/summarization_summary.csv
```

其中 `summarization_summary.csv` 统计了新闻数量、平均原文长度、平均摘要长度和平均压缩率等指标。

## 10. 特征工程模块

特征工程模块位于：

```text
src/feature_engineering.py
```

由于新闻数据和油价数据频率不同，本项目将两类数据统一聚合到周度层面。

周度新闻特征包括：

* 新闻数量；
* 平均情感分数；
* 主题分类置信度；
* 摘要压缩率；
* 不同情感类别数量和占比；
* 不同主题类别数量。

周度油价特征包括：

* 周开盘价格；
* 周收盘价格；
* 周平均价格；
* 周最高价格；
* 周最低价格；
* 上一周收盘价；
* 下一周收盘价预测目标。

输出文件包括：

```text
data/processed/weekly_features.csv
results/feature_engineering_summary.csv
```

该文件是油价预测模型的主要输入。

## 11. 油价预测模块

油价预测模块位于：

```text
src/price_prediction.py
```

本项目基于周度特征构建 WTI 原油价格预测模型。预测目标为下一周 WTI 收盘价格。

模型包括：

1. Baseline：使用当前周收盘价预测下一周收盘价；
2. Linear Regression：线性回归模型；
3. Ridge Regression：岭回归模型；
4. Random Forest：随机森林回归模型。

模型评价指标包括：

* MAE：平均绝对误差；
* RMSE：均方根误差；
* MAPE：平均绝对百分比误差。

输出文件包括：

```text
results/price_prediction_results.csv
results/price_prediction_metrics.csv
results/price_prediction_feature_importance.csv
```

其中 `price_prediction_metrics.csv` 保存不同模型的评价结果，`price_prediction_feature_importance.csv` 保存特征重要性分析结果。

## 12. 可视化系统

本项目使用 Streamlit 构建可视化系统。系统入口为：

```text
app/Home.py
```

运行命令为：

```bash
streamlit run app/Home.py
```

系统包括以下页面：

1. Home：首页总览；
2. Data Overview：数据总览；
3. Topic Classification：主题分类分析；
4. Sentiment Analysis：情感分析；
5. News Summary：新闻摘要展示；
6. Price Prediction：油价预测结果；
7. Result Review：结果复核。

系统能够展示新闻数据、油价数据、主题分布、情感分布、摘要结果、预测指标和模型结果，便于对实验流程进行整体复核。

## 13. 项目结构

```text
final_project/
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── data_collection.py
│   ├── text_preprocessing.py
│   ├── news_classification.py
│   ├── sentiment_analysis.py
│   ├── summarization.py
│   ├── feature_engineering.py
│   ├── price_prediction.py
│   └── utils.py
├── data/
│   ├── raw/
│   └── processed/
├── results/
├── app/
│   ├── Home.py
│   └── pages/
├── docs/
│   └── report.md
└── tests/
```

## 14. 实验结果总结

本项目完成了从能源新闻文本到 WTI 油价预测的完整实验流程。通过文本预处理、主题分类、情感分析和摘要提取，非结构化新闻文本被转换为可用于建模的结构化特征。

在预测阶段，项目构建了基准模型、线性回归、岭回归和随机森林模型，并使用 MAE、RMSE、MAPE 等指标进行评估。通过模型结果可以对比不同方法在小样本周度数据上的预测效果。

可视化系统进一步将各阶段结果集中展示，使项目不仅包含后端数据处理和建模流程，也具备可演示的系统界面。

## 15. 项目不足与改进方向

本项目仍存在一些不足：

1. 新闻数据规模较小，后续可以扩展到更长时间范围；
2. 当前主题分类主要基于关键词规则，后续可使用机器学习或深度学习分类模型；
3. 当前情感分析主要基于词典规则，后续可引入金融领域预训练语言模型；
4. 当前油价预测样本数量有限，深度学习模型暂未充分使用；
5. 后续可以接入更稳定的数据 API，提高自动化数据采集能力。

未来可以进一步扩展新闻数据规模，引入更多宏观经济变量和市场指标，并尝试 LSTM、GRU 等时间序列深度学习模型，以提升预测效果。

## 16. 结论

本项目构建了一个基于能源新闻情绪分析的 WTI 原油价格预测系统，实现了从新闻数据采集、文本处理、主题分类、情感分析、摘要提取、周度特征构建到油价预测和可视化展示的完整流程。

实验表明，新闻文本信息可以被转化为结构化指标，并作为油价预测模型的补充特征。虽然当前项目仍属于课程实验性质，但整体流程完整，具有较好的可复现性和展示性。
