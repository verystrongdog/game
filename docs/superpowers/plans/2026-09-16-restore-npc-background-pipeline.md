---
status: ready-for-execution
issue: 174
pr: 175
created: 2026-09-16
---

# Issue #174: Restore the NPC background production pipeline

> **For agentic workers:** Execute this plan phase by phase. Preserve every existing
> NPC draft byte-for-byte, keep disease rules and thresholds unchanged, and stage
> only files owned by #174. The worktree may contain unrelated Blender changes.

## Goal

Reconnect the repository's NPC drafting rules, 16 structured/narrative draft
pairs, disease-eligibility replay, ecosystem ledgers, and CI gates. The result
must make missing inputs and status drift fail explicitly without changing NPC
prose, diagnoses, or gameplay/runtime scope.

## Architecture context

Design documents and material data are the primary artifact. `code/tools/`
validates those artifacts; `code/sim/` contains research simulations and is not
the production pipeline.

The implementation adds one deep audit module with the external interface
`audit_repository(root) -> AuditReport`. Its implementation owns manifest
loading, draft pairing, draft-to-canonical adaptation, eligibility replay, and
ledger reconciliation. The CLI and fixture suite exercise the same interface.

The seam between material format and disease rules is explicit:

1. `validate_npc_materials.py` adapts an NPC `.gen.json` draft to canonical
   `{events, memories, declarations}` input.
2. `validate_eligibility.py` validates and evaluates only that canonical input.
3. Neither module infers declarations from narrative prose.

## Locked decisions

- `npc-materials-manifest.json` is authoritative for production-chain status;
  each `.gen.json` remains authoritative for NPC facts.
- `validated` means the eligibility production chain replayed successfully. It
  does not mean the literary draft received final editorial approval.
- The active patient pool contains 13 entries: seven newly replayable drafts
  and six legacy patients awaiting structured-declaration migration.
- Status allocation:
  - `validated`: 周卫国/PTSD, 杨秀兰/躯体症状, 苏晴/DID, 吴桐/AN,
    唐念安/OCD, 许一鸣/社交焦虑, 贺春兰/BN.
  - `needs-migration`: 顾维扬/MDD, 孙嘉禾/BD-II, 陈国强/SUD,
    林小满/MDD, 高远/BD-I, 王淑芬/环性.
  - `needs-review`: 刘建军. This is deliberately not `excluded`; the existing
    record recommends abandonment or major revision but contains no prior owner
    decision to discard it.
  - `demonstration`: 周桂芳.
  - `non-patient`: 郑晓敏.
- `needs-migration` can remain in the patient pool but cannot claim replay
  success. `needs-review`, `demonstration`, and `non-patient` cannot enter it.
- Production validation and mutation fixtures are separate commands and both
  belong to `docs-integrity`.
- No NPC draft, disease rule, threshold, Unity/Blender asset, C# runtime, or old
  simulation behavior is changed by this issue.

## Phase 1: Add the manifest contract

- [ ] Add `design/spec/material/npc-materials-manifest.json` with a schema
      version, draft root, expected material/patient counts, and 16 entries.
- [ ] For each entry, record its name, JSON path, narrative path, pipeline
      status, patient-pool membership, and target disease where applicable.
- [ ] Require unique names and paths, known status values, existing paired
      files, exactly 16 entries, and exactly 13 patient-pool members.
- [ ] Keep target disease as a replay contract, not a duplicate biography.

## Phase 2: Make eligibility input strict

Modify `code/tools/validate_eligibility.py` without changing its disease tables,
thresholds, or result semantics.

- [ ] Validate the canonical top-level containers `events`, `memories`, and
      `declarations` before evaluation.
- [ ] Reject unknown event types, malformed memory objects, and declaration
      values outside `0`, `1`, and `"MISSING"`.
- [ ] Make a raw `.gen.json` passed to the eligibility CLI fail clearly instead
      of silently evaluating an empty canonical patient.
- [ ] Preserve all 14 existing self-tests and their outcomes.

## Phase 3: Implement the NPC material audit

Add `code/tools/validate_npc_materials.py`.

- [ ] Expose `audit_repository(root) -> AuditReport`; make findings carry stable
      codes so the CLI and tests can identify failure classes.
- [ ] Scan the draft directory independently of the manifest, pair every
      `*.gen.json` with `<name>-叙事视图.md`, and report missing, duplicate, and
      unregistered material.
- [ ] Internally adapt `trauma_memories[].event_type` to `events`, preserve
      `trauma_memories` as `memories`, and extract only the exact
      `资格声明（#87 规范化声明）` block.
- [ ] Flatten known direct declaration atoms and known atoms inside `交叉声明`.
      Ignore explicitly documentary fields such as `判定` and `note`; reject
      conflicting values and unknown scalar atoms rather than guessing.
- [ ] Treat the PTSD explanatory object as annotation; PTSD replay continues to
      rely solely on the existing memory-representation rule.
- [ ] Replay all seven `validated` entries and require the manifest's target
      disease to be `ELIGIBLE`.
- [ ] Enforce the status/patient-pool rules for the other nine entries without
      manufacturing declarations for them.
- [ ] Reconcile the 13-name patient set with stable marked regions in
      `患者生态索引.md` and `多样性记账表.md`.
- [ ] Print an auditable summary and return nonzero when any error exists.

## Phase 4: Test the public interface

Add `code/tools/test_validate_npc_materials.py` using standard-library temporary
directories and the same `audit_repository` interface as production.

- [ ] Assert the real repository baseline: 16 pairs, 13 patient-pool members,
      and seven successful target-disease replays.
- [ ] Add mutation fixtures for a missing JSON or narrative partner.
- [ ] Add fixtures for manifest omission, duplicate name, and duplicate path.
- [ ] Remove or corrupt a validated declaration and assert replay failure.
- [ ] Inject an unknown event type and assert strict-input failure.
- [ ] Relabel a legacy draft as `validated` and assert that missing structured
      inputs cannot false-pass.
- [ ] Remove a patient from either human-readable ledger and assert a set
      mismatch.
- [ ] Assert stable finding codes and nonzero CLI outcomes, not implementation
      internals.

## Phase 5: Repair the documented production chain

- [ ] Update `design/events/NPC人生生成器设计.md` with the manifest → Adapter →
      eligibility replay → ledger/CI flow and repair the stale material path.
- [ ] Fix the three pre-refactor paths in
      `design/rules/skill-tree/素材起草规范.md`; require manifest registration and
      the complete NPC audit after drafting.
- [ ] Update `design/rules/skill-tree/资格声明侧规范.md` to document the Adapter
      seam instead of directing raw `.gen.json` into the eligibility CLI.
- [ ] Repair stale archive/material links in
      `design/rules/skill-tree/创伤记忆转化接口.md` without changing rules or
      thresholds.
- [ ] Mark the accepted six-axis constraints as current in
      `design/spec/material/叙事多样化维度定义.md`, while retaining the dated
      historical analysis and recording 刘建军/周桂芳/郑晓敏 statuses.
- [ ] Make the title, body, rows, and footer of
      `design/spec/material/批次配额表-P1补充.md` consistently describe finalized
      v1.0 and the seven completed drafts.
- [ ] Add stable reconciliation markers and the manifest relationship to
      `design/spec/material/患者生态索引.md` and
      `design/spec/material/多样性记账表.md`; preserve the 13-person set and fix
      the used/unused disease wording drift.
- [ ] Update only the documentation/path text in
      `code/sim/sim_npc_generator_mvp.py` to label it a historical five-disease
      research simulator rather than the production path.

## Phase 6: Register both gates

- [ ] Register `validate_npc_materials.py` and
      `test_validate_npc_materials.py` in `code/tools/run_all_checks.py`.
- [ ] Run both commands explicitly in `.github/workflows/ci.yml` under
      `docs-integrity`.
- [ ] Describe the resulting coverage as 15 production validators plus one
      fixture suite; keep the local registry and CI command list aligned.
- [ ] Synchronize `design/engineering/gates.json` and
      `design/engineering/build-and-test.md` with the commands and pass criteria.

## Phase 7: Verify and hand off

- [ ] Run `python3 code/tools/validate_eligibility.py --self-test`.
- [ ] Run `python3 code/tools/validate_npc_materials.py`.
- [ ] Run `python3 code/tools/test_validate_npc_materials.py`.
- [ ] Run `python3 code/tools/run_all_checks.py`.
- [ ] Run `python3 code/tools/check_clean_checkout.py`.
- [ ] Run `git diff --check`.
- [ ] Confirm `git diff --exit-code -- design/spec/material/drafts` is clean, so
      all 16 JSON and all 16 narrative drafts remain untouched.
- [ ] Treat the mutation fixture suite as the rollback drill, then rerun the
      real repository audit to prove the clean state still passes.
- [ ] Report any unrelated repository-wide `issues-snapshot` failures without
      expanding #174 to repair other issues.

## Expected changed files

- `design/spec/material/npc-materials-manifest.json` (new)
- `code/tools/validate_npc_materials.py` (new)
- `code/tools/test_validate_npc_materials.py` (new)
- `code/tools/validate_eligibility.py`
- `code/tools/run_all_checks.py`
- `code/sim/sim_npc_generator_mvp.py` (documentation/path text only)
- `.github/workflows/ci.yml`
- `design/engineering/gates.json`
- `design/engineering/build-and-test.md`
- `design/events/NPC人生生成器设计.md`
- `design/rules/skill-tree/素材起草规范.md`
- `design/rules/skill-tree/资格声明侧规范.md`
- `design/rules/skill-tree/创伤记忆转化接口.md`
- `design/spec/material/叙事多样化维度定义.md`
- `design/spec/material/批次配额表-P1补充.md`
- `design/spec/material/患者生态索引.md`
- `design/spec/material/多样性记账表.md`

## Risks and exclusions

- Unrelated Blender changes already present in the worktree must never be
  staged, rewritten, or removed.
- Markdown reconciliation intentionally reads only explicitly marked regions;
  arbitrary prose/table formatting must not become an implicit machine source.
- Open issues #168-#171 may independently make the repository-wide
  `issues-snapshot` job red. #174 owns `docs-integrity` and `clean-checkout`, not
  unrelated issue cleanup.
- There is no database, runtime-data, or gameplay migration.
