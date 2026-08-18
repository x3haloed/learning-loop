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
control packages. Live experiment `LL-0002` exercised that runner with GPT-5.6
Luna. The runner succeeded, but the live transcripts falsified evaluator epoch
`EVAL-0001`; see `reports/LL-0002.md`.

The next live run is blocked on qualification of `EVAL-0002`. Do not rerun the
old allocation as though additional samples could repair its ambiguous oracle.

The pilot runner defaults to the frozen `LL-0002` contract and refuses to
overwrite its evidence directory. Any future execution must use a new contract
and evidence root:

```bash
python3 research/bin/run_pilot.py \
  --contract research/contracts/<new-contract>.json \
  --evidence-root research/evidence/pilot/<new-experiment>
```
