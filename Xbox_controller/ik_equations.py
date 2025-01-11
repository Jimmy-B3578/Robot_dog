import math
import asyncio
import moteus

# These come from the separate library files
from ramp import Ramp, LINEAR, ONCEFORWARD
from interpolate_points import interpolation_y, interpolation_x

# Two moteus motor controllers for demonstration
c1 = moteus.Controller(1)
c2 = moteus.Controller(2)

# We'll keep track of the "old" filtered Y so it can accumulate
_filteredY_old = 0.0
_filteredX_old = 0.0

async def calculate_motor_positions(x1, y1):
    global _filteredY_old, _filteredX_old

    # ----------------------------------------------------------------
    # Step 1: Interpolate Y
    # ----------------------------------------------------------------

    y_interpolated = interpolation_y(y1, 500)
    x_interpolated = interpolation_x(x1, 500)

    # ----------------------------------------------------------------
    # Step 2: Filter the newly interpolated Y
    # ----------------------------------------------------------------

    def filter_value(new_val, old_val):
        FILTER = 1
        return (new_val + (old_val * FILTER)) / (FILTER + 1)

    y_filtered = filter_value(y_interpolated, _filteredY_old)
    _filteredY_old = y_filtered   # update for next time

    x_filtered = filter_value(x_interpolated, _filteredX_old)
    _filteredx_old = x_filtered

    # ----------------------------------------------------------------
    # Example geometry: the rest of your calculations
    #   (as from your snippet). We replace “y1” with “y_filtered.”
    # ----------------------------------------------------------------
    # Offsets
    x = (x_interpolated - 27.972)
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
    result1 = await c1.set_position(
        position=m1,
        accel_limit=20,
        velocity_limit=math.nan,
        kp_scale=1,
        kd_scale=1,
        watchdog_timeout=math.nan
    )
    result2 = await c2.set_position(
        position=m2,
        accel_limit=20,
        velocity_limit=math.nan,
        kp_scale=1,
        kd_scale=1,
        watchdog_timeout=math.nan
    )

    return result1, result2
