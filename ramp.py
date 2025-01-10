import time
import math


# ----------------------------------------------------------------
# Helper function to replicate Arduino's millis() in Python
# (returns milliseconds as an integer).
# ----------------------------------------------------------------
def millis():
    return int(time.time() * 1000)


# ----------------------------------------------------------------
# Enums (translated as integer constants or Python Enums).
# For simplicity, we’ll use integer constants here.
# ----------------------------------------------------------------
NONE = 0x00
LINEAR = 0x01
QUADRATIC_IN = 0x02
QUADRATIC_OUT = 0x03
QUADRATIC_INOUT = 0x04
CUBIC_IN = 0x05
CUBIC_OUT = 0x06
CUBIC_INOUT = 0x07
QUARTIC_IN = 0x08
QUARTIC_OUT = 0x09
QUARTIC_INOUT = 0x0A
QUINTIC_IN = 0x0B
QUINTIC_OUT = 0x0C
QUINTIC_INOUT = 0x0D
SINUSOIDAL_IN = 0x0E
SINUSOIDAL_OUT = 0x0F
SINUSOIDAL_INOUT = 0x10
EXPONENTIAL_IN = 0x11
EXPONENTIAL_OUT = 0x12
EXPONENTIAL_INOUT = 0x13
CIRCULAR_IN = 0x14
CIRCULAR_OUT = 0x15
CIRCULAR_INOUT = 0x16
ELASTIC_IN = 0x17
ELASTIC_OUT = 0x18
ELASTIC_INOUT = 0x19
BACK_IN = 0x1A
BACK_OUT = 0x1B
BACK_INOUT = 0x1C
BOUNCE_IN = 0x1D
BOUNCE_OUT = 0x1E
BOUNCE_INOUT = 0x1F

FORWARD = 0x00
BACKWARD = 0x01

ONCEFORWARD = 0x00
LOOPFORWARD = 0x01
FORTHANDBACK = 0x02
ONCEBACKWARD = 0x03
LOOPBACKWARD = 0x04
BACKANDFORTH = 0x05


# ----------------------------------------------------------------
# Generic functions (translated from C++ to Python).
# ----------------------------------------------------------------

def powin(k: float, p: int) -> float:
    return k ** p


def powout(k: float, p: int) -> float:
    return 1.0 - (1.0 - k) ** p


def powinout(k: float, p: int) -> float:
    k2 = k * 2.0
    if k2 < 1:
        return 0.5 * (k2 ** p)
    return 1.0 - 0.5 * abs((2 - k2) ** p)


def ramp_calc(k: float, m: int) -> float:
    """
    Replicates the switch-case ramp_mode logic from the Arduino code.
    """
    # Edge conditions
    if k == 0.0 or k == 1.0:
        return k

    # We reuse the same variable names a, p, s
    a = 0.0
    p = 0.0
    s = 0.0

    if m == QUADRATIC_IN:
        return powin(k, 2)
    elif m == QUADRATIC_OUT:
        return powout(k, 2)
    elif m == QUADRATIC_INOUT:
        return powinout(k, 2)
    elif m == CUBIC_IN:
        return powin(k, 3)
    elif m == CUBIC_OUT:
        return powout(k, 3)
    elif m == CUBIC_INOUT:
        return powinout(k, 3)
    elif m == QUARTIC_IN:
        return powin(k, 4)
    elif m == QUARTIC_OUT:
        return powout(k, 4)
    elif m == QUARTIC_INOUT:
        return powinout(k, 4)
    elif m == QUINTIC_IN:
        return powin(k, 5)
    elif m == QUINTIC_OUT:
        return powout(k, 5)
    elif m == QUINTIC_INOUT:
        return powinout(k, 5)
    elif m == SINUSOIDAL_IN:
        return 1.0 - math.cos(k * (math.pi / 2.0))
    elif m == SINUSOIDAL_OUT:
        return math.sin(k * (math.pi / 2.0))
    elif m == SINUSOIDAL_INOUT:
        return -0.5 * (math.cos(math.pi * k) - 1.0)
    elif m == EXPONENTIAL_IN:
        return (2.0 ** (10.0 * (k - 1.0)))
    elif m == EXPONENTIAL_OUT:
        return 1.0 - (2.0 ** (-10.0 * k))
    elif m == EXPONENTIAL_INOUT:
        k2 = k * 2.0
        if k2 < 1.0:
            return 0.5 * (2.0 ** (10.0 * (k2 - 1.0)))
        return 0.5 * (2.0 - (2.0 ** (-10.0 * (k2 - 1.0))))
    elif m == CIRCULAR_IN:
        return -(math.sqrt(1.0 - k * k) - 1.0)
    elif m == CIRCULAR_OUT:
        k2 = k - 1.0
        return math.sqrt(1.0 - k2 * k2)
    elif m == CIRCULAR_INOUT:
        k2 = k * 2.0
        if k2 < 1.0:
            return -0.5 * (math.sqrt(1.0 - k2 * k2) - 1.0)
        k3 = k2 - 2.0
        return 0.5 * (math.sqrt(1.0 - k3 * k3) + 1.0)
    elif m == ELASTIC_IN:
        a = 1.0
        p = 0.3 * 1.5
        s = p * math.asin(1.0 / a) / (2.0 * math.pi)
        k2 = k - 1.0
        return -(a * (2.0 ** (10.0 * k2)) * math.sin((k2 - s) * (2.0 * math.pi) / p))
    elif m == ELASTIC_OUT:
        a = 1.0
        p = 0.3
        s = p * math.asin(1.0 / a) / (2.0 * math.pi)
        return a * (2.0 ** (-10.0 * k)) * math.sin((k - s) * (2.0 * math.pi) / p) + 1.0
    elif m == ELASTIC_INOUT:
        a = 1.0
        p = 0.3 * 1.5
        s = p * math.asin(1.0 / a) / (2.0 * math.pi)
        k2 = 2.0 * k - 1.0
        if k2 < 0.0:
            return -0.5 * (a * (2.0 ** (10.0 * k2)) * math.sin((k2 - s) * (2.0 * math.pi) / p))
        return 0.5 * a * (2.0 ** (-10.0 * k2)) * math.sin((k2 - s) * (2.0 * math.pi) / p) + 1.0
    elif m == BACK_IN:
        s = 1.70158
        return k * k * ((s + 1.0) * k - s)
    elif m == BACK_OUT:
        s = 1.70158
        k2 = k - 1.0
        return k2 * k2 * ((s + 1.0) * k2 + s) + 1.0
    elif m == BACK_INOUT:
        s = 1.70158
        s *= 1.525
        k2 = k * 2.0
        if k2 < 1.0:
            return 0.5 * (k2 * k2 * ((s + 1.0) * k2 - s))
        k2 -= 2.0
        return 0.5 * (k2 * k2 * ((s + 1.0) * k2 + s) + 2.0)
    elif m == BOUNCE_IN:
        return 1.0 - ramp_calc(1.0 - k, BOUNCE_OUT)
    elif m == BOUNCE_OUT:
        if k < (1.0 / 2.75):
            return 7.5625 * k * k
        elif k < (2.0 / 2.75):
            k2 = k - (1.5 / 2.75)
            return 7.5625 * k2 * k2 + 0.75
        elif k < (2.5 / 2.75):
            k2 = k - (2.25 / 2.75)
            return 7.5625 * k2 * k2 + 0.9375
        else:
            k2 = k - (2.625 / 2.75)
            return 7.5625 * k2 * k2 + 0.984375
    elif m == BOUNCE_INOUT:
        if k < 0.5:
            return ramp_calc(k * 2.0, BOUNCE_IN) * 0.5
        return ramp_calc(k * 2.0 - 1.0, BOUNCE_OUT) * 0.5 + 0.5

    # Default: LINEAR
    return k


# ----------------------------------------------------------------
# Python class that replicates the template <class T> _ramp in C++.
# In Python, we'll just store values as floats (or the same type
# passed by the user, but Python is dynamically typed anyway).
# ----------------------------------------------------------------
class Ramp:
    def __init__(self, initial_value=0):
        self.init(initial_value)

    def init(self, _val):
        self.A = float(_val)  # origin
        self.B = float(_val)  # target
        self.val = float(_val)  # current ramped value
        self.mode = NONE
        self.t = millis()
        self.dur = 0
        self.pos = 0
        self.grain = 10
        self.loop = ONCEFORWARD
        self.speed = FORWARD
        self.paused = False
        self.automated = True

    def update(self):
        doUpdate = True
        newTime = 0
        delta = self.grain

        # If in automated mode, only update if enough time (>= grain) has passed
        if self.automated:
            newTime = millis()
            delta = newTime - self.t
            doUpdate = (delta >= self.grain)

        if self.mode != NONE and doUpdate:
            self.t = newTime

            # If finished, handle loop logic
            if self.isFinished():
                if self.loop == LOOPFORWARD:
                    self.pos = 0
                elif self.loop == LOOPBACKWARD:
                    self.pos = self.dur
                elif self.loop == FORTHANDBACK or self.loop == BACKANDFORTH:
                    if self.speed == FORWARD:
                        self.speed = BACKWARD
                    else:
                        self.speed = FORWARD
                # ONCEFORWARD, ONCEBACKWARD or defaults do nothing special

            if not self.paused:
                # Update position
                if self.speed == FORWARD:
                    if (self.pos + delta) < self.dur:
                        self.pos += delta
                    else:
                        self.pos = self.dur
                elif self.speed == BACKWARD:
                    if (self.pos - delta) > 0:
                        self.pos -= delta
                    else:
                        self.pos = 0

                # Recompute value
                if (self.mode != NONE) and (self.dur > 0) and (self.A != self.B):
                    k = float(self.pos) / float(self.dur)
                    # If B >= A, we ramp up; otherwise we ramp down
                    if self.B >= self.A:
                        self.val = self.A + (self.B - self.A) * ramp_calc(k, self.mode)
                    else:
                        self.val = self.A - (self.A - self.B) * ramp_calc(k, self.mode)
                else:
                    # If no duration or same values, just set final
                    self.val = self.B

        return self.val

    # ----------------------------------------------------------------
    # go(...) methods - in Python we implement with default arguments.
    # The original code has multiple overloads; we replicate by
    # setting default parameters in one method.
    # ----------------------------------------------------------------
    def go(self, _val, _dur=0, _mode=NONE, _loop=ONCEFORWARD):
        # Match the logic from the C++ code
        self.A = self.val
        self.B = float(_val)
        self.mode = _mode
        self.dur = _dur
        self.t = millis()

        if _dur == 0:
            self.val = self.B

        if _loop < ONCEBACKWARD:
            self.pos = 0
            self.speed = FORWARD
        else:
            self.pos = self.dur
            self.speed = BACKWARD

        self.loop = _loop
        self.paused = False
        return self.val

    # ----------------------------------------------------------------
    # Pause / Resume
    # ----------------------------------------------------------------
    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    # ----------------------------------------------------------------
    # State checks
    # ----------------------------------------------------------------
    def isFinished(self):
        """
        True if (pos == dur in forward mode) OR (pos == 0 in backward mode).
        """
        if self.speed == FORWARD:
            return (self.pos == self.dur)
        if self.speed == BACKWARD:
            return (self.pos == 0)
        return False

    def isRunning(self):
        """
        True if not finished and not paused.
        """
        return (not self.isFinished() and not self.paused)

    def isPaused(self):
        """
        Note: The original C++ code returns `(!paused)` which
        seems counterintuitive for "isPaused" name.
        We replicate it exactly.
        """
        return (not self.paused)  # EXACT replication of the original logic

    # ----------------------------------------------------------------
    # Setters
    # ----------------------------------------------------------------
    def setGrain(self, _grain):
        self.grain = _grain

    def setAutomation(self, _automated):
        self.automated = _automated

    # ----------------------------------------------------------------
    # Getters
    # ----------------------------------------------------------------
    def getCompletion(self):
        if self.dur == 0:
            return 100.0 if self.isFinished() else 0.0
        val = (self.pos * 10000.0) / self.dur
        return val / 100.0

    def getDuration(self):
        return self.dur

    def getPosition(self):
        return self.pos

    def getValue(self):
        return self.val

    def getOrigin(self):
        return self.A

    def getTarget(self):
        return self.B


# ----------------------------------------------------------------
# Class aliasing (optional in Python; you can just use `Ramp`).
# In C++ you had typedefs. In Python, you can simply do:
# ----------------------------------------------------------------
ramp = Ramp
rampByte = Ramp
rampUnsignedChar = Ramp
rampChar = Ramp
rampInt = Ramp
rampUnsignedInt = Ramp
rampLong = Ramp
rampUnsignedLong = Ramp
rampFloat = Ramp
rampDouble = Ramp
