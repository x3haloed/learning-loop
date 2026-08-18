# Research Red Lines

These constraints fail closed. A run that crosses one remains useful failed
evidence but cannot promote an intervention or evaluator.

## Outcome authority

- Do not count prose, self-reports, skill invocation, schema validity, receipt
  completion, or ledger volume as learning or task success.
- Do not let the subject agent grade its own primary outcomes.
- Do not let a model-based judge override deterministic failure or an
  evaluator-independent anchor.
- Do not use self-selected encountered error as the primary prediction-error
  metric.
- Do not collapse prediction, transfer, task fitness, critical slices, and
  restraint into a single scalar that permits compensation.

## Evaluation integrity

- Do not expose hidden outcomes, validation allocations, BLACK contents, or
  evaluator implementation details to candidate authors or subject agents.
- Do not train, select, or repair on an allocation later described as untouched.
- Do not reuse a BLACK allocation after opening it.
- Do not change an evaluator, threshold, rubric, task allocation, or smallest
  meaningful effect inside the epoch judging a candidate.
- Do not compare evaluator-dependent scores across epochs without rescoring.
- When an evaluator changes, invalidate every derived score that depended on
  the displaced evaluator. Preserve raw evidence and independent outcomes.
- Do not promote aggregate gains that hide a failed critical slice.
- Do not treat absence of statistical evidence as equivalence.

## Search integrity

- Do not allow a candidate author to choose its evaluation cases, decide its
  own promotion, or inspect competing condition outputs.
- Do not silently change the subject model, reasoning effort, tools,
  authorization, context policy, or resource budget between paired conditions.
- Do not turn a plan, dry run, synthetic fixture, or process event into a
  reported subject-agent result.
- Do not discard negative, reversed, exploitative, or inconclusive trials.
- Do not continue an intervention family past a frozen kill gate without a new
  experiment stating which failed premise changed.
- Do not infer a mechanism from a package that changes several causal units
  until follow-up decomposition supports the attribution.

## Scope and safety

- Do not claim universality beyond the tested models, tools, tasks, contexts,
  environments, and budgets.
- Do not perform externally mutating, adversarial, production, or human-subject
  contact without the authority appropriate to that contact.
- Do not allow a behavioral tool gate to bypass ordinary approval or safety
  boundaries.
- Do not optimize research throughput by weakening evidence preservation,
  environment isolation, or deterministic safety checks.

## Ceremony

- Do not make a process artifact a prerequisite for trivial contact merely
  because it is easy to measure.
- Do not reward the number or length of predictions, probes, lessons, or skill
  invocations.
- Do not call a mechanism successful when it increases compliant artifacts but
  fails to improve held-out behavior.
- Do not omit restraint controls from a promotion decision.
