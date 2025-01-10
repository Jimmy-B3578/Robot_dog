import asyncio
import pygame
import moteus
from Homing_sequence_function import home_motor
from ik_equations import calculate_motor_positions

x_scale_factor = 70
y_scale_factor = 70

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

            if joystick.get_button(1):
                await calculate_motor_positions(0, -50)

            else:
                await calculate_motor_positions(0, 0)

            # target_x = joystick.get_axis(2) * x_scale_factor
            # target_y = -joystick.get_axis(3) * y_scale_factor

            # Calculate joint angles function
            # await calculate_motor_positions(target_x, target_y)

            result1 = await c1.set_position(query=True)
            result2 = await c2.set_position(query=True)

            motor1_feedback.append(result1.values.get(1, 0))
            motor2_feedback.append(result2.values.get(1, 0))

            await asyncio.sleep(0.01)  # Small sleep interval for better performance

    finally:
        await c1.set_stop()
        await c2.set_stop()
        print("Cleaning up and stopping the motors.")

if __name__ == '__main__':
    asyncio.run(main())