### 7.30 更新
- 可显示中文 
- 增加英文 --> 中文的翻译功能 

### 7.31 更新 
-  容器化部署 

### 8.1 更新 
- 在没有 es 的时候进行模糊查询 
- 部署优化
- 增加悬停特效
- 时间日期国际化显示的 bug 修复

### 8.2 更新 
- 新增私信和用户通知（暂不可回复私信）



### 部署流程 
#### 部署 es
```
docker pull elasticsearch:6.8.1
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 elasticsearch:6.8.1
```

#### mysql 服务
- 使用宿主机的 mysql 服务 


### 使用 Dockerfile 构建 web 容器 
```
docker build -t microblog:latest .
```

### 推送到 docker 仓库 
```
docker tag microblog:latest furuiyang/microblog:latest
docker push furuiyang/microblog:latest
```

### 拉取服务 
```
docker pull furuiyang/microblog:latest
```

#### 启动 web 服务
```
docker run --name microblog -d -p 8000:5000 --rm \
-e SECRET_KEY=ruiyang \
-e DATABASE_URL=mysql+pymysql://root:ruiyang@172.17.0.1/microblog \
-e YOUDAO_URL=https://openapi.youdao.com/api -e YOUDAO_APP_KEY=0c5da03940d46b17 \
-e YOUDAO_APP_SECRET=bFsRiYrXoBK9sWI4nYTaMdf6fobMfhUv \
furuiyang/microblog:latest
``



### 其他
- 9300 被占用 查看端口占用： netstat -ntlp
- CREATE DATABASE `microblog` CHARACTER SET utf8 COLLATE utf8_general_ci;
- 更新国际化语言包： 
- flask translate update 
- flask translate compile
- 开放内网所有主机的开放权限： flask run --host=0.0.0.0
- 在本地运行一个模拟的电子邮件服务器，使用 python 的 SMPT 调试服务器，
它接受电子邮件，然后打印到控制台。要运行此服务器，需要在终端运行： 
python -m smtpd -n -c DebuggingServer localhost:8025
要用这个模拟邮件服务器来测试应用，那么你将设置MAIL_SERVER=localhost和MAIL_PORT=8025。