import logging
import sys
from enum import Enum

from container import Container
from interfaces.drone import Drone
from interfaces.simwing_io import SimWingIO  # Swap with PyBulletDrone or LiteWingDrone later
from tests.plans import get_test_flight_plan


class Drones(str, Enum):
    MAIN = "main"

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger("Main")

    drones: dict[str, Drone] = {Drones.MAIN.value: Drone(io=SimWingIO(gui=True, initial_battery=80))}
    container = Container(drones)

    for drone in drones:
        if not drones[drone].connect():
            logger.error(f"Failed to connect to drone {drone}. Exiting.")
            sys.exit(1)

    try:
        plan = get_test_flight_plan()
        container.run_plan(Drones.MAIN, plan)
    except KeyboardInterrupt:
        logger.warning("\n[INTERRUPT] Aborting flight via kill switch...")
        for drone in drones:
            drones[drone].e_stop()
    finally:
        for drone in drones:
            drones[drone].disconnect()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    main()