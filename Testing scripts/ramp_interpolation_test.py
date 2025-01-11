from Xbox_controller.ramp import Ramp, LINEAR

import time


def main():
    # Create a Ramp object with an initial value of 0
    my_ramp = Ramp(0)

    # We'll ramp from 0 to 100 over 3000ms using CUBIC_IN
    my_ramp.go(100, 2000, LINEAR)

    # Keep updating until the ramp is finished
    while not my_ramp.isFinished():
        current_val = my_ramp.update()
        # completion = my_ramp.getCompletion()
        print(f"Value: {current_val:.2f}")  # , Completion: {completion:.2f}%")

        # Sleep for ~10ms so we don't spam the console
        time.sleep(0.01)

    print("Done!")


if __name__ == "__main__":
    main()