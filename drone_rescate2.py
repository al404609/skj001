import GUI
import HAL
import utm
import cv2
import numpy as np

# Coordenadas del barco y víctimas
boat_lat = 40 + 16/60 + 48.2/3600
boat_long = 3 + 49/60 + 03.5/3600

victim_lat = 40 + 16/60 + 47.23/3600
victim_long = 3 + 49/60 + 01.78/3600

# Convertir coordenadas a UTM
coords_utm_boat = utm.from_latlon(boat_lat, boat_long)
coords_utm_victim = utm.from_latlon(victim_lat, victim_long)

# Calcular distancias
dist_y = coords_utm_victim[0] - coords_utm_boat[0]
dist_x = coords_utm_boat[1] - coords_utm_victim[1]
height = 3
angle = 0.6

def move_to_location(target_x, target_y, current_height):
    """
    Función para mover el dron a una ubicación específica
    """
    while not((target_x-1 < HAL.get_position()[0] < target_x+1) and
              (target_y-1 < HAL.get_position()[1] < target_y+1)):
        GUI.showImage(HAL.get_frontal_image())
        GUI.showLeftImage(HAL.get_ventral_image())
        HAL.set_cmd_pos(target_x, target_y, current_height, angle)

        x_pos = HAL.get_position()[0]
        y_pos = HAL.get_position()[1]
        print(f"Posición actual - X: {x_pos}, Y: {y_pos}")

def detect_victims(image):
    """
    Función para detectar víctimas usando clasificador de cascada
    """
    # Cargar clasificador de rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convertir imagen a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detectar rostros
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    return faces

def rescue_mission():
    """
    Función principal de misión de rescate
    """
    # Despegue
    HAL.takeoff(height)

    # Mover al punto de rescate
    move_to_location(dist_x, dist_y, height)

    # Número de víctimas a rescatar
    total_victims = 5
    rescued_victims = 0

    while rescued_victims < total_victims:
        # Capturar imagen frontal
        front_image = HAL.get_frontal_image()

        # Mostrar imágenes
        GUI.showImage(front_image)
        GUI.showLeftImage(HAL.get_ventral_image())

        # Detectar víctimas
        victims = detect_victims(front_image)

        # Marcar víctimas detectadas
        for (x, y, w, h) in victims:
            cv2.rectangle(front_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            rescued_victims += 1

        # Mostrar imagen con víctimas marcadas
        GUI.showImage(front_image)

        # Pequeña pausa para procesar
        HAL.sleep(1)

    # Volver al barco
    move_to_location(0, 0, height)

    # Aterrizar
    HAL.land()

# Ejecutar misión de rescate
rescue_mission()
while True:
