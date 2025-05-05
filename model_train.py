import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

#  Load Dataset 
df = pd.read_csv('plant_health_data.csv')


#  Prepare Data 
X = df[['Soil_Moisture', 'Ambient_Temperature', 'Humidity', 'Light_Intensity']]
y = df['Plant_Health_Status']
# x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)

#  Train Model 
model = RandomForestClassifier()
model.fit(X, y)

#  Save Model 
joblib.dump(model, 'plant_health_model.joblib')
print(" Model saved as 'plant_health_model.joblib'.")

#  Save Ideal Values from Healthy Samples 
healthy = df[df['Plant_Health_Status'] == 'Healthy']
ideal_values = {
    'ideal_soil': healthy['Soil_Moisture'].mean(),
    'ideal_humidity': healthy['Humidity'].mean()
}
joblib.dump(ideal_values, 'ideal_values.joblib')
print(" Ideal values saved as 'ideal_values.joblib'.")
