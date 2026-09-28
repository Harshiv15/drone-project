import logging

from interfaces.drone import Drone
from schemas.flight_plan import FlightPlan

logger = logging.getLogger(__name__)

class Container:
    def __init__(self, drones: dict[str, Drone]):
        self.drones = drones

    def run_plan(self, target_drone: str, plan: FlightPlan) -> bool:
        logger.info(f"Dispatching flight plan: '{plan.maneuver}'")
        success = self.drones[target_drone].execute_plan(plan)
        if success:
            logger.info(f"Plan '{plan.maneuver}' completed successfully.")
        else:
            logger.error(f"Plan '{plan.maneuver}' failed or was aborted.")
        return success