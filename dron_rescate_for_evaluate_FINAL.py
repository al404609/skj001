from GUI import GUI
from HAL import HAL
import cv2 as cv
import math
import utm
#boat_lat = 40 + 16/60 + 48.2/3600
#boat_long = 3 + 49/60 + 03.5/3600

#victim_lat = 40 + 16/60 + 47.23/3600
#victim_long = 3 + 49/60 + 01.78/3600

# Convertir coordenadas a UTM
#coords_utm_boat = utm.from_latlon(boat_lat, boat_long)
#coords_utm_victim = utm.from_latlon(victim_lat, victim_long)

############## LO HE PASADO DIRECTAMENTE PQ SI LO PONÍA CON LOS MÉTODOS DE ARRIBA SE ME IBA HACIA EL SENTIDO OPUESTO############

# Coordinates of the safety boat and known survivor location
boat_coordinates = (430492, 4459162)  # 40º16'48.2" N, 3º49'03.5" W
survivor_coordinates = (430532, 4459132)  # 40º16'47.23" N, 3º49'01.78" W

victims_x = boat_coordinates[1] - survivor_coordinates[1]  # Relative victims positions
victims_y = boat_coordinates[0] - survivor_coordinates[0]  # Relative victims positions
print("Victims position =: ", victims_x, "// y: ", victims_y)
boat_x = 0
boat_y = 0

takeoff_height = 3
angle = 0.6

x_pos = HAL.get_position()[0]
y_pos = HAL.get_position()[1]

face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

num_victims = 6 
saved_victims = 0
victims_locations = []

distance = 0  # Meters
distance_inc = 0.98  # Meters
spiral_angle = 0     # rads
spiral_angle_inc = 0.175# aprox 10 Degrees en rads
search_max_distance = 50     # Meters

distance_thr = 4.6  # new victim distance threshold in meters

# Takeoff
print("Taking off")
HAL.takeoff(takeoff_height)

# Inicializamos la posición objetivo en la posición relativa de las víctimas
target_x = victims_x
target_y = victims_y

# Flags para controlar los bucles
print("Drone ready: searching for victims")
is_searching = True
is_in_position = False

while is_searching:
    # Capturamos imágenes de las dos cámaras
    ventral_img = HAL.get_ventral_image()
    frontal_img = HAL.get_frontal_image()
    
    # Mostramos en pantalla las imágenes
    GUI.showImage(frontal_img)
    GUI.showLeftImage(ventral_img)
    
    # Obtenemos la posición actual del dron
    x_pos = HAL.get_position()[0]
    y_pos = HAL.get_position()[1]
    
    # Enviamos comando para moverse a la ubicación objetivo
    HAL.set_cmd_pos(target_x, target_y, takeoff_height, angle)
    
    # Verificamos si estamos en posición
    if is_in_position:
        # Convertimos la imagen ventral a blanco y negro
        img_gray = cv.cvtColor(ventral_img, cv.COLOR_BGR2GRAY)
        
        # Se hace un barrido de 0 a 360° en saltos de 10°
        for im_angle in range(0, 365, 10):
            # Obtenemos el alto y ancho de la imagen
            (h, w) = img_gray.shape[:2]
            center = (w // 2, h // 2)
            
            # Generamos la matriz de rotación
            M = cv.getRotationMatrix2D(center, im_angle, 1.0)
            
            # Aplicamos la rotación
            im_rot = cv.warpAffine(img_gray, M, (w, h))
            
            # Detectamos rostros
            detected_faces = face_cascade.detectMultiScale(im_rot, 1.1, 4)
            
            # Si encontramos caras, verificamos si ya han sido guardados
            if len(detected_faces) > 0:
                for face in detected_faces:
                    drone_location = HAL.get_position()
                    _drone_orientation = HAL.get_orientation()  # No se usa directamente, pero lo dejamos como referencia
                    
                    victim_location = (drone_location[0], drone_location[1])
                    
                    # Verificamos si la víctima ya está en la lista, comparando distancias
                    already_saved = False
                    for known_victim in victims_locations:
                        sqr_distance = (known_victim[0] - victim_location[0])**2 + (known_victim[1] - victim_location[1])**2
                        if sqr_distance < distance_thr**2:
                            # Ya existe una víctima en una ubicación cercana, la ignoramos
                            already_saved = True
                            break
                    
                    # Si no estaba guardada, la añadimos
                    if not already_saved:
                        victims_locations.append(victim_location)
                        print('saved victim +1 at location: ', victim_location)
                        print('saved victims: ', len(victims_locations))
        
        # Incrementamos el ángulo de la espiral
        spiral_angle += spiral_angle_inc
        # Actualizamos la distancia a recorrer en la espiral
        distance = (spiral_angle / (math.pi * 2)) * distance_inc
        # Calculamos la nueva ubicación objetivo
        target_x = victims_x + distance * math.cos(spiral_angle)
        target_y = victims_y + distance * math.sin(spiral_angle)
    
    # obtenemos y comprobamos si la dist < thr
    sqr_distance_to_position = (target_x - x_pos)**2 + (target_y - y_pos)**2
    is_in_position = (sqr_distance_to_position < 1)
    
    # Actualizamos la condición de búsqueda
    is_searching = (len(victims_locations) <= num_victims) and (distance < search_max_distance)

# se vuelve al origen
print("I think I have saved all victims!!!!!!")
target_x = boat_x
target_y = boat_y
is_in_position = False

while not is_in_position:
    # Obtenemos imágenes de las dos cámaras
    ventral_img = HAL.get_ventral_image()
    frontal_img = HAL.get_frontal_image()
    
    # Mostramos imágenes
    GUI.showImage(frontal_img)
    GUI.showLeftImage(ventral_img)
    
    # Vuelve el dron a origen
    HAL.set_cmd_pos(target_x, target_y, takeoff_height, angle)
    
    # Verificamos si llegamos
    x_pos = HAL.get_position()[0]
    y_pos = HAL.get_position()[1]
    sqr_distance_to_position = (target_x - x_pos)**2 + (target_y - y_pos)**2
    is_in_position = (sqr_distance_to_position < 1)

# Aterrizamos
print("Landing drone")
is_landed = False
while not is_landed:
    ventral_img = HAL.get_ventral_image()
    frontal_img = HAL.get_frontal_image()
    GUI.showImage(frontal_img)
    GUI.showLeftImage(ventral_img)
    HAL.land()
    is_landed = (HAL.get_landed_state() == 1)

print("Drone landed")
while True:
    pass
