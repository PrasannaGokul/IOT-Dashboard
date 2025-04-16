import paho.mqtt.client as mqtt
import time
import random
import math
import json

# Device access tokens from ThingsBoard (replace with your actual tokens)
DEVICE_TOKENS = {
    "animal1": "YOUR_DEVICE_ACCESS_TOKEN_1",
    "animal2": "YOUR_DEVICE_ACCESS_TOKEN_2"
}

# ThingsBoard MQTT broker settings
THINGSBOARD_HOST = "demo.thingsboard.io"
THINGSBOARD_PORT = 1883

# Wildlife simulation parameters
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
        
        # Path pattern (0: random, 1: circular, 2: migration)
        self.movement_pattern = random.choice([0, 1, 2])
        self.movement_phase = 0
        
    def move(self):
        # Different movement patterns
        if self.movement_pattern == 0:  # Random movement
            self.direction += random.uniform(-30, 30)
            self.speed = random.uniform(0, 3)
        elif self.movement_pattern == 1:  # Circular pattern around home
            self.movement_phase += 0.05
            radius = self.range_km * 0.5  # km
            delta_lat = radius * math.sin(self.movement_phase) * 0.009
            delta_lon = radius * math.cos(self.movement_phase) * 0.009
            self.current_lat = self.home_lat + delta_lat
            self.current_lon = self.home_lon + delta_lon
            self.speed = random.uniform(1, 4)
            return
        elif self.movement_pattern == 2:  # Migration pattern
            self.movement_phase += 0.01
            # Generate a figure-8 pattern
            delta_lat = self.range_km * math.sin(self.movement_phase) * 0.009
            delta_lon = self.range_km * math.sin(2 * self.movement_phase) * 0.009
            self.current_lat = self.home_lat + delta_lat
            self.current_lon = self.home_lon + delta_lon
            self.speed = random.uniform(2, 7)
            return
            
        # Convert direction to radians
        dir_rad = math.radians(self.direction)
        
        # Calculate new position (approximate conversion of km to degrees)
        delta_lat = self.speed * math.cos(dir_rad) * 0.009  # ~1km = 0.009 degrees latitude
        delta_lon = self.speed * math.sin(dir_rad) * 0.009  # ~1km = 0.009 degrees longitude
        
        self.current_lat += delta_lat
        self.current_lon += delta_lon
        
        # Limit movement within range of home
        dist_from_home = math.sqrt(
            (self.current_lat - self.home_lat)**2 + 
            (self.current_lon - self.home_lon)**2
        )
        
        if dist_from_home > (self.range_km * 0.009):
            # If too far from home, turn back gradually
            self.direction = (math.degrees(math.atan2(
                self.home_lon - self.current_lon,
                self.home_lat - self.current_lat
            )) + random.uniform(-20, 20)) % 360
    
    def update_vitals(self):
        # Update activity based on speed
        if self.speed < 0.5:
            self.activity = "resting"
            self.heart_rate = random.randint(50, 70)
        elif self.speed < 2:
            self.activity = "foraging"
            self.heart_rate = random.randint(70, 90)
        else:
            self.activity = "moving"
            self.heart_rate = random.randint(90, 120)
            
        # Update body temperature with small variations
        self.body_temp += random.uniform(-0.2, 0.2)
        self.body_temp = max(36.0, min(39.0, self.body_temp))
    
    def get_telemetry(self):
        self.move()
        self.update_vitals()
        
        # Create telemetry data packet
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

# Initialize animal trackers
animals = {
    "animal1": AnimalTracker("Lion", 12.9716, 77.5946, range_km=8),  # Bangalore coordinates
    "animal2": AnimalTracker("Tiger", 12.9845, 77.6060, range_km=10)
}

# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc} for animal: {userdata}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published for animal: {userdata}")

# Create MQTT clients for each animal
clients = {}
for animal_id, token in DEVICE_TOKENS.items():
    client = mqtt.Client(userdata=animal_id)
    client.username_pw_set(token)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
    client.loop_start()
    clients[animal_id] = client

# Main simulation loop
try:
    while True:
        for animal_id, animal in animals.items():
            telemetry = animal.get_telemetry()
            
            # Convert to JSON
            payload = json.dumps(telemetry)
            
            # Publish to ThingsBoard
            clients[animal_id].publish("v1/devices/me/telemetry", payload)
            
            print(f"Published for {animal_id}: {payload}")
        
        # Wait 5 seconds before next update
        time.sleep(5)
        
except KeyboardInterrupt:
    # Stop all MQTT clients
    for client in clients.values():
        client.loop_stop()
        client.disconnect()
    print("Simulation stopped")
