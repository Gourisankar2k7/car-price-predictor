# -*- coding: utf-8 -*-
"""FINAL CODE

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wQWQfoIaftTczBE9BjJZTi36g_ghZxRp
"""

# Import necessary libraries
import pandas as pd
import numpy as np
import gdown
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor

# Step 0: Download the dataset from Google Drive
# Use the file ID from your Google Drive link
file_id = "15MfmIbP8sjEbDeFg915MaEt1TvXP4N-F"
url = f"https://drive.google.com/uc?id={file_id}"
output = "cleaned_CAR_DETAILS.csv"
gdown.download(url, output, quiet=False)

# Step 1: Load and clean dataset
df = pd.read_csv(output)

# Create new features
df['car_age'] = 2024 - df['year']
df['mileage_per_year'] = df['km_driven'] / df['car_age']
df['price_per_km'] = df['selling_price'] / df['km_driven']

# One-hot encoding for categorical features
df = pd.get_dummies(df, columns=['fuel', 'seller_type', 'transmission'], drop_first=True)

# Handle missing values
numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
df[numerical_cols] = df[numerical_cols].fillna(df[numerical_cols].median())
categorical_cols = df.select_dtypes(include=['object']).columns
df[categorical_cols] = df[categorical_cols].fillna(df[categorical_cols].mode().iloc[0])

# Ensure 'owner' column is properly encoded into numeric values
if df['owner'].dtype == 'object':
    label_encoder = LabelEncoder()
    df['owner'] = label_encoder.fit_transform(df['owner'])

# Define features and target
X = df.drop(columns=['selling_price', 'name'], errors='ignore')  # Drop 'name' column if present
y = df['selling_price']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 2: Initialize and train XGBoost model
xgb_model = XGBRegressor(random_state=42)
xgb_model.fit(X_train, y_train)

# Predict on the test set
y_pred_xgb = xgb_model.predict(X_test)

# Calculate RMSE
rmse_xgb = np.sqrt(mean_squared_error(y_test, y_pred_xgb))
print(f'RMSE for XGBoost: {rmse_xgb}')

# Print feature names expected by the model
print(xgb_model.get_booster().feature_names)

# Step 3: Collect user input for prediction
car_age = int(input("Enter the car's age: "))  # Example: 5 years
km_driven = int(input("Enter the car's total kilometers driven: "))  # Example: 50000 km
fuel = input("Enter the fuel type (Petrol/Diesel/LPG/Electric): ")  # Example: Petrol
seller_type = input("Enter the seller type (Individual/Trustmark Dealer): ")  # Example: Individual
transmission = input("Enter the transmission type (Manual/Automatic): ")  # Example: Manual
owner = int(input("Enter the number of owners: "))  # Example: 1 owner

# Step 4: Create the feature vector for prediction
new_car_data = {
    'car_age': car_age,
    'km_driven': km_driven,
    'owner': owner,
    'fuel_Petrol': 1 if fuel.lower() == 'petrol' else 0,
    'fuel_Diesel': 1 if fuel.lower() == 'diesel' else 0,
    'fuel_LPG': 1 if fuel.lower() == 'lpg' else 0,
    'fuel_Electric': 1 if fuel.lower() == 'electric' else 0,
    'seller_type_Individual': 1 if seller_type.lower() == 'individual' else 0,
    'seller_type_Trustmark Dealer': 1 if seller_type.lower() == 'trustmark dealer' else 0,
    'transmission_Manual': 1 if transmission.lower() == 'manual' else 0,
    'mileage_per_year': km_driven / car_age,  # Adding mileage_per_year
    'price_per_km': km_driven / 1000,  # Adding price_per_km
    'year': 2024 - car_age  # Adding year feature
}

# Step 5: Convert the dictionary into a pandas DataFrame
new_car_df = pd.DataFrame([new_car_data])

# Ensure the input data has the same columns as the trained model
expected_columns = ['year', 'km_driven', 'owner', 'car_age', 'mileage_per_year', 'price_per_km',
                    'fuel_Diesel', 'fuel_Electric', 'fuel_LPG', 'fuel_Petrol',
                    'seller_type_Individual', 'seller_type_Trustmark Dealer', 'transmission_Manual']

# Reorder columns to match the trained model
new_car_df = new_car_df[expected_columns]

# Step 6: Use the trained model to predict the price
predicted_price = xgb_model.predict(new_car_df)

# Convert negative prediction to positive using absolute value
predicted_price = abs(predicted_price[0])

# Output the prediction
print(f"The predicted price for the car is: {predicted_price:,.2f}")