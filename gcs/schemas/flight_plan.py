from enum import Enum
from typing import Literal, Optional
from unittest import case

from pydantic import BaseModel, Field, model_validator


class Action(str, Enum):
    TAKEOFF = "takeoff"
    HOVER = "hover"
    ROTATE_CW = "rotate_cw"
    ROTATE_CCW = "rotate_ccw"
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    LAND = "land"

class FlightStep(BaseModel):
    action: str
    distance_m: Optional[float] = Field(0, ge=0)
    angle_deg: Optional[float] = Field(0, ge=0)
    duration_s: float = Field(1, gt=0)


class SafetyLimits(BaseModel):
    max_altitude_m: float = Field(15, le=15)
    max_distance_m: float = Field(20, le=30)
    min_battery: float = Field(20, ge=15)


class FlightPlan(BaseModel):
    maneuver: str
    max_speed_m_s: float
    steps: list[FlightStep] = Field(..., min_length=1)
    safety: SafetyLimits = SafetyLimits()

    @model_validator(mode="after")
    def validate_plan(self):
        match self.steps[0].action:
            case Action.TAKEOFF | Action.HOVER:
                pass
            case _:
                raise ValueError("First step must be takeoff or hover!")

        match self.steps[-1].action:
            case x if x == Action.LAND:
                pass
            case _:
                raise ValueError("Last step must be land!")

        for step in self.steps:
            match step.action:
                case Action.FORWARD | Action.BACKWARD | Action.LEFT | Action.RIGHT:
                    if step.angle_deg:
                        raise ValueError(f"Translation step {step.action} cannot have a rotational component!")
                case Action.ROTATE_CW | Action.ROTATE_CCW:
                    if step.distance_m:
                        raise ValueError(f"Rotation step {step.action} cannot have a translational component!")

        return self
