 
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