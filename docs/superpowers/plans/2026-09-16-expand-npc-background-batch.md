---
status: approved
issue: 177
created: 2026-09-16
---

# Issue #177: Expand and validate the NPC background batch

> **For agentic workers:** Execute this plan phase by phase. Derive narrative and
> qualification declarations from one structured evidence set, preserve all 16
> pre-existing draft pairs byte-for-byte, and never add character-specific logic
> to the production validator.

## Goal

Prove that the restored NPC background pipeline can produce genuinely new
material by adding four validated patients: two deliberately contrasting GAD
instances, one PDD instance, and one BED instance. Expand the production
baseline from 16 materials / 13 patients / 7 successful replays to
20 materials / 17 patients / 11 successful replays.

## Architecture context

The structured `.gen.json` file is the factual source for each patient. Its
paired narrative view renders the same facts for human readers. The manifest
registers production status, while the ecosystem index and diversity ledger
are reconciled human-readable projections.

Disease qualification remains mechanical and narrow: the existing adapter
passes structured events, memories, and declaration atoms to the existing
eligibility rules. Literary quality and same-disease differentiation remain
reviewable production evidence in the batch quota, not keyword heuristics in
the validator.

## Locked decisions

- The batch consists of:
  - `马会宁` — GAD, 1987, Lanzhou railway freight dispatcher; high-functioning
    concealment, voluntary help-seeking, old pocket radio.
  - `郭月芹` — GAD, 1963, rural Lüliang photo-studio darkroom worker; marked
    functional impairment, family-facilitated admission, biscuit tin of film
    negatives.
  - `罗惠琴` — PDD, 1971, Chongqing Wanzhou bus conductor turned transit-card
    clerk; chronic low mood without a clear episodic boundary, old ticket roll.
  - `方海潮` — BED, 1986, Ningbo wedding MC; bright public persona, concealed
    recurrent binge eating without regular compensation, red-taped microphone.
- Draft from structured qualification and diversity evidence first, then write
  the narrative view from the same facts.
- The two GAD instances must differ on at least two of the six diversity axes
  and at least three free background dimensions. Their pressure source, course
  structure, admission mode, and core-object combination may not match.
- Similarity review lives in an explicit GAD contrast matrix. The validator
  continues to enforce structure, registration, eligibility replay, and ledger
  consistency only.
- All four new entries are `validated` patient-pool members. Existing disease
  rules, thresholds, adapter behavior, and the original 16 draft pairs remain
  unchanged.

## Phase 1: Establish the P2 batch contract

- [ ] Add `design/spec/material/批次配额表-P2-生产验收.md`.
- [ ] Record each patient's disease target, identity, six-axis allocation,
      pressure source, course shape, admission mode, core object, and intended
      ecosystem relationship.
- [ ] Add the GAD contrast matrix and demonstrate at least two six-axis and
      three free-dimension differences.
- [ ] Distinguish diagnostic invariants from person-level design choices and
      state that semantic differentiation is human-review evidence.

## Phase 2: Add four structured factual sources

- [ ] Add `马会宁.gen.json`, `郭月芹.gen.json`, `罗惠琴.gen.json`, and
      `方海潮.gen.json` under `design/spec/material/drafts/`.
- [ ] Use only event types accepted by the eligibility layer.
- [ ] Give each draft the exact `资格声明（#87 规范化声明）` block and only
      declarations supported by its facts.
- [ ] Make the two GAD drafts replay through `GAD_WORRY_PATTERN_HISTORY=1` and
      `慢性冲突/高压`, while keeping their person-level designs distinct.
- [ ] Make PDD replay through `PDD_PERSISTENT_DEPRESSION_PATTERN=1` and
      `丧失/哀悼`, with mania, hypomania, and cyclic-history exclusions false.
- [ ] Make BED replay through `BINGE_HISTORY=1` and
      `BED_DISTRESS_PATTERN=1`, with an allowed recall event and explicit
      absence of regular compensation in the supporting facts.

## Phase 3: Add four narrative views

- [ ] Add one `<name>-叙事视图.md` for every new structured draft.
- [ ] Keep biographies, course, events, symptoms, admission path, and core
      object consistent with the paired JSON.
- [ ] Satisfy B1-B5 for every patient: at least four dialogue samples, six daily
      behavior fragments, an observable symptom table, a counter-intuitive
      point, and five sensory details.
- [ ] Give every patient at least two explicit difference directions and a
      relationship or contrast within the existing ward ecology.
- [ ] Avoid the shared “suffering → collapse → admission” skeleton, especially
      between the two GAD narratives.

## Phase 4: Register and reconcile the batch

- [ ] Add all four entries to
      `design/spec/material/npc-materials-manifest.json` as `validated` and
      `patient_pool: true` with targets `GAD`, `GAD`, `PDD`, and `BED`.
- [ ] Change expected counts to 20 materials and 17 patients.
- [ ] Update the marked patient region, tables, counts, used/unused disease
      summaries, and ecosystem descriptions in `患者生态索引.md`.
- [ ] Apply the matching patient region and six-axis/demographic allocations in
      `多样性记账表.md`.
- [ ] Keep the manifest and both human-readable ledgers set-identical.

## Phase 5: Expand regression coverage

- [ ] Update `code/tools/test_validate_npc_materials.py` baseline expectations
      to 20 materials, 17 patients, and 11 successful replays.
- [ ] Add all four names to the expected replay set.
- [ ] Add a generic expansion fixture only if the existing real-baseline and
      mutation fixtures do not demonstrate safe expansion.
- [ ] Do not add name-specific behavior to `validate_npc_materials.py`; change
      production code only if a general pipeline defect is exposed.

## Phase 6: Verify and hand off

- [ ] Run `python3 code/tools/validate_eligibility.py --self-test`.
- [ ] Run `python3 code/tools/validate_npc_materials.py`.
- [ ] Run `python3 code/tools/test_validate_npc_materials.py`.
- [ ] Run `python3 code/tools/run_all_checks.py`.
- [ ] Run `python3 code/tools/check_clean_checkout.py`.
- [ ] Run `git diff --check`.
- [ ] Compare the 16 original draft pairs against `origin/main` and require a
      zero diff.
- [ ] Confirm the final diff is limited to this plan, the P2 quota, eight new
      draft files, manifest, two ledgers, and necessary tests.
- [ ] Push the completed branch and turn the plan PR into the implementation PR
      closing #177.

## Expected changed files

- `docs/superpowers/plans/2026-09-16-expand-npc-background-batch.md` (new)
- `design/spec/material/批次配额表-P2-生产验收.md` (new)
- Four new `design/spec/material/drafts/*.gen.json` files
- Four new `design/spec/material/drafts/*-叙事视图.md` files
- `design/spec/material/npc-materials-manifest.json`
- `design/spec/material/患者生态索引.md`
- `design/spec/material/多样性记账表.md`
- `code/tools/test_validate_npc_materials.py`

`code/tools/validate_npc_materials.py` is intentionally outside the expected
diff unless execution reveals a general, reproducible production-chain defect.

## Risks and exclusions

- Disease declarations can technically replay while their prose lacks support;
  cross-view evidence review prevents this false success.
- Same-disease differentiation cannot be reduced to exact keyword matching;
  the quota contrast matrix is the auditable gate.
- No fifth patient, disease-rule change, gameplay/runtime integration,
  Blender/Unity work, or automated semantic-similarity model belongs here.
- Existing unrelated worktrees and user changes must not be modified.
