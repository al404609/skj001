from GUI import GUI
from HAL import HAL
import cv2 as cv
import math
import utm

# Coordinates of the safety boat and known survivor location
boat_coordinates = (430492, 4459162)  # 40º16'48.2" N, 3º49'03.5" W approx in meters
survivor_coordinates = (430532, 4459132)  # 40º16'47.23" N, 3º49'01.78" W approx in meters

victims_x = boat_coordinates[1] - survivor_coordinates[1]  # Relative victims positions
victims_y = boat_coordinates[0] - survivor_coordinates[0]  # Relative victims positions
print("Victims position =: ", victims_x, "// y: ", victims_y)
boat_x = 0
boat_y = 0

takeoff_height = 3
angle = 0.6

face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

num_victims = 5  # n-1
saved_victims = 0
victims_locations = []

distance = 0  # Meters
distance_inclination = 0.98  # Meters
spiral_angle = 0  # rads
spiral_inclination = 0.175  # approx 10 Degrees in rads
search_max_distance = 50  # Meters

distance_thr = 4.6  # new victim distance threshold in meters

def takeoff_drone():
    print("Taking off")
    HAL.takeoff(takeoff_height)

def capture_and_show_images():
    ventral_img = HAL.get_ventral_image()
    frontal_img = HAL.get_frontal_image()
    GUI.showImage(frontal_img)
    GUI.showLeftImage(ventral_img)
    return ventral_img, frontal_img

def move_to_position(target_x, target_y):
    HAL.set_cmd_pos(target_x, target_y, takeoff_height, angle)

def search_victims(ventral_img):
    img_gray = cv.cvtColor(ventral_img, cv.COLOR_BGR2GRAY)
    for im_angle in range(0, 365, 10):
        (h, w) = img_gray.shape[:2]
        center = (w // 2, h // 2)
        M = cv.getRotationMatrix2D(center, im_angle, 1.0)
        im_rot = cv.warpAffine(img_gray, M, (w, h))
        detected_faces = face_cascade.detectMultiScale(im_rot, 1.1, 4)
        if len(detected_faces) > 0:
            for face in detected_faces:
                drone_location = HAL.get_position()
                victim_location = (drone_location[0], drone_location[1])
                if not any((known_victim[0] - victim_location[0])**2 + (known_victim[1] - victim_location[1])**2 < distance_thr**2 for known_victim in victims_locations):
                    victims_locations.append(victim_location)
                    print('saved victim +1 at location: ', victim_location)
                    print('saved victims: ', len(victims_locations))

takeoff_drone()

# Inicializamos la posición objetivo en la posición relativa de las víctimas
target_x = victims_x
target_y = victims_y
is_searching = True
is_in_position = False

while is_searching:
    ventral_img, frontal_img = capture_and_show_images()
    
    current_position = HAL.get_position()
    x_pos, y_pos = current_position[0], current_position[1]
    
    move_to_position(target_x, target_y)
    
    if is_in_position:
        search_victims(ventral_img)
        spiral_angle += spiral_inclination
        distance = (spiral_angle / (math.pi * 2)) * distance_inclination
        target_x = victims_x + distance * math.cos(spiral_angle)
        target_y = victims_y + distance * math.sin(spiral_angle)
    
    sqr_distance_to_position = (target_x - x_pos)**2 + (target_y - y_pos)**2
    is_in_position = (sqr_distance_to_position < 1)
    is_searching = (len(victims_locations) <= num_victims) and (distance < search_max_distance)

print("I think I have saved all victims!!!!!!")
target_x = boat_x
target_y = boat_y
is_in_position = False

while not is_in_position:
    ventral_img, frontal_img = capture_and_show_images()
    move_to_position(target_x, target_y)
    current_position = HAL.get_position()
    x_pos, y_pos = current_position[0], current_position[1]
    sqr_distance_to_position = (target_x - x_pos)**2 + (target_y - y_pos)**2
    is_in_position = (sqr_distance_to_position < 1)

print("Landing drone")
HAL.land()
while HAL.get_landed_state() != 1:
    ventral_img, frontal_img = capture_and_show_images()

print("Drone landed")
while True:
    pass
