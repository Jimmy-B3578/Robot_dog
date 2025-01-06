import math
import asyncio
import numpy as np
from ik_equations import calculate_motor_positions

Overall_time = 2

array = [0.1, 0.2, 0.3, 0.4, 0.5, 0.55, 0.58, 0.6, 0.61, 0.62, 0.63, 0.64, 0.65]


async def main():
    time = round(Overall_time / (len(array) - 1), 3)

    for i in range(len(array) - 1):
        f = array[i]
        n = array[i + 1]
        d = round(n - f, 5)

        velocity = round(d / time, 2)

        print(f"Current: {f}")
        print(f"Difference: {d}")
        print(f"Target: {n}")
        print(f"Time in seconds: {time}")
        print(f"Velocity: {velocity}")
        print()  # For better readability

        await asyncio.sleep(time)

if __name__ == '__main__':
    asyncio.run(main())
