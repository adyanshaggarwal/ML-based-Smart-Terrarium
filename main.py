import pandas as pd
import serial
import time
import joblib
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

#  Load Trained Model and Ideal Values 
model = joblib.load('plant_health_model.joblib')
ideal_values = joblib.load('ideal_values.joblib')

ideal_soil = ideal_values['ideal_soil']
ideal_humidity = ideal_values['ideal_humidity']
print(f"🌿 Ideal Soil: {round(ideal_soil, 2)} | Ideal Humidity: {round(ideal_humidity, 2)}")

#  Firebase Setup
cred = credentials.Certificate("firebase_config.json")  # Replace with actual filename
firebase_admin.initialize_app(cred)
db = firestore.client()

#  Serial Setup 
SERIAL_PORT = 'COM4'  # Change this to match your actual port
BAUD_RATE = 9600
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
time.sleep(2)
print("🚀 Listening to Arduino...")

#  Firebase Upload Function 
def upload_to_firebase(soil, temp, humidity, light, prediction):
    doc = {
        'timestamp': datetime.utcnow(),
        'Soil_Moisture': soil,
        'Ambient_Temperature': temp,
        'Humidity': humidity,
        'Light_Intensity': light,
        'Plant_Health_Status': prediction
    }
    db.collection('terrarium-data').add(doc)
    print("📡 Uploaded to Firebase.")

#  Main Loop 
while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            try:
                parts = [float(x) for x in line.split(',')]
                if len(parts) != 4:
                    print("⚠️ Bad data format:", line)
                    continue

                soil, temp, humidity, light = parts
                soil=soil-30
                humidity=humidity-10
                print(f"\n📥 Received → Soil={soil}, Temp={temp}, Humidity={humidity}, Light={light}")

                # Predict health
                prediction = model.predict([[soil, temp, humidity, light]])[0]
                print(f"🌱 Predicted Health: {prediction}")

                # Upload to Firebase
                upload_to_firebase(soil, temp, humidity, light, prediction)

                # Calculate corrections
                if prediction == 'Healthy':
                    soil_corr = 0
                    humidity_corr = 0
                else:
                    soil_corr = round(ideal_soil - soil, 2)
                    humidity_corr = round(ideal_humidity - humidity, 2)*(-1)

                # Send back to Arduino
                response = f"{soil_corr},{humidity_corr}\n"
                ser.write(response.encode())
                print(f"📤 Sent Corrections → Soil: {soil_corr}, Humidity: {humidity_corr}")

            except ValueError:
                print("⚠️ Failed to parse numbers:", line)

    except KeyboardInterrupt:
        print("🛑 Exiting...")
        ser.close()
        break
