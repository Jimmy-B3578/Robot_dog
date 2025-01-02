# I am trying to achieve a way of providing a start and end point as well as interpolation points and a time to complete the movement and have the motor follow a smooth trajectory


import asyncio
import moteus
import math
import numpy as np
import matplotlib.pyplot as plt

interpolation_points = 5  # Number of interpolation points
movement_time = 1  # Total time for the entire movement
direction = 1  # Set direction (1 for forward, -1 for reverse)

controller = moteus.Controller(1)


# Calculate velocity for smooth motion between positions
def calculate_velocity(current_pos, target_pos):
    distance = abs(target_pos - current_pos)

    # Velocity is distance divided by time per segment
    velocity = distance / (movement_time / interpolation_points)

    return velocity, distance


async def main():
    await controller.set_stop()
    await controller.set_position_wait_complete(position=0, accel_limit=3)

    # Interpolated positions (moving from 0 to 1)
    calculated_positions = np.linspace(0, 1, interpolation_points)

    time_steps = []  # Record time at each step
    actual_positions = []  # Record actual positions from feedback
    expected_positions = []  # Record expected (calculated) positions

    for i in range(len(calculated_positions) - 1):
        current_pos = calculated_positions[i]
        target_pos = calculated_positions[i + 1]

        # Calculate velocity and distance for the current segment
        velocity, distance = calculate_velocity(current_pos, target_pos)

        # Append expected position for plotting
        expected_positions.append(current_pos)
        time_steps.append(i * (movement_time / interpolation_points))

        # Send command to move the motor
        result = await controller.set_position(
            position=current_pos,
            kp_scale=1,
            kd_scale=1,
            velocity=velocity,
            watchdog_timeout=math.nan,
            query=True,  # Request feedback
        )

        # Extract feedback values
        torque = result.values.get(3, 0)  # Torque corresponds to key 3
        current_position = result.values.get(1, 0)  # Position corresponds to key 1

        # Append actual position for plotting
        actual_positions.append(current_position)

        # Print details on one line
        print(
            f"Expected Pos: {current_pos:.4f}, Actual Pos: {current_position:.4f}, "
            f"Torque: {torque:.4f}, Velocity: {velocity:.4f}"
        )

        # Wait until the motor has reached the position with smooth motion
        await asyncio.sleep(movement_time / interpolation_points)

    # Add the final expected and actual positions
    expected_positions.append(calculated_positions[-1])
    actual_positions.append(actual_positions[-1])  # Repeat the last actual position
    time_steps.append((len(calculated_positions) - 1) * (movement_time / interpolation_points))

    # Send stop command
    await controller.set_stop()

    # Plot the expected vs actual positions
    plt.figure(figsize=(8, 5))
    plt.plot(time_steps, expected_positions, label='Calculated Position', marker='o')
    plt.plot(time_steps, actual_positions, label='Actual Position', marker='x', linestyle='--')
    plt.title('Expected vs Actual Position Over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Position')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    asyncio.run(main())
