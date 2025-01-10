import math
import asyncio
import moteus

# These come from the separate library files
from ramp import Ramp, LINEAR, ONCEFORWARD
from my_filter_lib import filter_value  # or inline if you prefer
from interpolate_points import interpolation_y

# If you do not want multiple files, just define:
#   filter_value(...)
#   interpolation_y(...)
#   in the same file with your main code.

# Two moteus motor controllers for demonstration
c1 = moteus.Controller(1)
c2 = moteus.Controller(2)

# We'll keep track of the "old" filtered Y so it can accumulate
_filteredY_old = 0.0

async def calculate_motor_positions(x1, y1):
    global _filteredY_old

    # ----------------------------------------------------------------
    # Step 1: Interpolate Y
    # ----------------------------------------------------------------
    y_interpolated = interpolation_y(y1, 400)

    # ----------------------------------------------------------------
    # Step 2: Filter the newly interpolated Y
    # ----------------------------------------------------------------
    # y_filtered = filter_value(y_interpolated, _filteredY_old)
    # _filteredY_old = y_filtered   # update for next time

    # ----------------------------------------------------------------
    # Example geometry: the rest of your calculations
    #   (as from your snippet). We replace “y1” with “y_filtered.”
    # ----------------------------------------------------------------
    # Offsets
    x = (x1 - 27.972)
    # Use filtered Y in geometry, not raw y1
    y = (y_interpolated - 232.631)

    gear_reduction = 6
    L1, L2 = 150, 180  # link lengths in mm

    # Law of cosines for theta2
    cos_theta2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_theta2 = max(min(cos_theta2, 1), -1)  # clamp for safety
    theta2 = math.acos(cos_theta2)

    # theta1
    phi = math.atan2(y, x)
    psi = math.atan2(L2 * math.sin(theta2), L1 + L2 * math.cos(theta2))
    theta1 = phi - psi

    # Convert angles to motor-friendly positions
    a1 = math.degrees(theta1) + 147.052
    a3 = 180 - math.degrees(theta2)
    a2 = 90 + a1 - a3  # simplified expression

    # Adjust for gear ratio
    m1 = (a1 / 360.0) * gear_reduction
    m2 = (a2 / 360.0) * gear_reduction

    # ----------------------------------------------------------------
    # Step 3: Send to motors
    # ----------------------------------------------------------------
    await c1.set_position(
        position=m1,
        accel_limit=20,
        velocity_limit=50,
        watchdog_timeout=math.nan
    )
    await c2.set_position(
        position=m2,
        accel_limit=20,
        velocity_limit=50,
        watchdog_timeout=math.nan
    )
