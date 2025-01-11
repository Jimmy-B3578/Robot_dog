import asyncio
import moteus


async def find_limit(controller, direction, torque_limit, resistance_threshold=0.8):
    """
    Moves the motor in the specified direction with low torque until resistance is detected.
    Returns the position where the resistance was encountered.
    """
    print(f"Starting to find limit in direction: {direction}")
    position = None

    try:
        while True:
            # Send command to move the motor
            result = await controller.set_position(
                position=float('nan'),  # Free position control
                velocity=direction * 1,  # Small constant velocity
                maximum_torque=torque_limit,  # Torque limit
                query=True,  # Request feedback
            )

            # Extract feedback values
            torque = result.values.get(3, 0)  # Torque corresponds to key 3
            current_position = result.values.get(1, 0)  # Position corresponds to key 1

            print(f"Position: {current_position:.4f}, Torque: {torque:.4f}")

            # Check for resistance based on the torque
            if abs(torque) > torque_limit * resistance_threshold:
                print("Resistance encountered!")
                position = current_position
                break

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Stop the motor after the loop completes or is interrupted
        await controller.set_stop()
        await asyncio.sleep(0.5)

    return position


async def main():
    # Initialize the Moteus controller
    controller = moteus.Controller()

    # Define parameters
    torque_limit = 0.2  # Low torque value
    resistance_threshold = 0.6  # Proportion of torque limit to detect resistance

    # Set stop to clear any existing errors
    await controller.set_stop()
    await asyncio.sleep(0.5)  # Give it time to stop

    # Finding positive limit
    print("Finding positive limit...")
    pos_limit = await find_limit(controller, direction=1, torque_limit=torque_limit,
                                 resistance_threshold=resistance_threshold)

    # Finding negative limit
    print("Finding negative limit...")
    neg_limit = await find_limit(controller, direction=-1, torque_limit=torque_limit,
                                 resistance_threshold=resistance_threshold)

    if pos_limit is not None and neg_limit is not None:
        # Print the positions found
        print(f"Positive Limit: {pos_limit:.4f}")
        print(f"Negative Limit: {neg_limit:.4f}")

        # Calculate the difference between the two positions
        position_difference = pos_limit - neg_limit
        print(f"Position Difference: {position_difference:.4f}")

        # Move to midpoint using set_position_wait_complete
        midpoint = (pos_limit + neg_limit) / 2
        print(f"Midpoint calculated: {midpoint:.4f}")
        print("Moving motor to midpoint...")
        await controller.set_position_wait_complete(position=midpoint, query=True)
        print("Motor at midpoint.")
        await controller.set_stop()

        # set the zero position at the mid point
        await controller.set_output_exact()

        # Find the gear ratio
        gearratio = (position_difference * 360) / 140
        print(f"Gear ratio: {gearratio:.4f}")
    else:
        print("Failed to determine limits.")


# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())