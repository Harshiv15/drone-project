from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class FlightStep(BaseModel):
    action: Literal[
        "takeoff",
        "hover",
        "rotate_cw",
        "rotate_ccw",
        "forward",
        "backward",
        "left",
        "right",
        "land"
    ]
    duration_s: float | int = Field(1, gt=0)
    distance_m: Optional[float | int] = Field(0, ge=0)
    angle_deg: Optional[float | int] = Field(0, ge=0)


class SafetyLimits(BaseModel):
    max_altitude: int = Field(15, le=15)
    max_distance: int = Field(20, le=30)
    min_battery: int = Field(20, ge=15)


class FlightPlan(BaseModel):
    maneuver: str
    duration: float | int
    max_speed: float | int
    steps: list[FlightStep]
    safety: SafetyLimits

    @model_validator(mode="after")
    def validate_plan(self):
        if not self.steps:
            raise ValueError("Flight plan must contain at least one step!")

        if self.steps[0].action not in ["takeoff", "hover"]:
            raise ValueError("First step must be takeoff or hover!")

        if self.steps[-1].action != "land":
            raise ValueError("Last step must be land!")

        total_duration = sum(step.duration_s for step in self.steps)
        if total_duration > self.duration:
            raise ValueError(
                f"Total step duration ({total_duration}s) exceeds declared maneuver duration ({self.duration}s)!"
            )

        return self
