import math

async def calculate_motor_positions(x1, y1, gear_reduction):
    # offsets
    x = x1 - 27.972
    y = y1 - 232.631

    # Link lengths in mm
    L1 = 150
    L2 = 180

    # Calculate theta2 using the law of cosines
    cos_theta2 = (x ** 2 + y ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
    cos_theta2 = max(min(cos_theta2, 1), -1)  # Clamp to valid range [-1, 1]
    theta2 = math.acos(cos_theta2)  # In radians

    # Calculate theta1
    phi = math.atan2(y, x)
    psi = math.atan2(L2 * math.sin(theta2), L1 + L2 * math.cos(theta2))
    theta1 = phi - psi

    # Convert adjusted angles to motor positions
    a1 = round(math.degrees(theta1) + 147.052, 3)
    a3 = 180 - math.degrees(theta2)
    a2 = round(90 - (-a1 + a3), 3)

    # adjust for gear ratio and motor controller
    m1 = a1 / 360 * gear_reduction
    m2 = a2 / 360 * gear_reduction

    return round(m1, 3), round(m2, 3)