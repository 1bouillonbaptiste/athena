import annotated_types
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
