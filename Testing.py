import math
import asyncio
import moteus
import numpy as np
from ik_equations import calculate_motor_positions

Overall_time = 2

c1 = moteus.Controller(1)
c2 = moteus.Controller(2)

async def generate_motor_positions(start_coord, end_coord, num_points):
    """
    Interpolate between start and end coordinates, calculate motor positions (theta1, theta2).

    Parameters:
        start_coord (tuple): Starting (x, y) coordinates.
        end_coord (tuple): Ending (x, y) coordinates.
        num_points (int): Number of interpolation points.

    Returns:
        list: List of tuples containing (theta1, theta2) for each interpolated coordinate.
    """
    # Interpolate x and y values
    x_values = np.linspace(start_coord[0], end_coord[0], num_points)
    y_values = np.linspace(start_coord[1], end_coord[1], num_points)

    motor_positions = []

    # Calculate motor positions for each interpolated point
    for x, y in zip(x_values, y_values):
        theta1, theta2 = await calculate_motor_positions(x, y)
        motor_positions.append((theta1, theta2))

    return motor_positions


async def main():
    # Input start and end coordinates, and number of points
    start_coord = (0, 0)  # Replace with user input or predefined values
    end_coord = (10, 10)  # Replace with user input or predefined values
    num_points = 100  # Number of interpolation points

    # Generate motor positions
    motor_positions = await generate_motor_positions(start_coord, end_coord, num_points)

    # Calculate time per step
    time = round(Overall_time / (len(motor_positions) - 1), 3)

    for i in range(len(motor_positions) - 1):
        current_pos = motor_positions[i]
        next_pos = motor_positions[i + 1]

        # Calculate the difference in motor angles
        difference = tuple(round(next_pos[j] - current_pos[j], 5) for j in range(2))

        # Calculate velocity (angle change per second)
        velocity = tuple(round(d / time, 5) for d in difference)

        print(f"Current Position: {current_pos}")
        print(f"Difference: {difference}")
        print(f"Target Position: {next_pos}")
        await c1.set_position(position=next_pos[0], velocity=velocity[0])
        await c1.set_position(position=next_pos[1], velocity=velocity[1])
        print(f"Time in seconds: {time}")
        print(f"Velocity: {velocity}")
        print()  # For better readability

        await asyncio.sleep(time)


if __name__ == '__main__':
    asyncio.run(main())
