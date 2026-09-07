from abc import ABC, abstractmethod
from dataclasses import dataclass

from schemas.flight_plan import FlightStep


@dataclass
class BaseIOInputs:
    connected: bool = False
    is_flying: bool = False
    battery_pct: int | float = 80
    altitude_m: int | float = 0
    yaw_deg: int | float = 0
    e_stopped: bool = False


class BaseIO(ABC):
    @abstractmethod
    def update_inputs(self, inputs: BaseIOInputs) -> None:
        pass

    @abstractmethod
    def connect(self) -> bool:
        """wifi/CRTP/stub"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def get_battery(self) -> int:
        pass

    @abstractmethod
    def e_stop(self) -> None:
        pass

    @abstractmethod
    def execute_step(self, step: FlightStep) -> bool:
        pass