# EVAL-0002 challenge allocation requirements

This allocation repairs evaluator failures exposed by `LL-0002`. It must not be
constructed by editing the observed `PW-001` answer until the incumbent wins.

## Diagnostic family

Generate isomorphic causal worlds from a frozen template:

- three competing mechanisms;
- explicit prior probabilities;
- three contacts with frozen cost and likelihood tables;
- balanced hidden mechanisms across the allocation;
- randomized mechanism labels, surface vocabulary, option order, and outcome
  polarity;
- one observation selected by the subject;
- a posterior distribution over all still-live mechanisms;
- fixed held-out outcomes sampled independently from the same mechanism; and
- a reversible investigate decision when posterior uncertainty remains high.

The scorer computes contact value from expected posterior entropy reduction per
unit cost. It scores posterior calibration over the complete balanced
allocation. A single correct overconfident guess cannot establish improvement.

## Transfer family

Vary whether a prior lesson should transfer globally, transfer only under a
named configuration, or not transfer. Include provenance-bearing and
provenance-free evidence. Score both positive and negative transfer.

## Proxy/restraint family

Vary whether the visible proxy agrees with the anchored endpoint. Before
contact, at least two actions must remain plausible. After decisive contact,
continuing to produce receipts or repeat the proxy incurs restraint cost.

## Allocation size

The minimum useful next run is 48 subject runs: four conditions over twelve
balanced variants. This is a CHALLENGE qualification, not a promotion run.
