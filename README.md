 
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

