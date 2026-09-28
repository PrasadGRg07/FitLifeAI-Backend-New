import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

# Load data
df = pd.read_csv('data/health_fitness_dataset.csv')

# Encode categorical variables
label_encoders = {}
for col in ['gender', 'activity_type', 'intensity', 'health_condition']:
    le = LabelEncoder()
    df[col + '_encoded'] = le.fit_transform(df[col].fillna('Unknown'))
    label_encoders[col] = le

df['activity_frequency'] = 100

# Features WITHOUT stress (for stress prediction)
features_no_stress = ['age', 'height_cm', 'weight_kg', 'bmi', 'calories_burned', 
                      'avg_heart_rate', 'daily_steps', 'hours_sleep', 'hydration_level',
                      'gender_encoded', 'activity_type_encoded', 'intensity_encoded', 
                      'health_condition_encoded', 'activity_frequency']

# Features WITH stress (for other predictions)
features_with_stress = ['age', 'height_cm', 'weight_kg', 'bmi', 'calories_burned', 
                        'avg_heart_rate', 'daily_steps', 'hours_sleep', 'stress_level',
                        'hydration_level', 'gender_encoded', 'activity_type_encoded', 
                        'intensity_encoded', 'health_condition_encoded', 'activity_frequency']

# 1. Train Stress Level Classifier (predicts stress category)
print("Training Stress Level Classifier...")
# Create stress categories with better distribution
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

X_stress = df[features_no_stress]
y_stress = df['stress_numeric']
X_train, X_test, y_train, y_test = train_test_split(X_stress, y_stress, test_size=0.2, random_state=42)
stress_model = RandomForestRegressor(n_estimators=30, random_state=42, max_depth=8)
stress_model.fit(X_train, y_train)
print(f"Stress Model Score: {stress_model.score(X_test, y_test):.3f}")
joblib.dump(stress_model, 'models/stress_level_model.pkl')

# 2. Train Health Score Model
print("\nTraining Health Score Model...")
df['health_score'] = (
    (df['hours_sleep'] / 9 * 20) +
    (df['daily_steps'] / 10000 * 20) +
    (df['hydration_level'] / 10 * 15) +
    ((10 - df['stress_numeric']) / 10 * 20) +
    (df['calories_burned'] / 1000 * 15) +
    ((100 - df['avg_heart_rate']) / 40 * 10)
).clip(0, 100)

df['stress_level'] = df['stress_numeric']
X_health = df[features_with_stress]
y_health = df['health_score']
X_train, X_test, y_train, y_test = train_test_split(X_health, y_health, test_size=0.2, random_state=42)
health_model = RandomForestRegressor(n_estimators=30, random_state=42, max_depth=8)
health_model.fit(X_train, y_train)
print(f"Health Model Score: {health_model.score(X_test, y_test):.3f}")
joblib.dump(health_model, 'models/health_score_model.pkl')

# 3. Train Stress Management Model
print("\nTraining Stress Management Model...")
df['stress_management'] = ((10 - df['stress_numeric']) * 10).clip(0, 100)
X_train, X_test, y_train, y_test = train_test_split(X_health, df['stress_management'], test_size=0.2, random_state=42)
stress_mgmt_model = RandomForestRegressor(n_estimators=30, random_state=42, max_depth=8)
stress_mgmt_model.fit(X_train, y_train)
print(f"Stress Management Model Score: {stress_mgmt_model.score(X_test, y_test):.3f}")
joblib.dump(stress_mgmt_model, 'models/stress_management_model.pkl')

# 4. Train Activity Level Model
print("\nTraining Activity Level Model...")
df['activity_level'] = (
    (df['daily_steps'] / 10000 * 40) +
    (df['calories_burned'] / 1000 * 40) +
    ((100 - df['avg_heart_rate']) / 40 * 20)
).clip(0, 100)
X_train, X_test, y_train, y_test = train_test_split(X_health, df['activity_level'], test_size=0.2, random_state=42)
activity_model = RandomForestRegressor(n_estimators=30, random_state=42, max_depth=8)
activity_model.fit(X_train, y_train)
print(f"Activity Model Score: {activity_model.score(X_test, y_test):.3f}")
joblib.dump(activity_model, 'models/activity_level_model.pkl')

# 5. Train Sleep Quality Model
print("\nTraining Sleep Quality Model...")
df['sleep_quality'] = (df['hours_sleep'] / 9 * 100).clip(0, 100)
X_train, X_test, y_train, y_test = train_test_split(X_health, df['sleep_quality'], test_size=0.2, random_state=42)
sleep_model = RandomForestRegressor(n_estimators=30, random_state=42, max_depth=8)
sleep_model.fit(X_train, y_train)
print(f"Sleep Model Score: {sleep_model.score(X_test, y_test):.3f}")
joblib.dump(sleep_model, 'models/sleep_quality_model.pkl')

# Save preprocessor
joblib.dump({'label_encoders': label_encoders}, 'models/preprocessor.pkl')

print("\n✅ All models trained and saved!")
