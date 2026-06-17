# 多来源共同提到的下一步工作

检索日期：2026-06-11。这里的“多来源”按不同论文、博客、Reddit/X 帖子或 ACL 页面计数；渠道包括 arXiv、ACL Anthology、Reddit、X、实验室博客/论文。排序规则：先看来源数，再看任务是否具体、是否可立即启动、是否尚未完全完成。

## P0. 建立 SAE/circuit 的统一实证评估：proxy、因果、下游任务、feature consistency 同时报告

**共同来源数：8+**

来源：

- [SAEBench](https://arxiv.org/abs/2503.09532)
- [Are Sparse Autoencoders Useful?](https://arxiv.org/abs/2502.16681)
- [Feature Consistency in SAEs](https://arxiv.org/abs/2505.20254)
- [Automatically Interpreting Millions of Features](https://arxiv.org/abs/2410.13928)
- [Output-Centric Feature Descriptions](https://aclanthology.org/2025.acl-long.288/)
- [Evaluating Sparse Autoencoders for Monosemantic Representation](https://aclanthology.org/2026.findings-eacl.313/)
- [Circuit Tracing methods](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [Open Problems in Mechanistic Interpretability](https://arxiv.org/abs/2501.16496)
- X: [SAEBench dissemination](https://x.com/safe_paper/status/1903883552065786042)

**为什么是下一步**

多个来源共同指出：仅看 reconstruction loss、sparsity、loss recovered 或 LLM 生成标签不够。需要同时评估 feature 是否稳定、是否 monosemantic、是否有输出因果作用、是否在下游任务中超过强 baseline、是否在 circuit 图中 faithful。

**尚未完成**

已有 SAEBench、PW-MCC、intervention scoring、output-centric labels 等组件，但还没有一个覆盖主流 SAE 架构、cross-layer/route/subspace/functional SAE、多个模型、多个任务和因果干预的社区标准。

**具体可做项目**

在同一批模型和层上复现并合并：

- SAE 架构：TopK、JumpReLU、Gated、Matryoshka、RouteSAE、SASA、SAE-NO。
- 指标：reconstruction/loss recovered、SAEBench 任务指标、PW-MCC consistency、input/output label quality、causal steering selectivity、downstream sparse probing、circuit faithfulness。
- 输出：每个架构的 rank stability、指标冲突矩阵、何时 proxy metric 会误导、推荐默认评估协议。

## P0. 自动化 attribution graph 的解释、supernode grouping 与人工负担降低

**共同来源数：7+**

来源：

- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [Circuit Tracing methods](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [Automatically Interpreting Millions of Features](https://arxiv.org/abs/2410.13928)
- [Output-Centric Feature Descriptions](https://aclanthology.org/2025.acl-long.288/)
- [ELIA](https://aclanthology.org/2026.eacl-demo.9/)
- [Open Problems in MI](https://arxiv.org/abs/2501.16496)
- Reddit [Anthropic Biology discussion](https://www.reddit.com/r/MachineLearning/comments/1jmhoq6/r_anthropic_on_the_biology_of_a_large_language/)
- X [AnthropicAI post](https://x.com/AnthropicAI/status/1905303860765225009)

**为什么是下一步**

Anthropic 的 attribution graph 需要人工理解、剪枝、打标签和 supernode grouping；Reddit 讨论直接质疑标签主观性。自动解释论文指出 feature label 必须覆盖输入触发和输出效果。ELIA 说明 component analysis 结果对非专家仍不易用。

**尚未完成**

目前已有自动 feature label 和 graph interface，但尚未形成能把百万级 feature、prompt-level attribution graph、causal validation、supernode grouping 和 UI 合并的自动流程。

**具体可做项目**

开发 graph-to-report pipeline：

- 对每个 graph node 生成 input-centric + output-centric + causal-effect label。
- 用 activation overlap、decoder/output effect、graph role 和 perturbation effect 聚类成 supernodes。
- 自动标出 high-confidence、ambiguous、possibly spurious labels。
- 在 Anthropic-style graphs、open LLM SAEs、ACL task circuits 上评估人工节省时间和 faithfulness。

## P0. 从 prompt-specific circuit 走向跨 prompt、长上下文、全局且 faithful 的 circuit

**共同来源数：7+**

来源：

- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [Circuit Tracing methods](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [Rethinking Circuit Completeness](https://arxiv.org/abs/2505.10039)
- [Circuit Stability](https://aclanthology.org/2025.acl-long.442/)
- [OpenAI sparse circuits](https://openai.com/index/understanding-neural-networks-through-sparse-circuits/)
- [Open Problems in MI](https://arxiv.org/abs/2501.16496)
- Reddit [symbolic extraction discussion](https://www.reddit.com/r/LocalLLaMA/comments/1990n31/extract_symbolic_ai_from_llm/)
- Reddit [Anthropic Biology discussion](https://www.reddit.com/r/MachineLearning/comments/1jmhoq6/r_anthropic_on_the_biology_of_a_large_language/)

**为什么是下一步**

多个来源指出 current circuits 往往 prompt-local、短上下文、单 token 或 case-study based。Anthropic 明确说 global circuits 更难理解，长 prompt 和长内部推理链会放大误差；Rethinking Circuit Completeness 指出 OR gates 等会造成遗漏；ACL Circuit Stability 要求跨输入的一致推理过程。

**尚未完成**

还没有可靠方法能从一组 prompt 中抽取同一机制的全局 circuit，并证明它完整、faithful、能预测未见 prompt。

**具体可做项目**

选择 3 个任务族：factual recall、addition、refusal/jailbreak。对每个任务：

- 收集 500-2000 个 prompt 变体。
- 构建 prompt-level graphs，再聚合出 shared circuit family。
- 用 noising + denoising intervention 检测 AND/OR/ADDER-style completeness。
- 报告 circuit stability 与任务泛化/失败的关系。

## P1. 解决 feature splitting、absorption 与“特征不是一维”的表征几何问题

**共同来源数：6+**

来源：

- [SASA](https://arxiv.org/abs/2606.06333)
- [SAE-NO](https://arxiv.org/abs/2509.03738)
- [Feature Consistency in SAEs](https://arxiv.org/abs/2505.20254)
- [SAEBench](https://arxiv.org/abs/2503.09532)
- [RouteSAE](https://aclanthology.org/2025.emnlp-main.346/)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

**为什么是下一步**

SASA 直接指出传统一维 decoder direction 会诱导 feature splitting；SAE-NO 指出空间/频率概念需要函数式表达；RouteSAE 指出单层抽取不足；Anthropic 需要手工 supernode grouping 来弥补 features 过细。

**尚未完成**

还没有清楚结论说明哪些任务需要 vector feature、subspace feature、functional feature、route feature 或 cross-layer transcoder feature。

**具体可做项目**

在同一模型同一层/跨层比较：

- 标准 TopK SAE vs SASA vs SAE-NO/FNO vs RouteSAE vs cross-layer transcoder。
- 指标：splitting ratio、absorption rate、supernode compression ratio、feature consistency、circuit faithfulness、干预副作用。
- 目标：给出“何时该用哪种 feature parameterization”的经验规则。

## P1. 建立 steering 的 target/off-target 安全基准，避免能力破坏和概念纠缠

**共同来源数：6+**

来源：

- [Locate, Steer, and Improve](https://arxiv.org/abs/2601.14004)
- [SAIF](https://arxiv.org/abs/2502.11356)
- [Sparse Latents Steer RAG](https://aclanthology.org/2025.acl-long.228/)
- [Persona Vectors](https://arxiv.org/abs/2507.21509)
- [EEG Foundation Models via SAEs](https://arxiv.org/abs/2605.13930)
- [DLM-Scope](https://arxiv.org/abs/2602.05859)
- Reddit [latent guardrails](https://www.reddit.com/r/LocalLLaMA/comments/1jqawj1/open_sourcing_latent_space_guardrails_that_catch/)
- Reddit [model pruning discussion](https://www.reddit.com/r/LocalLLaMA/comments/1lz17w8/madness_the_ignorants_question_would_it_be/)

**为什么是下一步**

Steering 已用于 instruction following、RAG、persona、安全 guardrails、DLM decoding、EEG clinical concepts。但 EEG 工作明确显示 off-target effects、wrecking-ball interventions 和 concept entanglement；Reddit 讨论也担心删除知识或控制 latent 会误伤其他能力。

**尚未完成**

缺少跨模型、跨任务的标准化 target/off-target protocol。多数论文只证明某个目标能被 steering，而不是系统证明副作用可控。

**具体可做项目**

构建 `SteerBench-MI`：

- 目标：instruction following、hallucination propensity、refusal、RAG citation reliance、persona trait、reasoning length。
- Off-target：通用能力、事实 QA、toxicity/refusal balance、calibration、domain transfer。
- 方法：SAE latent steering、linear vectors、persona vectors、DLM diffusion-time steering、latent guardrail。
- 输出：selectivity curve、dose-response、reversibility、entanglement diagnosis。

## P1. 把 MI 系统扩展到非文本/非自回归/专业模型，并重建适合各模态的指标

**共同来源数：6+**

来源：

- [DLM-Scope](https://arxiv.org/abs/2602.05859)
- [ASR models using SAEs](https://arxiv.org/abs/2605.12225)
- [EEG Foundation Models via SAEs](https://arxiv.org/abs/2605.13930)
- [Prisma](https://arxiv.org/abs/2504.19475)
- [What Do VLMs NOTICE?](https://aclanthology.org/2025.naacl-long.571/)
- [SAE-NO](https://arxiv.org/abs/2509.03738)
- [Open Problems in MI](https://arxiv.org/abs/2501.16496)

**为什么是下一步**

近一年最新 arXiv 明显在扩展到 DLM、ASR、EEG、vision/video、VLM。每个领域都需要新 grounding：diffusion time、audio frames、clinical taxonomy、spectral decoder、vision patches、functional/spatial concepts。

**尚未完成**

语言模型 residual-stream 的默认 SAE pipeline 不能直接保证适配这些模态；各模态的 monosemanticity、faithfulness、steering selectivity 指标仍分散。

**具体可做项目**

建立跨模态 MI comparison：

- 模态：AR LLM、DLM、Whisper ASR、EEG transformer、ViT/VLM。
- 统一：feature extraction、自动标签、causal intervention、task-level behavior。
- 模态特有：audio phonetic/non-linguistic labels、EEG spectral grounding、vision spatial/frequency localization、DLM diffusion-time dynamics。

## P1. 训练可解释模型与从 dense model 提取 sparse circuits 的桥接

**共同来源数：5+**

来源：

- [OpenAI sparse circuits](https://openai.com/index/understanding-neural-networks-through-sparse-circuits/)
- [Weight-sparse transformers paper](https://cdn.openai.com/pdf/41df8f28-d4ef-43e9-aed2-823f9393e470/circuit-sparsity-paper.pdf)
- [Sparse Attention Post-Training](https://arxiv.org/abs/2512.05865)
- [Open Problems in MI](https://arxiv.org/abs/2501.16496)
- Reddit [model pruning discussion](https://www.reddit.com/r/LocalLLaMA/comments/1lz17w8/madness_the_ignorants_question_would_it_be/)
- [Sparse but not Simpler](https://arxiv.org/abs/2603.15919)

**为什么是下一步**

OpenAI 指出可以训练更稀疏、更 traceable 的模型，但也指出下一步是 scale up、解释更多行为、从 dense models 提取 sparse circuits、提高训练效率。Sparse Attention Post-Training 说明训练后也能使 attention 更稀疏。视觉反例提醒“稀疏不一定更语义可解释”。

**尚未完成**

还不知道 sparse-by-design 能否扩展到 frontier-level capability，也不知道如何可靠桥接 dense production model 和 sparse interpretable proxy。

**具体可做项目**

训练/后训练 0.1B、1B、7B 三档模型：

- 路线 A：weight sparsity from scratch。
- 路线 B：dense model post-training sparse attention。
- 路线 C：dense-to-sparse activation bridge。
- 评估：能力、circuit size、faithfulness、deployment cost、是否能转移到 dense model 分析。

## P2. Reasoning feature 与 CoT faithfulness 的机制级 benchmark

**共同来源数：5+**

来源：

- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [I Have Covered All the Bases Here](https://arxiv.org/abs/2503.18878)
- [Persona Vectors](https://arxiv.org/abs/2507.21509)
- [Locate, Steer, and Improve](https://arxiv.org/abs/2601.14004)
- [Open Problems in MI](https://arxiv.org/abs/2501.16496)
- X [Anthropic Biology dissemination](https://x.com/AnthropicAI/status/1905303860765225009)

**为什么是下一步**

Reasoning models 让 MI 更迫切：外显 CoT 可能忠实，也可能是倒推或编造。ReasonScore/SAE steering 表明能找到 reasoning moments，但需要证明这些 feature 不是只控制文本长度或风格。

**尚未完成**

缺少标准 benchmark 来区分机制级 reasoning improvement、surface-level CoT verbosity、sycophancy、hint-following 和 hidden objective。

**具体可做项目**

设计 causal CoT faithfulness suite：

- 任务：math、multi-hop QA、code tracing、counterfactual hint、deceptive objective toy setting。
- 测量：内部 feature/circuit 是否先于答案形成；干预 feature 是否改变中间状态和最终答案；是否只增加 reasoning trace 长度。
- 输出：faithful、post-hoc rationalization、backward reasoning、hidden-goal activation 的分类器和证据图。

## P2. 面向非专家的 MI 工具与报告格式

**共同来源数：4+**

来源：

- [ELIA](https://aclanthology.org/2026.eacl-demo.9/)
- [Prisma](https://arxiv.org/abs/2504.19475)
- [SAEBench](https://arxiv.org/abs/2503.09532)
- [Anthropic Circuit Tracing methods](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- Reddit [Anthropic Biology discussion](https://www.reddit.com/r/MachineLearning/comments/1jmhoq6/r_anthropic_on_the_biology_of_a_large_language/)

**为什么是下一步**

大量 MI 结果需要图、feature table、perturbation、activation examples 和指标共同解释。非专家难以判断哪些结果可信，社区讨论也显示 terminology 和 anthropomorphic framing 会引发误解。

**尚未完成**

当前工具多服务专家研究流程，没有统一的“证据等级 + 反事实验证 + 局限说明”报告格式。

**具体可做项目**

制定 MI report schema：

- Evidence：activation examples、input/output labels、intervention result、faithfulness score、known failure modes。
- Graph：nodes、supernodes、edges、pruning threshold、dark-matter/error-node contribution。
- Claims：每个自然语言结论绑定证据等级。
- UI：研究者模式与审计者模式分离。

