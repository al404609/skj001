import GUI
import HAL
import cv2

# Configuración del controlador proporcional
Kp = 0.01

i = 0
while True:
    # Obtener imagen de la cámara
    img = HAL.getImage()

    # Convertir la imagen a HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Crear una máscara para el color rojo (ajustar estos valores dependiendo del color de la línea)
    red_mask = cv2.inRange(hsv, (0, 125, 125), (30, 255, 255))

    # Encontrar contornos de la línea
    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Si hay contornos, calcular el centro de masa
    if contours:
        M = cv2.moments(contours[0])
        if M["m00"] != 0:
            cX = M["m10"] / M["m00"]
            cY = M["m01"] / M["m00"]
        else:
            cX, cY = 0, 0
    else:
        cX, cY = 0, 0

    # Calcular el error respecto al centro de la imagen (320 en una imagen 640x480)
    if cX > 0:
        error = 320 - cX  # Error entre el centro de la imagen y la posición del centro de masa
        # Aplicar la constante proporcional para ajustar la velocidad angular
        HAL.setV(4)  # Velocidad constante (se puede ajustar)
        HAL.setW(Kp * error)  # Ajuste de la velocidad angular en función del error

    # Mostrar la imagen procesada en la GUI
    GUI.showImage(red_mask)

    # Imprimir la posición del centro de masa
    print('%d cX: %.2f cY: %.2f' % (i, cX, cY))

    # Incrementar el contador
    i += 1
