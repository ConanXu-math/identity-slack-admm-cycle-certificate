"""Export the complete exact period-66 orbit as machine-readable data.

The theorem checkers deliberately keep their stable JSON summaries compact.
This companion exporter records every cyclic phase without asking readers to
parse hundreds of long rational numbers from the manuscript appendix.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import sympy as sp

import strict_cycle_certificate as checker


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE.parent / "certificates" / "orbit_66.json"


def _exact(values: Iterable[sp.Expr]) -> list[str]:
    return [sp.sstr(value) for value in values]


def _decimal(values: Iterable[sp.Expr]) -> list[str]:
    return [str(sp.N(value, 18)) for value in values]


def _vector_record(values: Iterable[sp.Expr]) -> dict[str, list[str]]:
    vector = list(values)
    return {"exact": _exact(vector), "decimal": _decimal(vector)}


def build_payload() -> dict[str, object]:
    certificate = checker.build_certificate()
    if not certificate["valid"]:
        raise RuntimeError("the underlying exact period-66 certificate failed")

    states = certificate["states"][: checker.PERIOD]
    updates = certificate["updates"]
    word = certificate["problem"]["word"]
    compact = checker.certificate_payload(certificate)
    phases: list[dict[str, object]] = []

    for phase, state in enumerate(states):
        # updates[j]["x"] is x^{j+1}.  Cyclic closure therefore identifies
        # x^0 with the x-value produced by the phase-65 update.
        x_value = updates[(phase - 1) % checker.PERIOD]["x"]
        y_value = state[:2, 0]
        z_value = state[2:4, 0]
        lambda_value = state[4:6, 0]
        q_value = z_value + lambda_value
        mask = "".join("1" if value > 0 else "0" for value in q_value)
        expected_mask = "".join(str(bit) for bit in word[phase])
        if mask != expected_mask:
            raise RuntimeError(f"phase {phase}: mask mismatch {mask} != {expected_mask}")
        phases.append(
            {
                "phase_zero_based": phase,
                "mask": mask,
                "x": _vector_record(x_value),
                "y": _vector_record(y_value),
                "z": _vector_record(z_value),
                "lambda": _vector_record(lambda_value),
                "q_equals_z_plus_lambda": _vector_record(q_value),
            }
        )

    return {
        "schema_version": 1,
        "instance_id": checker.INSTANCE_ID,
        "status": "passed",
        "valid": len(phases) == checker.PERIOD,
        "period": checker.PERIOD,
        "phase_convention": (
            "Entry k records the cyclic state (x^k,y^k,z^k,lambda^k); "
            "q^k=z^k+lambda^k and mask k is derived from the exact sign of q^k."
        ),
        "exact_orbit_y_q_sha256": compact["exact_hashes"]["orbit_y_q"],
        "claim_boundary": (
            "This file is a deterministic data rendering of the accepted raw "
            "certificate, not an additional proof or an independent checker."
        ),
        "phases": phases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export all 66 exact cyclic ADMM states."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "instance_id": payload["instance_id"],
                "output": str(args.output.resolve()),
                "phases": len(payload["phases"]),
                "valid": payload["valid"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
