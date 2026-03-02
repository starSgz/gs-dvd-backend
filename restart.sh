#!/bin/bash

# 定义核心配置
PROJECT_DIR="/sgz/gs-dvd-backend"
LOG_FILE="${PROJECT_DIR}/uvicorn.log"
ENV_FILE="${PROJECT_DIR}/.env.prod"
PORT=9099
WORKERS=4

# 日志函数
log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

# 第一步：拉取代码
log_info "开始拉取最新代码..."
cd "${PROJECT_DIR}" || {
    log_error "进入项目目录失败"
    exit 1
}
git pull || {
    log_error "代码拉取失败"
    exit 1
}
log_info "代码拉取完成"

# 第二步：彻底杀死所有关联进程（解决workers残留）
log_info "清理所有uvicorn相关进程..."
# -f：匹配命令行，-9：强制杀死，|| true：没进程时不报错
pkill -9 -f "uvicorn app:app --port ${PORT}" || true
# 额外检查端口，确保释放
OLD_PIDS=$(lsof -ti :${PORT})
if [ -n "${OLD_PIDS}" ]; then
    kill -9 ${OLD_PIDS} || true
fi
# 等待端口释放（解决TIME_WAIT）
sleep 3
log_info "进程清理完成"

# 第三步：检查依赖（可选，新增）
log_info "检查Python依赖..."
${PROJECT_DIR}/venv/bin/pip install -r ${PROJECT_DIR}/requirements.txt --quiet || {
    log_error "依赖安装失败，继续启动服务..."
}

# 第四步：启动服务
log_info "启动后端服务..."
# 先清空旧日志（避免日志过大）
> ${LOG_FILE}
# 启动服务
nohup "${PROJECT_DIR}/venv/bin/uvicorn" app:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers ${WORKERS} \
    --env-file ${ENV_FILE} > ${LOG_FILE} 2>&1 &

# 验证启动
sleep 5  # 延长等待时间，确保服务完全启动
NEW_PID=$(lsof -ti :${PORT})
if [ -n "${NEW_PID}" ]; then
    log_info "服务启动成功！进程ID：${NEW_PID}"
else
    log_error "服务启动失败，日志路径：${LOG_FILE}"
    # 打印日志前10行，方便快速排查
    log_error "日志前10行："
    head -10 ${LOG_FILE}
    exit 1
fi

log_info "脚本执行完成"
exit 0