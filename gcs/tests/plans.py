from schemas.flight_plan import FlightPlan

TEST_360_PAN_JSON = """
{
  "maneuver": "360_pan",
  "max_speed_m_s": 10.0,
  "steps": [
    {"action": "takeoff", "distance_m": 1.0,  "duration_s": 1.0},
    {"action": "hover", "duration_s": 0.5},
    {"action": "backward", "distance_m": 1.0, "duration_s": 1.0},
    {"action": "left", "distance_m": 1.0, "duration_s": 1.0},
    {"action": "rotate_cw", "angle_deg": 45.0, "duration_s": 0.5},
    {"action": "forward", "distance_m": 1.414, "duration_s": 1.0},
    {"action": "hover", "duration_s": 0.5},
    {"action": "rotate_ccw", "angle_deg": 360.0, "duration_s": 6.0},
    {"action": "hover", "duration_s": 0.5},
    {"action": "land", "duration_s": 1.0}
  ]
}
"""


def get_test_flight_plan() -> FlightPlan:
    return FlightPlan.model_validate_json(TEST_360_PAN_JSON)