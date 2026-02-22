# 使用多阶段构建，支持本地开发
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

# 复制应用代码
COPY . /app /app/

# 创建数据目录
RUN mkdir -p /app/data

# 设置权限
RUN chmod +x /app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 启动应用
CMD ["python", "main.py", "--webui"]
