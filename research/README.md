# Research Harness

This directory turns `RESEARCH_PROGRAM.md` into an executable evidence program.

Stage 0 qualifies the ruler before any intervention search. It contains:

- deliberately adaptive and pathological control instruction packages;
- synthetic reference trajectories with known behavioral properties;
- a frozen evaluator-qualification contract;
- a deterministic scorer and assertion runner; and
- schemas for later agent-run evidence.

Synthetic qualification proves only that the measurement implementation reacts
correctly to known pathologies. It is not evidence that a real agent follows any
control package or that the adaptive loop works.

Run the local qualification suite:

```bash
python3 -m unittest discover -s research/tests -v
python3 research/bin/qualify_ruler.py
```

Machine-readable output:

```bash
python3 research/bin/qualify_ruler.py --json
```

The next stage will execute subject agents in isolated workspaces under exact
control packages. It is intentionally not performed by the Stage 0 command.
