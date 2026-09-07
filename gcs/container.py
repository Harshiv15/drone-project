import asyncio
import logging

from interfaces.drone import Drone

if __name__ == "main":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s")


class RobotContainer:
    def __init__(self, drone: Drone):
        self.drone = drone

    async def periodic(self):
        while True:
            self.drone.io.update_inputs(self.drone.inputs)
            await asyncio.sleep(0.02)

    async def run_maneuvers(self):
        pass
        # while True:
        #     plan = await wait_for_llm_trigger()
        #     await self.drone.execute_plan(plan)

    async def main(self):
        await asyncio.gather(
            self.periodic(),
            self.run_maneuvers()
        )