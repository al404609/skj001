from GUI import GUI
from HAL import HAL
import cv2 as cv
import math
import utm

# Constants
TAKEOFF_HEIGHT = 3
ANGLE = 0.6
NUM_VICTIMS = 5
DISTANCE_THR = 4.6
SPIRAL_INCLINATION = 0.175  # approx 10 Degrees in rads
SEARCH_MAX_DISTANCE = 50  # Meters

# Coordinates of the safety boat and known survivor location
BOAT_COORDINATES = (430492, 4459162)  # (x, y) in meters
SURVIVOR_COORDINATES = (430532, 4459132)  # (x, y) in meters

def calculate_relative_positions(boat_coords, survivor_coords):
    victims_x = boat_coords[1] - survivor_coords[1]  # Relative victims positions
    victims_y = boat_coords[0] - survivor_coords[0]  # Relative victims positions
    return victims_x, victims_y

def takeoff_drone(height):
    print("Taking off")
    HAL.takeoff(height)

def initialize_search():
    print("Drone ready: searching for victims")
    return True, False

def capture_images():
    return HAL.get_ventral_image(), HAL.get_frontal_image()

def detect_faces(image, face_cascade):
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray_image, 1.1, 4)
    return detected_faces

def move_to_position(target_x, target_y, height, angle):
    HAL.set_cmd_pos(target_x, target_y, height, angle)

def update_spiral_position(spiral_angle, distance_inclination, victims_x, victims_y):
    spiral_angle += SPIRAL_INCLINATION
    distance = (spiral_angle / (math.pi * 2)) * distance_inclination
    target_x = victims_x + distance * math.cos(spiral_angle)
    target_y = victims_y + distance * math.sin(spiral_angle)
    return target_x, target_y, spiral_angle

def is_in_position(target_x, target_y, current_x, current_y):
    sqr_distance_to_position = (target_x - current_x)**2 + (target_y - current_y)**2
    return sqr_distance_to_position < 1

face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
victims_x, victims_y = calculate_relative_positions(BOAT_COORDINATES, SURVIVOR_COORDINATES)

takeoff_drone(TAKEOFF_HEIGHT)

target_x, target_y = victims_x, victims_y
is_searching, is_in_position_flag = initialize_search()

victims_locations = []
spiral_angle = 0
distance_inclination = 0.98

while is_searching:
    ventral_img, frontal_img = capture_images()
    GUI.showImage(frontal_img)
    GUI.showLeftImage(ventral_img)
    
    current_position = HAL.get_position()
    current_x, current_y = current_position[0], current_position[1]
    move_to_position(target_x, target_y, TAKEOFF_HEIGHT, ANGLE)
    
    if is_in_position_flag:
        detected_faces = detect_faces(ventral_img, face_cascade)
        if detected_faces is not None:
            for _ in detected_faces:
                drone_location = HAL.get_position()
                victim_location = (drone_location[0], drone_location[1])
                
                if all((known_victim[0] - victim_location[0])**2 + (known_victim[1] - victim_location[1])**2 >= DISTANCE_THR**2 for known_victim in victims_locations):
                    victims_locations.append(victim_location)
                    print('Saved victim at location:', victim_location)
                    print('Saved victims:', len(victims_locations))
    
    target_x, target_y, spiral_angle = update_spiral_position(spiral_angle, distance_inclination, victims_x, victims_y)
    is_in_position_flag = is_in_position(target_x, target_y, current_x, current_y)
    is_searching = len(victims_locations) <= NUM_VICTIMS and spiral_angle * distance_inclination < SEARCH_MAX_DISTANCE

print("All victims saved. Returning to the boat.")
target_x, target_y = 0, 0
while not is_in_position(target_x, target_y, current_x, current_y):
    ventral_img, frontal_img = capture_images()
    GUI.showImage(frontal_img)
    GUI.showLeftImage(ventral_img)
    move_to_position(target_x, target_y, TAKEOFF_HEIGHT, ANGLE)
    current_position = HAL.get_position()
    current_x, current_y = current_position[0], current_position[1]

print("Landing drone")
HAL.land()
while HAL.get_landed_state() != 1:
    ventral_img, frontal_img = capture_images()
    GUI.showImage(frontal_img)
    GUI.showLeftImage(ventral_img)

print("Drone landed")
while True:
    pass
