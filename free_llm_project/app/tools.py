"""Custom tools for the agent (calculator, clock, unit conversion).

Every tool execution is audited into the app database. Tools are plain
functions decorated with @tool so Upsonic auto-generates their schemas.
"""

from __future__ import annotations

import datetime as _dt
import operator as _op

from upsonic.tools.config import tool

from app.database import db

_ALLOWED_OPS = {
    _op.add, _op.sub, _op.mul, _op.truediv, _op.pow, _op.mod,
    _op.floordiv, _op.neg,
}


@tool
def calculator(expression: str) -> float:
    """Evaluate a basic arithmetic expression safely, e.g. '(2+3)*4/5'."""
    try:
        code = compile(expression, "<calc>", "eval")
        for const in code.co_consts:
            if isinstance(const, type(_op.add)) and const not in _ALLOWED_OPS:
                raise ValueError("disallowed operator")
        names = {n.__name__: n for n in _ALLOWED_OPS}
        result = eval(code, {"__builtins__": {}}, names)  # noqa: S307 — sandboxed
        db.log_event("tool", model="calculator", detail={"expression": expression, "result": str(result)})
        return float(result)
    except Exception as exc:  # noqa: BLE001
        db.log_event("tool", model="calculator", success=False,
                     detail={"expression": expression, "error": str(exc)})
        raise


@tool
def current_time() -> str:
    """Return the current UTC date & time as an ISO-8601 string."""
    now = _dt.datetime.now(_dt.timezone.utc).isoformat()
    db.log_event("tool", model="current_time", detail={"time": now})
    return now


@tool
def convert_units(value: float, unit_from: str, unit_to: str) -> str:
    """Convert between common units. Supported pairs: celsius/fahrenheit, km/miles, kg/lb."""
    uf, ut = unit_from.lower().strip(), unit_to.lower().strip()
    table = {
        ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
        ("km", "miles"): lambda v: v * 0.621371,
        ("miles", "km"): lambda v: v / 0.621371,
        ("kg", "lb"): lambda v: v * 2.20462,
        ("lb", "kg"): lambda v: v / 2.20462,
    }
    fn = table.get((uf, ut))
    if fn is None:
        raise ValueError(f"Unsupported conversion {unit_from}->{unit_to}. Try: {sorted(table)}")
    out = f"{value:g} {uf} = {fn(value):.4g} {ut}"
    db.log_event("tool", model="convert_units", detail={"in": f"{value}{uf}", "out": out})
    return out


def get_custom_tools():
    """All custom tools for agent registration."""
    return [calculator, current_time, convert_units]
