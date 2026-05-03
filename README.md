## Baby things

### 概述

本系统用于记录婴儿成长过程中的日常活动和重要事项，简化宝爸宝妈的记录，主要包含以下关键功能：

- 日常活动记录：记录日常喂养、大便、洗澡、肚脐消毒、维生素补充等每日事项
- 重要事项记录：如疫苗接种、定时体检等
- 活动提醒：可创建定期提醒事项，例如补充维生素

### 系统结构

本系统采用前后端分离模式，前端是由VUE框架构建，要求需要适配移动端，未来会发布到小程序上，需要提前考虑兼容性。
后端使用Python + SQLite数据库。

### 其他重要功能

#### 用户登录与权限

需要提供用户注册、登录功能，注册需要管理员批准。

登录用户可以新增需要记录的婴幼儿，并管理可以查看和记录的用户清单。

管理员拥有全部权限。

#### 数据查看与导出

可以按照查看每天的活动时间轴，并支持导出指定时间内的所有数据。

#### 图片上传

记录活动时，可以上传最多5张图片。

使用aliyun oss存储。

### 其他要求

- 页面为可爱风格
- 记录活动页面提供大图标方便点击

## 当前实现进度（第一阶段）

已完成基础可运行版本（MVP 骨架）：

- 后端（FastAPI + SQLite）
	- 用户注册、登录
	- 管理员审批待审核用户
	- 婴儿档案创建与查询
	- 婴儿可见/可记录权限设置
	- 活动记录创建（含最多 5 张图片元数据）
	- 按天活动时间轴查询
- 前端（Vue + Vite，移动端优先）
	- 登录/注册页面
	- 首页（婴儿列表、创建婴儿、管理员审批入口）
	- 活动记录页面（大按钮活动类型选择 + 每日时间轴展示）

## 项目结构

```
baby-things/
	backend/
		app/
		requirements.txt
		.env.example
	frontend/
		src/
		package.json
		.env.example
```

## 本地启动

### 1. 启动后端

在 `backend` 目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

说明：

- 首次启动会自动创建 SQLite 数据库表。
- 在 `.env` 中设置 `BOOTSTRAP_ADMIN_USERNAME` 和 `BOOTSTRAP_ADMIN_PASSWORD`，可自动初始化管理员账号。

### 2. 启动前端

在 `frontend` 目录执行：

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

默认访问：`http://127.0.0.1:5173`

## 下一步建议

- 接入 OSS 签名上传（目前为图片元数据字段，已限制每条记录最多 5 张）
- 完成提醒功能（创建/编辑/停用）
- 完成导出功能（先 CSV）
- 增加自动化测试与权限回归测试