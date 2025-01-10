import asyncio
import moteus
import math

async def main():
    # Construct a default controller at id 1.
    c1 = moteus.Controller(1)
    c2 = moteus.Controller(2)

    await c1.set_position_wait_complete(position=0, accel_limit=10, watchdog_timeout=math.nan)
    await c2.set_position_wait_complete(position=0, accel_limit=10, watchdog_timeout=math.nan)

    await asyncio.sleep(1)

    await c1.set_stop()
    await c2.set_stop()

if __name__ == '__main__':
    asyncio.run(main())