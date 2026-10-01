"""检查声明的跨镜状态、事件与声音条件；不做媒体观感或物理真实性认证。"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import sys
from typing import Any


@dataclass
class Issue:
    severity: str
    unit: str
    code: str
    detail: str


def mapping(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label}必须是对象")
    return value


def sequence(value: Any, label: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{label}必须是数组")
    return value


def state_map(value: Any, label: str) -> dict[str, dict]:
    result = mapping(value, label)
    for entity, fields in result.items():
        if not isinstance(entity, str) or not entity:
            raise ValueError(f"{label}实体ID无效")
        mapping(fields, f"{label}.{entity}")
        for key, item in fields.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"{label}状态字段无效")
            if not isinstance(item, (str, int, float, bool, type(None))):
                raise ValueError(f"{label}.{entity}.{key}必须是标量或null")
            if isinstance(item, float) and not math.isfinite(item):
                raise ValueError(f"{label}.{entity}.{key}非有限数值")
    return result


def validate_plan(plan: dict, phase: str = "planning", base: Path | None = None) -> dict:
    entities = mapping(plan.get("entities"), "entities")
    state = deepcopy(state_map(plan.get("initial_state", {}), "initial_state"))
    units = sequence(plan.get("units"), "units")
    if not entities or not units:
        raise ValueError("entities和units不能为空")
    tolerances = mapping(plan.get("tolerances", {}), "tolerances")
    for key, value in tolerances.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"容差{key}必须是有限非负数")
    issues: list[Issue] = []
    unit_ids: set[str] = set()
    observed_files: set[Path] = set()
    repetition = 0

    def add(unit: str, code: str, detail: str, severity: str = "error") -> None:
        issues.append(Issue(severity, unit, code, detail))

    def matches(entity: str, key: str, left: Any, right: Any) -> bool:
        # bool与int不得因Python相等规则而混作同一机械状态。
        numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (left, right))
        if numeric:
            return abs(left - right) <= tolerances.get(f"{entity}.{key}", 0)
        return type(left) is type(right) and left == right

    def known_fields(declared: dict, unit: str) -> None:
        for entity, fields in declared.items():
            if entity not in entities or entity not in state:
                add(unit, "unknown_entity", f"未注册状态实体{entity}")
            for key, value in fields.items():
                if entity in state and key not in state[entity]:
                    add(unit, "unknown_field", f"未注册状态字段{entity}.{key}")
                if value is None:
                    add(unit, "unknown_state", f"{entity}.{key}尚未验证", "error" if phase == "execution" else "warning")

    def compare(declared: dict, current: dict, unit: str, code: str) -> None:
        for entity, fields in declared.items():
            for key, wanted in fields.items():
                if entity not in current or key not in current[entity]:
                    add(unit, code, f"{entity}.{key}没有已知前态")
                elif not matches(entity, key, wanted, current[entity][key]):
                    add(unit, code, f"{entity}.{key}: 声明{wanted!r}，已知{current[entity][key]!r}")

    known_fields(state, "initial")
    for position, raw in enumerate(units):
        unit = mapping(raw, f"units[{position}]")
        unit_id = unit.get("id")
        if not isinstance(unit_id, str) or not unit_id:
            raise ValueError("镜头ID须为非空字符串")
        if unit_id in unit_ids:
            add(unit_id, "duplicate_unit", "镜头ID重复")
        unit_ids.add(unit_id)
        duration = unit.get("duration_s")
        if duration is not None and (isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0):
            raise ValueError(f"{unit_id}.duration_s必须是有限正数")
        start = state_map(unit.get("start_state", {}), f"{unit_id}.start_state")
        end = state_map(unit.get("end_state", {}), f"{unit_id}.end_state")
        known_fields(start, unit_id)
        known_fields(end, unit_id)
        compare(start, state, unit_id, "state_reset")
        current = deepcopy(state)
        snapshots: dict[str, dict] = {}
        event_ids: set[str] = set()
        touched: set[str] = set(start) | set(end)
        for raw_event in sequence(unit.get("events", []), f"{unit_id}.events"):
            event = mapping(raw_event, "event")
            event_id = event.get("id")
            if not isinstance(event_id, str) or not event_id or event_id in event_ids:
                add(unit_id, "event_id", "事件ID缺失或重复")
                continue
            event_ids.add(event_id)
            if not isinstance(event.get("cause"), str) or not event["cause"].strip():
                add(unit_id, "missing_cause", f"事件{event_id}没有触发/动力原因")
            required = state_map(event.get("requires", {}), "event.requires")
            effects = state_map(event.get("effects", {}), "event.effects")
            known_fields(required, unit_id)
            known_fields(effects, unit_id)
            compare(required, current, unit_id, "event_precondition")
            touched.update(required)
            touched.update(effects)
            for entity, fields in effects.items():
                # 错误实体不能偷偷进入全局状态账本。
                if entity in state:
                    current[entity].update({k: v for k, v in fields.items() if k in state[entity]})
            snapshots[event_id] = deepcopy(current)
        for raw_sound in sequence(unit.get("sounds", []), f"{unit_id}.sounds"):
            sound = mapping(raw_sound, "sound")
            domain = sound.get("domain")
            if domain not in {"diegetic", "offscreen_diegetic", "subjective", "score"}:
                add(unit_id, "sound_domain", "声音类别未声明或无效")
                continue
            if not isinstance(sound.get("purpose"), str) or not sound["purpose"].strip():
                add(unit_id, "sound_purpose", "声音缺少用途/事件说明")
            window = sound.get("window_s")
            if window is not None:
                values = sequence(window, "sound.window_s")
                valid = len(values) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in values)
                if not valid or values[0] < 0 or values[1] <= values[0] or duration is None or values[1] > duration:
                    add(unit_id, "sound_window", "声音时间窗须满足0≤开始<结束≤本镜duration_s")
            elif duration is not None:
                add(unit_id, "sound_window", "已声明镜长的声音事件缺少window_s")
            if domain in {"diegetic", "offscreen_diegetic"}:
                source = sound.get("source")
                if source not in entities:
                    add(unit_id, "sound_source", "现场声没有已注册来源")
                at_event = sound.get("at_event")
                continuous = sound.get("continuous") is True
                if not continuous and at_event not in snapshots:
                    add(unit_id, "sound_trigger", "非连续现场声没有本镜触发事件")
                if not isinstance(sound.get("stop_condition"), str) or not sound["stop_condition"].strip():
                    add(unit_id, "sound_stop", "现场声没有停止条件或延续到何处的说明")
                stop_event = sound.get("ends_at_event")
                if stop_event is not None:
                    ordered = list(snapshots)
                    if stop_event not in snapshots or (at_event in snapshots and ordered.index(stop_event) < ordered.index(at_event)):
                        add(unit_id, "sound_stop_event", "声音停止事件不存在或早于触发事件")
                requires = state_map(sound.get("requires", {}), "sound.requires")
                if not requires:
                    add(unit_id, "sound_conditions", "现场声缺少连接/能量/环境等状态条件")
                known_fields(requires, unit_id)
                touched.update(requires)
                compare(requires, snapshots.get(at_event, state), unit_id, "sound_precondition")
            elif domain == "subjective" and sound.get("listener") not in entities:
                add(unit_id, "subjective_listener", "主观声须明确听者")
            exception = sound.get("exception_rule")
            if exception is not None:
                setup = sound.get("setup_unit")
                if not isinstance(exception, str) or not exception.strip() or setup not in unit_ids:
                    add(unit_id, "exception_setup", "异常规则缺少本镜或先前镜头的铺垫记录")
                if not sound.get("reaction") or not sound.get("payoff"):
                    add(unit_id, "exception_payoff", "异常缺少角色反应或兑现/有意悬念")
        for entity in touched:
            if entity in state:
                keys = set(state[entity])
                if entity not in start or not keys.issubset(start[entity]):
                    add(unit_id, "incomplete_start", f"{entity}缺少完整当前起态")
                if entity not in end or not keys.issubset(end[entity]):
                    add(unit_id, "incomplete_end", f"{entity}缺少完整终态")
        compare(end, current, unit_id, "unexplained_transition")
        # 在容差内采用声明的已复核终态，而非继续沿用计划效果值。
        for entity, fields in end.items():
            for key, value in fields.items():
                if entity in current and key in current[entity] and matches(entity, key, value, current[entity][key]):
                    current[entity][key] = value
        if phase == "execution":
            selected = mapping(unit.get("selected", {}), "selected")
            if selected.get("state_reviewed") is not True:
                add(unit_id, "unreviewed_output", "实际终态未声明复核")
            for field in ("media_path", "end_evidence"):
                value = selected.get(field)
                if not isinstance(value, str) or not value:
                    add(unit_id, "missing_evidence", f"缺少{field}")
                    continue
                file = Path(value)
                file = (base / file if base is not None and not file.is_absolute() else file).resolve()
                if not file.is_file():
                    add(unit_id, "missing_evidence", f"文件不存在: {file}")
                if field == "media_path":
                    if file in observed_files:
                        add(unit_id, "duplicate_selection", "重复入片路径")
                    observed_files.add(file)
        cast = sequence(unit.get("cast", []), "cast")
        if any(character not in entities for character in cast):
            add(unit_id, "unknown_cast", "角色未注册")
        static_solo = len(cast) == 1 and unit.get("composition") == "close" and unit.get("camera") == "locked" and bool(unit.get("dialogue"))
        repetition = repetition + 1 if static_solo else 0
        if repetition == 4:
            add(unit_id, "repeated_solo_close", "连续四个固定单人对白近景，检查关系/节奏目的；不是自动无聊判定", "warning")
        state = current
    return {"phase": phase, "units_checked": len(units), "issues": [asdict(i) for i in issues],
            "errors": sum(i.severity == "error" for i in issues),
            "warnings": sum(i.severity == "warning" for i in issues),
            "limitations": "Validates declared states, causes and files only; no physics, voice, visual or artistic acceptance."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--phase", choices=("planning", "execution"), default="planning")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        plan = mapping(json.loads(args.plan.read_text(encoding="utf-8-sig")), "plan")
        result = validate_plan(plan, args.phase, args.plan.resolve().parent)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.report is not None:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            # 使用独立报告，不默默覆盖上一轮检查证据。
            with args.report.open("x", encoding="utf-8") as file:
                file.write(output + "\n")
        print(output)
        return 1 if result["errors"] else 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"检查失败: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
