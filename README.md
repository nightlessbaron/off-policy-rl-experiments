# Off-Policy RL Experiments

Experiment registry for off-policy asynchronous reinforcement learning studies.

Each subdirectory represents a self-contained study with its own hypothesis, configuration, results catalog, and conclusions.

## Studies

| Study | Description | Status |
|-------|-------------|--------|
| [off-policy-clip-sweep-v3](off-policy-clip-sweep-v3/) | Effect of `clip_high` on async GRPO at fixed staleness | Active |

## Structure

Each study directory follows this layout:

```
<study-name>/
├── README.md           # Hypothesis, setup, methodology
├── catalog.md          # Experiment table with configs and final results
├── conclusions.md      # Post-study findings and recommendations
└── scripts/
    └── update_catalog.py   # Pull latest results from WandB
```

## Workflow

1. **Before launching**: Write `README.md` with hypothesis and setup
2. **During training**: Metrics are tracked in WandB; run `update_catalog.py` periodically to sync final results
3. **After completion**: Fill in `conclusions.md` with findings
