# 检索与更新说明

检索日期：2026-06-11。

## 检索口径

关键词组合：

- mechanistic interpretability
- sparse autoencoder / SAE
- circuit tracing / attribution graphs / circuit stability / circuit completeness
- feature consistency / monosemantic representation / automated interpretability
- steering / activation steering / sparse latents / persona vectors
- ASR / EEG / diffusion language model / VLM / vision / video mechanistic interpretability
- site filters: arxiv.org, aclanthology.org, reddit.com, x.com, transformer-circuits.pub, openai.com

时间口径：

- 主体为 2025-2026 年。
- 2024 工作只纳入对 2025-2026 研究仍是直接前置的自动解释或 SAE 工具。

## 分类原则

每篇工作按主要贡献归入一个主类，但可在多个下一步工作中作为证据：

- SAE 表征与架构
- SAE 评估与自动解释
- Circuit tracing 与 causal graph
- Steering、model editing、安全干预
- Reasoning、CoT faithfulness、hidden goals
- 跨模态/专业领域 MI
- Interpretability-by-design / sparse circuits
- ACL/NLP 任务级 MI
- 社区渠道信号

## “多源共同提到下一步工作”的判定

一个下一步工作被纳入 [next_work_cross_source.md](./next_work_cross_source.md) 需要满足：

1. 至少两个不同来源直接提出相同未解问题，或一个来源提出、另一个来源的新方法/失败结果明显指向同一空缺。
2. 不能只是宽泛口号，例如“需要更好可解释性”；必须能落到可执行研究问题。
3. 尚未完全完成：已有子组件或局部结果不算完成，除非有跨模型/跨任务/跨来源的标准化方法和充分验证。
4. 排序优先考虑：来源数、技术具体性、是否可立刻启动、是否有清晰评估方案。

## 更新建议

下次更新时优先补：

- arXiv 2606 之后的 `mechanistic interpretability`、`sparse autoencoder`、`circuit tracing` 新论文。
- ACL Anthology 2026 后续会议：ACL 2026、EMNLP 2026、BlackboxNLP 2026。
- Anthropic/OpenAI/DeepMind/Google/FAR AI/Redwood/Goodfire/Neuronpedia 的官方 release。
- X 需要人工打开或使用可用镜像/归档，因为本次自动抓取只能拿到搜索 snippet。

## 链接检查记录

2026-06-11 用 `curl -L --max-time 20` 对 Markdown 中 URL 做过一次批量检查：

- arXiv、ACL Anthology、Anthropic Transformer Circuits、OpenAI PDF 链接返回 200。
- OpenAI 博客页对命令行访问返回 403，但 PDF 可达。
- Reddit 与 X 对命令行访问返回 000/超时；这些条目只作为社区讨论或传播信号，需要浏览器/人工打开复核具体评论内容。
