from dataclasses import dataclass

class IRTError(ValueError):
    pass

@dataclass(frozen=True)
class ItemParameters:
    """a = discrimination, b = difficulty, c = pseudo-guessing."""
    item_id: str
    a: float
    b: float
    c: float = 0.0

    def __post_init__(self) -> None:
        if self.a <= 0:
            raise IRTError(f'{self.item_id}: discrimination must be positive')
        if not 0.0 <= self.c < 1.0:
            raise IRTError(f'{self.item_id}: guessing must be in [0, 1)')
        if not -5.0 <= self.b <= 5.0:
            raise IRTError(f'{self.item_id}: difficulty out of plausible range')

@dataclass(frozen=True)
class Item:
    item_id: str
    content_area: str
    skills: list[str]
    parameters: ItemParameters

@dataclass(frozen=True)
class Response:
    item: ItemParameters
    correct: bool

@dataclass(frozen=True)
class AbilityEstimate:
    theta: float
    standard_error: float
    iterations: int
    converged: bool

@dataclass(frozen=True)
class MasteryState:
    skill_id: str
    theta: float
    standard_error: float
    evidence_items: int
