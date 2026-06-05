# sp-codex-select Agent Skill Pilot 准入改进计划设计

## 背景

`docs/evaluation_report/agent_skill_evaluation_report-merged-best.md` 已将五份评估报告归并为一份路线图优先的评估结论。报告判断 `sp-codex-select` 当前适合作为内部 Draft / early Pilot 候选，但不建议直接按 Pilot Ready 或 Production Ready 使用。

本设计用于指导后续实施计划文档。实施计划只覆盖 P0 和 P1，目标是服务正式 Pilot 准入。

## 目标

产出一份可执行的实施计划，保存为：

`docs/superpowers/plans/2026-06-05-agent-skill-pilot-readiness.md`

计划应指导工程师把 `sp-codex-select` 从 Draft / early Pilot 候选推进到正式 Pilot 评审门槛。重点是让安全安装、评估证据、治理材料、文档契约、脚本测试、准入校验、fallback 语义和可观测性都能被本地命令验证。

## 范围

本次计划覆盖以下 P0 / P1 工作：

- 安装脚本覆盖保护。
- 评估证据包。
- 治理材料包。
- `SKILL.md` 审计章节和负触发边界。
- `route_tasks.py` 脚本契约与测试。
- `validate_skill.py` Draft / Pilot 阶段准入检查。
- fallback 语义拆分。
- observability 流程化。
- prompt injection 与外部输入不可信说明。

本次计划只覆盖以上 P0/P1 工作，不在文档中列出其他低优先级后续路线图。

## 推荐组织方式

采用“Pilot 准入分阶段计划”。

阶段 1 处理 P0 阻塞项：

1. 修复 `scripts/install_codex_assets.sh` 默认覆盖风险。
2. 新建 `evals/` 评估证据包和评估运行入口。
3. 新建 `governance/` 治理材料包。

阶段 2 处理 P1 强化项：

1. 补齐 `SKILL.md` 审计章节、负触发和安全说明。
2. 补 `route_tasks.py` 契约测试和代表性路由测试。
3. 升级 `scripts/validate_skill.py` 为 Draft / Pilot 准入检查器。
4. 拆分 fallback 语义，避免实现重试、审查升级和最终验证混用。
5. 将 observability 从建议升级为可校验流程。

该顺序优先处理有破坏性副作用的安装入口，再建立评估和治理证据，最后补足文档与脚本验证闭环。

## 文件边界

实施计划应围绕以下文件和目录展开：

- `scripts/install_codex_assets.sh`：安装 skill 和 Codex agent TOML。默认行为必须非破坏性；覆盖必须显式。
- `evals/eval_queries.json`：触发、负触发和 near-miss 查询集。
- `evals/evals.json`：路由输出期望集，覆盖 tier、agent、role、sandbox、hard flags 和 fallback。
- `scripts/run_evals.py`：轻量评估入口，输出通过率、失败用例和失败原因。
- `governance/risk_assessment.md`：能力边界、安全风险、误路由风险、安装风险、prompt injection 风险和回滚策略。
- `governance/review_record.md`：Draft / Pilot 评审结论、阻塞项和复审条件。
- `governance/changelog.md`：路由规则、模型映射、安装行为和安全策略变更记录。
- `SKILL.md`：主契约文档，新增审计章节但保持精炼。
- `scripts/route_tasks.py`： deterministic router，补充 fallback 输出语义和兼容策略。
- `scripts/validate_skill.py`：从 smoke validator 升级为阶段准入检查器。
- `tests/`：脚本测试目录，覆盖安装、路由、validator、eval runner 和 observability。
- `references/observability.md`：JSONL schema、分析字段和 Pilot 复盘规则。

## 数据流

实施计划应形成以下闭环：

评估报告问题 -> P0/P1 任务 -> 失败测试或校验 -> 代码/文档改动 -> 本地验证命令 -> Draft/Pilot validator -> governance review record 更新。

每个任务都应能回答：

- 为什么这项工作服务 Pilot 准入。
- 修改哪些文件。
- 用什么测试或命令证明行为改变。
- 失败时应该输出什么可操作信息。

## 错误处理要求

实施计划应明确以下错误处理行为：

- 安装目标已存在且未传 `--force` 时，拒绝覆盖并退出非零。
- `--dry-run` 不写入文件系统。
- 覆盖安装必须备份旧 skill 目录，或使用等价的显式安全策略。
- eval JSON 格式错误时，输出文件、用例 id 和缺失字段。
- 路由期望不匹配时，输出 expected / actual、task id 和失败字段。
- validator 缺少 P0/P1 材料时，按 Draft/Pilot stage 输出可操作错误。
- prompt injection 文本不得改变 skill 规则、sandbox、review policy 或审批要求。
- fallback 字段必须区分实现升级、审查升级和最终验证策略。

## 测试与验证

实施计划应优先使用轻量、本地、可重复的验证方式。若仓库不引入第三方依赖，测试可使用标准库 `unittest`；若执行环境已有 pytest，则可使用 `python3 -m pytest tests -v`。

计划应至少包含这些验证命令：

```bash
python3 scripts/validate_skill.py --stage draft .
python3 scripts/validate_skill.py --stage pilot .
python3 scripts/run_evals.py --suite evals/evals.json
python3 scripts/run_evals.py --suite evals/eval_queries.json
python3 -m pytest tests -v
```

若最终选择 `unittest`，计划应给出等价命令：

```bash
python3 -m unittest discover -s tests
```

## 复杂度控制

计划应以任务目标为导向，避免把 Pilot 准入改造成完整生产化项目。

具体约束：

- evals 做最小可审计包，不追求大规模 benchmark。
- governance 做三份核心文档，不引入复杂审批系统。
- observability 固定 schema 和基础分析，不接入外部平台。
- validator 只支持 Draft / Pilot 两个 stage。
- fallback 拆分只解决语义混用，不重写整个路由算法。
- `SKILL.md` 保持轻量，详细材料留在 `references/`、`evals/` 和 `governance/`。

## 实施计划验收标准

最终实施计划文档需要满足：

- 保存到 `docs/superpowers/plans/2026-06-05-agent-skill-pilot-readiness.md`。
- 只覆盖 P0/P1。
- 以 Pilot 准入分阶段顺序组织任务。
- 每个任务包含具体文件、失败测试或校验、实现步骤、验证命令和提交建议。
- 不包含未决内容。
- 明确当前工作完成后如何证明 Draft / Pilot 准入材料已具备。
