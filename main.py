import tkinter as tk
from datetime import datetime
import requests
from urllib.parse import urlencode
import pandas as pd
from PIL import Image, ImageTk




def backend():
    ################################# EL TIEMPO
    api_key = "YOUR_API"
    latitude = "37.26638"  # Coordenadas
    longitude = "-6.94004" # Coordenadas
    params = {
        'lat': latitude,
        'lon': longitude,
        'sections': 'all',
        'timezone': 'UTC',
        'language': 'en',
        'units': 'metric',
        'key': api_key
    }

    api_link_weather = 'https://www.meteosource.com/api/v1/free/point?' + urlencode(params)
    response = requests.get(api_link_weather)
    data = response.json()  # Cargar directamente la respuesta JSON

    # Procesar datos actuales
    temperature = data["current"]["temperature"]
    wind_speed = data["current"]["wind"]["speed"]
    wind_direction = data["current"]["wind"]["angle"]
    icon_num = data["current"]["icon_num"]
    precipitacion = data["current"]["precipitation"]["total"]
    #print(summary)
    
    ################################# CALIDAD DEL AIRE
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": 37.2664,
        "longitude": -6.94,
        "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "european_aqi"],
        "forecast_days": 1
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        hourly_data = data['hourly']
        timestamps = hourly_data['time']
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(timestamps),
            "pm10": hourly_data['pm10'],
            "pm2_5": hourly_data['pm2_5'],
            "carbon_monoxide": hourly_data['carbon_monoxide'],
            "nitrogen_dioxide": hourly_data['nitrogen_dioxide'],
            "european_aqi": hourly_data['european_aqi']
        })

        last_row = df.iloc[-1]
        aqi = hourly_data['european_aqi']
        return temperature, last_row['pm10'], last_row['pm2_5'], last_row['carbon_monoxide'], last_row['nitrogen_dioxide'], wind_speed, wind_direction, icon_num, last_row['european_aqi'], precipitacion
    return temperature, None, None, None, None, wind_speed, wind_direction, icon_num, aqi, precipitacion




def actualizar_hora():
    hora_actual = datetime.now().strftime("%H:%M:%S")
    hora_label.config(text=hora_actual)
    # Actualizar cada segundo para la hora
    root.after(1000, actualizar_hora)


def actualizar_datos():

    # Llamar a backend para actualizar los datos
    temperature, pm10, pm2_5, carbon_monoxide, nitrogen_dioxide, wind_speed, wind_direction, icon_num, aqi, precipitacion = backend()

    temperatura_label.config(text=f"{temperature}°C")
    
    viento_label.config(text=f"{wind_speed} km/h")

    ica_label.config(text=aqi)
    if aqi < 20:
        #good
        ica_label.config(bg="cyan")
    elif aqi>=20 and aqi<=40:
        #fair
        ica_label.config(bg="blue")
    elif aqi>40 and aqi<=60:
        #moderado
        ica_label.config(bg="yellow")
    elif aqi>60 and aqi<=80:
        #mala
        ica_label.config(bg="red")
    elif aqi>80 and aqi<=100:
        #muy mala
        ica_label.config(bg="red")
    elif aqi>100:
        #extremadamente mala
        ica_label.config(bg="purple")

    contaminantes_label.config(text=f"PM2.5: {round((pm2_5*4), 1)}%    PM10: {round((pm10*2), 1)}%\n NO2: {nitrogen_dioxide/25*100}%    CO: {carbon_monoxide/100}% ")
    precipitacion_label.config()
    imagen = Image.open(f"big/{icon_num}.png")
    imagen_tk = ImageTk.PhotoImage(imagen)
    label_icono = tk.Label(root, image=imagen_tk)
    label_icono.grid(row = 0, column= 0, padx=0, pady=0)

    precipitacion_label.config(text=f"{precipitacion}l/m2", )
    # Actualizar cada 20 minutos
    root.after(1200000, actualizar_datos) #Actualiza los datos cada media hora
    return icon_num
    


# Crear la ventana principal
import tkinter as tk

import tkinter as tk
from PIL import Image, ImageTk  # Required for handling images in Tkinter

# Initialize the main window
# Inicializar la ventana principal
root = tk.Tk()
root.geometry("600x300+1000+100")
root.overrideredirect(True)

# Crear un fondo con color y opacidad
root.configure(bg="#f0f0f0")
root.attributes("-alpha", 0.9)

# Crear una etiqueta para la hora
hora_label = tk.Label(root, text="", font=("Arial", 22, "bold"), fg="black", bg="#f0f0f0")
hora_label.place(x=80, y=20)

# Crear una etiqueta para la temperatura
temperatura_label = tk.Label(root, text="", font=("Arial", 20, "bold"), fg="black", bg="#f0f0f0")
temperatura_label.place(x=400, y=20)

# Crear una etiqueta para la velocidad del viento
viento_label = tk.Label(root, text="", font=("Arial", 16), fg="black", bg="#f0f0f0")
viento_label.place(x=250, y=100)

# Crear una etiqueta para la precipitación
precipitacion_label = tk.Label(root, text="", font=("Arial", 18), fg="blue", bg="#f0f0f0")
precipitacion_label.place(x=50, y=200)

# Crear una tabla para el ICA
ica_label = tk.Label(root, text="", font=("Arial", 18, "bold"), fg="white", bg="blue", relief="solid", padx=10, pady=10)
ica_label.place(x=330, y=170)

# Crear etiquetas dentro de la tabla ICA para los contaminantes
contaminantes_label = tk.Label(root, text="", font=("Arial", 9), fg="black", bg="white", relief="solid", padx=10, pady=10)
contaminantes_label.place(x=390, y=169)

# Llamar a la función de actualización de datos
icon_num = actualizar_datos()
actualizar_hora()

# Load and display an image for the summary

image = Image.open(f"big/{icon_num}.png")
image = image.resize((130, 100))  # Resize the image to fit the layout
summary_image = ImageTk.PhotoImage(image)

summary_label = tk.Label(root, image=summary_image)
summary_label.place(x=30, y=75)
# Ejecutar la ventana
root.attributes("-alpha", 0.6)  # 0.8 es un 80% de opacidad
root.mainloop()
