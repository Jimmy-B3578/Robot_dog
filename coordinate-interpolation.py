import asyncio
import math

import matplotlib.pyplot as plt
import moteus

from ik_equations import calculate_motor_positions

x_scale_factor = 50
y_scale_factor = 50
acceleration = 10
velocity = 3
kp = 7
kd = 2
time_to_move = 1
steps_scale = 75

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

# Storage for motor target positions, feedback positions, and time
time_log = []
motor1_targets = []
motor2_targets = []
motor1_feedback = []
motor2_feedback = []

# Parametric linear interpolation with smoothing for velocity
def smooth_interpolation(p1, p2, num_steps):
    x1, y1 = p1
    x2, y2 = p2

    # Calculate direction and distance
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)

    # Generate steps based on the number of steps and smooth velocity profile
    for step in range(num_steps):
        t = step / num_steps  # Normalized time (0 to 1)
        smoothed_t = (1 - math.cos(math.pi * t)) / 2  # Sinusoidal easing function

        # Interpolate the point with smoothing
        x_t = x1 + dx * smoothed_t
        y_t = y1 + dy * smoothed_t
        yield x_t, y_t, distance

async def main():
    # Clear any outstanding faults
    await c1.set_stop()
    await c2.set_stop()

    global time_log, motor1_targets, motor2_targets, motor1_feedback, motor2_feedback

    current_time = 0
    try:
        # Loop through the coordinates once
        for i in range(len(coordinates) - 1):
            p1 = coordinates[i]
            p2 = coordinates[i + 1]

            # Calculate the distance between the two points
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            distance = math.sqrt(dx**2 + dy**2)

            # Calculate the number of steps based on distance and desired time to move
            num_steps = max(10, int(distance * steps_scale))  # Scaling factor (50) controls smoothness

            # Parametric interpolation with smoothed velocity
            for target_x, target_y, _ in smooth_interpolation(p1, p2, num_steps):
                # Scale the coordinates to match your motor's range
                target_x_scaled = target_x * x_scale_factor
                target_y_scaled = -target_y * y_scale_factor  # Inverting Y-axis for proper movement

                # Calculate joint angles using inverse kinematics
                angles = await calculate_motor_positions(target_x_scaled, target_y_scaled)
                if angles is not None:
                    m1, m2 = angles

                    # Log target positions
                    time_log.append(current_time)
                    motor1_targets.append(m1)
                    motor2_targets.append(m2)

                    # Command the motors and retrieve feedback
                    result1 = await c1.set_position(
                        position=m1,
                        velocity_limit=velocity,
                        accel_limit=acceleration,
                        kp_scale=kp,
                        kd_scale=kd,
                        watchdog_timeout=math.nan,
                        query=True  # Enable querying to get feedback
                    )
                    result2 = await c2.set_position(
                        position=m2,
                        velocity_limit=velocity,
                        accel_limit=acceleration,
                        kp_scale=kp,
                        kd_scale=kd,
                        watchdog_timeout=math.nan,
                        query=True  # Enable querying to get feedback
                    )

                    # Log feedback positions
                    motor1_feedback.append(result1.values.get(1, 0))  # Key 1 corresponds to position
                    motor2_feedback.append(result2.values.get(1, 0))  # Key 1 corresponds to position

                current_time += time_to_move / num_steps
                # Sleep to maintain the movement duration
                await asyncio.sleep(time_to_move / num_steps)

        print("Completed one full loop of the square.")

    finally:
        await c1.set_stop()
        await c2.set_stop()
        print("Cleaning up and stopping the motors.")

        # Plot motor positions
        plt.figure(figsize=(10, 6))
        plt.plot(time_log, motor1_targets, label="Motor 1 Target Position", linestyle="--")
        plt.plot(time_log, motor2_targets, label="Motor 2 Target Position", linestyle="--")
        plt.plot(time_log, motor1_feedback, label="Motor 1 Feedback Position", alpha=0.7)
        plt.plot(time_log, motor2_feedback, label="Motor 2 Feedback Position", alpha=0.7)
        plt.xlabel("Time (s)")
        plt.ylabel("Motor Position")
        plt.title("Motor Target vs Feedback Positions Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    asyncio.run(main())