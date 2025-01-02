# I am trying to achieve a way of providing a start and end point as well as interpolation points and a time to complete the movement and have the motor follow a smooth trajectory


import asyncio
import moteus
import math
import numpy as np

interpolation_points = 10  # Number of interpolation points
movement_time = 1  # Total time for the entire movement

c1 = moteus.Controller(1)


# Calculate velocity for smooth motion between positions
def calculate_velocity(current_pos, target_pos):
    distance = abs(target_pos - current_pos)

    # Velocity is distance divided by time per segment
    velocity = distance / (movement_time / interpolation_points)

    return velocity


async def main():
    await c1.set_stop()
    await c1.set_position_wait_complete(position=0, accel_limit=3)

    # Interpolated positions (moving from 0 to 1)
    position = np.linspace(0, 1, interpolation_points)

    for i in range(len(position) - 1):
        current_pos = position[i]
        target_pos = position[i + 1]

        # Calculate velocity for the current segment
        velocity = calculate_velocity(current_pos, target_pos)

        # Move to the target position with the calculated velocity
        await c1.set_position(
            position=target_pos,
            velocity=velocity,
            watchdog_timeout=math.nan,
        )

        # Wait until the motor has reached the position with smooth motion
        await asyncio.sleep(movement_time / interpolation_points)

    await c1.set_stop()


if __name__ == '__main__':
    asyncio.run(main())
