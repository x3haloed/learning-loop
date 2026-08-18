# Adaptive Loop Instruction Research Program

## 1. Research objective

Find a minimal, scoped package of `AGENTS.md` instructions and skills that
causes coding agents to:

1. form consequential expectations before contact with the world;
2. choose contact that can discriminate between live explanations;
3. notice and explain material discrepancies rather than merely patch symptoms;
4. change later predictions or actions in the direction warranted by evidence;
5. transfer lessons to related cases and fresh contexts;
6. continue seeking informative error after familiar checks saturate; and
7. do all of this without substituting ceremony, evaluator gaming, or local
   proxy improvement for useful progress in the underlying task.

The research target is behavior, not textual agreement with the loop. A package
does not receive credit for mentioning predictions, producing a ledger, invoking
a skill, satisfying a schema, or claiming to have learned. Those are process
observations, never success evidence. Credit comes only from externally
observed changes in contact, prediction, transfer, and task outcomes.

There may be no universally exact package. The result of this program is a
smallest-supported package with an explicit validity scope: agent models,
tooling, task families, context lengths, and cost regime under which the result
has survived contact.

### 1.1 First-class hypotheses

The program maintains three hypotheses of equal standing.

- **H-loop:** a minimal package of loop instructions and triggered corrective
  skills induces the seven behaviors above without substituting ceremony,
  evaluator gaming, or local proxy improvement for useful progress.

- **H-representation-emergence:** functional learning pressures plus
  representation-failure detection are sufficient to cause agents to construct
  useful representational machinery when their incumbent representation stops
  transferring learning.

- **H-frontier-expansion:** the loop's default search is biased toward error
  correction over an already-represented model, so a package that additionally
  presses the agent to expand its model frontier outward—asking what relevant
  structure, cause, purpose, actor, or larger system lies just beyond what it
  currently represents, rather than only testing what it already believes—will
  change prediction or action in cases where the inward-only loop stays silent.
  This is distinct from `H-loop` and `H-representation-emergence`: it targets
  coverage of the model (structure not yet represented) rather than accuracy of
  an existing model or transfer of represented lessons. Its degenerate mode,
  guarded against by the same restraint costs as the other hypotheses, is
  infinite ontology excavation that never changes prediction or action.

Three conditions are compared under progressively stronger representation
pressure (Section 7.3):

- **A. No adaptive loop.** No loop instructions, no skills.
- **B. Adaptive loop, representation unconstrained.** The package search space
  of Section 4; no prescribed representation.
- **C. Adaptive loop plus a prescribed ledger/schema/retrieval mechanism.** An
  externally imposed representation, run only as a diagnostic comparison
  condition, permitted by the representation red line.

The decisive result would be **B eventually beating C**: B can invent
representations matched to the actual failure regime, while C is confined to
the researcher's ontology. That comparison tests the core claim the program
exists to establish.

## 2. Central threat model

The program assumes the subject agent will discover cheap ways to satisfy any
stable proxy it can see. Expected failure strategies include:

- narrating the loop without changing actions;
- logging vague or trivial predictions;
- selecting easy contacts that make prediction error appear low;
- producing many local discrepancies without improving the final task;
- overfitting to familiar scenario and evaluator language;
- invoking a skill by keyword rather than by condition;
- changing the evaluator or scope until a weak result passes;
- preserving lessons that are never retrieved;
- installing conventional ledgers, schemas, or retrieval machinery because
  such structures are conventional rather than because an observed transfer
  failure demands them;
- repeating a successful subloop after its marginal value has collapsed;
- avoiding ambitious claims, actions, or probes to protect calibration;
- spending enough ceremony to crowd out the work being improved; and
- exploiting aggregate metrics while failing a consequential slice.

The evaluator is therefore part of the attack surface. It may improve, but not
continuously or on its own authority. Evaluation changes occur only at declared
epoch boundaries, against evidence that does not depend on the evaluator being
replaced.

## 3. Normative authority

Before candidate search begins, freeze three sources of authority.

### 3.1 Behavioral target

`TARGET.md` will define the behavioral construct, required slices, stopping
conditions, and interpretation limits. Candidate-generating agents may propose
changes to it, but cannot apply them inside an active experiment epoch.

The target distinguishes four outcomes that must not be collapsed:

- **elicitation:** the agent states or records the relevant expectation;
- **contact quality:** the selected action is capable of resolving an important
  uncertainty;
- **learning:** evidence improves a later prediction or decision;
- **task fitness:** the underlying artifact or outcome improves under
  representative pressure.

An intervention can improve one while harming another.

### 3.2 Red lines

`RED_LINES.md` will forbid:

- counting process compliance as outcome success;
- training on or inspecting sealed evaluation outcomes;
- changing a threshold in the same epoch as the candidate judged by it;
- silently changing task scope, agent model, tool authority, or resource budget;
- promoting an aggregate improvement that hides a failed critical slice;
- interpreting evaluator-dependent scores across evaluator epochs as comparable;
- discarding failed, reversed, or exploitative trials;
- allowing a model-based judge to override deterministic task failure;
- requiring, rewarding, or preferentially exposing a particular durable
  representation as part of the default intervention; and
- claiming universality outside the tested validity scope.

### 3.3 Raw evidence

Task states, tool calls, captured predictions, contacts, outcomes, final
artifacts, costs, evaluator versions, candidate-package hashes, and environment
identities are retained independently of their interpretation. Derived scores
may be recomputed; original observations may not be rewritten.

## 4. Unit under search

Every candidate is an immutable **intervention package**:

```text
package = {
  agents_instructions,
  installed_skills,
  skill_catalog_descriptions,
  skill_bodies,
  package_manifest
}
```

The package manifest records exact content hashes, component IDs, ordering,
token count, and installation/discovery state.

Instructions are authored as independently switchable components before being
compiled into natural prose. Skills are independently switchable at the
catalog-description and body levels. This supports ablation without forcing the
deployed artifact to read like a checklist.

The intervention under test contains only things that define physics,
motivation, and triggered corrective procedures: core loop instructions, skill
descriptions and triggers, and skill bodies. Candidate component families
include:

- definitions and standing motivation;
- orientation and uncertainty selection;
- explicit prediction and precommitment;
- discrepancy recovery and causal discrimination;
- adaptation and adjacent probing;
- representation-failure detection and repair;
- evaluator-divergence handling;
- completion and stopping conditions;
- skill split, merge, trigger wording, and negative boundaries; and
- escalation when repeated local work ceases to improve held-out outcomes.

The search must include deletion, compression, and merge operations. More
instruction is not presumed better.

### 4.1 What is deliberately excluded from the package

The package contains no prescribed durable representation. No ledger, schema,
receipt, memory format, knowledge graph, or automatic retrieval mechanism is a
candidate component. The research question is not "which learning machinery
should we install?" but "can we induce the agent to notice when its learning
machinery is inadequate and invent an improvement?" Prescribing representation
would pre-answer that question and bake the researcher's ontology into the
intervention before any failure regime has demanded it.

Representations appear in the program in exactly two places:

- as subject-invented adaptations, judged only by their later behavioral
  consequences; and
- as externally imposed comparison conditions in experiments that
  specifically study imposed representation (condition C, Section 7.3),
  permitted by the representation red line.

## 5. External research instrumentation

The research program has two layers, and they must not blur.

### 5.1 Intervention under test

Only the package of Section 4: instructions, skill descriptions and triggers,
and skill bodies. No ledger, no durable schema, no automatic retrieval, no
required receipt, no prescribed memory format.

### 5.2 Research instrumentation

The harness may keep receipts, traces, hashes, predictions, and raw
observations **for scientific measurement**. The subject agent should not
experience those as part of its learning machinery.

Instrumentation must be observational where possible. For example, the harness
secretly snapshots the agent's stated expectation before an outcome is
revealed, so researchers can score calibration. That is observation.

Instrumentation is intervention-bearing when it changes the subject's
available representations or required workflow. Requiring the agent to fill
out `prediction_receipt.json` before a tool reveals a result changes the
agent's epistemic machinery. Instrumentation that changes the subject's
available representations or required workflow is a separate experimental
condition, not part of the default adaptive-loop package.

A captured prediction earns zero research utility by itself. The harness
separately scores whether the prediction was informative, whether the contact
discriminated, whether later forecasts improved, and whether the task
benefited. A thousand compliant artifacts with no transfer or task gain score
worse than a package that learns with little ceremony.

The same rule applies to anything the subject agent invents on its own:
existence is never success. Only a later behavioral consequence can validate
it.

## 6. Two evaluation lanes

Forced instrumentation can create the behavior it purports to observe. Every
candidate is therefore evaluated in two lanes.

### 6.1 Free-action lane (default condition)

The subject receives the task and intervention package, with ordinary tools.
The harness observes—via tool calls, transcripts, and file snapshots—whether
the agent spontaneously predicts, probes, invokes skills, updates, transfers,
and stops appropriately. When the agent states an expectation before an
outcome, the harness captures it observationally. This measures behavioral
induction without altering the agent's machinery.

### 6.2 Forced-prediction lane (diagnostic manipulation)

At predeclared consequential boundaries, the harness requires the agent to
state an expectation before revealing the next observation. This makes
predictions externally scorable and measures the quality of the agent's model
when elicitation is held constant.

The forced-prediction lane is a diagnostic manipulation, not a candidate
architecture for the final loop. A verified package cannot rely on forced
receipts. Any gain observed only in this lane is reported as an artifact of
the manipulation, and runs in this lane are labeled intervention-bearing
measurement.

Together these lanes distinguish:

- an agent that has a useful model but needs a behavioral nudge;
- an agent that produces compliant predictions with no useful model;
- an agent that acts adaptively without explicit ceremony; and
- an intervention that improves both spontaneous behavior and measured learning.

## 7. Experimental worlds

No one world is allowed to define the loop. The suite contains at least the
following independent families.

### 7.1 Controlled micro-worlds

Small environments with hidden causal rules, bounded contact budgets, and
deterministic or probabilistic ground truth. They permit exact scoring of:

- prediction quality before and after evidence;
- probe discrimination;
- boundary discovery;
- scope revision under distribution shift;
- recovery from surprising success and failure; and
- transfer to held-out instances.

### 7.2 Seeded software investigations

Repositories contain hidden but externally known failure mechanisms. Several
plausible explanations fit the initial symptoms, and cheap probes differ in
their information value. The endpoint is scored by hidden tests and by whether
the learned explanation predicts adjacent cases, not by the patch narrative.

### 7.3 Representation-pressure worlds

These worlds test `H-representation-emergence`. The agent receives work where
ordinary context is initially sufficient for learning to transfer. Conditions
are then introduced, progressively, under which its incumbent representation
stops working:

- context compaction;
- long delays between evidence and its later use;
- many unrelated distractors;
- contradictions;
- multiple scopes where a lesson applies differently;
- repeated rediscovery of the same constraint;
- parallel subproblems;
- prior evidence that must affect a much later decision; and
- changed evaluator interpretations while raw evidence remains relevant.

The package does not tell the agent what representation to build. Worlds are
scored on five questions:

1. **Notice:** does the agent detect that transfer is failing?
2. **Diagnose:** does it locate the failure in representation rather than in
   the domain, the artifact, or the evaluator?
3. **Invent:** does it construct a mechanism of its own?
4. **Repair:** does that mechanism reduce recurrence and improve later
   prediction or action?
5. **Discard:** does it later modify or discard the mechanism when that
   mechanism becomes maladaptive?

The fifth criterion is load-bearing. The program rewards the full self-loop—
*agent invented a ledger because causal lessons were being lost; later
discovered the ledger was too noisy; replaced it with scoped causal summaries;
transfer improved*—not the single act of *agent invented a ledger*. That
trajectory is illustrative: the passing shape is repair followed by further
repair under continuing pressure, not any particular representation.

Conditions A, B, and C (Section 1.1) all run on this family under progressively
stronger pressure, so the comparison tests whether an unconstrained loop
eventually beats a prescribed representation when both face the same failure
regime.

### 7.4 Evaluator-divergence worlds

The visible evaluator initially correlates with the true outcome and then
becomes incomplete or gameable. The subject must detect divergence without
being rewarded merely for declaring the evaluator broken. Hidden endpoint
outcomes determine whether changing the evaluation regime improved decisions.

### 7.5 Saturation worlds

Familiar checks continue passing while untested boundaries remain. These worlds
test `seek-prediction-error` and distinguish useful search from novelty seeking.

### 7.6 Restraint controls

Trivial, already-resolved, low-stakes, authorization-limited, and genuinely
complete tasks test whether the package knows when *not* to invoke the loop.
Unnecessary predictions, probes, skill invocations, mutations, and delay count
as task cost.

### 7.7 Ecological tasks

Realistic, longer coding and research tasks supply external validity. Their
scoring combines deterministic outcomes, blinded review where unavoidable, and
fresh follow-up tasks that test whether any lesson survived. These cannot
replace the controlled worlds because causal attribution is weaker.

## 8. Skill-trigger evaluation

Skill selection and skill effectiveness are different measurements.

Each trigger case includes a transcript or task state, required skills,
permitted skills, prohibited skills, and the evidence that justifies the label.
The suite includes:

- direct positives;
- lexical and semantic near misses;
- paraphrases;
- irrelevant keyword mentions;
- cases requiring several prior turns;
- overlapping failures where more than one skill is valid;
- cases where a tempting skill is premature; and
- cases where no skill should trigger.

Activation is measured from host-level skill selection/load telemetry. It is
not inferred from final prose. If the host cannot expose this event, the
research harness may use a randomized test-only body canary inaccessible from
the catalog description. This fallback is reported as intervention-bearing
measurement, not transparent observation.

Metrics include required-trigger recall, prohibited-trigger rate, overlap-set
accuracy, confusion matrices, time-to-trigger, and repeatability. Conditional
on activation, separate rubrics and world outcomes measure whether the skill
changed behavior appropriately.

The initial routing ontology is:

| Condition | Primary intervention |
| --- | --- |
| No discrepancy yet; choose a vulnerable uncertainty | `seek-prediction-error` |
| Material observation differs; cause unresolved | `resolve-prediction-error` |
| Evidence failed to alter a later prediction or action | `repair-learning-representation` |
| Evaluator and reality-grounded outcome systematically diverge | `evolve-evaluation-regime` |

This ontology is a hypothesis to test. Overlap may prove more effective than
exclusive routing.

## 9. Outcome measures

There is no single optimization score. Candidates are compared on a vector of
outcomes with conjunctive promotion gates.

### 9.1 Primary outcomes

1. **Held-out prediction loss.** Proper scoring rules for probabilistic
   predictions, absolute error for quantities, and exact outcome error where
   appropriate, all on contacts the subject did not select.
2. **Transfer gain.** Improvement on related unseen cases and fresh-context
   decisions after relevant evidence.
3. **Underlying task fitness.** Hidden-test success, decision regret, or another
   outcome grounded outside the candidate's own evaluator.
4. **Critical-slice floor.** Worst-slice behavior on boundaries, distribution
   shifts, contradictions, evaluator divergence, and restraint controls.

### 9.2 Diagnostic outcomes

- spontaneous prediction rate at consequential moments;
- informativeness and discriminating power of selected contacts;
- material model revisions per unit of contact cost;
- recurrence of previously resolved error;
- transfer-failure detection latency under representation pressure;
- whether a detected transfer failure is attributed to representation rather
  than to the domain, artifact, or evaluator;
- rate of subject-invented representational mechanisms and their causal
  relation to reduced recurrence;
- rate at which the agent later modifies or discards an invented mechanism
  when that mechanism becomes maladaptive;
- skill activation precision and recall;
- causal explanation accuracy on hidden adjacent cases;
- time, tokens, tool calls, and externally mutating actions;
- unnecessary ceremony on restraint controls; and
- gap between logged compliance and actual outcome improvement.

Observed failures encountered by the agent are not a primary error metric. A
stronger agent may encounter more error because it probes harder regimes.
Prediction-error reduction is measured at fixed hidden checkpoints; error
discovery is measured separately.

## 10. Promotion rule

A challenger may replace an incumbent only when all of the following hold on
untouched validation evidence:

1. paired held-out prediction loss improves by a predeclared practically
   meaningful amount, with an uncertainty bound excluding material harm;
2. underlying task fitness is non-inferior overall and on every critical slice;
3. transfer improves or remains non-inferior when the candidate's claimed
   mechanism is not transfer-related;
4. restraint cost remains below its frozen ceiling;
5. no deterministic red line fails;
6. no newly discovered exploit explains the measured gain; and
7. the claimed mechanism predicts at least one observed process difference.

Candidates that trade outcomes without clearing every gate remain on a Pareto
frontier; they do not silently replace the default. A process metric alone can
never promote a candidate.

Thresholds and smallest effects of interest are set during evaluator
qualification using deliberately good, broken, verbose, evasive, and gaming
policies. Those qualification cases are disjoint from candidate search. Once an
epoch begins, its evaluator, thresholds, task allocation, and promotion rule
are frozen.

## 11. Co-evolving, adversarial evaluation

The research program uses controlled evaluator evolution rather than a fixed
benchmark or an unrestricted moving target.

Within an epoch:

- the evaluator implementation and rubric are frozen;
- discovery and visible validation allocations are fixed;
- candidate packages may evolve;
- a red-team agent searches for packages or trajectories that score well
  without improving the underlying target; and
- all candidate-dependent raw evidence is retained.

At an epoch boundary:

1. evaluator challengers are built from observed false positives, false
   negatives, saturated slices, and successful attacks;
2. each challenger is judged against an evaluator-independent anchor containing
   deterministic outcomes and separately obtained human judgments where the
   target terminates in human experience;
3. the challenger replaces the incumbent only if it improves anchor agreement
   without weakening existing critical slices;
4. ties retain the incumbent;
5. scores dependent on the displaced evaluator are invalidated and candidate
   artifacts are lazily rescored; and
6. raw evidence and evaluator-independent outcomes survive the transition.

This adopts the useful Red Queen structure—frozen within-epoch utility,
anchor-gated evaluator replacement, and selective erasure—without allowing the
candidate and its judge to drift together unchecked.

The sealed BLACK suite is never used to evolve the evaluator or candidate. Once
opened, it is spent. A later search epoch requires a newly generated and frozen
BLACK allocation from held-out world templates, seeds, repositories, and human
cases.

## 12. Agent-led search organization

The program assigns separate roles with isolated context and authority:

- **research director:** selects the next high-information experiment from
  visible evidence and remaining uncertainty;
- **candidate author:** edits one intervention package and states its predicted
  mechanism and failure risk;
- **subject agents:** perform tasks under immutable candidate packages without
  access to hidden outcomes or competing conditions;
- **attack agent:** searches for evaluator exploits, ritual compliance, and
  low-value local minima;
- **harness:** allocates worlds, enforces budgets, captures raw evidence, and
  applies deterministic scoring;
- **evaluator challenger:** proposes evaluator repairs at epoch boundaries;
- **independent auditor:** reviews promotions, evaluator replacements, and a
  sample of model-judged cases; and
- **archivist:** preserves manifests, lineage, failures, reversals, and
  interpretation boundaries.

The candidate author does not select its tasks, view sealed results, edit the
evaluator, or decide its own promotion. The research director may use aggregate
visible results but not hidden task contents.

### 12.1 Candidate-generation grammar

Candidate authors edit through declared operators so the search remains
inspectable:

- add, remove, compress, expand, or reorder one instruction component;
- split, merge, add, or remove one skill;
- change a skill's catalog trigger separately from its body;
- transplant a component from a successful package into a different lineage;
- revert a prior edit; or
- propose a larger component jump with an explicit reason smaller edits cannot
  discriminate the live hypotheses.

Ordinary experiments change one causal unit. Larger jumps receive a separate
lineage and must later be decomposed before their mechanism is considered
understood.

Every proposal states:

- the observed limitation in the parent package;
- why the changed component should alter subject behavior;
- which primary or diagnostic outcome should move;
- which outcome should remain unchanged;
- the cheapest world capable of falsifying the mechanism; and
- the most likely way the candidate could game the current evaluator.

### 12.2 Candidate archive and scheduler

The search maintains a diverse archive rather than one hill-climbing champion.
Archive cells are indexed by intervention family, mechanism, complexity band,
and behavioral profile. A package with a lower aggregate score may remain if it
is uniquely strong on transfer, restraint, skill routing, or exploit resistance.

At each research step, the director chooses among four actions:

1. **expand** a promising or behaviorally distinct package;
2. **replicate** an uncertain comparison;
3. **attack** a package or evaluator whose gain may be cheap compliance; or
4. **repair the ruler** at an epoch boundary after a demonstrated evaluator
   failure.

Selection favors expected information gain per subject-run cost, not expected
score alone. The scheduler must reserve fixed budget shares for replication,
negative controls, attacks, and underexplored component families so early noisy
winners do not monopolize the program.

Evaluation follows a funnel:

1. installation and trigger smoke tests;
2. cheap controlled micro-worlds and restraint controls;
3. broader controlled worlds;
4. representation-pressure episodes;
5. seeded software investigations;
6. ecological tasks; and
7. sealed confirmation.

A candidate killed at a cheap gate is not run at later gates unless a new
experiment identifies which failed premise has changed.

### 12.3 Evidence allocations

Each world family is generated into immutable allocations:

- **DISCOVERY:** visible outcomes available for mechanism development;
- **VALIDATION:** hidden outcomes used for frozen promotion decisions;
- **CHALLENGE:** adversarial cases created against a frozen candidate or
  evaluator, then held out from the repair they motivate; and
- **BLACK:** sealed final confirmation, spent permanently when opened.

Repeated package search must not query the same validation allocation without
limit. An epoch has a fixed validation-query budget. Exhausting it closes the
epoch and requires either promotion from the existing evidence or a new frozen
allocation. Challenge cases join a future anchor or validation allocation only
after their generation process, expected answer, and independence have been
audited.

### 12.4 Comparison design

Candidate and incumbent run on paired world instances, blocked by subject model,
task family, difficulty, and context condition. Their order is randomized where
shared machine state or evaluator order could matter. Subject agents receive
fresh contexts and cannot observe the other condition.

Comparisons proceed sequentially under a predeclared maximum budget:

- stop early for deterministic red-line failure;
- stop for futility when the candidate cannot clear the smallest meaningful
  effect within the remaining budget;
- stop for promotion only when every conjunctive gate clears; and
- otherwise report the result as uncertain rather than converting absence of
  evidence into equivalence.

Uncertainty is computed over world instances and repeated subject runs, not
over individual log lines or predictions treated as independent. Model, world,
and task-family effects remain visible in the report. The package archive uses
conservative lower bounds for selection, while raw paired effect distributions
remain available for later evaluator regimes.

## 13. Search stages

### Stage 0 — Qualify the ruler

Construct deliberately adaptive, prose-only, ritualistic, evasive, and broken
reference policies. Confirm that the suite distinguishes them in the predicted
directions. Repair insensitive evaluators before candidate search begins.

### Stage 1 — Establish baselines

Run at least:

- no loop instructions and no skills (condition A);
- current `AGENTS.md` only;
- current skills only where the host can discover them;
- current `AGENTS.md` plus current skills (condition B);
- the loop plus a prescribed ledger/schema/retrieval mechanism (condition C,
  run as a diagnostic comparison, not a search candidate); and
- a token-length-matched neutral instruction control.

Use paired worlds, fixed budgets, repeated subject runs, and identical model
and tool configurations.

### Stage 2 — Isolate behavioral actuators

Test instruction prose, skill triggers, and skill bodies separately and in
combination. Begin with cheap trigger, micro-world, and restraint gates.
Escalate only survivors to representation-pressure and ecological tasks. The
package grammar contains no prescribed representation; any candidate that
adds one is condition C, a diagnostic comparison rather than an adaptive-loop
candidate.

### Stage 3 — Adversarial epoch

Freeze the best visible package and evaluator. Ask attack agents to generate
tasks and package variants that maximize measured success while withholding
real learning. Add confirmed evaluator failures to a challenger evaluator, not
to the active epoch.

### Stage 4 — Controlled evaluator transition

Qualify the challenger on the independent anchor. If promoted, invalidate all
dependent scores and re-evaluate the surviving package archive. Record which
apparent gains disappear under the stronger evaluator.

### Stage 5 — Instruction and skill minimization

Take the strongest robust package and perform deletion and interaction tests:

1. remove each instruction component and skill alone;
2. use grouped delta debugging to remove larger subsets;
3. test pairwise and selected higher-order interactions where removals disagree;
4. add removed components back to confirm reversibility; and
5. prefer the smaller package when the larger one is not meaningfully better.

A component is retained only if removing it crosses a promotion gate, damages a
critical slice, or enables a repeatable exploit. This produces a
smallest-supported set within the searched component grammar, not a claim of
metaphysical uniqueness.

### Stage 6 — Replication and scope

Repeat the minimized package across:

- at least two agent model families or capability levels;
- multiple context lengths and compaction conditions;
- controlled and ecological task families;
- fresh world templates and seeds;
- cold and warm lesson state; and
- at least one independent operator or environment.

Failures narrow the validity scope or reopen candidate search. They are not
averaged away.

### Stage 7 — Sealed confirmation

Freeze the exact package, runner, evaluator, thresholds, and environment. Run
the BLACK suite once. Publish the complete result, including failures and cost.
If BLACK fails, it becomes evidence for the next epoch but cannot be reused as
that epoch's BLACK suite.

## 14. Experiment and evidence contract

Every serious experiment receives an append-only `LL-NNNN` record containing:

- research question;
- prior belief and consequential prediction;
- candidate and incumbent hashes;
- changed component IDs;
- proposed causal mechanism;
- evaluator epoch and frozen gate contract;
- world allocation manifest and visibility class;
- subject model, tools, budgets, seeds, and environment;
- raw-evidence manifest and hashes;
- primary and diagnostic outcomes by slice;
- attack findings;
- result relative to the prediction;
- disposition: `promoted`, `conditional`, `rejected`, `reversed`,
  `ruler-qualified`, `evaluator-repair`, `scope-decision`, or `unexecuted`;
- interpretation boundary;
- smallest lesson that changes the next experiment; and
- links to superseded or reversing experiments.

Plans and compliant artifacts are never reported as results.

## 15. Repository shape

```text
TARGET.md
RED_LINES.md
RESEARCH_PROGRAM.md
research/
  components/
    agents/
    skills/
  instrumentation/
  packages/
  contracts/
  worlds/
    micro/
    software/
    representation-pressure/
    evaluator-divergence/
    saturation/
    restraint/
    ecological/
  evaluators/
  anchors/
  experiments/
  evidence/
  reports/
  bin/
```

Large raw evidence may live outside Git, but manifests, content hashes,
schemas, small representative fixtures, experiment records, and frozen
contracts remain versioned.

## 16. Completion claim

The program may claim a **verified adaptive-loop package for scope S** only
when:

1. it beats the no-loop, current-loop, and neutral-length baselines on held-out
   prediction loss and transfer;
2. underlying task fitness is non-inferior overall and on critical slices;
3. its apparent gain survives an adversarial evaluator epoch;
4. its gap between process compliance and outcome improvement is acceptably
   small;
5. its skill triggers meet the frozen routing gates;
6. it prescribes no durable representation and its measured gain does not
   depend on forced receipt instrumentation;
7. minimization has found no removable component under the declared smallest
   effect and uncertainty bounds;
8. the result replicates across the declared scope; and
9. the exact frozen package passes sealed confirmation.

The package is not certified because it runs the loop. It is certified because,
under representative pressure, agents using it make better held-out predictions,
carry evidence into later behavior, and improve or preserve the work that the
loop exists to serve.

## 17. Design precedents

This program borrows two structures while retaining its own normative target:

- The local Prismwing/MiMo research program demonstrates frozen targets,
  red lines, cheap falsification gates, immutable discovery/validation/BLACK
  allocations, append-only negative results, full-path promotion, and explicit
  redirection after a mechanism family is exhausted.
- *The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators*
  motivates frozen evaluator epochs, evaluator-independent anchors, controlled
  evaluator replacement, and erasure of scores that depended on a displaced
  evaluator. Its own stated limitation—that evaluator progress remains bounded
  by anchor quality—is adopted here as a primary threat rather than treated as
  resolved.
