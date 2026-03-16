 
    测试环境
    uvicorn app:app --host 0.0.0.0 --port 9099 --workers 4 --env-file .env.dev
    # 生产环境
    uvicorn app:app --host 0.0.0.0 --port 9099 --workers 4 --env-file .env.prod

    # 生产启动命令
    nohup /sgz/gs-dvd-backend/venv/bin/uvicorn app:app --host 0.0.0.0 --port 9099 --workers 4 --env-file .env.prod > /sgz/gs-dvd-backend/uvicorn.log 2>&1 &
    
    # 运维
    netstat -tulpn | grep 9099
    ps -ef | grep uvicorn | grep -v grep
    fuser -k 9099/tcp
    pkill -f uvicorn
    
    查看worker
    ps -ef | grep "uvicorn app:app --host 0.0.0.0 --port 9099" | grep -v grep
    ps -ef | grep 111666 | grep -v grep | wc -l

    nohup /sgz/gs-dvd-backend/restart.sh > /sgz/gs-dvd-backend/restart.log 2>&1 &
    
    #前端配置nginx必须加
    # API 请求代理到后端
    location /prod-api/ {
        proxy_pass         http://127.0.0.1:9099/;
        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
    try_files $uri $uri/ /index.html;


    #  重启
    cd /sgz/gs-dvd-backend
    git pull
    # 重新安装可能新增的依赖
    ./venv/bin/pip install -r requirements.txt
    # 重启服务
    supervisorctl restart gs-dvd-backend

### supervisord方案
    路径:/etc/supervisord.d/gs-dvd.ini
    ```
    [program:gs-dvd-backend]
    ; 启动命令，注意要使用虚拟环境中的路径
    command=/sgz/gs-dvd-backend/venv/bin/uvicorn app:app --host 0.0.0.0 --port 9099 --workers 4 --env-file /sgz/gs-dvd-backend/.env.prod
    
    ; 运行目录
    directory=/sgz/gs-dvd-backend
    
    ; 启动参数
    autostart=true          ; 随 supervisor 启动而启动
    autorestart=unexpected  ; 异常退出后自动重启
    startsecs=5             ; 启动 5 秒后没有异常退出才算启动成功
    stopwaitsecs=10         ; 停止时等待时间
    
    ; 用户权限（建议使用非 root 用户，如果目录权限允许）
    user=root
    
    ; 日志配置
    stdout_logfile=/sgz/gs-dvd-backend/uvicorn.log
    stdout_logfile_maxbytes=50MB   ; 日志轮转大小
    stdout_logfile_backups=10       ; 保留 10 个备份
    stderr_logfile=/sgz/gs-dvd-backend/uvicorn.err.log
    ```
    重启
    supervisorctl restart gs-dvd-backend
    重载配置
    supervisorctl update
    