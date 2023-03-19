from dataclasses import dataclass
import math
import random
from global_land_mask import globe


@dataclass
class Coordinate:
    latitude: float
    longitude: float

    @classmethod
    def random_land_coordinate(cls):
        while True:
            latitude, longitude = _get_random_latitude_longitude()
            if globe.is_land(latitude, longitude):
                return cls(latitude, longitude)


def _get_random_latitude_longitude() -> tuple[float, float]:
    # radians to degrees Correction Factor
    cf = 180.0 / math.pi

    # angle with Equator - from +pi/2 to -pi/2
    radians_latitude = math.asin(2 * random.uniform(0.0, 1.0) - 1.0)
    # longitude in radians - from -pi to +pi
    radians_longitude = (2 * random.uniform(0.0, 1.0) - 1.0) * math.pi
    return round(radians_latitude * cf, 6), round(radians_longitude * cf, 6)
