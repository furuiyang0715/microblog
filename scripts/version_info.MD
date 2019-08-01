### 7.30 更新
- 可显示中文 
- 增加英文 --> 中文的翻译功能 

### 7.31 更新 
-  容器化部署 

### 8.1 更新 
- ELASTICSEARCH_URL=http://localhost:9200
- 在没有 es 的时候进行模糊查询 


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

#### 启动 web 服务
```
docker run --name microblog -d -p 8000:5000 --rm \
-e SECRET_KEY=ruiyang \
-e DATABASE_URL=mysql+pymysql://root:ruiyang@172.17.0.1/microblog \
-e ELASTICSEARCH_URL=http://172.17.0.1:9200 \
-e YOUDAO_URL=https://openapi.youdao.com/api -e YOUDAO_APP_KEY=0c5da03940d46b17 \
-e YOUDAO_APP_SECRET=bFsRiYrXoBK9sWI4nYTaMdf6fobMfhUv \
microblog:latest
```



### 其他
- 9300 被占用 查看端口占用： netstat -ntlp