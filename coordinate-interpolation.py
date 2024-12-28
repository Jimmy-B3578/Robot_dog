import asyncio
import moteus
import math
from ik_equations import calculate_motor_positions
import numpy as np

x_scale_factor = 50
y_scale_factor = 50
acceleration = 10
velocity = 1
torque_v = 0.5
reduction_ratio = 6

c1 = moteus.Controller(1)
c2 = moteus.Controller(2)

# Predefined list of coordinates within the range of 1 to -1 for both x and y
coordinates = [
    (1.0, 1.0),  # Top-right corner
    (1.0, -1.0),  # Bottom-right corner
    (-1.0, -1.0),  # Bottom-left corner
    (-1.0, 1.0),  # Top-left corner
    (1.0, 1.0)  # Back to top-right corner to close the square
]


# Function for linear interpolation between two points
def interpolate_points(p1, p2, num_steps=20):
    # p1 and p2 are tuples (x, y)
    x1, y1 = p1
    x2, y2 = p2

    interpolated_points = []
    for t in np.linspace(0, 1, num_steps):  # num_steps determines the number of interpolated points
        x_t = x1 + (x2 - x1) * t
        y_t = y1 + (y2 - y1) * t
        interpolated_points.append((x_t, y_t))

    return interpolated_points


async def main():
    # Clear any outstanding faults
    await c1.set_stop()
    await c2.set_stop()

    try:
        while True:  # Loop the tracing indefinitely
            # Generate interpolated coordinates to trace the square
            interpolated_coordinates = []
            for i in range(len(coordinates) - 1):
                p1 = coordinates[i]
                p2 = coordinates[i + 1]
                interpolated_coordinates.extend(interpolate_points(p1, p2, num_steps=20))  # 20 steps per segment

            # Move through all interpolated coordinates
            for target_x, target_y in interpolated_coordinates:
                # Scale the coordinates to match your motor's range
                target_x_scaled = target_x * x_scale_factor
                target_y_scaled = -target_y * y_scale_factor  # Inverting Y-axis for proper movement

                # Calculate joint angles using inverse kinematics
                angles = await calculate_motor_positions(target_x_scaled, target_y_scaled, reduction_ratio)
                if angles is not None:
                    m1, m2 = angles

                    # Command the motors to move to the calculated positions
                    await c1.set_position(
                        position=m1,
                        velocity_limit=velocity,
                        accel_limit=acceleration,
                        maximum_torque=torque_v,
                        watchdog_timeout=math.nan,
                        query=False)

                    await c2.set_position(
                        position=m2,
                        velocity_limit=velocity,
                        accel_limit=acceleration,
                        maximum_torque=torque_v,
                        watchdog_timeout=math.nan,
                        query=False)

                await asyncio.sleep(0.05)  # Small sleep interval between movements for smooth motion

            print("Completed one full loop of the square.")
            await asyncio.sleep(1)  # Pause briefly before starting the next loop

    finally:
        await c1.set_stop()
        await c2.set_stop()
        print("Cleaning up and stopping the motors.")


if __name__ == '__main__':
    asyncio.run(main())
