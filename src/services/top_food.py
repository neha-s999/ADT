from flask import Flask, request
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

NUT_DAILY_VALUES = {
    "calories": 2000,
    "carbohydrates": 300,
    "cholesterol": 0.003,
    "fat" : 65,
    "fiber": 25,
    "proteins": 50
}

NUT_NAMES_MAP = {
    "calories" : "energy_100g",
    "carbohydrates": "carbohydrates_100g",
    "cholesterol": "cholesterol_100g",
    "fat" : "fat_100g",
    "fiber": "fiber_100g",
    "proteins": "proteins_100g"
}

def preprocess_data(df):
    # normalize df
    for key, val in NUT_DAILY_VALUES.items():
        column = NUT_NAMES_MAP[key]
        df[column] /= val
        df[column] *= 2
    return df

def get_recommendations(user_input, knn_model, nutrition_df):
    # Normalize user input according to daily values
    user_input_normalized = [(NUT_DAILY_VALUES[key] - float(user_input[key])) / NUT_DAILY_VALUES[key] for key in user_input]

    # Query the model with normalized user input
    _, indices = knn_model.kneighbors([user_input_normalized], n_neighbors=3)

    # Retrieve recommended products
    recommended_products = [nutrition_df.loc[i]['product_name'] for i in indices[0]]
    return recommended_products

@app.route("/", methods=['POST'])
def similar_foods():
    user_input = request.json  # Assuming JSON input with nutritional parameters
    if user_input is None:
        return "Error: No input provided", 400

    # Load nutritional data
    nutrition_df = pd.read_csv("data/nutrition_values.csv", header=0)
    nutrition_values_df = nutrition_df.drop(["product_name", "sugars_100g"], axis=1)

    # Preprocess data
    nutrition_values_df = preprocess_data(nutrition_values_df)

    # Train Nearest Neighbors model
    knn_model = NearestNeighbors(n_neighbors=5, algorithm='ball_tree', metric="euclidean").fit(nutrition_values_df)

    # Get recommendations
    recommended_products = get_recommendations(user_input, knn_model, nutrition_df)

    response_dict = {"recommended": recommended_products}
    return response_dict

if __name__ == "__main__":
    app.run(port=5002, debug=True)
