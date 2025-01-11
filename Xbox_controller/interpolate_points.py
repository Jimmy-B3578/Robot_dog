from Xbox_controller.ramp import Ramp, LINEAR, ONCEFORWARD

myRampY = Ramp(0)
interpolationFlagY = 0
savedValueY = 0

myRampX = Ramp(0)
interpolationFlagX = 0
savedValueX = 0


def interpolation_y(input_val: int, duration: int) -> int:
    global interpolationFlagY, savedValueY, myRampY

    # Check for new data
    if input_val != savedValueY:
        interpolationFlagY = 0

    # Bookmark the old value
    savedValueY = input_val

    # If not yet ramping, initialize the ramp
    if interpolationFlagY == 0:
        myRampY.go(input_val, duration, LINEAR, ONCEFORWARD)
        interpolationFlagY = 1

    # Update and return the current ramp value
    output = myRampY.update()
    return int(output)  # cast to int if desired

def interpolation_x(input_val: int, duration: int) -> int:
    global interpolationFlagX, savedValueX, myRampX

    # Check for new data
    if input_val != savedValueX:
        interpolationFlagX = 0

    # Bookmark the old value
    savedValueX = input_val

    # If not yet ramping, initialize the ramp
    if interpolationFlagX == 0:
        myRampX.go(input_val, duration, LINEAR, ONCEFORWARD)
        interpolationFlagX = 1

    # Update and return the current ramp value
    output = myRampX.update()
    return int(output)  # cast to int if desired
