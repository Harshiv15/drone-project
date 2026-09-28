import logging

from interfaces.base_io import BaseIO, BaseIOInputs
from schemas.flight_plan import FlightPlan

logger = logging.getLogger(__name__)


class Drone:
    def __init__(self, io: BaseIO):
        self._io = io
        self.inputs: BaseIOInputs = BaseIOInputs()

    def connect(self) -> bool:
        logger.info("Connecting to drone...")
        success = self._io.connect()
        if success:
            self.periodic()
            logger.info(f"Connected. Battery: {self.inputs.battery_pct}%.")
        return success

    def disconnect(self):
        logger.info("Disconnecting link.")
        self._io.disconnect()

    def e_stop(self):
        self._io.e_stop()
        self.periodic()

    def execute_plan(self, plan: FlightPlan) -> bool:
        self.periodic()

        if not self.inputs.connected:
            logging.error("[REJECTED] Drone is not connected!")
            return False

        if self.inputs.battery_pct < plan.safety.min_battery:
            logging.error(
                f"[REJECTED] Battery low ({self.inputs.battery_pct}% < {plan.safety.min_battery}% required)!"
            )
            return False

        for idx, step in enumerate(plan.steps):
            if self.inputs.e_stopped:
                logging.critical(f"[ABORT] Execution aborted before step {idx + 1}/{len(plan.steps)}]!")
                return False

            logger.info(f"Executing step {idx + 1}/{len(plan.steps)} [{step.action.upper()}]")

            success = self._io.execute_step(step)
            if success:
                logger.info(f"Step {idx + 1}/{len(plan.steps)} completed")
            else:
                logging.error(f"[FAIL] Step {idx + 1} FAILED! Killing motors")
                self.e_stop()
                return False
        return True

    def periodic(self):
        self._io.update_inputs(self.inputs)