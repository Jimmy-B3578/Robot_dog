import math
import asyncio
import moteus
from interpolate_points import interpolation_z

c1 = moteus.Controller(1)
c2 = moteus.Controller(2)

async def calculate_motor_positions(x1, y1):
    # offsets
    x = (x1 - 27.972)
    y = (y1 - 232.631)
    gear_reduction = 6

    # Link lengths in mm
    L1, L2 = 150, 180

    # Calculate theta2 using the law of cosines
    cos_theta2 = max(min((x ** 2 + y ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2), 1), -1)  # Clamp to [-1, 1]
    theta2 = math.acos(cos_theta2)  # In radians

    # Calculate theta1
    phi = math.atan2(y, x)
    psi = math.atan2(L2 * math.sin(theta2), L1 + L2 * math.cos(theta2))
    theta1 = phi - psi

    # Convert angles to motor positions
    a1 = round(math.degrees(theta1) + 147.052, 3)
    a3 = 180 - math.degrees(theta2)
    a2 = round(90 + a1 - a3, 3)  # Simplified expression for a2

    # Adjust for gear ratio
    m1, m2 = (angle / 360 * gear_reduction for angle in (a1, a2))

    # Input is expected to be a coordinate representing millimeters from the 0 position of the leg
    # Output is given as a motor position relative to the zero position of each motor which is half-way
    # from either end of the limit of each motor

    await c1.set_position(position=m1, accel_limit=20, velocity_limit=10, watchdog_timeout=math.nan)
    await c2.set_position(position=m2, accel_limit=20, velocity_limit=10, watchdog_timeout=math.nan)