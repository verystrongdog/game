#!/usr/bin/env python3
"""审计 NPC 背景素材生产链。

公开接口只有 ``audit_repository(root) -> AuditReport``。模块内部负责 manifest、
素材配对、格式适配、资格回放与人类可读台账核对；不从叙事文字推断声明。

来源：docs/superpowers/plans/2026-09-16-restore-npc-background-pipeline.md
      （Issue #174 锁定方案）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys
from typing import Any

from validate_eligibility import (
    KNOWN_DECLARATION_ATOMS,
    VERIFIED,
    EligibilityInputError,
    eligibility_for,
)


MANIFEST_REL = Path("design/spec/material/npc-materials-manifest.json")
DEFAULT_DRAFT_ROOT = Path("design/spec/material/drafts")
PATIENT_LEDGER_RELS = (
    Path("design/spec/material/患者生态索引.md"),
    Path("design/spec/material/多样性记账表.md"),
)
NON_PATIENT_LEDGER_REL = Path("design/spec/material/患者生态索引.md")

KNOWN_STATUSES = {
    "validated",
    "needs-migration",
    "needs-review",
    "demonstration",
    "non-patient",
    "excluded",
}
PATIENT_STATUSES = {"validated", "needs-migration"}
KNOWN_ATOMS = KNOWN_DECLARATION_ATOMS
DECLARATION_BLOCK = "资格声明（#87 规范化声明）"
DOCUMENTARY_FIELDS = {"判定", "note"}
ANNOTATION_FIELDS = {"PTSD"}


@dataclass(frozen=True)
class Finding:
    """稳定 code 用于 CI 与 fixture；message/subject 只用于展示。"""

    code: str
    subject: str
    message: str


@dataclass
class AuditReport:
    findings: list[Finding] = field(default_factory=list)
    material_count: int = 0
    patient_count: int = 0
    replayed_names: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.findings

    @property
    def replay_count(self) -> int:
        return len(self.replayed_names)

    def add(self, code: str, subject: str, message: str) -> None:
        self.findings.append(Finding(code, subject, message))

    def codes(self) -> set[str]:
        return {finding.code for finding in self.findings}


class AdapterError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _safe_repo_path(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative:
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _scan_draft_pairs(draft_root: Path, report: AuditReport) -> tuple[set[str], set[str]]:
    if not draft_root.is_dir():
        report.add("DRAFT_ROOT_MISSING", str(draft_root), "素材目录不存在")
        return set(), set()

    json_names = {path.name[: -len(".gen.json")] for path in draft_root.glob("*.gen.json")}
    narrative_names = {
        path.name[: -len("-叙事视图.md")] for path in draft_root.glob("*-叙事视图.md")
    }
    for name in sorted(json_names - narrative_names):
        report.add("DRAFT_PAIR_MISSING_NARRATIVE", name, "结构化草稿缺少叙事视图")
    for name in sorted(narrative_names - json_names):
        report.add("DRAFT_PAIR_MISSING_JSON", name, "叙事视图缺少结构化草稿")
    return json_names, narrative_names


def _merge_atom(declarations: dict[str, Any], atom: str, value: Any) -> None:
    if atom not in KNOWN_ATOMS:
        raise AdapterError("ADAPTER_UNKNOWN_DECLARATION_ATOM", f"未知声明原子 {atom}")
    if value not in (0, 1, "MISSING") or isinstance(value, bool):
        raise AdapterError(
            "ADAPTER_INVALID_DECLARATION_VALUE",
            f"声明 {atom} 只能是 0、1 或 MISSING",
        )
    if atom in declarations and declarations[atom] != value:
        raise AdapterError("ADAPTER_CONFLICTING_DECLARATION", f"声明 {atom} 出现冲突值")
    declarations[atom] = value


def _adapt_draft(draft: Any) -> dict[str, Any]:
    """把当前素材格式适配为资格判定器的规范输入。"""
    if not isinstance(draft, dict):
        raise AdapterError("ADAPTER_INVALID_DRAFT", "结构化草稿顶层必须是 object")
    memories = draft.get("trauma_memories")
    if not isinstance(memories, list):
        raise AdapterError("ADAPTER_INVALID_MEMORIES", "trauma_memories 必须是 array")

    declaration_block = draft.get(DECLARATION_BLOCK)
    if not isinstance(declaration_block, dict):
        raise AdapterError(
            "ADAPTER_DECLARATION_BLOCK_MISSING",
            f"缺少精确结构化声明块 {DECLARATION_BLOCK}",
        )

    declarations: dict[str, Any] = {}
    for key, value in declaration_block.items():
        if key in DOCUMENTARY_FIELDS:
            continue
        if key in ANNOTATION_FIELDS:
            if not isinstance(value, dict):
                raise AdapterError(
                    "ADAPTER_INVALID_ANNOTATION",
                    f"说明字段 {key} 必须是 object",
                )
            continue
        if key == "交叉声明":
            if not isinstance(value, dict):
                raise AdapterError("ADAPTER_INVALID_CROSS_DECLARATIONS", "交叉声明必须是 object")
            for cross_key, cross_value in value.items():
                if cross_key in DOCUMENTARY_FIELDS:
                    continue
                _merge_atom(declarations, cross_key, cross_value)
            continue
        _merge_atom(declarations, key, value)

    events: list[Any] = []
    for index, memory in enumerate(memories):
        if not isinstance(memory, dict):
            raise AdapterError("ADAPTER_INVALID_MEMORIES", f"trauma_memories[{index}] 必须是 object")
        events.append(memory.get("event_type"))
    return {"events": events, "memories": memories, "declarations": declarations}


def _marked_names(
    path: Path,
    start_marker: str,
    end_marker: str,
    report: AuditReport,
    marker_kind: str,
) -> set[str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.add("LEDGER_READ_ERROR", str(path), str(exc))
        return None
    start_count, end_count = text.count(start_marker), text.count(end_marker)
    if start_count != 1 or end_count != 1:
        report.add(
            "LEDGER_MARKER_MISSING",
            str(path),
            f"{marker_kind} 区域必须各有一个起止 marker",
        )
        return None
    before, remainder = text.split(start_marker, 1)
    del before
    region, after = remainder.split(end_marker, 1)
    del after
    names: set[str] = set()
    invalid_lines: list[str] = []
    for raw_line in region.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("<!--"):
            continue
        match = re.fullmatch(r"[-*]\s+([^\s`|，,]+)", line)
        if not match:
            invalid_lines.append(line)
            continue
        name = match.group(1)
        if name in names:
            report.add("LEDGER_DUPLICATE_NAME", f"{path}:{name}", f"{marker_kind} 重复姓名")
        names.add(name)
    if invalid_lines:
        report.add(
            "LEDGER_REGION_INVALID",
            str(path),
            f"{marker_kind} 仅允许 '- 姓名' 行: {invalid_lines[0]}",
        )
    return names


def _audit_ledgers(root: Path, patient_names: set[str], other_names: set[str], report: AuditReport) -> None:
    patient_start = "<!-- npc-patient-pool:start -->"
    patient_end = "<!-- npc-patient-pool:end -->"
    for relative in PATIENT_LEDGER_RELS:
        actual = _marked_names(root / relative, patient_start, patient_end, report, "患者池")
        if actual is not None and actual != patient_names:
            report.add(
                "PATIENT_LEDGER_MISMATCH",
                str(relative),
                f"患者池差异：缺少 {sorted(patient_names - actual)}；多出 {sorted(actual - patient_names)}",
            )

    other_start = "<!-- npc-non-patient-materials:start -->"
    other_end = "<!-- npc-non-patient-materials:end -->"
    actual_other = _marked_names(
        root / NON_PATIENT_LEDGER_REL,
        other_start,
        other_end,
        report,
        "非患者池素材",
    )
    if actual_other is not None and actual_other != other_names:
        report.add(
            "NON_PATIENT_LEDGER_MISMATCH",
            str(NON_PATIENT_LEDGER_REL),
            f"非患者池素材差异：缺少 {sorted(other_names - actual_other)}；多出 {sorted(actual_other - other_names)}",
        )


def audit_repository(root: str | Path) -> AuditReport:
    root = Path(root).resolve()
    report = AuditReport()
    manifest_path = root / MANIFEST_REL
    try:
        manifest = _load_json(manifest_path)
    except FileNotFoundError:
        report.add("MANIFEST_MISSING", str(MANIFEST_REL), "NPC 素材 manifest 不存在")
        _scan_draft_pairs(root / DEFAULT_DRAFT_ROOT, report)
        return report
    except (OSError, json.JSONDecodeError) as exc:
        report.add("MANIFEST_INVALID_JSON", str(MANIFEST_REL), str(exc))
        _scan_draft_pairs(root / DEFAULT_DRAFT_ROOT, report)
        return report

    if not isinstance(manifest, dict):
        report.add("MANIFEST_INVALID_SHAPE", str(MANIFEST_REL), "manifest 顶层必须是 object")
        _scan_draft_pairs(root / DEFAULT_DRAFT_ROOT, report)
        return report
    if manifest.get("schema_version") != 1:
        report.add("MANIFEST_SCHEMA_VERSION", str(MANIFEST_REL), "schema_version 必须为 1")

    draft_root_relative = manifest.get("draft_root")
    draft_root = _safe_repo_path(root, draft_root_relative)
    if draft_root is None:
        report.add("MANIFEST_INVALID_DRAFT_ROOT", str(MANIFEST_REL), "draft_root 必须是仓库内相对路径")
        draft_root = root / DEFAULT_DRAFT_ROOT
    scanned_json, scanned_narratives = _scan_draft_pairs(draft_root, report)

    materials = manifest.get("materials")
    if not isinstance(materials, list):
        report.add("MANIFEST_INVALID_MATERIALS", str(MANIFEST_REL), "materials 必须是 array")
        return report
    report.material_count = len(materials)
    expected_material_count = manifest.get("expected_material_count")
    if not isinstance(expected_material_count, int) or isinstance(expected_material_count, bool):
        report.add("MANIFEST_INVALID_EXPECTED_COUNT", str(MANIFEST_REL), "expected_material_count 必须是 integer")
    elif len(materials) != expected_material_count:
        report.add(
            "MATERIAL_COUNT_MISMATCH",
            str(MANIFEST_REL),
            f"manifest 有 {len(materials)} 项，预期 {expected_material_count}",
        )

    seen_names: set[str] = set()
    seen_json_paths: set[str] = set()
    seen_narrative_paths: set[str] = set()
    manifest_names: set[str] = set()
    patient_names: set[str] = set()
    other_names: set[str] = set()

    for index, entry in enumerate(materials):
        subject = f"materials[{index}]"
        if not isinstance(entry, dict):
            report.add("MANIFEST_INVALID_ENTRY", subject, "素材条目必须是 object")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            report.add("MANIFEST_INVALID_NAME", subject, "name 必须是非空 string")
            continue
        subject = name
        manifest_names.add(name)
        if name in seen_names:
            report.add("MANIFEST_DUPLICATE_NAME", name, "manifest 姓名重复")
        seen_names.add(name)

        json_path_value = entry.get("json_path")
        narrative_path_value = entry.get("narrative_path")
        for value, seen, duplicate_code, field_name in (
            (json_path_value, seen_json_paths, "MANIFEST_DUPLICATE_JSON_PATH", "json_path"),
            (narrative_path_value, seen_narrative_paths, "MANIFEST_DUPLICATE_NARRATIVE_PATH", "narrative_path"),
        ):
            if not isinstance(value, str) or not value:
                report.add("MANIFEST_INVALID_PATH", name, f"{field_name} 必须是非空相对路径")
            elif value in seen:
                report.add(duplicate_code, value, f"{field_name} 重复")
            else:
                seen.add(value)

        json_path = _safe_repo_path(root, json_path_value)
        narrative_path = _safe_repo_path(root, narrative_path_value)
        expected_json_path = (draft_root / f"{name}.gen.json").resolve()
        expected_narrative_path = (draft_root / f"{name}-叙事视图.md").resolve()
        if json_path is None:
            report.add("MANIFEST_INVALID_PATH", name, "json_path 必须位于仓库内")
        elif not json_path.is_file():
            report.add("MANIFEST_JSON_MISSING", name, f"文件不存在: {json_path_value}")
        elif json_path != expected_json_path:
            report.add("MANIFEST_PATH_NAME_MISMATCH", name, "json_path 与姓名/素材目录不匹配")
        if narrative_path is None:
            report.add("MANIFEST_INVALID_PATH", name, "narrative_path 必须位于仓库内")
        elif not narrative_path.is_file():
            report.add("MANIFEST_NARRATIVE_MISSING", name, f"文件不存在: {narrative_path_value}")
        elif narrative_path != expected_narrative_path:
            report.add("MANIFEST_PATH_NAME_MISMATCH", name, "narrative_path 与姓名/素材目录不匹配")

        status = entry.get("status")
        patient_pool = entry.get("patient_pool")
        target = entry.get("target_disease")
        if status not in KNOWN_STATUSES:
            report.add("MANIFEST_INVALID_STATUS", name, f"未知状态: {status!r}")
        if not isinstance(patient_pool, bool):
            report.add("MANIFEST_INVALID_PATIENT_POOL", name, "patient_pool 必须是 boolean")
        elif patient_pool:
            patient_names.add(name)
            if status not in PATIENT_STATUSES:
                report.add("STATUS_PATIENT_POOL_CONFLICT", name, f"状态 {status!r} 不得进入患者池")
        else:
            other_names.add(name)
            if status in PATIENT_STATUSES:
                report.add("STATUS_PATIENT_POOL_CONFLICT", name, f"状态 {status!r} 必须进入患者池")
        if status in PATIENT_STATUSES and target not in VERIFIED:
            report.add("MANIFEST_INVALID_TARGET_DISEASE", name, f"患者素材目标病种无效: {target!r}")
        if status not in PATIENT_STATUSES and target is not None:
            report.add("MANIFEST_UNEXPECTED_TARGET_DISEASE", name, "非患者池素材不得声明回放目标")

        if json_path is not None and json_path.is_file():
            try:
                draft = _load_json(json_path)
            except (OSError, json.JSONDecodeError) as exc:
                report.add("DRAFT_INVALID_JSON", name, str(exc))
                continue
            identity_name = draft.get("identity", {}).get("name") if isinstance(draft, dict) else None
            if identity_name != name:
                report.add("DRAFT_IDENTITY_MISMATCH", name, f"identity.name={identity_name!r}")
            if status == "validated":
                try:
                    canonical = _adapt_draft(draft)
                    results = eligibility_for(canonical)
                except AdapterError as exc:
                    report.add(exc.code, name, str(exc))
                except EligibilityInputError as exc:
                    report.add("ELIGIBILITY_INPUT_INVALID", name, str(exc))
                else:
                    actual = results.get(target, ("UNKNOWN", "目标病种无结果"))
                    if actual[0] != "ELIGIBLE":
                        report.add(
                            "TARGET_REPLAY_NOT_ELIGIBLE",
                            name,
                            f"{target}: {actual[0]} ({actual[1]})",
                        )
                    else:
                        report.replayed_names.append(name)

    report.patient_count = len(patient_names)
    expected_patient_count = manifest.get("expected_patient_count")
    if not isinstance(expected_patient_count, int) or isinstance(expected_patient_count, bool):
        report.add("MANIFEST_INVALID_EXPECTED_COUNT", str(MANIFEST_REL), "expected_patient_count 必须是 integer")
    elif len(patient_names) != expected_patient_count:
        report.add(
            "PATIENT_COUNT_MISMATCH",
            str(MANIFEST_REL),
            f"患者池有 {len(patient_names)} 人，预期 {expected_patient_count}",
        )
    for name in sorted(scanned_json - manifest_names):
        report.add("DRAFT_UNREGISTERED_JSON", name, "结构化草稿未登记到 manifest")
    for name in sorted(scanned_narratives - manifest_names):
        report.add("DRAFT_UNREGISTERED_NARRATIVE", name, "叙事视图未登记到 manifest")
    for name in sorted(manifest_names - scanned_json):
        report.add("MANIFEST_ENTRY_NOT_SCANNED_JSON", name, "manifest 条目不在素材目录 JSON 扫描结果中")
    for name in sorted(manifest_names - scanned_narratives):
        report.add("MANIFEST_ENTRY_NOT_SCANNED_NARRATIVE", name, "manifest 条目不在素材目录叙事视图扫描结果中")

    _audit_ledgers(root, patient_names, other_names, report)
    return report


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) > 1:
        print("用法: validate_npc_materials.py [repository-root]", file=sys.stderr)
        return 2
    root = Path(argv[0]) if argv else Path(__file__).resolve().parents[2]
    report = audit_repository(root)
    print(
        f"NPC 素材审计: materials={report.material_count}, "
        f"patients={report.patient_count}, replays={report.replay_count}, "
        f"findings={len(report.findings)}"
    )
    for finding in report.findings:
        print(f"  [{finding.code}] {finding.subject}: {finding.message}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
