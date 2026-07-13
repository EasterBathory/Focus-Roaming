# 焦点漫游 · Focus Roaming

焦点漫游——基于场景智能推荐的摄影助手平台

## 功能

1. 本项目面向摄影爱好者解决选时难、找机位难、选址难、行程规划难四大核心痛点。 
2. 创新构建摄影专属地图层，通过生态化社区构建让用户可自主上传心仪点位，同时标注推荐机位、智能圈定观星区域，一站式提供点位定位、实景预览与路线导航服务。 
3.采用前后端分离架构，以百度地图 + Leaflet 为地图引擎，结合 FastAPI 后端与阿里云 AI 视觉，打造一站式摄影智能服务平台。 
4.核心提供 22 类场景实时评分、全国摄影机位推荐、AI 拍摄偏好分析、暗夜观星区筛选、24 小时时间线规划功能。 
5.实现按需 API 调度、多因子加权评分、光污染离线估算、本地存储离线降级，轻量化、高可用、低延迟。 
6. 未来将接入 AR 实景导航，实现预览构图与实景指引，完成从决策、抵达到拍摄的全流程闭环。

## 目录结构

```
starmap/
├── backend/      FastAPI 后端（Python）
│   ├── main.py         主入口 & API 路由
│   ├── auth.py         JWT 认证
│   ├── models.py       SQLAlchemy 数据模型
│   ├── database.py     数据库连接
│   └── email_code.py   邮箱验证码发送
└── frontend/
    └── index.html      前端单页应用
```

## 后端启动

```bash
cd starmap/backend

# 1. 复制环境变量并编辑
cp .env.example .env

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
uvicorn main:app --reload --port 8003
```

## 前端

开发时用 VS Code Live Server 打开 `frontend/index.html`（默认 5501 端口）。

前端 API 地址写死为 `http://127.0.0.1:8003`。
