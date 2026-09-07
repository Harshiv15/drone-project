import logging

from interfaces.base_io import BaseIO, BaseIOInputs
from schemas.flight_plan import FlightStep

logger = logging.getLogger(__name__)

class LitewingBase(BaseIO):
    """stub until my batteries arrive"""


    def connect(self) -> bool:
        pass

    def disconnect(self) -> None:
        pass

    def e_stop(self) -> None:
        pass

    def get_battery(self) -> int:
        pass

    def execute_step(self, step: FlightStep) -> bool:
        pass

    def update_inputs(self, inputs: BaseIOInputs) -> None:
        pass