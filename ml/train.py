"""
ML Training Script for Crop Recommendation System
Trains RandomForest for technique classification and XGBoost for yield prediction.
"""
import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, f1_score
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create models directory if it doesn't exist
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def create_sample_dataset():
    """
    Create a sample dataset for training if no real data is available.
    """
    logger.info("Creating sample dataset for training...")
    
    # Sample data parameters
    n_samples = 1000
    
    # Categorical features
    crops = ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton', 'Soybean', 'Potato', 'Tomato', 'Onion', 'Chili']
    seasons = ['Kharif', 'Rabi', 'Zaid', 'Monsoon', 'Winter', 'Summer']
    soils = ['Clay', 'Sandy', 'Loamy', 'Silty', 'Peaty', 'Chalky']
    preferences = ['Organic', 'Inorganic', 'Mixed']
    fertilizer_types = ['Organic', 'Inorganic', 'Mixed']
    
    # Generate sample data
    np.random.seed(42)
    
    data = {
        'crop': np.random.choice(crops, n_samples),
        'season': np.random.choice(seasons, n_samples),
        'soil': np.random.choice(soils, n_samples),
        'preference': np.random.choice(preferences, n_samples),
        'lat': np.random.uniform(8.0, 37.0, n_samples),  # India latitude range
        'lon': np.random.uniform(68.0, 97.0, n_samples),  # India longitude range
        'N': np.random.normal(100, 30, n_samples),
        'P': np.random.normal(50, 15, n_samples),
        'K': np.random.normal(40, 12, n_samples),
        'pH': np.random.normal(6.5, 1.0, n_samples),
        'rainfall': np.random.normal(1000, 300, n_samples),
        'temperature': np.random.normal(25, 5, n_samples),
        'humidity': np.random.normal(65, 15, n_samples),
        'fertilizer_type': np.random.choice(fertilizer_types, n_samples),
    }
    
    # Generate yield based on rules
    base_yields = {
        'Rice': 4000, 'Wheat': 3500, 'Maize': 5000, 'Sugarcane': 80000,
        'Cotton': 500, 'Soybean': 2500, 'Potato': 25000, 'Tomato': 50000,
        'Onion': 30000, 'Chili': 15000
    }
    
    yields = []
    for i in range(n_samples):
        crop = data['crop'][i]
        base_yield = base_yields.get(crop, 3000)
        
        # Add some variation based on other factors
        variation = np.random.normal(1.0, 0.2)
        soil_factor = {'Clay': 0.9, 'Sandy': 0.8, 'Loamy': 1.0, 'Silty': 1.1, 'Peaty': 1.2, 'Chalky': 0.8}
        season_factor = {'Kharif': 1.0, 'Rabi': 1.1, 'Zaid': 0.9, 'Monsoon': 1.0, 'Winter': 1.1, 'Summer': 0.9}
        
        yield_val = base_yield * variation * soil_factor[data['soil'][i]] * season_factor[data['season'][i]]
        yields.append(max(0, yield_val))  # Ensure non-negative
    
    data['yield'] = yields
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save sample dataset
    dataset_path = os.path.join(os.path.dirname(__file__), 'sample_dataset.csv')
    df.to_csv(dataset_path, index=False)
    logger.info(f"Sample dataset saved to {dataset_path}")
    
    return df

def load_dataset(dataset_path=None):
    """
    Load dataset from CSV file or create sample dataset.
    """
    if dataset_path and os.path.exists(dataset_path):
        logger.info(f"Loading dataset from {dataset_path}")
        return pd.read_csv(dataset_path)
    else:
        logger.info("No dataset found, creating sample dataset...")
        return create_sample_dataset()

def preprocess_data(df):
    """
    Preprocess the dataset for training.
    """
    logger.info("Preprocessing data...")
    
    # Handle missing values
    numeric_columns = ['N', 'P', 'K', 'pH', 'rainfall', 'temperature', 'humidity', 'yield']
    categorical_columns = ['crop', 'season', 'soil', 'preference', 'fertilizer_type']
    
    # Fill missing numeric values with median
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    # Fill missing categorical values with mode
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mode()[0])
    
    # Encode categorical variables
    label_encoders = {}
    for col in categorical_columns:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
    
    # Scale numerical features
    scaler = StandardScaler()
    numeric_features = ['N', 'P', 'K', 'pH', 'rainfall', 'temperature', 'humidity', 'lat', 'lon']
    available_numeric = [col for col in numeric_features if col in df.columns]
    
    if available_numeric:
        df[available_numeric] = scaler.fit_transform(df[available_numeric])
    
    return df, label_encoders, scaler

def train_technique_classifier(X, y, label_encoders):
    """
    Train RandomForest classifier for fertilizer technique prediction.
    """
    logger.info("Training technique classifier...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train RandomForest
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    rf_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    logger.info(f"Technique Classifier - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
    logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
    
    # Cross-validation
    cv_scores = cross_val_score(rf_model, X, y, cv=5, scoring='accuracy')
    logger.info(f"Cross-validation scores: {cv_scores}")
    logger.info(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return rf_model

def train_yield_predictor(X, y):
    """
    Train XGBoost regressor for yield prediction.
    """
    logger.info("Training yield predictor...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train XGBoost
    xgb_model = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    
    xgb_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = xgb_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"Yield Predictor - MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.4f}")
    
    # Cross-validation
    cv_scores = cross_val_score(xgb_model, X, y, cv=5, scoring='neg_mean_absolute_error')
    logger.info(f"Cross-validation MAE: {-cv_scores.mean():.2f} (+/- {cv_scores.std() * 2:.2f})")
    
    return xgb_model

def main():
    """
    Main training function.
    """
    logger.info("Starting ML model training...")
    
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), 'sample_dataset.csv')
    df = load_dataset(dataset_path)
    
    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Preprocess data
    df_processed, label_encoders, scaler = preprocess_data(df.copy())
    
    # Prepare features and targets
    feature_columns = ['crop', 'season', 'soil', 'preference', 'lat', 'lon', 'N', 'P', 'K', 'pH', 'rainfall', 'temperature', 'humidity']
    available_features = [col for col in feature_columns if col in df_processed.columns]
    
    X = df_processed[available_features]
    y_technique = df_processed['fertilizer_type']
    y_yield = df_processed['yield']
    
    logger.info(f"Features used: {available_features}")
    logger.info(f"Training samples: {X.shape[0]}")
    
    # Train technique classifier
    tech_model = train_technique_classifier(X, y_technique, label_encoders)
    
    # Train yield predictor
    yield_model = train_yield_predictor(X, y_yield)
    
    # Save models and preprocessors
    tech_model_path = os.path.join(MODEL_DIR, 'tech_model.pkl')
    yield_model_path = os.path.join(MODEL_DIR, 'yield_model.pkl')
    scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
    encoders_path = os.path.join(MODEL_DIR, 'label_encoders.pkl')
    
    joblib.dump(tech_model, tech_model_path)
    joblib.dump(yield_model, yield_model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(label_encoders, encoders_path)
    
    logger.info(f"Models saved to {MODEL_DIR}")
    logger.info("Training completed successfully!")
    
    # Print model information
    print("\n" + "="*50)
    print("MODEL TRAINING SUMMARY")
    print("="*50)
    print(f"Dataset size: {df.shape[0]} samples")
    print(f"Features: {len(available_features)}")
    print(f"Technique classes: {len(np.unique(y_technique))}")
    print(f"Yield range: {y_yield.min():.0f} - {y_yield.max():.0f}")
    print(f"Models saved to: {MODEL_DIR}")
    print("="*50)

if __name__ == "__main__":
    main()
