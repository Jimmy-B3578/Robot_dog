from ramp import Ramp, LINEAR, ONCEFORWARD

myRampZ = Ramp(0)
interpolationFlagZ = 0
savedValueZ = 0


def interpolation_y(input_val: int, duration: int) -> int:
    global interpolationFlagZ, savedValueZ, myRampZ

    # Check for new data
    if input_val != savedValueZ:
        interpolationFlagZ = 0

    # Bookmark the old value
    savedValueZ = input_val

    # If not yet ramping, initialize the ramp
    if interpolationFlagZ == 0:
        myRampZ.go(input_val, duration, LINEAR, ONCEFORWARD)
        interpolationFlagZ = 1

    # Update and return the current ramp value
    output = myRampZ.update()
    return int(output)  # cast to int if desired
