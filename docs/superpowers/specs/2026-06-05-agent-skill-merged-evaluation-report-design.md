# sp-codex-select Agent Skill 合并评估报告设计

## 背景

本次任务需要检查、核验并合并五份由不同 LLM 撰写的 `sp-codex-select Agent Skill` 评估报告，产出一份“合并最强版评估报告”，用于指导后续优化改进工作。

输入报告位于 `docs/evaluation_report/`：

- `agent_skill_evaluation_report-qwen3.6.md`
- `agent_skill_evaluation_report-minimax-m3.md`
- `agent_skill_evaluation_report-kimi-k2.6.md`
- `agent_skill_evaluation_report-gpt5.5.md`
- `agent_skill_evaluation_report-glm5.1.md`

最终报告采用用户确认的“路线图优先”形式，避免简单拼接五份报告。

## 目标

产出一份可执行的优化工作手册，保存为：

`docs/evaluation_report/agent_skill_evaluation_report-merged-best.md`

报告应优先回答三个问题：

1. 当前 `sp-codex-select` 离 Pilot / Production 准入还缺什么。
2. 哪些问题需要优先修复，为什么。
3. 每项优化如何验收，如何证明已经改好。

## 非目标

- 不修改 `SKILL.md`、脚本、agent TOML 或现有参考文档。
- 不删除或改写五份原始评估报告。
- 不把所有原报告内容逐字融合成冗长全文。
- 不引入外部资料作为主要依据；本次核验以仓库现状和五份本地报告为准。

## 编纂方法

报告将按“结论先行、证据支撑、任务落地”的方式编写。

处理每条建议时，先归并五份报告中的相同或相近问题，再对照仓库事实分类：

- 已确认：仓库当前状态支持该问题判断。
- 部分确认：问题方向成立，但原报告表述过重、遗漏已有材料或需要调整。
- 待决策：属于产品策略或治理标准选择，不能仅凭仓库事实定论。
- 不采纳：与当前仓库事实明显不符，或改动收益不足。

## 最终报告结构

1. 执行摘要：成熟度判断、最高优先级问题、推荐行动顺序。
2. 核验方法：说明输入来源、核验范围、归并规则和证据分级。
3. 关键事实核验：对 `SKILL.md`、`README.md`、`scripts/*`、`references/*`、`assets/codex-agents/*` 的短证据。
4. 优化路线图：按 P0 / P1 / P2 / P3 分组，每项包含问题、证据、影响、建议改法、验收标准。
5. 阶段准入计划：Draft 到 Pilot，再到 Production 的最低门槛。
6. 实施任务清单：可直接转为 issue 或开发计划。
7. 验证方案：脚本测试、路由样例、安装安全、文档一致性和可观测性检查。
8. 原报告共识与分歧附录：保留来源映射，但不作为主体。

## 重点优化主题

最终报告应覆盖以下主题，并按可执行优先级排序：

- 评估集和评估证据缺失。
- 治理材料缺失或不足。
- `install_codex_assets.sh` 覆盖安装风险。
- `SKILL.md` 标准章节不足，触发边界和负触发不够明确。
- `description` 过长且包含易变模型名。
- `route_tasks.py` 脚本契约、错误处理、测试覆盖和配置一致性不足。
- `validate_skill.py` 校验覆盖过窄。
- fallback 语义混合实现升级、审查升级和最终验证升级。
- 模型名硬编码和版本兼容策略不足。
- observability 只有建议，尚未成为强制记录、校验和复盘流程。
- examples 与 references 的定位、引用和维护关系不够清楚。

## 验收标准

最终 Markdown 报告需要满足：

- 文件已保存到 `docs/evaluation_report/agent_skill_evaluation_report-merged-best.md`。
- 报告主体以行动路线图为核心，而不是五份报告的顺序摘要。
- 每个 P0 / P1 问题都有证据、影响、建议改法和验收标准。
- 明确区分仓库事实、原报告共识和编纂判断。
- 保留五份报告的来源映射，便于追溯。
- 不包含 `TBD`、`TODO` 或未决占位。
- Markdown 标题层级清晰，适合后续作为优化计划输入。
