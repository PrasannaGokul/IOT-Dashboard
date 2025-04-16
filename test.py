import json
import math
import random
from time import sleep

# Import your simulation classes here.
# If your AnimalTracker class is defined in a file, for example, animal_sim.py,
# make sure to adjust the import below:
# from animal_sim import AnimalTracker

# For demonstration, here is the definition of the AnimalTracker class extracted from your code.
# You might want to import it instead.

class AnimalTracker:
    def __init__(self, animal_id, home_lat, home_lon, range_km=5):
        self.animal_id = animal_id
        self.home_lat = home_lat
        self.home_lon = home_lon
        self.range_km = range_km
        self.current_lat = home_lat
        self.current_lon = home_lon
        self.speed = 0
        self.direction = random.randint(0, 360)
        self.heart_rate = random.randint(50, 80)
        self.body_temp = random.uniform(36.5, 38.5)
        self.activity = "resting"
        self.movement_pattern = random.choice([0, 1, 2])
        self.movement_phase = 0

    def move(self):
        if self.movement_pattern == 0:  # Random movement
            self.direction += random.uniform(-30, 30)
            self.speed = random.uniform(0, 3)
        elif self.movement_pattern == 1:  # Circular pattern around home
            self.movement_phase += 0.05
            radius = self.range_km * 0.5
            delta_lat = radius * math.sin(self.movement_phase) * 0.009
            delta_lon = radius * math.cos(self.movement_phase) * 0.009
            self.current_lat = self.home_lat + delta_lat
            self.current_lon = self.home_lon + delta_lon
            self.speed = random.uniform(1, 4)
            return
        elif self.movement_pattern == 2:  # Migration pattern
            self.movement_phase += 0.01
            delta_lat = self.range_km * math.sin(self.movement_phase) * 0.009
            delta_lon = self.range_km * math.sin(2 * self.movement_phase) * 0.009
            self.current_lat = self.home_lat + delta_lat
            self.current_lon = self.home_lon + delta_lon
            self.speed = random.uniform(2, 7)
            return

        # Convert direction to radians
        dir_rad = math.radians(self.direction)
        # Calculate new position (approximate conversion of km to degrees)
        delta_lat = self.speed * math.cos(dir_rad) * 0.009
        delta_lon = self.speed * math.sin(dir_rad) * 0.009
        self.current_lat += delta_lat
        self.current_lon += delta_lon

        # Keep animal within the allowed range of home
        dist_from_home = math.sqrt(
            (self.current_lat - self.home_lat) ** 2 +
            (self.current_lon - self.home_lon) ** 2
        )
        if dist_from_home > (self.range_km * 0.009):
            self.direction = (math.degrees(math.atan2(
                self.home_lon - self.current_lon,
                self.home_lat - self.current_lat)) + random.uniform(-20, 20)) % 360

    def update_vitals(self):
        if self.speed < 0.5:
            self.activity = "resting"
            self.heart_rate = random.randint(50, 70)
        elif self.speed < 2:
            self.activity = "foraging"
            self.heart_rate = random.randint(70, 90)
        else:
            self.activity = "moving"
            self.heart_rate = random.randint(90, 120)

        self.body_temp += random.uniform(-0.2, 0.2)
        self.body_temp = max(36.0, min(39.0, self.body_temp))

    def get_telemetry(self):
        self.move()
        self.update_vitals()
        return {
            "latitude": self.current_lat,
            "longitude": self.current_lon,
            "speed": round(self.speed, 2),
            "direction": round(self.direction),
            "heart_rate": self.heart_rate,
            "body_temp": round(self.body_temp, 1),
            "activity": self.activity,
            "battery": random.randint(60, 100)
        }

def run_test():
    # Initialize an AnimalTracker object (using arbitrary sample coordinates)
    tracker = AnimalTracker("TestAnimal", 12.9716, 77.5946, range_km=5)
    
    # Get telemetry data and validate the keys and basic value types
    telemetry = tracker.get_telemetry()
    required_keys = [
        "latitude", "longitude", "speed",
        "direction", "heart_rate", "body_temp",
        "activity", "battery"
    ]
    
    missing_keys = [key for key in required_keys if key not in telemetry]
    if missing_keys:
        raise AssertionError(f"Missing telemetry keys: {missing_keys}")
    
    # Check that numeric values are numbers
    for key in ["latitude", "longitude", "speed", "direction", "heart_rate", "body_temp", "battery"]:
        if not isinstance(telemetry[key], (int, float)):
            raise AssertionError(f"Telemetry key '{key}' is not numeric: {telemetry[key]}")
    
    # Check that activity is a non-empty string
    if not isinstance(telemetry["activity"], str) or not telemetry["activity"]:
        raise AssertionError("Telemetry 'activity' is invalid.")
    
    print("Telemetry test passed")
    # Optionally, print the telemetry payload as json
    print("Telemetry payload:", json.dumps(telemetry, indent=2))

if __name__ == '__main__':
    # Run the test; any AssertionError will cause the action to fail.
    run_test()
