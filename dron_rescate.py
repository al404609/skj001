import GUI
import HAL
import utm

# Función para convertir coordenadas DMS (grados, minutos, segundos) a grados decimales
def dms_a_decimal(grados, minutos, segundos):
    return grados + (minutos / 60) + (segundos / 3600)

# Coordenadas del bote de seguridad
lat_bote_grados = 40
lat_bote_minutos = 16
lat_bote_segundos = 48.2

lon_bote_grados = 3
lon_bote_minutos = 49
lon_bote_segundos = 3.5

# Coordenadas de los sobrevivientes
lat_sobrevivientes_grados = 40
lat_sobrevivientes_minutos = 16
lat_sobrevivientes_segundos = 47.23

lon_sobrevivientes_grados = 3
lon_sobrevivientes_minutos = 49
lon_sobrevivientes_segundos = 1.78

# Convertir las coordenadas a formato decimal
boat_lat = dms_a_decimal(lat_bote_grados, lat_bote_minutos, lat_bote_segundos)  # Latitud del bote
boat_lon = -dms_a_decimal(lon_bote_grados, lon_bote_minutos, lon_bote_segundos)  # Longitud del bote (negativa por ser oeste)

victim_lat = dms_a_decimal(lat_sobrevivientes_grados, lat_sobrevivientes_minutos, lat_sobrevivientes_segundos)  # Latitud de los sobrevivientes
victim_lon = -dms_a_decimal(lon_sobrevivientes_grados, lon_sobrevivientes_minutos, lon_sobrevivientes_segundos)  # Longitud de los sobrevivientes (negativa por ser oeste)
victim_UTM = utm.from_latlon(victim_lat, victim_lon) 
boat_UTM = utm.from_latlon(boat_lat, boat_lon)

difference_x = victim_UTM[0]-boat_UTM[0]
difference_y = victim_UTM[1]-boat_UTM[1]
print(difference_x)
print(difference_y)

while True:
    # Enter iterative code!

