================================================================================

                              AI 考 证 教 练

               围绕明确的考试目标，把备考计划拆到每一天

================================================================================

[ frontend  Vue 3 + Element Plus ]  [ backend  FastAPI ]
[ database  MySQL ]                 [ cache  Redis ]
[ AI  DeepSeek / Qwen ]             [ status  active ]

项目简介
--------

AI 考证教练是一款面向职业资格考试的智能学习平台。用户可以选择目标证书，
结合考试日期、当前基础与每日可用时间，由 AI 生成分钟级备考计划。系统通过
今日训练、我的待办、学习日历和每日总结，帮助用户持续管理复习进度。

主要功能
--------

· 用户注册、登录与邮箱验证码
· 覆盖计算机、财会、法律、建筑、消防、教育、医药等行业的证书广场
· DeepSeek 与 Qwen 计划模型可选
· 按考试日期和个人时间生成分钟级学习与休息安排
· 今日训练、待办勾选、计划收起与历史日期查看
· 自定义学习日历，已完成日期自动标记
· 每日总结支持 Markdown 和类 Word 富文本编辑
· 会员套餐与本地模拟支付流程

运行环境
--------

· Node.js 20+
· Python 3.11+
· MySQL 8.0+
· Redis 6.0+

一、准备 MySQL
--------

1. 启动本地 MySQL。
2. 创建项目数据库：

   CREATE DATABASE ai_exam_coach
   CHARACTER SET utf8mb4
   COLLATE utf8mb4_unicode_ci;

3. 数据表会在 FastAPI 首次启动时自动创建。

二、启动 Redis
--------

邮箱验证码等临时数据保存在 Redis 中，请先启动本地 Redis：

   redis-server

三、启动后端
--------

1. 进入后端目录：

   cd backend

2. 创建并启用 Python 虚拟环境：

   python3 -m venv .venv
   source .venv/bin/activate

   Windows PowerShell 使用：
   .venv\Scripts\Activate.ps1

3. 安装后端依赖：

   pip install -r requirements.txt

4. 复制环境变量示例：

   cp .env.example .env

   Windows 使用：
   copy .env.example .env

5. 编辑 backend/.env，至少需要配置：

   · SECRET_KEY：用于签发登录令牌的随机密钥
   · DATABASE_URL：本地 MySQL 连接地址
   · REDIS_URL：本地 Redis 连接地址
   · EMAIL_CODE_SECRET：邮箱验证码签名密钥
   · AI_API_KEY / QWEN_API_KEY：需要使用对应 AI 模型时填写

   真实密钥请只保存在 .env，不要提交到 Git。

6. 初始化证书广场数据：

   python -m scripts.seed_certificates

7. 启动 FastAPI：

   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

后端地址：http://localhost:8000
API 文档：http://localhost:8000/docs

四、启动前端
--------

1. 新开一个终端，进入前端目录：

   cd frontend

2. 安装依赖：

   npm install

3. 复制前端环境变量：

   cp .env.example .env

   Windows 使用：
   copy .env.example .env

4. 启动 Vue 3 开发服务：

   npm run dev

前端地址：http://localhost:5173

五、邮箱与图片配置（可选）
--------

· 本地开发可保持 EMAIL_DELIVERY_MODE=console，验证码会输出到后端终端。
· 邮箱发送需在 backend/.env 中配置 SMTP 服务器与授权码。
· 证书图片可使用 backend/assets/certificates 中的素材，也可配置腾讯云 COS。
· COS、SMTP 和 AI 密钥均不包含在本仓库中。

目录结构
--------

Habit_Formation/
├── backend/                 FastAPI 后端
│   ├── app/api/             API 路由
│   ├── app/models/          SQLAlchemy 模型
│   ├── app/schemas/         请求与响应结构
│   ├── app/services/        邮件和 AI 计划服务
│   ├── assets/certificates/ 证书分类图片
│   └── scripts/             数据初始化脚本
├── frontend/                Vue 3 前端
│   ├── src/components/      公共组件
│   ├── src/router/          路由与菜单配置
│   ├── src/services/        前端 API 封装
│   ├── src/store/           用户状态管理
│   └── src/views/           页面
└── readme.txt               项目说明

安全说明
--------

本仓库不包含 .env、真实数据库密码、AI API Key、SMTP 授权码、
腾讯云 COS SecretId / SecretKey 或其他私密凭据。

================================================================================
