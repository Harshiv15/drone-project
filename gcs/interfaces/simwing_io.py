import math
import os
import time

import numpy as np
import pybullet as p
import pybullet_data

from interfaces.base_io import BaseIO, BaseIOInputs
from schemas.flight_plan import FlightStep


class SimWingIO(BaseIO):
    def __init__(self, gui: bool = True, initial_battery: float = 95.0):
        self.gui = gui
        self.battery_pct = initial_battery
        self.connected = False
        self.is_flying = False
        self.e_stopped = False

        self.client_id = -1
        self.drone_id = -1

        self.pos = np.array([0.0, 0.0, 0.0])
        self.yaw_rad = 0.0

    def connect(self) -> bool:
        connection_mode = p.GUI if self.gui else p.DIRECT
        self.client_id = p.connect(connection_mode)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)

        # Load floor
        p.loadURDF("plane.urdf")

        start_pos = [0, 0, 0.02]
        start_orientation = p.getQuaternionFromEuler([0, 0, 0])

        urdf_path = os.path.join(os.getcwd(), "assets", "cf2x.urdf")

        if os.path.exists(urdf_path):
            self.drone_id = p.loadURDF(urdf_path, start_pos, start_orientation)
        else:
            print("[SimWingIO] Local cf2x.urdf not found. Spawning fallback box.")
            col_box = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.04, 0.04, 0.01])
            self.drone_id = p.createMultiBody(baseMass=0.035, baseCollisionShapeIndex=col_box, basePosition=start_pos)

        p.resetDebugVisualizerCamera(
            cameraDistance=1,
            cameraYaw=45,
            cameraPitch=-20,
            cameraTargetPosition=[0, 0, 0.1]
        )

        self.connected = True
        return True

    def disconnect(self) -> None:
        if self.connected and self.client_id >= 0:
            p.disconnect(self.client_id)
            self.connected = False

    def e_stop(self) -> None:
        self.e_stopped = True
        self.is_flying = False
        if self.connected and self.drone_id >= 0:
            p.resetBaseVelocity(self.drone_id, linearVelocity=[0, 0, -1.0])

    def get_battery(self) -> int:
        return int(self.battery_pct)

    def execute_step(self, step: FlightStep) -> bool:
        if not self.connected or self.e_stopped:
            return False

        start_pos = np.copy(self.pos)
        target_pos = np.copy(self.pos)
        start_yaw = self.yaw_rad
        target_yaw = self.yaw_rad

        if step.action == "takeoff":
            self.is_flying = True
            alt = step.distance_m if (step.distance_m and step.distance_m > 0) else 0.8
            target_pos[2] = alt

        elif step.action == "land":
            target_pos[2] = 0.02

        elif step.action == "rotate_cw":
            angle_rad = math.radians(step.angle_deg if step.angle_deg else 0.0)
            target_yaw -= angle_rad

        elif step.action == "rotate_ccw":
            angle_rad = math.radians(step.angle_deg if step.angle_deg else 0.0)
            target_yaw += angle_rad

        elif step.action in ["forward", "backward", "left", "right"]:
            dist = step.distance_m if (step.distance_m and step.distance_m > 0) else 0.5
            dx, dy = 0.0, 0.0
            if step.action == "forward":
                dx = dist
            elif step.action == "backward":
                dx = -dist
            elif step.action == "left":
                dy = dist
            elif step.action == "right":
                dy = -dist

            cos = math.cos(self.yaw_rad)
            sin = math.sin(self.yaw_rad)
            target_pos[0] += dx * cos - dy * sin
            target_pos[1] += dx * sin + dy * cos

        fps = 60
        total_ticks = max(1, int(step.duration_s * fps))
        dt = step.duration_s / total_ticks

        for tick in range(total_ticks):
            if self.e_stopped:
                return False

            alpha = (tick + 1) / total_ticks
            # Interpolated trajectory setpoint
            cur_target_pos = (1 - alpha) * start_pos + alpha * target_pos
            cur_target_yaw = (1 - alpha) * start_yaw + alpha * target_yaw

            # Update body pose in PyBullet world
            quat = p.getQuaternionFromEuler([0, 0, cur_target_yaw])
            p.resetBasePositionAndOrientation(self.drone_id, cur_target_pos.tolist(), quat)
            p.stepSimulation()

            # Drain tiny simulated battery per second
            self.battery_pct -= (2 * dt)

            # Sync real-world time to avoid fast-forwarding unless configured
            time.sleep(dt)

        # Update cached state after completing the step
        self.pos = target_pos
        self.yaw_rad = target_yaw

        if step.action == "land":
            self.is_flying = False

        return True

    def update_inputs(self, inputs: BaseIOInputs) -> None:
        inputs.connected = self.connected
        inputs.is_flying = self.is_flying
        inputs.e_stopped = self.e_stopped
        inputs.battery_pct = round(self.battery_pct, 1)

        if self.connected and self.drone_id >= 0:
            position, orientation = p.getBasePositionAndOrientation(self.drone_id)
            euler = p.getEulerFromQuaternion(orientation)
            inputs.altitude_m = round(position[2], 3)
            inputs.yaw_deg = round(math.degrees(euler[2]) % 360, 2)