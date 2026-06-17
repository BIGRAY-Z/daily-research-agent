# 机械可解释性 MI 最新研究综述

检索日期：2026-06-11。时间窗口以 2025-2026 年为主，少量 2024 工作只作为直接前置技术引用。

## 1. Sparse Dictionary Learning / SAE 主线

**最新内容**

SAE 仍是当前 MI 的核心工具：把 dense activation 分解到稀疏 latent/features，用于解释、干预、steering 和 circuit tracing。但 2025-2026 的问题不再是“SAE 能不能找到可解释特征”，而是“找到的特征是否稳定、是否是一维、是否有因果作用、能否跨层/跨模态/跨任务复用”。

代表工作：

- [Subspace-Aware Sparse Autoencoders for Effective Mechanistic Interpretability](https://arxiv.org/abs/2606.06333), arXiv 2026-06-04：指出传统 SAE 的单 decoder direction 假设会把多维特征拆成很多 near-collinear latents；提出 SASA，用 decoder subspaces、Top-s group gating 和 nuclear-norm rank control 减少 feature splitting/absorption。
- [Mechanistic Interpretability with Sparse Autoencoder Neural Operators](https://arxiv.org/abs/2509.03738), arXiv 2025-09，2026-05 修订：把 SAE 从向量 latent 推向函数空间，提出 SAE-NO / SAE-FNO，用 concept sparsity + domain sparsity 描述概念“在哪里、如何表达”，更适合视觉、空间、频率结构。
- [Route Sparse Autoencoder to Interpret Large Language Models](https://aclanthology.org/2025.emnlp-main.346/), EMNLP 2025：批评单层 SAE 难捕获跨层 activation，提出 route-style SAE 捕捉跨层传播。
- [Position: Mechanistic Interpretability Should Prioritize Feature Consistency in SAEs](https://arxiv.org/abs/2505.20254), arXiv 2025-05：提出应系统测量 feature consistency，用 PW-MCC 等指标衡量不同训练 run 是否收敛到等价 feature set。
- [SAEBench](https://arxiv.org/abs/2503.09532), ICML 2025：提供 200+ SAE、8 类架构/算法和 8 个指标，强调 proxy metrics 不一定对应实际 interpretability/应用效果。
- [Are Sparse Autoencoders Useful? A Case Study in Sparse Probing](https://arxiv.org/abs/2502.16681), arXiv 2025-02：在 sparse probing 中用强 baseline 检验 SAE，发现 SAE 不稳定优于非 SAE 方法，要求更严格的下游评估。

**方法变化**

- 从单层、单向量 feature 转向 subspace feature、functional feature、route/cross-layer feature。
- 从 reconstruction/sparsity proxy 转向 causal steering、downstream probes、feature consistency、monosemanticity、faithfulness 和 application-level metrics。
- 从“解释一个 latent”转向“解释 latent 的 causal role 和跨层交互”。

**开放风险**

SAE 的 learned features 可能存在 splitting、absorption、不一致、评价指标冲突、解释标签不反映输出因果作用等问题。因此 SAE 目前更像强工具箱，而不是已经可靠的“模型显微镜”。

## 2. Auto-Interpretability 与 SAE 评估

**最新内容**

当 SAE latent 数量达到百万级，人类无法逐个命名，自动解释和评估成为瓶颈。

代表工作：

- [Automatically Interpreting Millions of Features in Large Language Models](https://arxiv.org/abs/2410.13928), arXiv 2024，2025 修订：构建开源 pipeline，用 LLM 生成和评分 SAE feature 描述，提出更便宜的 scoring 方法和 intervention scoring。
- [Enhancing Automated Interpretability with Output-Centric Feature Descriptions](https://aclanthology.org/2025.acl-long.288/), ACL 2025：指出仅从 activating inputs 生成描述会错过 feature 对输出的因果作用；用 feature stimulation 后的 top output tokens 或 unembedding 产生 output-centric descriptions，并与 input-centric 描述结合。
- [Evaluating Sparse Autoencoders for Monosemantic Representation](https://aclanthology.org/2026.findings-eacl.313/), Findings EACL 2026：把 monosemantic representation 的评估作为中心问题。
- [SAEBench](https://arxiv.org/abs/2503.09532)：标准化比较 SAE 架构，强调代理指标与实践效果脱节。

**方法变化**

- 解释不再只看 top activating contexts，而是结合输入触发条件、输出影响、steering/intervention 和自动评分。
- 自动解释开始与 feature similarity、run-to-run consistency、layer-to-layer similarity 联动。
- 工具层面从单篇实验转向开放 benchmark、可视化界面和可复现评估。

**开放风险**

自动标签仍可能“听起来合理但不因果”。需要把自然语言标签、feature activation、output effect 和 perturbation 结果绑定评估。

## 3. Circuit Tracing / Attribution Graph / Causal Graph

**最新内容**

2025 年 Anthropic 的两篇 Transformer Circuits 文章是这一方向的中心事件：

- [Circuit Tracing: Revealing Computational Graphs in Language Models](https://transformer-circuits.pub/2025/attribution-graphs/methods.html), 2025-03-27：用 cross-layer transcoders 构建 replacement model，把 prompt 上的计算写成 attribution graph；再用 pruning、交互式界面和 perturbation validation 检验图是否对应原模型。
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html), 2025-03-27：把方法应用到 Claude 3.5 Haiku，案例包括 two-hop reasoning、poem planning、multilingual circuits、addition、medical diagnosis、entity recognition/hallucination、refusal、jailbreak、CoT faithfulness 和 hidden goal。

相关补充：

- [Rethinking Circuit Completeness in Language Models: AND, OR, and ADDER Gates](https://arxiv.org/abs/2505.10039), arXiv 2025：关注 circuit discovery 的 completeness，指出 OR gates 等结构会让标准发现方法遗漏关键机制。
- [Circuit Stability Characterizes Language Model Generalization](https://aclanthology.org/2025.acl-long.442/), ACL 2025：用 circuit stability 作为模型泛化评估角度。

**方法变化**

- 从 activation patching / head-level circuit 转向 feature-level causal graph。
- 用 cross-layer transcoder 替换 MLP，冻结 attention patterns 和 normalization denominators，让 prompt-local feature-feature attribution 更清晰。
- 用 perturbation experiments 验证 attribution graph，而非只看图形解释。
- 用 interface、pruning、supernode grouping 降低图复杂度。

**开放风险**

Anthropic 明确列出多个限制：长 prompt、长内部推理链、reconstruction error/dark matter、inactive features 与 inhibitory circuits、graph complexity、feature splitting、global circuits 难理解、mechanistic faithfulness 不保证、attention pattern 形成尚未解释。这些限制正构成下一阶段研究路线图。

## 4. Steering、Model Editing 与 Safety Intervention

**最新内容**

MI 正在从观察性科学转向可操作干预：locate -> steer -> improve。

代表工作：

- [Locate, Steer, and Improve](https://arxiv.org/abs/2601.14004), arXiv 2026，2026-04 修订：把 actionable MI 系统整理成 localizing、steering、improving，用于 alignment、capability、efficiency。
- [SAIF](https://arxiv.org/abs/2502.11356), arXiv 2025：用 SAE latent 解释和 steering instruction following，强调精确 feature identification、final layer 和 instruction positioning。
- [Sparse Latents Steer Retrieval-Augmented Generation](https://aclanthology.org/2025.acl-long.228/), ACL 2025：用 sparse latents 控制 RAG 行为。
- [Persona Vectors](https://arxiv.org/abs/2507.21509), arXiv 2025：自动提取 persona trait directions，用于监控和控制 sycophancy、hallucination propensity 等人格/行为漂移。
- [Mechanistic Interpretability of EEG Foundation Models via Sparse Autoencoders](https://arxiv.org/abs/2605.13930), arXiv 2026：提出 target vs off-target probe area 评估 steering selectivity，并暴露 clinical entanglement 和 wrecking-ball interventions。
- Reddit [latent guardrails 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1jqawj1/open_sourcing_latent_space_guardrails_that_catch/)：社区关注 latent-space guardrail、hallucination detection 和安全拦截，但也伴随滥用、评估和误伤担忧。

**方法变化**

- 从“feature 有语义”推进到“feature intervention 能改变输出”。
- 从单个方向 steering 转向目标/副作用并重的 selectivity 评估。
- 从能力提升和安全纠偏两个方向同时使用 MI。

**开放风险**

干预容易产生 off-target damage，尤其在概念纠缠时会破坏整体能力或其他属性。当前缺少跨模型、跨任务、跨模态的标准化 steering safety benchmark。

## 5. Reasoning、CoT Faithfulness、Hidden Goals

**最新内容**

MI 被用于研究 reasoning model 的内部推理过程、CoT 是否忠实、模型是否隐藏目标。

代表工作：

- Anthropic [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)：区分模型真实执行其 CoT 所述步骤、编造理由、或从提示线索倒推答案的情况，并展示 hidden-goal model 的内部机制。
- [I Have Covered All the Bases Here](https://arxiv.org/abs/2503.18878), arXiv 2025：用 SAE 和 ReasonScore 识别 reasoning moments 中的 features，steering 后 reasoning benchmark 有提升且 reasoning trace 变长。
- [Persona Vectors](https://arxiv.org/abs/2507.21509)：把 trait vectors 用于监控训练过程中的人格/行为漂移。

**方法变化**

- 从外部 CoT 文本分析走向内部 feature/circuit causal analysis。
- 用 feature activation 与 steering 检验“推理词/反思/不确定性”是否对应真实机制。
- 用 internal directions 监控微调导致的行为变化。

**开放风险**

需要区分“真的改善推理机制”与“只让模型输出更长推理文本”。对 hidden goals、deception、sycophancy 的检测仍缺少全面、可扩展、低误报的机制级 benchmark。

## 6. 非自回归、音频、脑电、视觉、多模态与专业领域

**最新内容**

2026 年明显出现“把 SAE/MI 从文本 LLM 扩展出去”的趋势。

代表工作：

- [DLM-Scope](https://arxiv.org/abs/2602.05859), arXiv 2026：第一个面向 diffusion language models 的 SAE-based MI 框架，研究 diffusion-time interventions、decoding order 信号和 post-training 稳定性。
- [Mechanistic Interpretability of ASR models using Sparse Autoencoders](https://arxiv.org/abs/2605.12225), arXiv 2026：把 SAE 用到 Whisper encoder frame-level embeddings，发现 linguistic / non-linguistic features 和 cross-lingual feature steering。
- [Mechanistic Interpretability of EEG Foundation Models via Sparse Autoencoders](https://arxiv.org/abs/2605.13930), arXiv 2026：把 TopK SAE 用于 SleepFM、REVE、LaBraM，结合临床 taxonomy 和 spectral decoder。
- [Prisma](https://arxiv.org/abs/2504.19475), arXiv 2025：视觉/视频 MI 工具包，覆盖 75+ vision/video transformers、80+ pretrained SAE weights、SAE/transcoder/crosscoder 训练和 circuit analysis。
- [What Do VLMs NOTICE?](https://aclanthology.org/2025.naacl-long.571/), NAACL 2025：面向 VLM 的 MI pipeline。
- [Sparse Autoencoder Neural Operators](https://arxiv.org/abs/2509.03738)：面向空间/频率结构和跨分辨率泛化。

**方法变化**

- 从 token-level residual stream 扩展到 frame-level audio embeddings、EEG embeddings、vision patches、function-space concepts。
- 增加领域 grounding：临床 taxonomy、频谱解码、跨语言语音 steering、视觉局部/频率结构。

**开放风险**

不同模态的 activation 结构、任务目标和 ground truth 差异很大。文本 LLM 的 SAE 指标和解释习惯不一定直接适用。

## 7. Interpretability-by-Design / Sparse Circuits

**最新内容**

OpenAI 把方向从“训练后解释 dense model”扩展到“训练时让模型更可解释”。

代表工作：

- [Understanding neural networks through sparse circuits](https://openai.com/index/understanding-neural-networks-through-sparse-circuits/), OpenAI 2025-11-13：训练 weight-sparse transformers，让 circuits 更小、更易 trace；提出 capability-interpretability frontier，并指出下一步包括扩展到更大模型、解释更多行为、从 dense model 提取 sparse circuits、提高训练效率。
- [Weight-sparse transformers have interpretable circuits](https://cdn.openai.com/pdf/41df8f28-d4ef-43e9-aed2-823f9393e470/circuit-sparsity-paper.pdf), OpenAI PDF：论文版。
- [Sparse Attention Post-Training for Mechanistic Interpretability](https://arxiv.org/abs/2512.05865), arXiv 2025：通过 post-training attention sparsity 在保留 loss 的同时简化 circuit。
- Reddit [model slimming / pruning 讨论](https://www.reddit.com/r/LocalLLaMA/comments/1lz17w8/madness_the_ignorants_question_would_it_be/)：社区直觉也指向 pruning、distillation、knowledge removal，但指出 LLM 知识不按可删除类别整齐组织。

**方法变化**

- 从后验分解走向训练约束：weight sparsity、attention sparsity、activation bridges、dense-to-sparse extraction。
- 把 interpretability 纳入模型设计 objective，而不是只作为事后分析。

**开放风险**

目前 sparse circuit 模型远小于 frontier 模型，且大量计算仍未解释。稀疏性是否会在复杂开放任务中保持能力和可解释性，是未解决问题。

## 8. ACL/NLP 任务级 MI

**最新内容**

ACL 系列论文把 MI 应用于更具体的 NLP 行为、任务偏差和可用工具。

代表工作：

- [Mechanistic Interpretability of Emotion Inference in Large Language Models](https://aclanthology.org/2025.findings-acl.679/), Findings ACL 2025：研究 LLM emotion inference 的内部机制。
- [Anchored Answers: Unravelling Positional Bias in GPT-2's Multiple-Choice Questions](https://aclanthology.org/2025.findings-acl.124/), Findings ACL 2025：用 MI 分析 multiple-choice positional bias。
- [Circuit Stability Characterizes Language Model Generalization](https://aclanthology.org/2025.acl-long.442/), ACL 2025：把 circuit stability 作为泛化能力刻画。
- [Simplifying Outcomes of Language Model Component Analyses with ELIA](https://aclanthology.org/2026.eacl-demo.9/), EACL 2026 demo：交互式工具，降低 component analysis 结果的使用门槛。
- [Where Do LLMs Compose Meaning?](https://aclanthology.org/2026.eacl-long.214/), EACL 2026：用 layerwise analysis 和 intervention/信息论研究 compositional robustness。

**方法变化**

- NLP 社区更关注“特定行为如何形成”和“分析工具如何让非 MI 专家使用”。
- MI 开始进入 emotion、bias、RAG、ICL、compositionality、SQL 等具体 NLP workflow。

**开放风险**

任务级发现容易局限在单模型/单数据集/单提示模板。需要把任务级 MI 与全局 circuit、feature stability 和 robust benchmark 连接起来。

## 9. 社区渠道：Reddit 与 X 的信号

**Reddit**

- [r/MachineLearning: Anthropic On the Biology](https://www.reddit.com/r/MachineLearning/comments/1jmhoq6/r_anthropic_on_the_biology_of_a_large_language/)：社区关注 attribution graph、inner-monologue tracing、safety，同时质疑“biology/think”等表述是否过度拟人化，以及 replacement model 的标签是否主观。
- [r/LocalLLaMA: Extract symbolic AI from LLM](https://www.reddit.com/r/LocalLLaMA/comments/1990n31/extract_symbolic_ai_from_llm/)：社区把 circuit extraction 视作接近 symbolic extraction 的路径，但指出当前常局限在单 token、prompt-specific 或 fuzzy concept。
- [r/LocalLLaMA: model slimming/pruning](https://www.reddit.com/r/LocalLLaMA/comments/1lz17w8/madness_the_ignorants_question_would_it_be/)：社区希望删除不需要的知识/专家，但也承认 LLM 表征纠缠，不能按类别干净移除。
- [r/LocalLLaMA: latent guardrails](https://www.reddit.com/r/LocalLLaMA/comments/1jqawj1/open_sourcing_latent_space_guardrails_that_catch/)：社区对 latent-space guardrails 和 hallucination detection 有兴趣，但争议集中在误伤、滥用和验证。

**X**

X 页面抓取较受限，本次仅将可检索 snippet 作为社区传播信号，不作为技术细节主证据：

- [AnthropicAI: On the Biology of a Large Language Model](https://x.com/AnthropicAI/status/1905303860765225009)：传播 Anthropic circuit tracing 案例。
- [safe_paper: SAEBench](https://x.com/safe_paper/status/1903883552065786042)：传播 SAEBench。
- [Lee Sharkey: Open Problems in Mechanistic Interpretability](https://x.com/leedsharkey/status/1884565908342874380)：传播 open problems review。
- [mathemagic1an: MI has made major strides](https://x.com/mathemagic1an/status/2035850046735098065)：社区把 Anthropic biology 工作视作近期进展代表。

