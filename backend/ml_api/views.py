from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import joblib
import pandas as pd
import numpy as np
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models = {}
label_encoders = None

def load_model(model_name):
    global label_encoders
    if model_name not in models:
        try:
            if model_name == 'health':
                models['health'] = joblib.load(os.path.join(base_dir, 'models/health_score_model.pkl'))
            elif model_name == 'stress':
                models['stress'] = joblib.load(os.path.join(base_dir, 'models/stress_level_model.pkl'))
            elif model_name == 'stress_mgmt':
                models['stress_mgmt'] = joblib.load(os.path.join(base_dir, 'models/stress_management_model.pkl'))
            elif model_name == 'activity':
                models['activity'] = joblib.load(os.path.join(base_dir, 'models/activity_level_model.pkl'))
            elif model_name == 'sleep':
                models['sleep'] = joblib.load(os.path.join(base_dir, 'models/sleep_quality_model.pkl'))
            elif model_name == 'preprocessor':
                preprocessor_data = joblib.load(os.path.join(base_dir, 'models/preprocessor.pkl'))
                label_encoders = preprocessor_data['label_encoders']
                models['preprocessor'] = True
        except Exception as e:
            print(f"Model loading error for {model_name}: {e}")
            models[model_name] = None
    return models.get(model_name)

@api_view(['GET'])
def root(request):
    return Response({"message": "Health Score Prediction API"})

@api_view(['GET'])
def health_check(request):
    return Response({"status": "healthy"})

def prepare_features(data, include_stress=False):
    load_model('preprocessor')
    df = pd.DataFrame([data])
    df['gender_encoded'] = label_encoders['gender'].transform(df['gender'])
    df['activity_encoded'] = label_encoders['activity_type'].transform(df['activity_type'])
    df['intensity_encoded'] = label_encoders['intensity'].transform(df['intensity'])
    df['health_condition_encoded'] = label_encoders['health_condition'].transform(df['health_condition'].fillna('Unknown'))
    df['activity_frequency'] = 100
    df['stress_level'] = data.get('stress_level', 5)

    cols = ['age', 'height_cm', 'weight_kg', 'bmi', 'calories_burned', 'avg_heart_rate',
            'daily_steps', 'hours_sleep', 'stress_level', 'hydration_level',
            'gender_encoded', 'activity_encoded', 'intensity_encoded',
            'health_condition_encoded', 'activity_frequency']
    return df[cols].values

@api_view(['POST'])
def predict_health_score(request):
    model = load_model('health')
    if not model:
        return Response({"detail": "Model not loaded"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        features = prepare_features(request.data)
        prediction = model.predict(features)[0]
        return Response({"health_score": round(float(prediction), 2)})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def predict_activity_level(request):
    model = load_model('activity')
    if not model:
        return Response({"detail": "Model not loaded"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        features = prepare_features(request.data)
        prediction = model.predict(features)[0]
        return Response({"activity_score": round(float(prediction), 2)})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def predict_stress_management(request):
    model = load_model('stress_mgmt')
    if not model:
        return Response({"detail": "Model not loaded"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        features = prepare_features(request.data)
        prediction = model.predict(features)[0]
        return Response({"stress_score": round(float(prediction), 2)})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def predict_sleep_quality(request):
    model = load_model('sleep')
    if not model:
        return Response({"detail": "Model not loaded"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        features = prepare_features(request.data)
        prediction = model.predict(features)[0]
        return Response({"sleep_quality": round(float(prediction), 2)})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def predict_stress_level(request):
    model = load_model('stress')
    if not model:
        return Response({"detail": "Model not loaded"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        features = prepare_features(request.data)
        prediction = model.predict(features)[0]
        return Response({"stress_level": round(float(prediction), 2)})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def predict_all(request):
    health_model = load_model('health')
    stress_model = load_model('stress')
    stress_mgmt_model = load_model('stress_mgmt')
    activity_model = load_model('activity')
    sleep_model = load_model('sleep')
    
    if not health_model:
        return Response({"detail": "Health model not loaded"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        # Step 1: Predict stress WITHOUT stress_level in features
        data_temp = request.data.copy()
        
        # Prepare features WITHOUT stress_level for stress prediction
        load_model('preprocessor')
        df = pd.DataFrame([data_temp])
        df['gender_encoded'] = label_encoders['gender'].transform(df['gender'])
        df['activity_type_encoded'] = label_encoders['activity_type'].transform(df['activity_type'])
        df['intensity_encoded'] = label_encoders['intensity'].transform(df['intensity'])
        df['health_condition_encoded'] = label_encoders['health_condition'].transform(df['health_condition'].fillna('Unknown'))
        df['activity_frequency'] = 100
        
        cols_no_stress = ['age', 'height_cm', 'weight_kg', 'bmi', 'calories_burned', 'avg_heart_rate',
                          'daily_steps', 'hours_sleep', 'hydration_level', 'gender_encoded',
                          'activity_type_encoded', 'intensity_encoded', 'health_condition_encoded', 'activity_frequency']
        features_no_stress = df[cols_no_stress].values

        if stress_model:
            stress_level = float(stress_model.predict(features_no_stress)[0])
        else:
            stress_level = 5.0

        # Heuristic stress calculation (fallback if model gives constant values)
        hours_sleep = float(request.data.get('hours_sleep', 7))
        heart_rate = float(request.data.get('avg_heart_rate', 70))
        daily_steps = int(request.data.get('daily_steps', 5000))
        hydration = int(request.data.get('hydration_level', 5))

        heuristic_stress = 5
        if hours_sleep < 6: heuristic_stress += 2
        elif hours_sleep < 7: heuristic_stress += 1
        if heart_rate > 85: heuristic_stress += 2
        elif heart_rate > 75: heuristic_stress += 1
        if daily_steps < 3000: heuristic_stress += 1
        if hydration < 4: heuristic_stress += 1
        heuristic_stress = max(1, min(10, heuristic_stress))

        # Use heuristic if model prediction seems wrong
        if stress_level == 10 or stress_level < 1:
            stress_level = heuristic_stress
        
        # Step 2: Use predicted stress for other models
        data_with_stress = request.data.copy()
        data_with_stress['stress_level'] = stress_level
        features = prepare_features(data_with_stress)
        
        health_score = health_model.predict(features)[0]
        stress_score = stress_mgmt_model.predict(features)[0] if stress_mgmt_model else 100 - (stress_level * 10)
        activity_score = activity_model.predict(features)[0] if activity_model else float(request.data.get('calories_burned', 0)) / 5
        sleep_quality = sleep_model.predict(features)[0] if sleep_model else float(request.data.get('hours_sleep', 0)) * 10
        
        if health_score >= 80:
            interpretation = "Excellent"
            color = "green"
        elif health_score >= 60:
            interpretation = "Good"
            color = "blue"
        elif health_score >= 40:
            interpretation = "Fair"
            color = "orange"
        else:
            interpretation = "Needs Improvement"
            color = "red"
        
        # Rulebased Recommendations
        recommendations = []
        daily_steps = int(request.data.get('daily_steps', 0))
        hours_sleep = float(request.data.get('hours_sleep', 0))
        bmi = float(request.data.get('bmi', 0))
        calories_burned = float(request.data.get('calories_burned', 0))
        hydration = int(request.data.get('hydration_level', 0))
        heart_rate = float(request.data.get('avg_heart_rate', 0))
        
        # Workout recommendations
        if daily_steps < 5000:
            recommendations.append({
                "type": "workout",
                "priority": "high",
                "title": "Increase Daily Activity",
                "message": f"Your daily steps ({daily_steps}) are below recommended.",
                "action": "Start with a 20-minute walk after meals"
            })
        elif daily_steps < 8000:
            recommendations.append({
                "type": "workout",
                "priority": "medium",
                "title": "Boost Your Steps",
                "message": f"You're at {daily_steps} steps. Aim for 10,000!",
                "action": "Take stairs instead of elevator, park farther away"
            })
        
        if calories_burned < 300 and activity_score < 60:
            recommendations.append({
                "type": "workout",
                "priority": "high",
                "title": "Increase Exercise Intensity",
                "message": "Low calorie burn detected.",
                "action": "Try 30 minutes of moderate cardio 3x per week"
            })
        
        # Rest recommendations
        if hours_sleep < 6:
            recommendations.append({
                "type": "rest",
                "priority": "high",
                "title": "Critical: Improve Sleep",
                "message": f"You're only getting {hours_sleep} hours of sleep.",
                "action": "Aim for 7-9 hours. Set a consistent bedtime routine"
            })
        elif hours_sleep < 7:
            recommendations.append({
                "type": "rest",
                "priority": "medium",
                "title": "Optimize Sleep Duration",
                "message": f"Sleep at {hours_sleep}h is below optimal.",
                "action": "Try going to bed 30 minutes earlier"
            })
        
        if stress_level >= 7:
            recommendations.append({
                "type": "rest",
                "priority": "high",
                "title": "High Stress Detected",
                "message": "Your stress levels are concerning.",
                "action": "Practice meditation, deep breathing, or yoga daily"
            })
        elif stress_level >= 5:
            recommendations.append({
                "type": "rest",
                "priority": "medium",
                "title": "Manage Stress Levels",
                "message": "Moderate stress detected.",
                "action": "Take regular breaks, practice mindfulness"
            })
        
        if heart_rate > 90:
            recommendations.append({
                "type": "rest",
                "priority": "medium",
                "title": "Elevated Heart Rate",
                "message": f"Resting heart rate of {heart_rate} is high.",
                "action": "Ensure adequate rest and consider stress management"
            })
        
        # Diet recommendations
        if bmi > 30:
            recommendations.append({
                "type": "diet",
                "priority": "high",
                "title": "Weight Management Required",
                "message": f"BMI of {bmi:.1f} indicates obesity.",
                "action": "Focus on calorie deficit: more vegetables, lean protein"
            })
        elif bmi > 25:
            recommendations.append({
                "type": "diet",
                "priority": "medium",
                "title": "Weight Optimization",
                "message": f"BMI of {bmi:.1f} is above healthy range.",
                "action": "Reduce processed foods, increase whole grains"
            })
        elif bmi < 18.5:
            recommendations.append({
                "type": "diet",
                "priority": "medium",
                "title": "Underweight Concern",
                "message": f"BMI of {bmi:.1f} is below healthy range.",
                "action": "Increase calorie intake with nutrient-dense foods"
            })
        
        if hydration < 6:
            recommendations.append({
                "type": "diet",
                "priority": "high",
                "title": "Hydration Critical",
                "message": f"Only {hydration} glasses of water per day.",
                "action": "Drink at least 8 glasses (2L) of water daily"
            })
        elif hydration < 8:
            recommendations.append({
                "type": "diet",
                "priority": "low",
                "title": "Increase Hydration",
                "message": f"Current hydration: {hydration} glasses.",
                "action": "Aim for 8-10 glasses per day"
            })
        
        # General recommendation if all is good
        if not recommendations:
            recommendations.append({
                "type": "general",
                "priority": "low",
                "title": "Keep Up The Great Work!",
                "message": "Your health metrics look good.",
                "action": "Maintain your current healthy lifestyle"
            })
        
        return Response({
            "health_score": round(float(health_score), 2),
            "stress_score": round(float(stress_score), 2),
            "activity_score": round(float(activity_score), 2),
            "sleep_quality": round(float(sleep_quality), 2),
            "stress_level": round(float(stress_level), 2),
            "interpretation": interpretation,
            "color": color,
            "explanation": "Scores calculated using ML models trained on health and fitness data.",
            "recommendations": recommendations
        })
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
