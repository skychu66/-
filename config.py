import os
import re
import math
import json
from collections import Counter
from datetime import datetime
import requests

# ========== 配置 ==========
API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
MODEL_NAME = os.getenv('MODEL_NAME', 'qwen-turbo')  # 使用更快的模型
API_BASE = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
KB_PATH = os.path.join(os.path.dirname(__file__), 'knowledge')
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
HISTORY_LENGTH = 5
