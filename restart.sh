#!/bin/bash

# 定义核心配置（方便后续修改）
PROJECT_DIR="/sgz/gs-dvd-backend"
LOG_FILE="${PROJECT_DIR}/uvicorn.log"
ENV_FILE="${PROJECT_DIR}/.env.prod"
PORT=9099
WORKERS=4

# 脚本执行过程中的日志输出函数
log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

# 第一步：拉取最新代码
log_info "开始拉取最新代码..."
cd "${PROJECT_DIR}" || {
    log_error "进入项目目录 ${PROJECT_DIR} 失败，脚本退出"
    exit 1
}

git pull
if [ $? -ne 0 ]; then
    log_error "代码拉取失败，请检查仓库连接或分支状态"
    exit 1
fi
log_info "代码拉取完成"

# 第二步：查找并杀死旧进程
log_info "开始清理旧的 uvicorn 进程..."
# 方式1：通过端口查找进程（更精准）
OLD_PIDS=$(lsof -ti :${PORT})
# 方式2：备用方案 - 通过命令特征查找进程（防止端口占用检测失效）
if [ -z "${OLD_PIDS}" ]; then
    OLD_PIDS=$(ps aux | grep "uvicorn app:app --host 0.0.0.0 --port ${PORT}" | grep -v grep | awk '{print $2}')
fi

if [ -n "${OLD_PIDS}" ]; then
    log_info "找到旧进程ID：${OLD_PIDS}，开始杀死进程..."
    kill -9 ${OLD_PIDS}
    if [ $? -eq 0 ]; then
        log_info "旧进程已成功杀死"
    else
        log_error "杀死旧进程失败，请手动检查"
        exit 1
    fi
else
    log_info "未找到运行中的旧进程，跳过杀死步骤"
fi

# 第三步：重启服务
log_info "开始启动后端服务..."
nohup "${PROJECT_DIR}/venv/bin/uvicorn" app:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers ${WORKERS} \
    --env-file ${ENV_FILE} > ${LOG_FILE} 2>&1 &

# 检查服务是否启动成功
sleep 2
NEW_PID=$(lsof -ti :${PORT})
if [ -n "${NEW_PID}" ]; then
    log_info "服务启动成功！进程ID：${NEW_PID}"
else
    log_error "服务启动失败，请查看日志：${LOG_FILE}"
    exit 1
fi

log_info "脚本执行完成"
exit 0