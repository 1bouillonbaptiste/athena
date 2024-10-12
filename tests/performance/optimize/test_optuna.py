from pydantic import BaseModel, Field

from athena.performance.optimize.optuna import pydantic_model_to_constraints, Constraint


def test_pydantic_model_to_constraints():
    class TemporaryModel(BaseModel):
        field_str: str
        field_int: int = Field()
        field_int_min_max_included: int = Field(ge=0, le=10)
        field_int_min_max_excluded: int = Field(gt=0, lt=10)
        field_float: float = Field()
        field_float_min_max_included: float = Field(ge=0, le=3.14)
        field_float_min_max_excluded: float = Field(gt=0, lt=3.14)

    assert pydantic_model_to_constraints(model=TemporaryModel) == [
        Constraint(name="field_int", type=int, min=None, max=None),
        Constraint(name="field_int_min_max_included", type=int, min=0, max=10),
        Constraint(name="field_int_min_max_excluded", type=int, min=1, max=9),
        Constraint(name="field_float", type=float, min=None, max=None),
        Constraint(name="field_float_min_max_included", type=float, min=0, max=3.14),
        Constraint(name="field_float_min_max_excluded", type=float, min=0, max=3.14),
    ]
