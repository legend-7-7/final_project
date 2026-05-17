# 基于全球能源新闻情绪分析的 WTI 原油价格预测系统

## 1. 项目简介

本项目围绕“能源新闻文本信息能否辅助 WTI 原油价格预测”这一问题展开研究。

项目以能源相关新闻文本和 WTI 原油价格数据为基础，构建了从新闻数据采集、文本预处理、主题分类、情感分析、新闻摘要、周度特征构建到油价预测与系统可视化展示的完整实验流程。

项目最终形成了可复现的 Python 代码、阶段性数据结果、预测模型结果以及基于 Streamlit 的可视化展示系统。

## 2. 研究背景

WTI 原油价格受到供需关系、库存变化、地缘政治、宏观金融环境、极端天气和突发事件等多种因素影响。

传统油价预测方法通常依赖历史价格、成交量或宏观经济变量等结构化数据。然而，能源市场中的许多重要信息往往首先以新闻文本形式出现。新闻报道能够反映市场事件、投资者预期、风险冲击和舆论情绪，因此新闻文本信息可以作为油价预测的重要补充特征。

## 3. 项目目标

本项目主要目标包括：

- 构建能源新闻文本数据集
- 对新闻文本进行清洗、分词和结构化处理
- 建立能源新闻主题分类体系
- 计算新闻情感指标和情感极性分布
- 提取新闻摘要，降低新闻阅读成本
- 将新闻文本特征与 WTI 油价时间序列进行周度对齐
- 构建油价预测模型并进行结果评估
- 使用 Streamlit 搭建可视化展示系统

## 4. 数据来源

本项目使用两类数据：

### 4.1 能源新闻数据

能源新闻数据来自 EIA RSS 信息源。项目采集新闻标题、摘要、链接、来源等字段，并保存为：

```text
data/raw/eia_energy_news.csv
````

### 4.2 WTI 油价数据

WTI 油价数据保存于本地文件：

```text
data/raw/wti_price.csv
```

该数据用于后续周度特征构建和油价预测建模。

## 5. 技术路线

项目整体流程如下：

```text
能源新闻数据采集
→ 文本预处理
→ 新闻主题分类
→ 情感分析
→ 新闻摘要提取
→ 周度文本特征构建
→ WTI 油价数据对齐
→ 油价预测模型训练
→ 预测结果评估
→ Streamlit 可视化展示
```

## 6. 功能模块

### 6.1 数据采集模块

对应文件：

```text
src/data_collection.py
```

负责采集 EIA 能源相关新闻，并读取本地 WTI 油价数据。

输出文件：

```text
data/raw/eia_energy_news.csv
data/raw/wti_price.csv
```

### 6.2 文本预处理模块

对应文件：

```text
src/text_preprocessing.py
```

负责对新闻文本进行清洗、分词、去停用词和结构化处理。

输出文件：

```text
data/processed/processed_news.csv
```

### 6.3 新闻主题分类模块

对应文件：

```text
src/news_classification.py
```

根据关键词规则将新闻划分为供给、需求、库存、地缘政治、金融市场、天气事件、天然气、能源转型等主题。

输出文件：

```text
data/processed/classified_news.csv
```

### 6.4 情感分析模块

对应文件：

```text
src/sentiment_analysis.py
```

基于通用情感词典和能源领域词典计算新闻情感分数，并划分为 positive、negative、neutral 三类。

输出文件：

```text
data/processed/sentiment_news.csv
results/sentiment_summary.csv
```

### 6.5 新闻摘要模块

对应文件：

```text
src/summarization.py
```

基于句子词频、标题重合度和句子位置权重生成抽取式新闻摘要。

输出文件：

```text
data/processed/summarized_news.csv
results/summarization_summary.csv
```

### 6.6 特征工程模块

对应文件：

```text
src/feature_engineering.py
```

将新闻数量、情感分数、主题分布、摘要压缩率等文本指标按周聚合，并与 WTI 油价数据进行时间对齐。

输出文件：

```text
data/processed/weekly_features.csv
results/feature_engineering_summary.csv
```

### 6.7 油价预测模块

对应文件：

```text
src/price_prediction.py
```

基于周度特征构建 WTI 油价预测模型，模型包括：

* Baseline
* Linear Regression
* Ridge Regression
* Random Forest

评价指标包括：

* MAE
* RMSE
* MAPE

输出文件：

```text
results/price_prediction_results.csv
results/price_prediction_metrics.csv
results/price_prediction_feature_importance.csv
```

### 6.8 可视化系统模块

对应目录：

```text
app/
```

使用 Streamlit 构建可视化展示系统，包括：

* 首页总览
* 数据总览
* 主题分类分析
* 情感分析
* 新闻摘要展示
* 油价预测结果
* 结果复核

运行入口：

```text
app/Home.py
```

## 7. 项目结构

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
│   │   ├── eia_energy_news.csv
│   │   └── wti_price.csv
│   ├── processed/
│   │   ├── processed_news.csv
│   │   ├── classified_news.csv
│   │   ├── sentiment_news.csv
│   │   ├── summarized_news.csv
│   │   └── weekly_features.csv
│   └── external/
├── results/
│   ├── sentiment_summary.csv
│   ├── summarization_summary.csv
│   ├── feature_engineering_summary.csv
│   ├── price_prediction_results.csv
│   ├── price_prediction_metrics.csv
│   └── price_prediction_feature_importance.csv
├── app/
│   ├── Home.py
│   └── pages/
│       ├── 1_Data_Overview.py
│       ├── 2_Topic_Classification.py
│       ├── 3_Sentiment_Analysis.py
│       ├── 4_News_Summary.py
│       ├── 5_Price_Prediction.py
│       └── 6_Result_Review.py
├── docs/
│   └── report.md
└── tests/
```

## 8. 技术工具

本项目使用以下技术工具：

* Python
* pandas
* numpy
* requests
* python-dateutil
* scikit-learn
* plotly
* streamlit
* Git / GitHub

## 9. 安装依赖

```bash
pip install -r requirements.txt
```

如果下载较慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 10. 运行方式

### 10.1 数据采集

```bash
python src/data_collection.py
```

### 10.2 文本预处理

```bash
python src/text_preprocessing.py
```

### 10.3 新闻主题分类

```bash
python src/news_classification.py
```

### 10.4 情感分析

```bash
python src/sentiment_analysis.py
```

### 10.5 新闻摘要

```bash
python src/summarization.py
```

### 10.6 特征工程

```bash
python src/feature_engineering.py
```

### 10.7 油价预测

```bash
python src/price_prediction.py
```

### 10.8 启动可视化系统

```bash
streamlit run app/Home.py
```

## 11. 分支说明

* main：最终稳定版本
* dev：开发整合分支
* feature/project-structure：项目结构搭建
* feature/readme：项目说明文档
* feature/data-collection：数据采集模块
* feature/text-processing：文本预处理模块
* feature/topic-classification：新闻主题分类模块
* feature/sentiment-analysis：情感分析模块
* feature/summarization：新闻摘要模块
* feature/feature-engineering：特征工程模块
* feature/price-prediction：油价预测模块
* feature/streamlit-ui：可视化系统模块
* feature/report：课程报告整理

## 12. 当前进度

* [x] 项目结构搭建
* [x] README 文档
* [x] 数据采集
* [x] 文本预处理
* [x] 新闻主题分类
* [x] 情感分析
* [x] 新闻摘要
* [x] 特征工程
* [x] 油价预测
* [x] Streamlit 可视化系统
* [x] 课程报告整理

## 13. 项目说明

本项目为课程大作业项目，重点在于构建完整的数据分析与预测流程。由于样本规模有限，预测结果主要用于展示新闻文本特征在油价预测任务中的应用流程，而不是作为真实投资或交易依据。