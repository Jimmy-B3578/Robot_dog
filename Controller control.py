import asyncio
import pygame
import moteus
from Homing_sequence_function import home_motor
from ik_equations import calculate_motor_positions

x_scale_factor = 120
y_scale_factor = 70
acceleration = 10
velocity = 1
torque_v = 0.5
reduction_ratio = 6

c1 = moteus.Controller(1)
c2 = moteus.Controller(2)

async def main():
    # Clear any outstanding faults
    await c1.set_stop()
    await c2.set_stop()

    try:
        while True:
            # Initialize Pygame and the joystick
            pygame.init()
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            pygame.event.pump()

            # Exit the loop if button 0 is pressed
            if joystick.get_button(2):
                print("Button 0 pressed. Stopping motor...")
                break

            # Homing sequence for motors
            if joystick.get_button(4):
                await c1.set_stop()
                await asyncio.sleep(0.5)
                await home_motor(c2)

            if joystick.get_button(5):
                await c2.set_stop()
                await asyncio.sleep(0.5)
                await home_motor(c1)

            target_x = joystick.get_axis(2) * x_scale_factor
            target_y = -joystick.get_axis(3) * y_scale_factor

            # Calculate joint angles function
            angles = await calculate_motor_positions(target_x, target_y, reduction_ratio)
            if angles is not None:
                m1, m2 = angles

                # Command the motors to the calculated positions
                await c1.set_position(position=m1, velocity_limit=velocity, accel_limit=acceleration, maximum_torque=torque_v, query=True)
                await c2.set_position(position=m2, velocity_limit=velocity, accel_limit=acceleration, maximum_torque=torque_v, query=True)

            await asyncio.sleep(0.02)  # Small sleep interval for better performance

    finally:
        await c1.set_stop()
        await c2.set_stop()
        print("Cleaning up and stopping the motors.")

if __name__ == '__main__':
    asyncio.run(main())