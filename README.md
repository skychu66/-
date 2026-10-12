# RAG 知识库问答系统 - 简化版

## 功能特点
- 使用 TF-IDF + 余弦相似度进行文本检索
- 调用通义千问 API 生成回答
- Flask Web 界面，本地运行
- 保留5轮对话历史
- 显示参考来源

## 安装依赖
```bash
pip install flask requests -i https://pypi.tuna.tsinghua.edu.cn/simple
```
（flask 和 requests 已预装）

## 使用方法
1. 将 TXT 文件放入 `knowledge/` 文件夹
2. 运行 `python app.py`
3. 浏览器访问 http://127.0.0.1:5000

## 文件结构
- config.py - 配置
- rag_engine.py - RAG 核心引擎
- app.py - Flask Web 应用
- templates/index.html - 前端界面
- knowledge/ - 知识库文件夹（放 TXT 文件）
