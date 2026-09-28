import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np

# Load models
stress_model = joblib.load('models/stress_level_model.pkl')
health_model = joblib.load('models/health_score_model.pkl')
stress_mgmt_model = joblib.load('models/stress_management_model.pkl')
activity_model = joblib.load('models/activity_level_model.pkl')
sleep_model = joblib.load('models/sleep_quality_model.pkl')
preprocessor = joblib.load('models/preprocessor.pkl')
le = preprocessor['label_encoders']

# Load test data
df = pd.read_csv('data/health_fitness_dataset.csv')

# Encode
for col in ['gender', 'activity_type', 'intensity', 'health_condition']:
    df[col + '_encoded'] = le[col].transform(df[col].fillna('Unknown'))
df['activity_frequency'] = 100

# Test cases
test_cases = [
    {"name": "Healthy Person", "age": 25, "height_cm": 170, "weight_kg": 65, "bmi": 22.5, 
     "calories_burned": 800, "avg_heart_rate": 60, "daily_steps": 15000, "hours_sleep": 8, 
     "hydration_level": 10, "gender": "M", "activity_type": "Running", "intensity": "High", 
     "health_condition": "Unknown", "expected_stress": "Low (1-4)"},
    
    {"name": "Unhealthy Person", "age": 45, "height_cm": 170, "weight_kg": 95, "bmi": 32.9, 
     "calories_burned": 100, "avg_heart_rate": 90, "daily_steps": 2000, "hours_sleep": 5, 
     "hydration_level": 2, "gender": "M", "activity_type": "Walking", "intensity": "Low", 
     "health_condition": "Unknown", "expected_stress": "High (7-10)"},
    
    {"name": "Average Person", "age": 30, "height_cm": 165, "weight_kg": 70, "bmi": 25.7, 
     "calories_burned": 400, "avg_heart_rate": 75, "daily_steps": 7000, "hours_sleep": 7, 
     "hydration_level": 6, "gender": "F", "activity_type": "Running", "intensity": "Medium", 
     "health_condition": "Unknown", "expected_stress": "Medium (4-7)"},
]

print("=" * 80)
print("MODEL ACCURACY TEST")
print("=" * 80)

for tc in test_cases:
    print(f"\n{tc['name']}:")
    print(f"  Input: HR={tc['avg_heart_rate']}, Steps={tc['daily_steps']}, Sleep={tc['hours_sleep']}h, Hydration={tc['hydration_level']}")
    
    # Prepare features
    test_df = pd.DataFrame([tc])
    test_df['gender_encoded'] = le['gender'].transform(test_df['gender'])
    test_df['activity_type_encoded'] = le['activity_type'].transform(test_df['activity_type'])
    test_df['intensity_encoded'] = le['intensity'].transform(test_df['intensity'])
    test_df['health_condition_encoded'] = le['health_condition'].transform(test_df['health_condition'])
    test_df['activity_frequency'] = 100
    
    # Predict stress (without stress in features)
    cols_no_stress = ['age', 'height_cm', 'weight_kg', 'bmi', 'calories_burned', 'avg_heart_rate', 
                      'daily_steps', 'hours_sleep', 'hydration_level', 'gender_encoded', 
                      'activity_type_encoded', 'intensity_encoded', 'health_condition_encoded', 'activity_frequency']
    X_no_stress = test_df[cols_no_stress]
    stress_pred = stress_model.predict(X_no_stress)[0]
    
    # Add stress for other predictions
    test_df['stress_level'] = stress_pred
    cols_with_stress = cols_no_stress[:8] + ['stress_level'] + cols_no_stress[8:]
    X_with_stress = test_df[cols_with_stress]
    
    health_pred = health_model.predict(X_with_stress)[0]
    stress_mgmt_pred = stress_mgmt_model.predict(X_with_stress)[0]
    activity_pred = activity_model.predict(X_with_stress)[0]
    sleep_pred = sleep_model.predict(X_with_stress)[0]
    
    print(f"  Predictions:")
    print(f"    Stress Level: {stress_pred:.1f}/10 (Expected: {tc['expected_stress']})")
    print(f"    Health Score: {health_pred:.1f}/100")
    print(f"    Stress Management: {stress_mgmt_pred:.1f}/100")
    print(f"    Activity Level: {activity_pred:.1f}/100")
    print(f"    Sleep Quality: {sleep_pred:.1f}/100")

# Overall model performance on dataset
print("\n" + "=" * 80)
print("OVERALL MODEL PERFORMANCE ON DATASET")
print("=" * 80)

# Prepare full dataset
cols_no_stress = ['age', 'height_cm', 'weight_kg', 'bmi', 'calories_burned', 'avg_heart_rate', 
                  'daily_steps', 'hours_sleep', 'hydration_level', 'gender_encoded', 
                  'activity_type_encoded', 'intensity_encoded', 'health_condition_encoded', 'activity_frequency']

# Create synthetic targets
df['stress_score'] = 5.0
df.loc[df['hours_sleep'] < 6, 'stress_score'] += 3
df.loc[df['hours_sleep'] < 7, 'stress_score'] += 1
df.loc[df['hours_sleep'] >= 8, 'stress_score'] -= 2
df.loc[df['avg_heart_rate'] > 85, 'stress_score'] += 3
df.loc[df['avg_heart_rate'] > 75, 'stress_score'] += 1
df.loc[df['avg_heart_rate'] < 65, 'stress_score'] -= 2
df.loc[df['daily_steps'] < 3000, 'stress_score'] += 2
df.loc[df['daily_steps'] >= 10000, 'stress_score'] -= 2
df.loc[df['hydration_level'] < 4, 'stress_score'] += 1
df.loc[df['hydration_level'] >= 8, 'stress_score'] -= 1
df['stress_numeric'] = df['stress_score'].clip(1, 10).round()

X_no_stress = df[cols_no_stress]
y_stress = df['stress_numeric']
stress_predictions = stress_model.predict(X_no_stress)

print(f"\nStress Model:")
print(f"  R² Score: {r2_score(y_stress, stress_predictions):.3f}")
print(f"  Mean Absolute Error: {mean_absolute_error(y_stress, stress_predictions):.2f}")
print(f"  Prediction Range: {stress_predictions.min():.1f} - {stress_predictions.max():.1f}")

print("\n✅ Model testing complete!")
