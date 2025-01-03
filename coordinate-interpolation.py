import asyncio
import math
import moteus
import matplotlib.pyplot as plt
from ik_equations import calculate_motor_positions

x_scale_factor = 50
y_scale_factor = 50
reduction_ratio = 6
time_to_move = 1  # Total time to move
steps_scale = 10

# Storage for diagnostic motor angles, velocities, and time per step
motor_angles_log = []
motor1_velocities = []
motor2_velocities = []
time_log = []  # Log of the times for plotting against time

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

# Linear interpolation for constant motion
def linear_interpolation(p1, p2, num_steps):
    x1, y1 = p1
    x2, y2 = p2

    # Calculate direction and distance
    dx = x2 - x1
    dy = y2 - y1

    # Generate steps based on the number of steps
    for step in range(num_steps):
        t = step / num_steps  # Normalized time (0 to 1)

        # Interpolate the point linearly
        x_t = x1 + dx * t
        y_t = y1 + dy * t
        yield x_t, y_t

async def main():
    # Clear any outstanding faults
    await c1.set_stop()
    await c2.set_stop()

    global motor_angles_log, motor1_velocities, motor2_velocities, time_log

    try:
        # Loop through the coordinates once
        total_time_elapsed = 0  # To track the total time elapsed for each step
        for i in range(len(coordinates) - 1):
            p1 = coordinates[i]
            p2 = coordinates[i + 1]

            # Calculate the distance between the two points
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            distance = math.sqrt(dx**2 + dy**2)

            # Calculate the number of steps based on distance and desired time to move
            num_steps = max(10, int(distance * steps_scale))  # Scaling factor (10) controls smoothness

            # Linear interpolation with constant velocity
            for step_idx, (target_x, target_y) in enumerate(linear_interpolation(p1, p2, num_steps)):
                # Scale the coordinates to match your motor's range
                target_x_scaled = target_x * x_scale_factor
                target_y_scaled = -target_y * y_scale_factor  # Inverting Y-axis for proper movement

                # Calculate joint angles using inverse kinematics
                angles = await calculate_motor_positions(target_x_scaled, target_y_scaled, reduction_ratio)
                if angles is not None:
                    m1, m2 = angles

                    # Store the angles for diagnostics (without triggering motor movement)
                    motor_angles_log.append((m1, m2))

                    # Calculate the velocity for the motor positions (difference between consecutive positions)
                    if len(motor_angles_log) >= 2:
                        # Motor position differences
                        prev_m1, prev_m2 = motor_angles_log[-2]
                        m1_diff = m1 - prev_m1
                        m2_diff = m2 - prev_m2

                        # Time per step
                        time_per_step = time_to_move / num_steps
                        total_time_elapsed += time_per_step
                        time_log.append(total_time_elapsed)  # Log the time

                        # Calculate velocities (both positive and negative are handled)
                        m1_velocity = m1_diff / time_per_step
                        m2_velocity = m2_diff / time_per_step

                        # Log velocities
                        motor1_velocities.append(m1_velocity)
                        motor2_velocities.append(m2_velocity)

        print("Completed one full loop of the square.")

        # Print the motor angles, velocities, and time per step together
        print("Motor Angles, Velocities, and Time Per Step Log:")
        for idx, (angles, m1_velocity, m2_velocity, step_time) in enumerate(zip(motor_angles_log, motor1_velocities, motor2_velocities, time_log)):
            m1, m2 = angles
            print(f"Step {idx + 1}: Motor 1 Angle = {m1}, Motor 2 Angle = {m2} | "
                  f"Motor 1 Velocity = {m1_velocity:.4f}, Motor 2 Velocity = {m2_velocity:.4f} | "
                  f"Time = {step_time:.4f} s")

        # Plotting the velocities using matplotlib
        plt.figure(figsize=(10, 6))
        plt.plot(time_log, motor1_velocities, label='Motor 1 Velocity', color='blue', linestyle='-', marker='o')
        plt.plot(time_log, motor2_velocities, label='Motor 2 Velocity', color='red', linestyle='-', marker='x')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Velocity (units/second)')
        plt.title('Motor Velocities Over Time')
        plt.legend()
        plt.grid(True)
        plt.show()

    finally:
        await c1.set_stop()
        await c2.set_stop()
        print("Cleaning up and stopping the motors.")

if __name__ == '__main__':
    asyncio.run(main())
