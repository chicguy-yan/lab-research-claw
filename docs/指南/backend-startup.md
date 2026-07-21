# 后端启动说明

本文档用于启动 `ResearchAgentPrivateWorkspace/backend` 下的 FastAPI 后端，并补充当前 `frontend` 的正确启动方式。

## 1. 进入后端目录

```bash
cd /Users/fenke/projects/study_ai/2-未完成项目存档/zly\ 规划-0219/ResearchAgentPrivateWorkspace/backend
```

## 2. 准备 Python 环境

如果项目已经有虚拟环境，可以直接激活；如果没有，可以新建一个：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 3. 配置环境变量

先复制示例文件：

```bash
cp .env.example .env
```

然后至少检查这些配置：

```env
OPENAI_API_KEY=你的真实可用 key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

说明：

- `OPENAI_API_KEY` 不配置时，服务通常仍能启动。
- 但调用 `/api/chat` 时，模型侧会返回错误提示，无法正常对话。
- `EMBEDDING_*` 和 `BRAVE_API_KEY` 目前都属于可选配置。

## 4. 启动后端

在 `backend` 目录下执行：

```bash
cd /Users/fenke/projects/study_ai/2-未完成项目存档/zly\ 规划-0219/ResearchAgentPrivateWorkspace/backend
source .venv/bin/activate
python app.py
```

说明：

- `app.py` 已固定后端地址为 `http://127.0.0.1:8002`
- 启动时会额外提示你是否用了错误的 Python 环境
- 也会提醒不要再把前端切到旧端口 `8000/8003`

启动后默认地址：

```text
http://localhost:8002
```

## 5. 启动成功后的验证

健康检查：

```bash
curl http://localhost:8002/
```

预期返回类似：

```json
{"status":"ok","service":"experimental-research-openclaw-backend"}
```

再检查一个核心接口：

```bash
curl http://localhost:8002/api/sessions
```

如果能返回 JSON，会话系统就已经可用了。

## 6. 前端联调

### 6.1 不要再用 Finder 直接打开 `frontend/index.html`

当前前端已经切到 `React + Vite + TypeScript`。

因此：

- 不能再通过 Finder 双击 `frontend/index.html` 直接打开
- 也不要指望“浏览器刷新一下就行”
- 必须启动 Vite dev server

否则页面虽然能打开静态壳，但模块脚本、路由、HMR、测试环境都会不正常。

### 6.2 进入前端目录

```bash
cd /Users/fenke/projects/study_ai/2-未完成项目存档/zly\ 规划-0219/ResearchAgentPrivateWorkspace/frontend
```

### 6.3 安装前端依赖

如果是第一次启动，先安装依赖：

```bash
npm install
```

如果 `frontend/node_modules` 已存在，可以跳过这一步。

### 6.4 启动前端开发服务器

在 `frontend` 目录下执行：

```bash
npm run dev
```

Vite 默认会输出类似：

```text
Local:   http://localhost:5173/
```

建议直接在浏览器打开：

```text
http://localhost:5173
```

### 6.5 前后端联调顺序

推荐顺序：

1. 先启动后端 `python app.py`
2. 确认后端固定在 `8002`
3. 再启动前端 `npm run dev`
4. 打开 `http://localhost:5173`

前端会默认请求：

```text
http://127.0.0.1:8002
```

如果你改过地址，也可以在页面顶栏手动改 `Backend` 输入框。

前端页面默认会连：

```text
http://localhost:8002
```

前端默认也固定到 `http://localhost:8002`，并会自动纠正缓存里的旧地址 `8000/8003`。

## 7. 常见问题

### 7.1 端口占用

当前约定就是固定使用 `8002`。如果 `8002` 被占用，优先停掉旧进程，而不是继续换端口，否则前端容易再次连错。

```bash
lsof -nP -iTCP:8002 -sTCP:LISTEN
```

确认占用进程后再关闭它。

### 7.2 `OPENAI_API_KEY` 未配置

现象：

- 服务能启动
- `/api/chat` 无法正常返回模型内容

处理方式：

- 检查 `backend/.env`
- 确认 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL` 已填入真实可用值

### 7.3 首次启动较慢

后端启动时会自动初始化：

- `backend/.openclaw/workspace-default`
- 默认 workspace 模板
- SessionManager / AgentManager

首次启动比后续稍慢是正常现象。

## 8. 推荐启动顺序

```bash
cd ResearchAgentPrivateWorkspace/backend
source .venv/bin/activate
python app.py
```

然后另开一个终端：

```bash
cd ResearchAgentPrivateWorkspace/frontend
npm run dev
```

确认前端正常后，在浏览器打开：

```text
http://localhost:5173
```
