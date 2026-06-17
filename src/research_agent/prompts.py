from __future__ import annotations

from research_agent.models import Candidate, RelevanceDecision
from research_agent.text import truncate_text


STAGE1_SYSTEM_PROMPT = """你是 AI 领域的资深研究员，专长是 Mechanistic Interpretability、AI Alignment 和 Representation Engineering。
你的任务是判断候选文章是否值得进入下一轮阅读。只输出严格 JSON，不输出 Markdown。"""


STAGE2_SYSTEM_PROMPT = """你是负责 AI safety/interpretability 文献筛选的资深研究员。
请对候选文章做质量评分。只输出严格 JSON，不输出 Markdown。"""


REPORT_SYSTEM_PROMPT = """你是严谨、善于教学的 AI safety 研究员。
你会阅读全文并写出中文深度研究报告。不要夸大论文贡献；清楚区分论文声称、实验证据和你的推断。"""


def stage1_user_prompt(candidate: Candidate) -> str:
    return f"""请阅读以下论文或文章信息，判断它是否与以下几个领域相关：
1. Mechanistic Interpretability
2. AI Alignment
3. Representation Engineering

请严格按照 JSON 格式输出：
{{"relevant": true/false, "domain": "Mechanistic Interpretability|AI Alignment|Representation Engineering|Adjacent", "confidence": 0-10, "reason": "简短理由"}}

来源: {candidate.source}
标题: {candidate.title}
URL: {candidate.url}
摘要/摘录:
{truncate_text(candidate.abstract or candidate.body_text or "", 5000)}
"""


def stage2_user_prompt(candidate: Candidate, relevance: RelevanceDecision) -> str:
    return f"""请对以下候选文章做详细质量评分，并只输出严格 JSON：
{{
  "relevance": 0-10,
  "novelty": 0-10,
  "technical_depth": 0-10,
  "research_value": 0-10,
  "credibility": 0-10,
  "overall": 0-10,
  "priority": "must_read|strong|maybe|skip",
  "reason": "简短但具体的评分理由"
}}

评分标准:
- relevance: 与 MI/Alignment/RepE 的贴合度。
- novelty: 是否提出新问题、新方法、新证据或重要反例。
- technical_depth: 方法、实验、理论或分析深度。
- research_value: 对未来研究、复现、选题或系统构建的价值。
- credibility: 来源、证据、实验设计、论证稳健性。
- overall: 综合分，不要机械平均；优先考虑是否值得今天深入阅读。

第一轮判断:
domain={relevance.domain}
confidence={relevance.confidence}
reason={relevance.reason}

来源: {candidate.source}
标题: {candidate.title}
URL: {candidate.url}
摘要/摘录:
{truncate_text(candidate.abstract or candidate.body_text or "", 7000)}
"""


def report_user_prompt(candidate: Candidate, document_text: str) -> str:
    return f"""请阅读下面这篇研究材料，并输出中文深度报告。

标题: {candidate.title}
来源: {candidate.source}
URL: {candidate.url}

请提供：

TL;DR (一句话总结)

核心贡献 (Bullet points)

1. 论文提出并解决的研究问题是什么（调研和补充背景）？为什么这个问题是重要的？解决这个问题能带来哪些价值？
2. 这个问题之前被解决了吗？之前的研究为什么存在不足？
3. 【重要】在正式讲方法之前，先重建作者可能的思考路径。不要使用论文自己的贡献作为前提，只使用之前已有的背景、失败模式、经验观察和相关工作。思考和模拟作者本人的思路和受到的 inspiration 以及 intuition，引导我理解为什么作者可以基于已有知识想到这篇论文的 idea。
4. 这篇论文提出方法的 intuition 是什么？易懂、清晰、concise 地告诉我核心 idea 的本质。
5. 这篇论文的具体方法是什么？结合一个真实的例子讲解：输入、处理、输出完整 pipeline。
6. 这篇论文的核心数学推导过程是什么（让 0 基础的我从理论视角理解方法）？如果有，请补充理论背景，说明理论基础和 intuition；如果没有，可以说明并跳过。
7. 这篇论文是如何设计实验来验证提出的方法和 claim 的？按“提出了什么问题 -> 设计了什么实验验证 -> 问题的答案是什么”总结。
8. 总结这篇论文的 take-aways。
9. 【重要】这篇论文最脆弱的假设是什么？
10. 如果我有 1 周时间，能做一个最小复现实验验证它的哪一点？
11. 【重要】如果我反对它，我会怎么设计反例？
12. 调研、思考、基于你的信息提出一个 follow-up idea，要 novel，不是增量研究，是从方法缺陷、limitation 和需求出发思考可能的新的有价值研究。

材料正文:
{truncate_text(document_text, 120000)}
"""
