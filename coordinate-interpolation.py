import asyncio
import math
import moteus
import matplotlib.pyplot as plt
from ik_equations import calculate_motor_positions

# Scales for your coordinate system
x_scale_factor = 50
y_scale_factor = 50

# Velocity and acceleration parameters sent to Moteus
acceleration = 10
velocity = 3
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
    (1.0, 1.0),   # Top-right corner
    (1.0, -1.0),  # Bottom-right corner
    (-1.0, -1.0), # Bottom-left corner
    (-1.0, 1.0),  # Top-left corner
    (1.0, 1.0)    # Back to top-right corner to close the square
]

# Storage for motor target positions, feedback positions, and time
time_log = []
motor1_targets = []
motor2_targets = []
motor1_feedback = []
motor2_feedback = []

def smooth_interpolation(p1, p2, num_steps):
    """
    Generates (x, y) points between p1 and p2 using a sinusoidal easing function
    to smooth velocity over 'num_steps' steps. Now includes the final point.
    """
    x1, y1 = p1
    x2, y2 = p2

    # Calculate direction and distance
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)

    for step in range(num_steps + 1):  # +1 to ensure we include the final point
        t = step / num_steps if num_steps > 0 else 1.0
        # Sinusoidal (cosine) easing from 0 to 1
        smoothed_t = (1 - math.cos(math.pi * t)) / 2

        x_t = x1 + dx * smoothed_t
        y_t = y1 + dy * smoothed_t
        yield x_t, y_t, distance

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

    current_time = 0.0

    try:
        # Loop through the coordinates
        for i in range(len(coordinates) - 1):
            p1 = coordinates[i]
            p2 = coordinates[i + 1]

            # Calculate distance between the two points
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            distance = math.sqrt(dx**2 + dy**2)

            # Determine how many interpolation steps
            num_steps = max(10, int(distance * steps_scale))

            # Determine the total time to move this segment, scaled by distance
            segment_time = distance * time_per_unit_distance

            # Interpolate along p1->p2 with smoothing
            for target_x, target_y, _ in smooth_interpolation(p1, p2, num_steps):
                # Scale the coordinates for your mechanism
                target_x_scaled = target_x * x_scale_factor
                target_y_scaled = -target_y * y_scale_factor  # Y is inverted if needed

                # Compute inverse kinematics
                angles = await calculate_motor_positions(target_x_scaled, target_y_scaled)
                if angles is not None:
                    m1, m2 = angles

                    # Log target positions
                    time_log.append(current_time)
                    motor1_targets.append(m1)
                    motor2_targets.append(m2)

                    # Command the motors
                    result1 = await c1.set_position(
                        position=m1,
                        velocity=velocity,
                        accel_limit=acceleration,
                        kp_scale=kp,
                        kd_scale=kd,
                        watchdog_timeout=math.nan,
                        query=True  # Retrieve feedback
                    )
                    result2 = await c2.set_position(
                        position=m2,
                        velocity=velocity,
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
                time_per_step = segment_time / (num_steps if num_steps > 0 else 1)
                current_time += time_per_step
                await asyncio.sleep(time_per_step)

        print("Completed one full loop of the square.")

    finally:
        # Ensure motors are stopped
        await c1.set_stop()
        await c2.set_stop()
        print("Cleaning up and stopping the motors.")

        # Plot the results
        plt.figure(figsize=(10, 6))
        plt.plot(time_log, motor1_targets, label="Motor 1 Target", linestyle="--")
        plt.plot(time_log, motor2_targets, label="Motor 2 Target", linestyle="--")
        plt.plot(time_log, motor1_feedback, label="Motor 1 Feedback", alpha=0.7)
        plt.plot(time_log, motor2_feedback, label="Motor 2 Feedback", alpha=0.7)
        plt.xlabel("Time (s)")
        plt.ylabel("Motor Position (rev or rad)")
        plt.title("Motor Target vs Feedback Positions Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    asyncio.run(main())
