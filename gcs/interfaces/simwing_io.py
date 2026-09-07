import logging
import time

from interfaces.base_io import BaseIO, BaseIOInputs
from schemas.flight_plan import FlightStep

logger = logging.getLogger(__name__)

class MockBase(BaseIO):
    def __init__(self, simulated_battery: int = 80, sim_speedup: float = 1.0):
        self.battery_pct = simulated_battery
        self.sim_speedup = sim_speedup
        self.connected = False
        self.is_flying = False
        self.altitude_m = 0
        self.yaw_deg = 0
        self.emergency_stop_tripped = False

    def connect(self):
        logger.info("Connecting to virtual drone link (UDP Mock Stream)...")
        self.connected = True
        logger.info(f"Connected. Battery: {self.battery_pct}%.")
        return True

    def disconnect(self):
        logger.info("Disconnecting link.")
        self.connected = False
        self.is_flying = False

    def e_stop(self):
        self.emergency_stop_tripped = True
        self.is_flying = False
        self.altitude_m = 0
        logger.critical("!!! EMERGENCY KILL SWITCH TRIGGERED - MOTORS CUT !!!")

    def get_battery(self) -> int:
        return self.battery_pct

    def execute_step(self, step: FlightStep):
        if self.emergency_stop_tripped:
            logger.error("Cannot execute step: Emergency stop was tripped.")
            return False

        if not self.connected:
            logger.error("Cannot execute step: Not connected.")
            return False

        if step.action == "takeoff":
            self.is_flying = True
            self.altitude_m = 10
            logger.info(f"[EXEC] Action: TAKEOFF -> Hovering at {self.altitude_m}m")

        elif step.action == "land":
            self.is_flying = False
            self.altitude_m = 0
            logger.info("[EXEC] Action: LAND -> Touchdown complete. Motors disarmed.")

        elif step.action in ["rotate_cw", "rotate_ccw"]:
            logger.info(f"[EXEC] Action: YAW ({step.action}) by {step.angle_deg}° over {step.duration_s}s")
            if step.action == "rotate_cw":
                self.yaw_deg += step.angle_deg
            else:
                self.yaw_deg -= step.angle_deg

        elif step.action in ["forward", "backward", "left", "right"]:
            logger.info(
                f"[EXEC] Action: TRANSLATE ({step.action}) by {step.distance_m}m over {step.duration_s}s")

        elif step.action == "hover":
            logger.info(f"[EXEC] Action: HOVER for {step.duration_s}s")

        sleep_time = step.duration_s / self.sim_speedup
        time.sleep(sleep_time)
        return True

    def update_inputs(self, inputs: BaseIOInputs) -> None:
        inputs.connected = self.connected
        inputs.is_flying = self.is_flying
        inputs.altitude_m = self.altitude_m
        inputs.battery_pct = self.battery_pct
        inputs.yaw_deg = self.yaw_deg
        inputs.e_stopped = self.emergency_stop_tripped
