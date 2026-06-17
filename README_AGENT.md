# Daily AI Safety Research Agent

这个项目会每天抓取 arXiv、Hugging Face Papers、Alignment Forum、Anthropic Research 和 Transformer Circuits 的候选文章，用 OpenAI-compatible API 做三阶段处理，然后把 top 6 深度报告发到邮箱。

默认部署方式是 GitHub Actions。你不需要个人电脑全天开机。

## 目录

- `src/research_agent/`: Python agent 源码。
- `tests/`: 不依赖真实 API 的核心测试。
- `.github/workflows/daily-research-agent.yml`: 每日定时任务。
- `.env.example`: 本地环境变量模板。
- `data/state.json`: 运行后生成，记录已处理文章，避免重复推送。
- `reports/YYYY-MM-DD/`: 运行后生成的 Markdown/JSON 报告。
- `docs/superpowers/specs/2026-06-16-research-agent-design.md`: 设计文档。
- `docs/superpowers/plans/2026-06-16-research-agent-implementation.md`: 实现计划。

## 你需要准备的东西

1. 一个 GitHub 仓库。
2. 你的 OpenAI-compatible 中转站：
   - `OPENAI_BASE_URL`
   - `OPENAI_API_KEY`
   - `STAGE1_MODEL`
   - `STAGE2_MODEL`
   - `REPORT_MODEL`
3. 一个支持 SMTP 的邮箱：
   - QQ 邮箱、163 邮箱、企业邮箱都可以。
   - 密码通常不是登录密码，而是“SMTP 授权码”或“应用专用密码”。

## 推荐模型分工

- `STAGE1_MODEL`: 便宜、快、JSON 稳定的模型，用于粗筛。
- `STAGE2_MODEL`: Kimi/Claude Sonnet 级别模型，用于质量评分。
- `REPORT_MODEL`: 你说的 `gpt5.5xhigh` 或最高质量模型，用于阅读全文和写报告。

只要你的中转站兼容 OpenAI Chat Completions API，模型名可以任意配置。

## 本地安装和试跑

```bash
cd /public/home/zhangrm2022/lately_work
python -m pip install -e ".[dev]"
cp .env.example .env
```

编辑 `.env` 后，在当前 shell 导入：

```bash
set -a
source .env
set +a
```

先跑测试：

```bash
pytest -v
```

只测试抓取，不调用 LLM，不发邮件：

```bash
python -m research_agent run --dry-run --skip-llm
```

如果当前机器外网受限，只验证 CLI、报告写入和 artifact 结构：

```bash
SKIP_SOURCES=true python -m research_agent run --dry-run --skip-llm
```

只看抓取列表：

```bash
python -m research_agent collect --limit 30
```

确认 SMTP 能发信：

```bash
python -m research_agent test-email
```

完整本地 dry run，不发邮件但会调用 LLM 生成报告：

```bash
python -m research_agent run --dry-run
```

完整运行并发邮件：

```bash
python -m research_agent run
```

## 环境变量说明

必填：

```bash
OPENAI_BASE_URL=https://your-gateway.example.com/v1
OPENAI_API_KEY=sk-...
STAGE1_MODEL=cheap-json-model
STAGE2_MODEL=kimi-or-claude-sonnet
REPORT_MODEL=gpt5.5xhigh

SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_smtp_authorization_code
SMTP_USE_SSL=true
SMTP_STARTTLS=false
EMAIL_FROM=your_email@example.com
EMAIL_TO=target@example.com
```

常用可选：

```bash
LOOKBACK_DAYS=3
MAX_REPORTS=8
STAGE1_CONFIDENCE_THRESHOLD=7
LLM_TIMEOUT_SECONDS=90
REPORT_TIMEOUT_SECONDS=420
REPORT_MAX_CHARS=90000
REPORT_LANGUAGE=zh
SEND_EMAIL=true
STATE_PATH=data/state.json
REPORT_DIR=reports
SKIP_SOURCES=false
```

多个收件人用英文逗号分隔：

```bash
EMAIL_TO=a@example.com,b@example.com
```

## QQ/163/企业邮箱 SMTP 配置

QQ 邮箱常见配置：

```bash
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USE_SSL=true
SMTP_STARTTLS=false
SMTP_USERNAME=你的QQ邮箱地址
SMTP_PASSWORD=QQ邮箱SMTP授权码
EMAIL_FROM=你的QQ邮箱地址
```

163 邮箱常见配置：

```bash
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USE_SSL=true
SMTP_STARTTLS=false
SMTP_USERNAME=你的163邮箱地址
SMTP_PASSWORD=163邮箱客户端授权密码
EMAIL_FROM=你的163邮箱地址
```

企业邮箱配置看服务商文档。一般是：

```bash
SMTP_PORT=465
SMTP_USE_SSL=true
SMTP_STARTTLS=false
```

如果服务商要求 STARTTLS：

```bash
SMTP_PORT=587
SMTP_USE_SSL=false
SMTP_STARTTLS=true
```

## GitHub Actions 部署

1. 新建 GitHub 仓库。
2. 把当前目录内容推上去：

```bash
git init
git add .
git commit -m "feat: add daily research agent"
git branch -M main
git remote add origin git@github.com:YOUR_NAME/YOUR_REPO.git
git push -u origin main
```

3. 打开 GitHub 仓库页面。
4. 进入 `Settings -> Secrets and variables -> Actions`。
5. 在 `Secrets` 添加：

```text
OPENAI_BASE_URL
OPENAI_API_KEY
STAGE1_MODEL
STAGE2_MODEL
REPORT_MODEL
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_USE_SSL
SMTP_STARTTLS
EMAIL_FROM
EMAIL_TO
```

6. 在 `Variables` 可选添加：

```text
LOOKBACK_DAYS=3
MAX_REPORTS=6
STAGE1_CONFIDENCE_THRESHOLD=6
REPORT_LANGUAGE=zh
SEND_EMAIL=true
SKIP_SOURCES=false
ANTHROPIC_URLS=https://www.anthropic.com/research
TRANSFORMER_CIRCUITS_URLS=https://transformer-circuits.pub/
ALIGNMENT_FORUM_URLS=https://www.alignmentforum.org/
```

7. 进入 `Actions -> Daily Research Agent -> Run workflow`。
8. 第一次建议：
   - `dry_run=true`
   - `skip_llm=true`
   这样只验证抓取、测试、报告 artifact，不调用 LLM，不发邮件。
9. 第二次建议：
   - `dry_run=true`
   - `skip_llm=false`
   验证中转站 API 和报告生成。
10. 第三次再用：
   - `dry_run=false`
   - `skip_llm=false`
   验证真实邮件发送。

工作流默认每天 UTC 23:00 运行。美国时间会因时区不同对应下午或晚上。你可以修改 `.github/workflows/daily-research-agent.yml` 里的 cron。

## 报告结果在哪里

每次运行会生成：

```text
reports/YYYY-MM-DD/digest.md
reports/YYYY-MM-DD/digest.json
reports/YYYY-MM-DD/items/*.md
data/state.json
```

GitHub Actions 会把这些作为 artifact 上传，并在成功后提交回仓库。`data/state.json` 用来避免同一篇文章每天重复发送。

## Notion 预留接口

当前已经有 `src/research_agent/delivery/notion.py` 作为预留 adapter。后续要打通时，你需要：

1. 创建 Notion integration。
2. 给目标 database/page 授权。
3. 配置：

```bash
NOTION_TOKEN=ntn_...
NOTION_DATABASE_ID=...
```

4. 在 `send_to_notion()` 里调用 Notion Pages API，把 `digest.md` 写成 page，把每篇 item 写成 child page。

## 常见问题

### GitHub Actions 报 Missing LLM environment variables

检查 Secrets 是否拼写完全一致：

```text
OPENAI_BASE_URL
OPENAI_API_KEY
STAGE1_MODEL
STAGE2_MODEL
REPORT_MODEL
```

### SMTP 登录失败

优先检查：

- 是否开启 SMTP 服务。
- `SMTP_PASSWORD` 是否是授权码，不是网页登录密码。
- `SMTP_HOST` 和端口是否匹配 SSL/STARTTLS。
- `EMAIL_FROM` 是否和 `SMTP_USERNAME` 一致。

### 抓取候选为空

先运行：

```bash
python -m research_agent collect --limit 50
```

如果 GitHub Actions 网络访问某来源失败，单个来源会被跳过，不会让整次运行失败。你可以增加：

```bash
LOOKBACK_DAYS=7
```

### LLM JSON 解析失败

代码会自动进行一次修复提示。如果仍失败，通常是模型不服从 JSON。换一个更稳定的 `STAGE1_MODEL` 或 `STAGE2_MODEL`。

### 报告太长或费用太高

降低：

```bash
MAX_REPORTS=3
```

或把 `REPORT_MODEL` 换成便宜一点的长上下文模型。

## 当前 MVP 的边界

- PDF 不是直接上传给模型，而是本地抽取文本后送入模型。这样最兼容 OpenAI-compatible 中转站。
- Alignment Forum 和 Hugging Face 页面结构可能变化；代码已做容错，但如果来源改版，需要更新 collector。
- Notion 是预留接口，不会在首版自动发送。
