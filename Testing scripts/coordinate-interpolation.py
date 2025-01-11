import asyncio
import math
import moteus
import matplotlib.pyplot as plt
from Xbox_controller.ik_equations import calculate_motor_positions
from Xbox_controller.interpolate_points import interpolate_coordinates  # Import the new interpolation function

# Velocity and acceleration parameters sent to Moteus
acceleration = 20
velocity_limit = 25
kp = 1
kd = 1

# Adjust how quickly each segment is traversed (seconds per unit distance)
time_per_unit_distance = 1.0

# A scaling factor that dictates how many interpolation steps you take per unit distance
steps_scale = 75

c1 = moteus.Controller(1)
c2 = moteus.Controller(2)

# Predefined list of coordinates within the range of 1 to -1 for both x and y
coordinates = [
    (50.0, 50.0),    # Top-right corner
    (50.0, -50.0),   # Bottom-right corner
    (-50.0, -50.0),  # Bottom-left corner
    (-50.0, 50.0),   # Top-left corner
    (50.0, 50.0)     # Back to top-right corner to close the square
]

# Storage for motor target positions, feedback positions, time, and XY coordinates
time_log = []
motor1_targets = []
motor2_targets = []
motor1_feedback = []
motor2_feedback = []
interpolated_x = []
interpolated_y = []

async def main():
    # Clear any outstanding faults (with query to verify status if needed)
    await c1.set_stop(query=True)
    await c2.set_stop(query=True)

    global time_log, motor1_targets, motor2_targets, motor1_feedback, motor2_feedback
    time_log.clear()
    motor1_targets.clear()
    motor2_targets.clear()
    motor1_feedback.clear()
    motor2_feedback.clear()
    interpolated_x.clear()
    interpolated_y.clear()

    current_time = 0.0

    try:
        # Loop through the coordinates
        for i in range(len(coordinates) - 1):
            p1 = coordinates[i]
            p2 = coordinates[i + 1]

            # Determine how many interpolation steps
            num_steps = 200

            # Use the imported interpolate_coordinates function
            interpolated_points = await interpolate_coordinates(p1, p2, num_steps, mode="sinusoidal")

            for target_x, target_y in interpolated_points:
                # Store the interpolated coordinates for plotting
                interpolated_x.append(target_x)
                interpolated_y.append(target_y)

                # Compute inverse kinematics
                angles = await calculate_motor_positions(target_x, target_y)
                if angles is not None:
                    m1, m2 = angles

                    # Log target positions
                    time_log.append(current_time)
                    motor1_targets.append(m1)
                    motor2_targets.append(m2)

                    # Command the motors
                    result1 = await c1.set_position(
                        position=m1,
                        velocity_limit=velocity_limit,
                        accel_limit=acceleration,
                        kp_scale=kp,
                        kd_scale=kd,
                        watchdog_timeout=math.nan,
                        query=True  # Retrieve feedback
                    )
                    result2 = await c2.set_position(
                        position=m2,
                        velocity_limit=velocity_limit,
                        accel_limit=acceleration,
                        kp_scale=kp,
                        kd_scale=kd,
                        watchdog_timeout=math.nan,
                        query=True  # Retrieve feedback
                    )

                    # Log feedback positions (Key 1 is position in Moteus)
                    motor1_feedback.append(result1.values.get(1, 0))
                    motor2_feedback.append(result2.values.get(1, 0))

                # Update time and sleep so each segment lasts 'segment_time'
                time_per_step = 2 / (num_steps if num_steps > 0 else 1)
                current_time += time_per_step
                await asyncio.sleep(0.02)

        print("Completed one full loop of the square.")

    finally:
        # Ensure motors are stopped
        await c1.set_stop()
        await c2.set_stop()
        print("Cleaning up and stopping the motors.")

        # Plot the results
        plt.figure(figsize=(10, 6))

        # Plot motor targets and feedback positions
        plt.subplot(2, 1, 1)
        plt.plot(time_log, motor1_targets, label="Motor 1 Target", linestyle="--")
        plt.plot(time_log, motor2_targets, label="Motor 2 Target", linestyle="--")
        plt.plot(time_log, motor1_feedback, label="Motor 1 Feedback", alpha=0.7)
        plt.plot(time_log, motor2_feedback, label="Motor 2 Feedback", alpha=0.7)
        plt.xlabel("Time (s)")
        plt.ylabel("Motor Position (rev or rad)")
        plt.title("Motor Target vs Feedback Positions Over Time")
        plt.legend()
        plt.grid(True)

        # Plot the interpolated x and y coordinates
        plt.subplot(2, 1, 2)
        plt.plot(interpolated_x, interpolated_y, label="Interpolated Path", color="blue")
        plt.scatter(*zip(*coordinates), color="red", label="Waypoints", zorder=5)
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title("Interpolated X-Y Path")
        plt.legend()
        plt.grid(True)

        # Show the plots
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    asyncio.run(main())
