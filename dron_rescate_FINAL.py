import GUI
import HAL
import utm
import cv2
import numpy as np

# Coordenadas de referencia
lat_barco = 40 + 16/60 + 48.2/3600
lon_barco = 3 + 49/60 + 3.5/3600

lat_persona = 40 + 16/60 + 47.23/3600
lon_persona = 3 + 49/60 + 1.78/3600

# Conversión a UTM
utm_barco = utm.from_latlon(lat_barco, lon_barco)
utm_persona = utm.from_latlon(lat_persona, lon_persona)

# Cálculo de distancias en el plano UTM
dif_y = utm_persona[0] - utm_barco[0]
dif_x = utm_barco[1] - utm_persona[1]

# Parámetros de vuelo
altura_vuelo = 3
angulo_rumbo = 0.6

def navegar_hasta_objetivo(obj_x, obj_y, altura):
    """
    Desplaza el dron hasta la posición objetivo
    """
    while not (obj_x - 1 < HAL.get_position()[0] < obj_x + 1 and
               obj_y - 1 < HAL.get_position()[1] < obj_y + 1):
        
        # Se muestran las imágenes disponibles
        GUI.showImage(HAL.get_frontal_image())
        GUI.showLeftImage(HAL.get_ventral_image())
        
        # Se ordena al dron desplazarse
        HAL.set_cmd_pos(obj_x, obj_y, altura, angulo_rumbo)
        
        # Reporte de posición actual
        actual_x, actual_y = HAL.get_position()[0], HAL.get_position()[1]
        print(f"Posición actual -> X: {actual_x}, Y: {actual_y}")

def buscar_rostros(imagen):
    """
    Localiza rostros en la imagen usando un clasificador en cascada
    """
    clasificador_rostro = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    rostros_detectados = clasificador_rostro.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return rostros_detectados

def mision_busqueda_rescate():
    """
    Control principal de la misión de búsqueda y rescate
    """
    # Inicio (despegue)
    HAL.takeoff(altura_vuelo)

    # Navegar hacia la zona de rescate
    navegar_hasta_objetivo(dif_x, dif_y, altura_vuelo)

    # Cantidad de víctimas objetivo
    victimas_objetivo = 5 # reducida 1 por el index
    conteo_victimas = 0

    while conteo_victimas < victimas_objetivo:
        # Obtenemos la imagen frontal
        imagen_frontal = HAL.get_frontal_image()

        # Se muestran las imágenes en pantalla
        GUI.showImage(imagen_frontal)
        GUI.showLeftImage(HAL.get_ventral_image())

        # Se buscan rostros (víctimas)
        encontrados = buscar_rostros(imagen_frontal)

        # Dibujar rectángulos en cada rostro detectado
        for (x, y, w, h) in encontrados:
            cv2.rectangle(imagen_frontal, (x, y), (x + w, y + h), (0, 255, 0), 2)
            conteo_victimas += 1

        # Mostrar la imagen con detecciones
        GUI.showImage(imagen_frontal)

        # Pausa breve para permitir procesamiento
        HAL.sleep(1)

    # Regreso al punto de partida (barco)
    navegar_hasta_objetivo(0, 0, altura_vuelo)

    # Aterrizaje
    HAL.land()

# Se ejecuta la misión
mision_busqueda_rescate()

# Bucle permanente (importante dejarlo al final)
while True:
    pass
