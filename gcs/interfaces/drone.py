import logging

from interfaces.base_io import BaseIO, BaseIOInputs
from schemas.flight_plan import FlightPlan


class Drone:
    def __init__(self, io: BaseIO):
        self.io = io
        self.inputs = BaseIOInputs()

    def periodic(self):
        self.io.update_inputs(self.inputs)

    def execute_plan(self, plan: FlightPlan) -> bool:
        self.periodic()
        logging.info(f"--- Starting Maneuver: {plan.maneuver} ---")

        if self.inputs.battery_pct < plan.safety.min_battery:
            logging.error(
                f"[REJECTED] Battery low ({self.inputs.battery_pct}% < {plan.safety.min_battery}% required)!"
            )
            return False

        if not self.inputs.connected:
            logging.error("[REJECTED] Drone is not connected!")
            return False

        for idx, step in enumerate(plan.steps):
            if self.inputs.e_stopped:
                logging.critical(f"[ABORT] Execution aborted before step {idx + 1}!")
                return False

            success = self.io.execute_step(step)
            if not success:
                logging.error(f"[FAIL] Step {idx + 1} failed. Triggering failsafe land!")
                self.io.e_stop()
                return False

        logging.info(f"--- Maneuver '{plan.maneuver}' Completed Successfully! ---")
        return True