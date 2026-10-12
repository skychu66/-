import os
import re
import math
import json
import hashlib
from collections import Counter
from datetime import datetime
import requests
from config import *

SIMILARITY_THRESHOLD = 0.001
CACHE_EXPIRE = 300

class SimpleRAGEngine:
    def __init__(self):
        self.chunks = []
        self.chunk_sources = []
        self.chat_history = []
        self.cache = {}
        
    def _tokenize(self, text):
        english_tokens = re.findall(r'[a-zA-Z0-9_]+', text)
        chinese_tokens = re.findall(r'[\u4e00-\u9fff]+', text)
        return english_tokens + chinese_tokens
    
    def extract_keywords(self, question):
        stop_words = {'什么', '怎么', '如何', '的', '是', '在', '我', '你', '他', '她', '它', 
                      '这', '那', '有', '没有', '吗', '呢', '吧', '啊', '请', '问', '一下', '多少',
                      '相关', '内容', '信息', '怎么样', '哪些', '查询', '改成', '数据', '参数',
                      '改枪码', '改枪', '枪码', '码'}  # 移除这些停止词
        tokens = self._tokenize(question)
        keywords = [t.lower() for t in tokens if t.lower() not in stop_words and len(t) > 0]
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        return unique_keywords
    
    def calculate_match_score(self, question, chunk):
        keywords = self.extract_keywords(question)
        chunk_lower = chunk.lower()
        
        if not keywords:
            return 0, [], 0
        
        score = 0
        matched_keywords = []
        match_count = 0
        
        for kw in keywords:
            if kw in chunk_lower:
                score += 10
                matched_keywords.append(kw)
                match_count += 1
        
        # 所有关键词都匹配才给高分奖励
        if match_count == len(keywords):
            score += 50
        
        return score, matched_keywords, match_count
    
    def _tf_idf(self, text, corpus):
        tokens = self._tokenize(text)
        tf = Counter(tokens)
        idf = {}
        for word in tf.keys():
            count = sum(1 for doc in corpus if word in self._tokenize(doc))
            idf[word] = math.log(len(corpus) / (1 + count))
        vector = {}
        for word, tf_val in tf.items():
            vector[word] = tf_val * idf.get(word, 0)
        return vector
    
    def _cosine_similarity(self, vec1, vec2):
        if not vec1 or not vec2:
            return 0.0
        intersection = set(vec1.keys()) & set(vec2.keys())
        if not intersection:
            return 0.0
        numerator = sum(vec1[w] * vec2[w] for w in intersection)
        denom1 = math.sqrt(sum(v**2 for v in vec1.values()))
        denom2 = math.sqrt(sum(v**2 for v in vec2.values()))
        if denom1 == 0 or denom2 == 0:
            return 0.0
        return numerator / (denom1 * denom2)
    
    def load_knowledge(self, folder_path=None):
        if folder_path is None:
            folder_path = KB_PATH
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return f'知识库文件夹已创建: {folder_path}\n请在此文件夹中放入TXT文件'
        
        txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        if not txt_files:
            return f'知识库中没有找到TXT文件\n路径: {folder_path}'
        
        self.chunks = []
        self.chunk_sources = []
        
        for file in txt_files:
            file_path = os.path.join(folder_path, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return f'读取失败 {file}: {str(e)}'
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    self.chunks.append(line)
                    self.chunk_sources.append(file)
        
        return f'知识库加载完成！\n共 {len(self.chunks)} 个文本片段\n来自 {len(txt_files)} 个文件'
    
    def retrieve(self, question, top_k=3):
        if not self.chunks:
            return []
        
        keywords = self.extract_keywords(question)
        results = []
        
        for i, chunk in enumerate(self.chunks):
            kw_score, matched, match_count = self.calculate_match_score(question, chunk)
            
            query_vec = self._tf_idf(question, self.chunks)
            chunk_vec = self._tf_idf(chunk, self.chunks)
            sim = self._cosine_similarity(query_vec, chunk_vec)
            
            final_score = kw_score + sim * 0.1
            
            results.append((final_score, kw_score, sim, matched, match_count, i, chunk, self.chunk_sources[i]))
        
        results.sort(key=lambda x: (x[4], x[0]), reverse=True)
        
        # 只返回所有关键词都匹配的结果
        filtered = [(fs, kws, s, m, mc, i, c, src) for fs, kws, s, m, mc, i, c, src in results 
                    if mc == len(keywords) and fs >= 50]
        
        return [(sim, chunk, source, matched) for _, _, sim, matched, _, _, chunk, source in filtered[:top_k]]
    
    def get_cache_key(self, question):
        return hashlib.md5(question.encode('utf-8')).hexdigest()
    
    def ask(self, question):
        if not self.chunks:
            return '知识库为空，请先加载知识库', []
        
        cache_key = self.get_cache_key(question)
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.now().timestamp() - cached['time'] < CACHE_EXPIRE:
                return cached['answer'], cached['sources']
        
        results = self.retrieve(question, top_k=5)
        if not results:
            return '抱歉，还未录入你查询的信息。', []
        
        # 直接返回内容
        if len(results) == 1:
            answer = results[0][1]
        else:
            answer = "\n\n".join([r[1] for r in results])
        
        sources = list(set([src for _, _, src, _ in results]))
        
        full_answer = answer
        self.cache[cache_key] = {'answer': full_answer, 'sources': sources, 'time': datetime.now().timestamp()}
        
        return full_answer, sources

engine = SimpleRAGEngine()
