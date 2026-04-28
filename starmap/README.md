# 焦点漫游 · Focus Roaming

基于地理位置的摄影观星参数查询工具。选择任意地点，获取实时天气、云量、能见度、光污染、月相等数据，并提供 3D 真实星图。

## 功能

- 🗺️ 全球地点搜索（Photon + 高德双引擎）
- 📍 点击地图获取观星参数（观星评分、天气、云量、能见度、Bortle 光污染等级）
- 🌌 3D 实时星图（基于真实天文算法，220+ 颗命名亮星 + 行星 + 月亮，可拖拽旋转）
- 👤 用户系统（邮箱验证码注册/登录、头像上传裁剪）
- ⭐ 历史记录 & 收藏
- 📤 地点分享（链接/文字/文件/二维码）

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
