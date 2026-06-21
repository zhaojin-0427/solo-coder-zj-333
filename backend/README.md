# 电台节目共享平台 - 后端

基于 Django 4.2 + Django REST Framework 开发的电台节目共享平台后端服务。

## 技术栈

- Django 4.2
- Django REST Framework 3.14.0
- SQLite 数据库
- JWT 认证 (djangorestframework-simplejwt)
- CORS 支持 (django-cors-headers)

## 项目结构

```
backend/
├── manage.py
├── requirements.txt
├── README.md
├── radio_platform/          # 项目主配置
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                 # 用户账户应用
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py             # FamilyGroup, User 模型
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
└── core/                     # 核心业务应用
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    ├── management/           # 管理命令
    │   ├── __init__.py
    │   └── commands/
    │       ├── __init__.py
    │       └── init_data.py  # 数据初始化命令
    ├── models.py             # Topic, ProgramExcerpt, Version, Comment, FollowUpItem
    ├── serializers.py
    ├── services.py           # 业务逻辑服务
    ├── urls.py
    └── views.py
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 执行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. 初始化测试数据

```bash
python manage.py init_data
```

这将创建以下测试数据：
- 1个家庭组：幸福一家人
- 4个专题：社区通知、健康提醒、戏曲节目、便民服务
- 3个测试用户（密码均为 `test123456`）：
  - `grandpa` - 张爷爷（老人角色 👴）
  - `daughter` - 张女儿（家属角色 👩）
  - `son` - 张儿子（家属角色 👨）
- 10条节目摘录数据（包含重复记录和老人补充笔记）
- 2条评论
- 3条待跟进事项

### 4. 启动服务

```bash
python manage.py runserver 9422
```

服务将在 `http://localhost:9422` 启动。

## API 端点

### 认证

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login/` | JWT 登录获取 Token | 公开 |
| POST | `/api/auth/refresh/` | 刷新 Token | 公开 |

### 节目摘录

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/excerpts/` | 获取节目摘录列表 | 需要登录 |
| POST | `/api/excerpts/` | 创建节目摘录 | 需要登录 |
| GET | `/api/excerpts/:id/` | 获取节目摘录详情 | 需要登录 |
| PUT | `/api/excerpts/:id/` | 更新节目摘录 | 需要登录 |
| DELETE | `/api/excerpts/:id/` | 删除节目摘录 | 需要登录 |
| GET | `/api/excerpts/:id/versions/` | 获取版本历史 | 需要登录 |
| POST | `/api/excerpts/:id/merge/` | 合并重复记录 | 需要登录 |
| GET | `/api/excerpts/:id/comments/` | 获取评论列表 | 需要登录 |
| POST | `/api/excerpts/:id/comments/` | 添加评论 | 需要登录 |

### 专题

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/topics/` | 获取专题列表 | 公开 |
| POST | `/api/topics/` | 创建专题 | 需要登录 |
| PUT | `/api/topics/:id/` | 更新专题 | 需要登录 |

### 家庭

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/family/members/` | 获取家庭成员列表 | 需要登录 |
| GET | `/api/family/feed/` | 获取家庭共享时间线 | 需要登录 |

### 待跟进事项

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/followups/` | 获取待跟进事项列表 | 需要登录 |
| POST | `/api/followups/` | 创建待跟进事项 | 需要登录 |
| PUT | `/api/followups/:id/` | 更新事项状态 | 需要登录 |

### 统计

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/statistics/` | 获取统计数据 | 需要登录 |

统计数据包含：
- 高频收听栏目（TOP5）
- 专题内容数量分布
- 重复记录比例
- 待确认摘录数量
- 待处理待跟进事项数量

## API 使用示例

### 登录获取 Token

```bash
curl -X POST http://localhost:9422/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "grandpa", "password": "test123456"}'
```

响应：
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "grandpa",
    "first_name": "张爷爷",
    "role": "elderly",
    "avatar": "👴",
    ...
  }
}
```

### 获取节目摘录列表

```bash
curl http://localhost:9422/api/excerpts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 创建节目摘录

```bash
curl -X POST http://localhost:9422/api/excerpts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-06-21",
    "program_name": "健康讲座",
    "time_slot": "09:00-10:00",
    "content_summary": "夏季养生要注意...",
    "elderly_notes": "记得多喝水",
    "topic_id": 2
  }'
```

### 合并重复记录

```bash
curl -X POST http://localhost:9422/api/excerpts/1/merge/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "duplicate_id": 9,
    "merge_note": "合并重复的体检通知"
  }'
```

## 配置说明

### 数据库

默认使用 SQLite 数据库，数据库文件位于 `backend/db.sqlite3`。

### 端口

默认端口配置为 9422。

### JWT 配置

- Access Token 有效期：7天
- Refresh Token 有效期：30天

### CORS 配置

默认允许所有来源访问，可在 `settings.py` 中修改。

## 管理员后台

创建超级用户：

```bash
python manage.py createsuperuser
```

访问后台：`http://localhost:9422/admin/`

## 测试账号

| 用户名 | 密码 | 角色 | 姓名 |
|--------|------|------|------|
| grandpa | test123456 | 老人 | 张爷爷 |
| daughter | test123456 | 家属 | 张女儿 |
| son | test123456 | 家属 | 张儿子 |
