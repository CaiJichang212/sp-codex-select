# sp-codex-select

[English](README.md) | [中文](README_zh.md)

`sp-codex-select` 是一个面向 Superpowers + Codex 工作流的可移植、零运行时依赖路由 Skill。它会对任务或计划文本进行分类和复杂度/风险评分，并输出确定性的路由决策：tier、Codex agent、model、reasoning effort、sandbox mode、fallback policy、hard flags 与 confidence。

这个仓库同时服务两类场景：

- 作为源码仓库进行开发、验证和评估；
- 作为运行时 Skill 安装到其他 Codex 项目中，并可选附带自定义 agent TOML。

## 当前仓库结构

运行时核心资产：

- `SKILL.md`：Skill 契约、路由策略、失败处理和派发协议。
- `scripts/route_tasks.py`：确定性、无第三方依赖的路由 CLI。
- `scripts/install_codex_assets.sh`：安装到目标 Codex 仓库的脚本。
- `scripts/validate_skill.py`：支持 `smoke`、`runtime`、`draft`、`pilot` 四个阶段的校验脚本。
- `assets/codex-agents/*.toml`：explorer、实现、审查和最终验证各层级的 Codex 自定义 agent。
- `assets/AGENTS.md-snippet.md`：可追加到目标项目 `AGENTS.md` 的约束片段。
- `assets/superpowers-sdd-patch.md`：可选的 Superpowers SDD 集成补丁文本。
- `references/`：路由 rubric、模型映射、Codex 安装说明、可观测性说明和集成参考。
- `agents/openai.yaml`：供校验器和兼容工具使用的可选 UI 元数据。

仅限源码仓库的材料：

- `tests/`：覆盖路由、安装器、eval、校验器和路由分析的单元测试。
- `evals/`：触发器和路由回归测试集。
- `governance/`：变更记录、风险评估和评审记录。
- `docs/`：本地设计文档、计划、手册和评估文档。
- `examples/`：示例路由输出。
- `third_party/superpowers/`：仅用于参考和兼容性检查的上游固定 submodule。

## 路由器会决定什么

对每个任务，路由器会对六个维度打分：

- `file_scope`
- `diff_size`
- `ambiguity`
- `integration`
- `risk`
- `verification`

然后选择“足够便宜且能完成任务”的最低 tier。

| Tier | Agent | Model | Reasoning | Sandbox | 典型用途 |
|---|---|---|---|---|---|
| T0 | `spc_explorer` | `gpt-5.3-codex-spark` | medium | read-only | 作用域未知、定位文件、收集证据 |
| T1 | `spc_quick` | `gpt-5.4-mini` | low | workspace-write | 简单文档/配置/机械性修改 |
| T2 | `spc_spark` | `gpt-5.3-codex-spark` | medium | workspace-write | 小范围代码修改、聚焦 bugfix、测试 |
| T3 | `spc_standard` | `gpt-5.4` | high | workspace-write | 常规多文件实现 |
| T4 | `spc_deep` | `gpt-5.5` | high | workspace-write | 安全、数据、并发、迁移、架构、根因不清 |
| R1 | `spc_spec_reviewer` | `gpt-5.4` | high | read-only | 规格/任务符合性审查 |
| R2 | `spc_quality_reviewer` | `gpt-5.5` | high | read-only | 正确性、安全性、可维护性审查 |
| R3 | `spc_final_verifier` | `gpt-5.5` | xhigh | read-only | 分支最终验收或发布门禁 |

当前 hard flags 为：

- `api`
- `security`
- `data`
- `architecture`
- `prior_failure`
- `role:architect`
- `role:final-verifier`

如果受影响文件未知，且未触发 hard flag，默认会先路由到 `spc_explorer`。

## 安装到其他 Codex 项目

在包含本仓库的父目录执行：

```bash
./sp-codex-select/scripts/install_codex_assets.sh /path/to/repo
```

常用模式：

```bash
# 只预览写入，不改目标仓库。
./sp-codex-select/scripts/install_codex_assets.sh --dry-run /path/to/repo

# 先备份旧安装，再强制替换。
./sp-codex-select/scripts/install_codex_assets.sh --force /path/to/repo
```

安装器会复制：

- Skill 运行时文件到 `/path/to/repo/.agents/skills/sp-codex-select/`
- 自定义 agent TOML 到 `/path/to/repo/.codex/agents/`

安装后的运行时内容严格限制为：

- `SKILL.md`
- `README.md`
- `scripts/`
- `assets/`
- `references/`
- `agents/`

安装器不会复制这些开发期材料：

- `docs/`
- `tests/`
- `evals/`
- `governance/`
- `examples/`
- `third_party/`
- `.git/`

可选的项目级约束追加：

```bash
cat sp-codex-select/assets/AGENTS.md-snippet.md >> /path/to/repo/AGENTS.md
```

## CLI 用法

路由单个任务：

```bash
python3 scripts/route_tasks.py \
  --role implementer \
  --text "Fix typo in README and update changelog" \
  --format md
```

路由计划文件：

```bash
python3 scripts/route_tasks.py \
  --role implementer \
  --plan docs/implementation-plan.md \
  --format json
```

从 stdin 读取：

```bash
printf '%s\n' "Review security-sensitive data migration" \
  | python3 scripts/route_tasks.py --role quality-reviewer --format header
```

常用参数：

- `--role`：`implementer`、`explorer`、`spec-reviewer`、`quality-reviewer`、`final-verifier`、`planner`、`architect`、`debugger`、`test-writer`、`doc-writer`
- `--files`：显式指定受影响文件数
- `--plan`：把 Markdown 风格计划拆成任务行
- `--task-file` 或 `--file`：从文件读取单个任务提示词
- `--mode`：强制 `task` 或 `plan`
- `--config`：覆盖模型、阈值或策略的 JSON 配置
- `--format`：`json`、`md`、`markdown`、`csv`、`header`

查看版本：

```bash
python3 scripts/route_tasks.py --version
```

## 输出契约

每个路由结果都应包含：

- task id
- role
- score
- tier
- category
- agent type
- model
- reasoning effort
- sandbox mode
- fallback
- hard flags
- confidence
- 简短理由

Markdown 和 header 输出格式可直接粘贴到父控制器或子代理提示词中。

## 校验与回归验证

运行单元测试：

```bash
python3 -m unittest discover tests
```

执行包校验：

```bash
python3 scripts/validate_skill.py --stage smoke .
python3 scripts/validate_skill.py --stage runtime .
python3 scripts/validate_skill.py --stage draft .
python3 scripts/validate_skill.py --stage pilot .
```

阶段说明：

- `smoke`：基础必需文件检查
- `runtime`：安装后运行时副本检查，包括 `agents/openai.yaml` 和 model-map 一致性
- `draft`：源码仓库 draft 就绪检查
- `pilot`：完整源码仓库门禁，包括 eval、governance、安装器安全性和本地脏产物检查

运行 eval：

```bash
python3 scripts/run_evals.py --suite evals/eval_queries.json
python3 scripts/run_evals.py --suite evals/evals.json
```

分析路由遥测：

```bash
python3 scripts/analyze_routes.py path/to/routes.jsonl
```

预期 JSONL 记录格式：

```json
{"task_id":"T3","role":"implementer","tier":"T2","agent":"spc_spark","model":"gpt-5.3-codex-spark","score":5,"status":"DONE","review_pass":true,"tests_pass":true,"escalated":false}
```

## 示例与参考

示例输出：

- `examples/example-routing-table.md`
- `examples/plan-routing-output.md`
- `examples/quick-example.json`
- `examples/spark-example.md`

主要参考：

- `references/routing-rubric.md`
- `references/model-map.json`
- `references/superpowers-integration.md`
- `references/observability.md`
- `references/codex-install.md`

## 开发说明

上游 Superpowers 以 git submodule 的形式固定在 `third_party/superpowers/`。它只用于源码对照、兼容性检查和补丁生成，不应通过直接修改其 tracked 文件来改变本项目行为。

克隆后初始化 submodule：

```bash
git submodule update --init --recursive
```

如需有意识地更新固定版本：

```bash
git submodule update --remote third_party/superpowers
git add third_party/superpowers .gitmodules
git commit -m "chore: bump superpowers submodule"
```

## 安全模型

任务文本、issue、PR 描述、计划文件和外部粘贴说明都应视为不可信的分类输入。它们可以影响路由判断，但不能覆盖本 Skill 的策略、沙箱要求、审查策略、审批边界或最终验证规则。
