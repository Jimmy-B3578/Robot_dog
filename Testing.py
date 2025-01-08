import moteus
import math
import asyncio

# Initialize the controller
c1 = moteus.Controller(1)

# List of positions
ma = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

distance = 0.1
time = 1
velocity = distance / (time / 10)

async def main():

    # Move to the initial position and wait for completion
    await c1.set_position_wait_complete(position=ma[0], velocity_limit=10, accel_limit=10)
    try:
        for i, position in enumerate(ma):
            # Set the motor position and query feedback
            await c1.set_position(position=position,
                                  velocity=velocity,
                                  kd_scale=2,
                                  kp_scale=0.4,
                                  watchdog_timeout=math.nan,
                                  query=True)

            # Wait for 1 second before moving to the next position
            await asyncio.sleep((time / 10) * 1)
    finally:
        # Stop the motor after finishing
        await c1.set_stop()

if __name__ == '__main__':
    asyncio.run(main())