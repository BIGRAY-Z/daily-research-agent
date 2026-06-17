# 来源索引

检索日期：2026-06-11。技术结论优先使用论文、官方实验室文章和 ACL Anthology；Reddit/X 作为社区需求、质疑和传播热度的辅助来源。

| 渠道 | 日期 | 来源 | 主要用途 |
|---|---:|---|---|
| arXiv | 2026-06-04 | [Subspace-Aware Sparse Autoencoders for Effective Mechanistic Interpretability](https://arxiv.org/abs/2606.06333) | SASA；多维特征、feature splitting、subspace decoder |
| arXiv | 2026-05-13 | [Mechanistic Interpretability of EEG Foundation Models via Sparse Autoencoders](https://arxiv.org/abs/2605.13930) | EEG/clinical grounding；target/off-target steering；entanglement |
| arXiv | 2026-05-12 | [Mechanistic Interpretability of ASR models using Sparse Autoencoders](https://arxiv.org/abs/2605.12225) | Whisper/ASR；frame-level SAE；cross-lingual steering |
| arXiv | 2026-02-05 | [DLM-Scope](https://arxiv.org/abs/2602.05859) | Diffusion language models；diffusion-time intervention |
| arXiv | 2026-01, revised 2026-04 | [Locate, Steer, and Improve](https://arxiv.org/abs/2601.14004) | Actionable MI survey；locate/steer/improve pipeline |
| arXiv | 2025-09, revised 2026-05 | [Sparse Autoencoder Neural Operators](https://arxiv.org/abs/2509.03738) | Functional representation hypothesis；SAE-NO/FNO |
| arXiv | 2025-07 | [Persona Vectors](https://arxiv.org/abs/2507.21509) | Trait directions；monitoring and controlling personality shifts |
| arXiv | 2025-05 | [Feature Consistency in SAEs](https://arxiv.org/abs/2505.20254) | PW-MCC；run-to-run feature consistency |
| arXiv | 2025-05 | [Rethinking Circuit Completeness](https://arxiv.org/abs/2505.10039) | Circuit completeness；AND/OR/ADDER gates |
| arXiv | 2025-04 | [Prisma](https://arxiv.org/abs/2504.19475) | Vision/video MI toolkit |
| arXiv | 2025-03 | [SAEBench](https://arxiv.org/abs/2503.09532) | SAE benchmark；proxy-vs-practical metric gap |
| arXiv | 2025-03 | [Reasoning Features via SAEs](https://arxiv.org/abs/2503.18878) | ReasonScore；reasoning feature steering |
| arXiv | 2025-02 | [Are Sparse Autoencoders Useful?](https://arxiv.org/abs/2502.16681) | Strong baselines for sparse probing；SAE utility critique |
| arXiv | 2025-02 | [SAIF](https://arxiv.org/abs/2502.11356) | Instruction-following SAE features and steering |
| arXiv | 2025-01 | [Open Problems in Mechanistic Interpretability](https://arxiv.org/abs/2501.16496) | Field-level open problem framing |
| arXiv | 2025-01 | [Output-Centric Feature Descriptions preprint](https://arxiv.org/abs/2501.08319) | Auto-interpretability；output causal role labels |
| arXiv | 2024, revised 2025 | [Automatically Interpreting Millions of Features](https://arxiv.org/abs/2410.13928) | Open-source auto-interp pipeline；intervention scoring |
| Anthropic | 2025-03-27 | [Circuit Tracing methods](https://transformer-circuits.pub/2025/attribution-graphs/methods.html) | Cross-layer transcoder；replacement model；attribution graph |
| Anthropic | 2025-03-27 | [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) | Claude 3.5 Haiku case studies；limitations |
| OpenAI | 2025-11-13 | [Understanding neural networks through sparse circuits](https://openai.com/index/understanding-neural-networks-through-sparse-circuits/) | Interpretability-by-design；weight-sparse transformers |
| OpenAI PDF | 2025 | [Weight-sparse transformers have interpretable circuits](https://cdn.openai.com/pdf/41df8f28-d4ef-43e9-aed2-823f9393e470/circuit-sparsity-paper.pdf) | Sparse circuit details |
| arXiv | 2025-12 | [Sparse Attention Post-Training](https://arxiv.org/abs/2512.05865) | Post-training sparse attention as structural prior |
| arXiv | 2026-03 | [Sparse but not Simpler](https://arxiv.org/abs/2603.15919) | Vision sparsity caution；sparse circuits not automatically semantic |
| ACL | 2026 | [Evaluating Sparse Autoencoders for Monosemantic Representation](https://aclanthology.org/2026.findings-eacl.313/) | Monosemanticity evaluation |
| ACL | 2026 | [ELIA](https://aclanthology.org/2026.eacl-demo.9/) | Tooling/accessibility for component analyses |
| ACL | 2026 | [Where Do LLMs Compose Meaning?](https://aclanthology.org/2026.eacl-long.214/) | Compositional robustness and layerwise analysis |
| ACL | 2025 | [Output-Centric Feature Descriptions](https://aclanthology.org/2025.acl-long.288/) | ACL version of auto-interp improvement |
| ACL | 2025 | [Sparse Latents Steer RAG](https://aclanthology.org/2025.acl-long.228/) | RAG steering with sparse latents |
| ACL | 2025 | [Circuit Stability](https://aclanthology.org/2025.acl-long.442/) | Circuit stability as generalization signal |
| ACL | 2025 | [Emotion Inference MI](https://aclanthology.org/2025.findings-acl.679/) | Emotion inference mechanism |
| ACL | 2025 | [Anchored Answers](https://aclanthology.org/2025.findings-acl.124/) | Positional bias mechanism |
| ACL | 2025 | [What Do VLMs NOTICE?](https://aclanthology.org/2025.naacl-long.571/) | VLM MI pipeline |
| ACL/EMNLP | 2025 | [Route Sparse Autoencoder](https://aclanthology.org/2025.emnlp-main.346/) | Cross-layer/route SAE |
| Reddit | 2025 | [Anthropic Biology discussion](https://www.reddit.com/r/MachineLearning/comments/1jmhoq6/r_anthropic_on_the_biology_of_a_large_language/) | Community reaction; interest in attribution graphs; concerns about wording/subjective labels |
| Reddit | 2024 | [Extract symbolic AI from LLM](https://www.reddit.com/r/LocalLLaMA/comments/1990n31/extract_symbolic_ai_from_llm/) | Demand for symbolic/circuit extraction; single-token/prompt-specific bottleneck |
| Reddit | 2025 | [Model slimming/pruning discussion](https://www.reddit.com/r/LocalLLaMA/comments/1lz17w8/madness_the_ignorants_question_would_it_be/) | Community interest in pruning/knowledge removal; concern about entanglement |
| Reddit | 2025 | [Latent guardrails](https://www.reddit.com/r/LocalLLaMA/comments/1jqawj1/open_sourcing_latent_space_guardrails_that_catch/) | Community interest in latent-space control and hallucination detection |
| X | 2025 | [AnthropicAI post on Biology](https://x.com/AnthropicAI/status/1905303860765225009) | Community dissemination signal |
| X | 2025 | [SAEBench post](https://x.com/safe_paper/status/1903883552065786042) | Community dissemination signal |
| X | 2025 | [Lee Sharkey Open Problems post](https://x.com/leedsharkey/status/1884565908342874380) | Community dissemination signal |
| X | 2026 | [MI major strides post](https://x.com/mathemagic1an/status/2035850046735098065) | Community commentary signal |

## 可信度说明

- 高：arXiv/ACL/Anthropic/OpenAI 原文，用于技术结论。
- 中：Reddit 可读帖子，用于社区需求、质疑、应用想象，不用于证明论文结论。
- 低到中：X snippet，由于页面抓取受限，仅用于传播热度和议题出现，不作为技术主证据。

