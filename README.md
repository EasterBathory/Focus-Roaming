# 焦点漫游 · Focus Roaming

**面向摄影爱好者的场景化摄影辅助平台**  
A scene-oriented photography assistant for photography enthusiasts.

[中文](#中文) · [English](#english)

---

## 中文

### 项目简介

焦点漫游（Focus Roaming）是一个围绕摄影地点发现与拍摄决策构建的 Web 项目。项目希望帮助摄影爱好者更方便地发现拍摄地点、了解场景信息，并辅助安排拍摄时间与路线。

当前仓库包含前端页面和基于 FastAPI 的后端服务。项目原始说明还提出了摄影机位推荐、场景评分、拍摄偏好分析及观星区域筛选等方向。具体功能以当前代码实际实现为准，持续开发中的能力不应视为已交付功能。

### 项目特点

- **地图与地点探索**：围绕摄影地点和机位信息组织地图体验。
- **场景化辅助**：项目规划包含场景评分、拍摄时间规划等能力。
- **用户功能**：后端包含用户认证及相关数据模型。
- **智能化扩展**：仓库说明涉及 AI 视觉分析与拍摄偏好分析方向。

> 说明：以上为项目定位与仓库现有说明的归纳。请以当前代码和实际部署效果核验各功能状态。

### 技术栈

| 层次 | 技术 |
|---|---|
| 前端 | HTML、CSS、JavaScript |
| 地图 | Leaflet（项目说明中还提及地图服务 API） |
| 后端 | Python、FastAPI、Uvicorn |
| 数据访问 | SQLAlchemy、PyMySQL |
| 认证 | JWT（python-jose） |
| 配置 | python-dotenv |
| 外部服务 | 邮件服务；项目代码/配置中预留地图与 AI 服务配置 |

### 仓库结构

```text
.
├── README.md
├── .gitignore
└── starmap/
    ├── README.md
    ├── backend/
    │   ├── main.py
    │   ├── auth.py
    │   ├── models.py
    │   ├── database.py
    │   ├── email_code.py
    │   ├── requirements.txt
    │   └── .env.example
    └── frontend/
        └── index.html
```

### 本地运行

#### 1. 环境要求

- Python 3.10 或更高版本（建议使用独立虚拟环境）
- MySQL（如果当前后端配置启用了数据库）
- VS Code 或其他代码编辑器

#### 2. 启动后端

在项目根目录执行：

```bash
cd starmap/backend
python -m venv .venv
```

Windows：

```powershell
.venv\\Scripts\\Activate.ps1
```

macOS / Linux：

```bash
source .venv/bin/activate
```

安装依赖并准备环境变量：

```bash
pip install -r requirements.txt
```

将 `.env.example` 复制为 `.env`，再根据本机环境填写数据库、JWT、邮件及第三方服务配置。不要将真实密钥提交到 Git。

启动服务：

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8003
```

#### 3. 启动前端

使用 VS Code Live Server 打开 `starmap/frontend/index.html`，或使用其他静态文件服务器提供前端页面。

当前项目说明中提到前端 API 地址使用本地 `http://127.0.0.1:8003`。如果部署到其他地址，请先检查并调整前端 API 配置及后端 CORS 设置。

### 配置说明

后端环境变量模板位于 `starmap/backend/.env.example`。请复制为同目录下的 `.env`，并填写自己的配置：

- MySQL：`DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`
- JWT：`JWT_SECRET`
- 邮件：`SMTP_*` 或项目实际使用的邮件 API 配置
- 地图服务：`AMAP_KEY`
- AI 服务：`ALI_AK_ID`、`ALI_AK_SECRET`（如启用）

请勿在 README、截图、提交记录或公开 issue 中粘贴密钥、验证码、数据库密码或个人隐私信息。

### 当前状态与后续计划

本仓库仍需持续完善。建议后续补充并验证：

- 可复现的数据库初始化/迁移说明
- 前端 API 地址的环境化配置
- 自动化测试与接口文档
- 实际运行截图和演示视频
- 部署配置与生产环境安全说明

### 贡献与反馈

欢迎通过 GitHub Issues 反馈问题或提出改进建议。提交代码前，请确保不包含本地环境文件、密钥、数据库备份及个人数据。

### 许可证

当前仓库尚需确认开源许可证。明确许可协议前，默认不要将代码视为可任意再分发或商用。

---

## English

### Overview

**Focus Roaming** is a web project designed to support photography enthusiasts in discovering photography locations and making scene-oriented shooting decisions. The project aims to make it easier to explore locations, review scene information, and plan shooting times and routes.

The repository contains a web frontend and a backend service built with FastAPI. The existing project notes also describe planned or intended capabilities such as photography spot recommendations, scene scoring, preference analysis, and stargazing-area discovery. Please verify each capability against the current implementation before treating it as a released feature.

### Highlights

- **Map-based discovery** for photography locations and spots.
- **Scene-oriented assistance**, with planned capabilities for scene scoring and shooting-time planning.
- **User features**, supported by backend authentication and data models.
- **Intelligent extensions**, including AI-assisted visual analysis described in the project notes.

### Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Mapping | Leaflet (the project notes also refer to a map service API) |
| Backend | Python, FastAPI, Uvicorn |
| Data access | SQLAlchemy, PyMySQL |
| Authentication | JWT via python-jose |
| Configuration | python-dotenv |
| External services | Email; map and AI service configuration is present in the project setup |

### Run Locally

1. Install Python 3.10+ and, if required by the backend configuration, MySQL.
2. Create and activate a virtual environment in `starmap/backend`.
3. Install dependencies with `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and fill in your own local configuration. Never commit real credentials.
5. Start the API:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8003
```

6. Serve `starmap/frontend/index.html` with VS Code Live Server or another static file server.

The current project notes refer to a local API endpoint at `http://127.0.0.1:8003`. Review the frontend API configuration and backend CORS settings when using a different host or deployment environment.

### Configuration and Security

The backend environment template is `starmap/backend/.env.example`. Configure database, JWT, email, map, and optional AI credentials locally in `.env`. Do not commit secrets, personal data, database dumps, or local environment files.

### Project Status

The project is under active improvement. Database setup instructions, frontend environment configuration, automated tests, API documentation, screenshots, and deployment guidance should be validated and expanded as the implementation evolves.

### License

A license has not yet been confirmed in this repository. Until a license is added, do not assume the code is available for unrestricted reuse or redistribution.
