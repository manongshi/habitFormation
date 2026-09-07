<div align="center">

# AI 考证教练

### 围绕明确的考试目标，把备考计划拆到每一天

[![Vue 3](https://img.shields.io/badge/Vue-3.5-42b883?style=for-the-badge&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![Element Plus](https://img.shields.io/badge/Element_Plus-2.9-409eff?style=for-the-badge&logo=element&logoColor=white)](https://element-plus.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479a1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-6.0+-dc382d?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)

[![Repository status](https://img.shields.io/badge/status-active-36a269?style=flat-square)](https://github.com/manongshi/habitFormation)
[![GitHub stars](https://img.shields.io/github/stars/manongshi/habitFormation?style=flat-square&logo=github)](https://github.com/manongshi/habitFormation/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/manongshi/habitFormation?style=flat-square&logo=git)](https://github.com/manongshi/habitFormation/commits/main)

<img src="docs/assets/readme-hero.png" alt="AI 考证教练项目横幅" width="78%" />

**AI 考证教练**是一款面向职业资格考试的智能学习平台。  
选择目标证书，填写考试日期和可用时间，让 AI 生成分钟级备考计划。

</div>

---

## ✨ 主要功能

| 功能 | 说明 |
| --- | --- |
| 🎯 证书广场 | 覆盖计算机、财会、法律、建筑、消防、教育、医药等行业的职业资格考试 |
| 🧠 AI 学习计划 | 可选 DeepSeek 或 Qwen，结合基础、弱项、考试日期与每日时长生成计划 |
| ⏱️ 分钟级安排 | 将每天的学习、复习和离屏休息安排到具体时间 |
| ✅ 我的待办 | 按证书展示当日任务，支持勾选完成、收起与历史日期查看 |
| 📅 学习日历 | 选择任意日期查看当天计划，完成日期会自动标记 |
| 📝 每日总结 | 支持 Markdown 和类 Word 富文本两种编辑方式 |
| 🔐 账号系统 | 支持邮箱验证码注册、登录、JWT 身份认证和用户状态保持 |
| 💳 会员套餐 | 包含套餐展示、订单创建与本地模拟支付流程 |

## 🧱 技术架构

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite、Vue Router、Pinia、Element Plus |
| 编辑器 | md-editor-v3、WangEditor |
| 后端 | Python、FastAPI、SQLAlchemy、Pydantic |
| 数据库 | MySQL 8.0+ |
| 临时数据 | Redis 6.0+ |
| AI 模型 | DeepSeek、Qwen（OpenAI 兼容接口） |
| 对象存储 | 腾讯云 COS（可选） |

## 🚀 快速开始

### 1. 环境要求

- Node.js 20+
- Python 3.11+
- MySQL 8.0+
- Redis 6.0+

### 2. 准备 MySQL

```sql
CREATE DATABASE ai_exam_coach
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

FastAPI 首次启动时会自动创建数据表。

### 3. 启动 Redis

```bash
redis-server
```

邮箱验证码等临时数据保存在 Redis 中。

### 4. 启动后端

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell 启用虚拟环境：

```powershell
.venv\Scripts\Activate.ps1
copy .env.example .env
```

编辑 `backend/.env` 后，初始化证书广场数据并启动后端：

```bash
python -m scripts.seed_certificates
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- 后端服务：<http://localhost:8000>
- API 文档：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/api/v1/health>

### 5. 启动前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

打开 <http://localhost:5173> 访问系统。

## ⚙️ 环境变量

<details>
<summary><strong>展开查看后端关键配置</strong></summary>

| 变量 | 用途 |
| --- | --- |
| `SECRET_KEY` | JWT 登录令牌签名密钥 |
| `DATABASE_URL` | MySQL 连接地址 |
| `REDIS_URL` | Redis 连接地址 |
| `EMAIL_CODE_SECRET` | 邮箱验证码签名密钥 |
| `AI_API_KEY` | DeepSeek API Key |
| `QWEN_API_KEY` | Qwen API Key |
| `SMTP_*` | 真实邮件发送配置 |
| `COS_*` | 腾讯云 COS 图片存储配置 |

> 本地开发可使用 `EMAIL_DELIVERY_MODE=console`，注册验证码会输出到后端终端。

</details>

## 🗂️ 项目结构

```text
Habit_Formation/
├── backend/                 # FastAPI 后端
│   ├── app/api/             # API 路由
│   ├── app/models/          # SQLAlchemy 模型
│   ├── app/schemas/         # 请求与响应结构
│   ├── app/services/        # 邮件与 AI 计划服务
│   ├── assets/certificates/ # 证书分类素材
│   └── scripts/             # 数据初始化脚本
├── frontend/                # Vue 3 前端
│   ├── src/components/      # 公共组件
│   ├── src/router/          # 路由与菜单
│   ├── src/services/        # API 请求封装
│   ├── src/store/           # Pinia 用户状态
│   └── src/views/           # 业务页面
├── docs/assets/             # README 图片资源
└── README.md
```

## 🔐 安全说明

- 请从 `.env.example` 复制本地 `.env`。
- 不要将数据库密码、AI API Key、SMTP 授权码或 COS Secret 提交到 Git。
- 项目的 `.gitignore` 已默认排除真实环境文件、私钥、本地依赖、日志和缓存。

---

<div align="center">

**让备考不再是一份模糊的长期愿望，而是今天可以完成的具体行动。**

</div>
