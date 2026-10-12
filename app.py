"""
Flask Web 界面 - RAG 知识库问答系统
"""
from flask import Flask, render_template, request, jsonify
from rag_engine import engine
from config import HISTORY_LENGTH
from datetime import datetime

app = Flask(__name__)

# 启动时自动加载知识库
@app.before_request
def load_kb_if_needed():
    if not engine.chunks:
        engine.load_knowledge()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/load_kb', methods=['POST'])
def load_kb():
    status = engine.load_knowledge()
    return jsonify({"status": status})

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '').strip()
    if not question:
        return jsonify({"error": "问题不能为空"})
    answer, sources = engine.ask(question)
    engine.chat_history.append({"role": "user", "content": question, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    engine.chat_history.append({"role": "assistant", "content": answer, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    if len(engine.chat_history) > HISTORY_LENGTH * 2:
        engine.chat_history = engine.chat_history[-HISTORY_LENGTH * 2:]
    return jsonify({"answer": answer, "sources": sources, "history_count": len(engine.chat_history) // 2})

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    engine.chat_history = []
    return jsonify({"status": "对话历史已清空"})

@app.route('/api/kb_status', methods=['GET'])
def kb_status():
    return jsonify({"chunk_count": len(engine.chunks), "file_count": len(set(engine.chunk_sources)), "history_count": len(engine.chat_history) // 2})

if __name__ == '__main__':
    print("=" * 50)
    print("RAG 知识库问答系统")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
