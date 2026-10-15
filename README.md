# Mechanical Interpretability Latest Work Notes

检索日期：2026-06-11

本文件夹整理 2025-2026 年机械可解释性（mechanistic interpretability, MI）近期工作，覆盖 arXiv、ACL Anthology、Reddit、X、Anthropic Transformer Circuits、OpenAI 等来源。

阅读顺序：

1. [mi_latest_survey_2026-06-11.md](./mi_latest_survey_2026-06-11.md)：按研究子类整理最新内容、方法、代表论文和趋势。
2. [next_work_cross_source.md](./next_work_cross_source.md)：特别标注两个及以上不同来源共同提到、仍未完全完成的下一步工作，按“来源数、具体性、可执行性”排序。
3. [sources_table.md](./sources_table.md)：来源索引、渠道、日期和证据用途。
4. [method_notes.md](./method_notes.md)：检索口径、可信度标注和如何继续更新。

核心结论：

- MI 的主线正在从“找到可解释特征”转向“评估这些特征是否稳定、因果有效、可用于 circuit tracing 和安全干预”。
- Sparse autoencoder 仍是中心工具，但 2025-2026 的焦点已经明显转向 SAE 的评估、特征一致性、多维/功能型特征、跨层/路由式架构和应用边界。
- Anthropic 的 attribution graph / cross-layer transcoder 工作把“可解释特征”推进到“prompt-level 计算图”，同时也暴露了长上下文、attention 形成、全局 circuit、faithfulness、人工分组等未解问题。
- OpenAI 的 sparse circuits 路线代表“为可解释性训练模型”的方向，和后验 SAE/circuit tracing 形成互补，但是否能扩展到 frontier 模型仍未解决。
- ACL/EMNLP/EACL 论文正在把 MI 拉向 NLP 任务、RAG、emotion inference、ICL、monosemanticity 评估和可用工具。
- Reddit/X 的信号主要反映社区对 circuit tracing、symbolic extraction、pruning/knowledge removal、latent guardrails 的兴趣与质疑，不应替代论文证据。

# Mechanistic Interpretability: Notes on Recent Work

Search date: 2026-06-11

This folder compiles recent work on mechanistic interpretability (MI) from 2025–2026, covering sources including arXiv, ACL Anthology, Reddit, X, Anthropic's Transformer Circuits, and OpenAI.

Recommended reading order:

1. [mi_latest_survey_2026-06-11.md](./mi_latest_survey_2026-06-11.md): Recent developments, methods, representative papers, and trends organized by research subarea.
2. [next_work_cross_source.md](./next_work_cross_source.md): Highlights unfinished next steps mentioned by at least two distinct sources, ranked by the number of supporting sources, specificity, and feasibility.
3. [sources_table.md](./sources_table.md): A source index listing channels, dates, and how each source is used as evidence.
4. [method_notes.md](./method_notes.md): Search scope and criteria, credibility labels, and guidance for future updates.

Key takeaways:

- MI's central focus is shifting from "finding interpretable features" to "evaluating whether these features are stable, causally effective, and useful for circuit tracing and safety interventions."
- Sparse autoencoders (SAEs) remain a central tool, but the focus in 2025–2026 has clearly shifted toward SAE evaluation, feature consistency, multidimensional and functional features, cross-layer and routing-based architectures, and limits of applicability.
- Anthropic's work on attribution graphs and cross-layer transcoders advances "interpretable features" into "prompt-level computation graphs," while also exposing unresolved challenges involving long contexts, how attention patterns form, global circuits, faithfulness, and manual grouping.
- OpenAI's sparse circuits approach represents the direction of "training models for interpretability," complementing post hoc SAE analysis and circuit tracing. Whether this approach can scale to frontier models remains unresolved.
- ACL, EMNLP, and EACL papers are bringing MI into closer contact with NLP tasks, RAG, emotion inference, in-context learning (ICL), monosemanticity evaluation, and practical tools.
- Signals from Reddit and X primarily reflect community interest in, and skepticism about, circuit tracing, symbolic extraction, pruning and knowledge removal, and latent guardrails. They should not substitute for evidence from research papers.
