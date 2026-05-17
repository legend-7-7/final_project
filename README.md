# 基于全球能源新闻情绪分析的 WTI 原油价格预测系统

## 1. 项目简介

本项目围绕“能源新闻文本信息能否辅助 WTI 原油价格预测”这一问题展开研究。

项目以能源相关新闻文本和 WTI 原油价格数据为基础，构建从新闻数据采集、文本预处理、主题分类、情感分析、新闻摘要、周度特征构建到油价预测与系统可视化展示的完整实验流程。

项目最终将形成可复现的 Python 代码、阶段性数据结果、预测模型结果以及基于 Streamlit 的可视化展示系统。

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

## 4. 技术路线

项目整体流程如下：

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

## 5. 功能模块

### 5.1 数据采集模块

负责采集或读取能源相关新闻数据和 WTI 原油价格数据，并保存为原始数据文件。

### 5.2 文本预处理模块

负责对新闻标题和正文进行拼接、清洗、分词、去停用词和词形还原，为后续分析提供标准化文本。

### 5.3 新闻主题分类模块

根据能源新闻内容，将新闻划分为不同主题类别，例如供给、需求、地缘政治、库存、金融市场、天气事件等。

### 5.4 情感分析模块

计算新闻文本的情感分数，并统计积极、消极和中立新闻的分布情况。

### 5.5 新闻摘要模块

基于文本特征提取新闻关键句，生成简短摘要，用于信息压缩和系统展示。

### 5.6 特征工程模块

将新闻数量、情感分数、主题分布等文本指标按周聚合，并与 WTI 原油价格数据进行时间对齐。

### 5.7 油价预测模块

构建预测模型，对 WTI 原油价格进行预测，并使用 MAE、RMSE、MAPE 等指标评估模型效果。

### 5.8 可视化系统模块

使用 Streamlit 构建可视化系统，展示数据概况、主题分类、情感指标、新闻摘要、预测结果和模型评估。

## 6. 项目结构

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
│   ├── processed/  
│   └── external/  
├── models/  
├── results/  
├── app/  
│   ├── Home.py  
│   └── pages/  
├── docs/  
└── tests/

## 7. 技术工具

本项目计划使用以下技术工具：

- Python
- pandas
- numpy
- scikit-learn
- nltk / spaCy
- matplotlib
- plotly
- streamlit
- tensorflow / keras 或 pytorch

## 8. 分支说明

- main：最终稳定版本
- dev：开发整合分支
- feature/project-structure：项目结构搭建
- feature/readme：项目说明文档
- feature/data-collection：数据采集模块
- feature/text-processing：文本预处理模块
- feature/sentiment-analysis：情感分析模块
- feature/summarization：新闻摘要模块
- feature/feature-engineering：特征工程模块
- feature/price-prediction：油价预测模块
- feature/streamlit-ui：可视化系统模块
- feature/report：课程报告整理

## 9. 运行方式

后续完成系统开发后，可使用以下命令运行：

streamlit run app/Home.py

## 10. 当前进度

- [x] 项目结构搭建
- [x] README 初稿
- [ ] 数据采集
- [ ] 文本预处理
- [ ] 新闻主题分类
- [ ] 情感分析
- [ ] 新闻摘要
- [ ] 特征工程
- [ ] 油价预测
- [ ] Streamlit 可视化系统
- [ ] 课程报告整理