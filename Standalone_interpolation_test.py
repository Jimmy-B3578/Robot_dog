import moteus
import math
import asyncio
import matplotlib.pyplot as plt

# Initialize the controller
c1 = moteus.Controller(1)

# List of positions
ma = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

distance = 0.1
time = 1
velocity = distance / (time / 10)

# Lists to store time, calculated, and actual values
time_log = []
calculated_values = []
actual_values = []

async def main():
    global time_log, calculated_values, actual_values
    start_time = asyncio.get_event_loop().time()

    # Move to the initial position and wait for completion
    await c1.set_position_wait_complete(position=ma[0], velocity_limit=10, accel_limit=10)

    for i, position in enumerate(ma):
        elapsed_time = asyncio.get_event_loop().time() - start_time
        time_log.append(elapsed_time)

        # Append calculated value
        calculated_values.append(position)

        # Set the motor position and query feedback
        result = await c1.set_position(position=position,
                                       velocity=velocity,
                                       kd_scale=2,
                                       kp_scale=0.4,
                                       watchdog_timeout=math.nan,
                                       query=True)
        motor_feedback = result.values.get(1, 0)
        actual_values.append(motor_feedback)

        print(f"Time: {elapsed_time:.2f}s, Target: {position}, Feedback: {motor_feedback:.4f}")

        # Wait for 1 second before moving to the next position
        await asyncio.sleep((time / 10) * 1)

    # Stop the motor after finishing
    await c1.set_stop()

    # Plot the results
    plot_results()

def plot_results():
    plt.figure(figsize=(10, 6))
    plt.plot(time_log, calculated_values, label="Calculated Values", marker='o')
    plt.plot(time_log, actual_values, label="Actual Values", marker='x')
    plt.xlabel("Time (s)")
    plt.ylabel("Position")
    plt.title("Motor Position: Calculated vs Actual")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    asyncio.run(main())
