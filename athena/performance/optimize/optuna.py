from typing import Any

import annotated_types
from optuna import Trial
from pydantic import BaseModel
from dataclasses import dataclass


@dataclass
class Constraint:
    """Store a constraint."""

    name: str
    type: int | float
    min: int | float | None = None
    max: int | float | None = None


def pydantic_model_to_constraints(model: BaseModel) -> list[Constraint]:
    """Convert pydantic BaseModel fields constraints into optuna readable constraints."""
    constraints = []
    for name, infos in model.model_fields.items():
        if infos.annotation not in [int, float]:
            continue
        new_constraint = Constraint(name=name, type=infos.annotation)
        for metadata in infos.metadata:
            match type(metadata):
                case annotated_types.Ge:
                    new_constraint.min = metadata.ge
                case annotated_types.Le:
                    new_constraint.max = metadata.le
                case annotated_types.Gt:
                    new_constraint.min = (
                        (metadata.gt + 1) if infos.annotation is int else metadata.gt
                    )
                case annotated_types.Lt:
                    new_constraint.max = (
                        (metadata.lt - 1) if infos.annotation is int else metadata.lt
                    )
                case _:
                    NotImplementedError(
                        f"Could not convert metadata type {type(metadata)} to a valid constraint."
                    )
        constraints.append(new_constraint)
    return constraints


def constraints_to_parameters(
    trial: Trial, constraints: list[Constraint]
) -> dict[str:Any]:
    strategy_parameters = {}
    for constraint in constraints:
        if constraint.type is int:
            strategy_parameters.update(
                {
                    constraint.name: trial.suggest_int(
                        name=constraint.name,
                        low=constraint.min or 0,
                        high=constraint.max or float("inf"),
                    )
                }
            )
        elif constraint.type is float:
            strategy_parameters.update(
                {
                    constraint.name: trial.suggest_float(
                        name=constraint.name,
                        low=constraint.min or 0,
                        high=constraint.max or float("inf"),
                    )
                }
            )
    return strategy_parameters
