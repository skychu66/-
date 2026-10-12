@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   RAG 知识库问答系统
echo ========================================
echo.
echo 正在启动服务...
echo.
python app.py
pause
