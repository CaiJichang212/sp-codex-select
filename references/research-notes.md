# Research notes

The skill is based on three engineering patterns:

1. Skills use progressive disclosure: short metadata is visible by default, detailed instructions/scripts load only when selected.
2. Route by task/category rather than raw model name. This mirrors category-based delegation systems and keeps model choices configurable.
3. Use cascade/fallback: cheap-capable first for easy tasks, direct strong routing for risky tasks, and escalation after BLOCKED/review failure.

Academic and open-source inspirations include FrugalGPT-style cascades, RouteLLM-style strong/weak routing with thresholds, RouterBench-style evaluation, and LiteLLM-style router/fallback infrastructure.
