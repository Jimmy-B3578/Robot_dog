import numpy as np
import math

async def interpolate_coordinates(start, end, num_points, mode="linear"):
    """
    Generates interpolated coordinates between start and end points with different modes.

    :param start: Tuple of (x, y) for the starting point.
    :param end: Tuple of (x, y) for the ending point.
    :param num_points: Number of points to interpolate, including start and end.
    :param mode: Interpolation mode - 'linear', 'exponential', or 'sinusoidal'.
    :return: List of interpolated points [(x1, y1), (x2, y2), ...].
    """
    if num_points < 2:
        raise ValueError("Number of points must be at least 2 to include start and end.")

    x_start, y_start = start
    x_end, y_end = end

    # Create interpolation parameter (t) from 0 to 1
    t = np.linspace(0, 1, num_points)

    if mode == "linear":
        x_points = np.linspace(x_start, x_end, num_points)
        y_points = np.linspace(y_start, y_end, num_points)

    elif mode == "exponential":
        t_exp = np.exp(t) - 1  # Exponential scaling
        t_exp /= t_exp[-1]  # Normalize to [0, 1]
        x_points = np.linspace(x_start, x_end, num_points)
        y_mid = (y_start + y_end) / 2
        amplitude = (y_end - y_start) / 2
        y_points = y_mid + amplitude * (np.exp(t_exp) - 1) / (np.exp(1) - 1)  # Exponential curve along Y

    elif mode == "sinusoidal":
        x_points = np.linspace(x_start, x_end, num_points)
        amplitude = (y_end - y_start) / 2  # Define amplitude based on y range
        y_mid = (y_start + y_end) / 2      # Midpoint for sinusoidal oscillation
        y_points = y_mid + amplitude * np.sin(t * math.pi)  # Sinusoidal variation

    else:
        raise ValueError("Invalid mode. Choose from 'linear', 'exponential', or 'sinusoidal'.")

    # Combine x and y points into a list of tuples
    return [(x, y) for x, y in zip(x_points, y_points)]
