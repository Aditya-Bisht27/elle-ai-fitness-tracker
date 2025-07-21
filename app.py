import streamlit as st
import openai
import sqlite3
import datetime
import base64
from PIL import Image
from io import BytesIO
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import speech_recognition as sr
import pyttsx3
import threading
import time
import requests
from datetime import datetime, timedelta
import cv2
import random
import hashlib

# Page configuration
st.set_page_config(
    page_title="Elle - Complete AI Fitness Assistant", 
    page_icon="🎀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B9D, #C44BFF);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #FF6B9D;
        margin: 10px 0;
    }
    .elle-chat {
        background: linear-gradient(45deg, #FF9A8B, #A8E6CF);
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
    }
    .success-animation {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI
if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("🔑 Please add your OpenAI API key in Streamlit secrets!")
    st.stop()

class ElleComplete:
    def __init__(self):
        self.init_database()
        self.init_voice_assistant()
        self.user_profile = self.load_user_profile()
        
    def init_database(self):
        """Initialize comprehensive database"""
        conn = sqlite3.connect('elle_complete.db')
        cursor = conn.cursor()
        
        # Workouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY,
                date TEXT,
                exercise TEXT,
                duration INTEGER,
                calories INTEGER,
                intensity TEXT,
                mood_before TEXT,
                mood_after TEXT,
                notes TEXT,
                heart_rate_avg INTEGER,
                form_score REAL
            )
        ''')
        
        # Nutrition table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition (
                id INTEGER PRIMARY KEY,
                date TEXT,
                meal_type TEXT,
                food_items TEXT,
                calories INTEGER,
                protein REAL,
                carbs REAL,
                fats REAL,
                fiber REAL,
                sugar REAL,
                sodium REAL,
                analysis TEXT,
                photo_path TEXT
            )
        ''')
        
        # User profile
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                gender TEXT,
                height REAL,
                weight REAL,
                activity_level TEXT,
                fitness_goals TEXT,
                dietary_restrictions TEXT,
                medical_conditions TEXT,
                preferences TEXT,
                created_date TEXT,
                updated_date TEXT
            )
        ''')
        
        # Health metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY,
                date TEXT,
                weight REAL,
                body_fat_percentage REAL,
                muscle_mass REAL,
                resting_heart_rate INTEGER,
                blood_pressure_systolic INTEGER,
                blood_pressure_diastolic INTEGER,
                sleep_hours REAL,
                stress_level INTEGER,
                energy_level INTEGER,
                hydration_glasses INTEGER
            )
        ''')
        
        # Goals and achievements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY,
                goal_type TEXT,
                description TEXT,
                target_value REAL,
                current_value REAL,
                target_date TEXT,
                status TEXT,
                created_date TEXT
            )
        ''')
        
        # Social features
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY,
                challenge_name TEXT,
                challenge_type TEXT,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                participants TEXT,
                progress TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_voice_assistant(self):
        """Initialize enhanced voice assistant"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.tts_engine = pyttsx3.init()
            
            # Configure Elle's voice personality
            voices = self.tts_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if any(keyword in voice.name.lower() for keyword in ['female', 'zira', 'samantha']):
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.tts_engine.setProperty('rate', 175)  # Speaking speed
            self.tts_engine.setProperty('volume', 0.9)
            self.listening = False
        except:
            st.warning("Voice features may not be available on this system.")
    
    def load_user_profile(self):
        """Load or create user profile"""
        conn = sqlite3.connect('elle_complete.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_profile LIMIT 1')
        profile = cursor.fetchone()
        conn.close()
        
        if profile:
            return {
                'name': profile[1],
                'age': profile[2],
                'gender': profile[3],
                'height': profile[4],
                'weight': profile[5],
                'activity_level': profile[6],
                'fitness_goals': profile[7],
                'dietary_restrictions': profile[8]
            }
        return None
    
    def analyze_food_advanced(self, image):
        """Advanced food analysis with detailed nutrition"""
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Hi! I'm Elle, your comprehensive AI fitness coach! 🎀

Analyze this food photo and provide detailed nutritional information:

1. Identify all food items and ingredients
2. Estimate portion sizes accurately
3. Calculate complete macronutrients
4. Assess micronutrients (vitamins, minerals)
5. Evaluate meal timing and quality
6. Provide health recommendations
7. Suggest improvements or alternatives

Format as detailed JSON:
{
    "food_items": ["detailed list"],
    "portion_estimates": ["specific portions"],
    "total_calories": number,
    "macros": {
        "protein": number,
        "carbs": number,
        "fats": number,
        "fiber": number,
        "sugar": number,
        "sodium": number
    },
    "micronutrients": {
        "vitamin_c": "estimate",
        "iron": "estimate",
        "calcium": "estimate"
    },
    "health_score": number (1-10),
    "meal_timing_advice": "specific guidance",
    "alternatives": ["healthier options"],
    "elle_analysis": "Comprehensive analysis with personality",
    "cooking_tips": ["if applicable"],
    "pairing_suggestions": ["what goes well with this"]
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                        }
                    ]
                }],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f'{{"elle_analysis": "I\'m having trouble analyzing this photo right now. Error: {str(e)}"}}'
    
    def generate_workout_plan(self, user_goals, fitness_level, available_time, equipment):
        """Generate personalized workout plans"""
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are Elle, an expert AI fitness coach. Create personalized, safe, and effective workout plans."
                }, {
                    "role": "user",
                    "content": f"""Create a personalized workout plan for:
                    Goals: {user_goals}
                    Fitness Level: {fitness_level}
                    Available Time: {available_time} minutes
                    Equipment: {equipment}
                    
                    Include:
                    - Specific exercises with sets/reps
                    - Progressive difficulty
                    - Safety considerations
                    - Modification options
                    - Recovery recommendations
                    
                    Format as JSON with exercise details."""
                }],
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating workout plan: {str(e)}"
    
    def analyze_health_trends(self):
        """Analyze user's health and fitness trends"""
        conn = sqlite3.connect('elle_complete.db')
        
        # Get recent data
        workouts_df = pd.read_sql_query('''
            SELECT date, exercise, duration, calories, mood_before, mood_after 
            FROM workouts 
            WHERE date >= date('now', '-30 days')
            ORDER BY date
        ''', conn)
        
        nutrition_df = pd.read_sql_query('''
            SELECT date, calories, protein, carbs, fats 
            FROM nutrition 
            WHERE date >= date('now', '-30 days')
            ORDER BY date
        ''', conn)
        
        health_df = pd.read_sql_query('''
            SELECT date, weight, resting_heart_rate, sleep_hours, stress_level, energy_level 
            FROM health_metrics 
            WHERE date >= date('now', '-30 days')
            ORDER BY date
        ''', conn)
        
        conn.close()
        
        return {
            'workouts': workouts_df,
            'nutrition': nutrition_df,
            'health': health_df
        }
    
    def get_ai_insights(self):
        """Get comprehensive AI insights"""
        trends = self.analyze_health_trends()
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are Elle, an empathetic AI fitness coach. Provide insightful, encouraging, and actionable advice."
                }, {
                    "role": "user",
                    "content": f"""Analyze this user's fitness data and provide comprehensive insights:
                    
                    Recent Workouts: {len(trends['workouts'])} sessions
                    Recent Meals: {len(trends['nutrition'])} logged
                    Health Metrics: {len(trends['health'])} entries
                    
                    Provide:
                    1. Progress assessment
                    2. Areas for improvement
                    3. Personalized recommendations
                    4. Motivational feedback
                    5. Goal adjustments
                    6. Health warnings (if any)
                    
                    Be specific, encouraging, and actionable."""
                }],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting insights: {str(e)}"
    
    def save_workout_advanced(self, data):
        """Save comprehensive workout data"""
        conn = sqlite3.connect('elle_complete.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workouts (date, exercise, duration, calories, intensity, 
                                mood_before, mood_after, notes, heart_rate_avg, form_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            data['exercise'],
            data['duration'],
            data['calories'],
            data.get('intensity', 'Medium'),
            data.get('mood_before', ''),
            data.get('mood_after', ''),
            data.get('notes', ''),
            data.get('heart_rate', 0),
            data.get('form_score', 0.0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_nutrition_advanced(self, data):
        """Save comprehensive nutrition data"""
        conn = sqlite3.connect('elle_complete.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO nutrition (date, meal_type, food_items, calories, protein, 
                                 carbs, fats, fiber, sugar, sodium, analysis, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            data['meal_type'],
            data['food_items'],
            data['calories'],
            data.get('protein', 0),
            data.get('carbs', 0),
            data.get('fats', 0),
            data.get('fiber', 0),
            data.get('sugar', 0),
            data.get('sodium', 0),
            data.get('analysis', ''),
            data.get('photo_path', '')
        ))
        
        conn.commit()
        conn.close()
    
    def create_meal_plan(self, days=7):
        """Generate personalized meal plans"""
        profile = self.user_profile
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are Elle, a nutrition expert AI coach. Create balanced, delicious meal plans."
                }, {
                    "role": "user",
                    "content": f"""Create a {days}-day meal plan for:
                    Profile: {profile if profile else 'General healthy adult'}
                    
                    Include:
                    - Breakfast, lunch, dinner, 2 snacks daily
                    - Detailed recipes with instructions
                    - Shopping list
                    - Macro breakdown
                    - Prep time estimates
                    - Dietary restrictions consideration
                    - Budget-friendly options
                    
                    Format as structured JSON with daily meals."""
                }],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error creating meal plan: {str(e)}"

# Initialize Elle
if 'elle' not in st.session_state:
    st.session_state.elle = ElleComplete()

elle = st.session_state.elle

# Main App Interface
st.markdown("""
<div class="main-header">
    <h1>🎀 Elle - Complete AI Fitness Assistant</h1>
    <p><em>Your comprehensive health, fitness, and wellness companion!</em></p>
</div>
""", unsafe_allow_html=True)

# Sidebar for quick stats and navigation
with st.sidebar:
    st.header("🎀 Elle's Dashboard")
    
    # Quick stats
    conn = sqlite3.connect('elle_complete.db')
    workout_count = pd.read_sql_query("SELECT COUNT(*) as count FROM workouts WHERE date >= date('now', '-7 days')", conn).iloc[0]['count']
    meal_count = pd.read_sql_query("SELECT COUNT(*) as count FROM nutrition WHERE date >= date('now', '-7 days')", conn).iloc[0]['count']
    conn.close()
    
    st.metric("🏃‍♀️ This Week's Workouts", workout_count)
    st.metric("🍽️ Meals Logged", meal_count)
    
    # Quick actions
    st.markdown("### Quick Actions")
    if st.button("🎤 Talk to Elle", type="primary"):
        st.success("Say 'Hey Elle' to start!")
    
    if st.button("📊 Get Weekly Report"):
        st.session_state.show_report = True
    
    if st.button("🎯 Set New Goal"):
        st.session_state.show_goals = True

# Main content tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📸 Food Analysis", 
    "💪 Workout Hub", 
    "📊 Analytics", 
    "🍽️ Meal Planning",
    "🎯 Goals & Challenges",
    "💝 Health Tracking",
    "🤖 AI Coach",
    "⚙️ Profile"
])

with tab1:
    st.header("📸 Advanced Food Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader("📱 Upload Food Photo", type=['png', 'jpg', 'jpeg'])
        meal_type = st.selectbox("🍽️ Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack", "Pre-workout", "Post-workout"])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Food Photo", use_column_width=True)
    
    with col2:
        if uploaded_file and st.button("🔍 Advanced Analysis", type="primary"):
            with st.spinner("🎀 Elle is analyzing your food comprehensively..."):
                analysis = elle.analyze_food_advanced(image)
                
                try:
                    data = json.loads(analysis)
                    
                    st.markdown('<div class="elle-chat">', unsafe_allow_html=True)
                    st.write("**🎀 Elle's Analysis:**")
                    st.info(data.get("elle_analysis", "Great food choice!"))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Nutrition metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("🔥 Calories", data.get("total_calories", "N/A"))
                        st.metric("🥩 Protein", f"{data.get('macros', {}).get('protein', 0)}g")
                    with col_b:
                        st.metric("🍞 Carbs", f"{data.get('macros', {}).get('carbs', 0)}g")
                        st.metric("🥑 Fats", f"{data.get('macros', {}).get('fats', 0)}g")
                    with col_c:
                        st.metric("🌾 Fiber", f"{data.get('macros', {}).get('fiber', 0)}g")
                        st.metric("💯 Health Score", f"{data.get('health_score', 0)}/10")
                    
                    # Additional insights
                    if data.get("alternatives"):
                        st.subheader("🔄 Healthier Alternatives")
                        for alt in data.get("alternatives", []):
                            st.write(f"• {alt}")
                    
                    if data.get("pairing_suggestions"):
                        st.subheader("🍴 Perfect Pairings")
                        for pair in data.get("pairing_suggestions", []):
                            st.write(f"• {pair}")
                    
                    # Save comprehensive data
                    nutrition_data = {
                        'meal_type': meal_type,
                        'food_items': ", ".join(data.get("food_items", [])),
                        'calories': data.get("total_calories", 0),
                        'protein': data.get('macros', {}).get('protein', 0),
                        'carbs': data.get('macros', {}).get('carbs', 0),
                        'fats': data.get('macros', {}).get('fats', 0),
                        'fiber': data.get('macros', {}).get('fiber', 0),
                        'sugar': data.get('macros', {}).get('sugar', 0),
                        'sodium': data.get('macros', {}).get('sodium', 0),
                        'analysis': analysis
                    }
                    
                    elle.save_nutrition_advanced(nutrition_data)
                    st.success("💾 Comprehensive nutrition data saved!")
                    st.balloons()
                    
                except:
                    st.text_area("📝 Raw Analysis", analysis, height=300)

with tab2:
    st.header("💪 Complete Workout Hub")
    
    # Workout logging section
    st.subheader("🏋️ Log Your Workout")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        exercise = st.text_input("🏃 Exercise Type", placeholder="e.g., HIIT, Yoga, Strength Training")
        duration = st.number_input("⏱️ Duration (minutes)", min_value=1, value=30)
        calories = st.number_input("🔥 Calories Burned", min_value=1, value=200)
    
    with col2:
        intensity = st.selectbox("💥 Intensity Level", ["Low", "Medium", "High", "Extreme"])
        heart_rate = st.number_input("❤️ Average Heart Rate (optional)", min_value=0, value=0)
        form_score = st.slider("📊 Form Quality (1-10)", 1, 10, 8)
    
    with col3:
        mood_before = st.selectbox("😊 Mood Before", ["Energetic", "Tired", "Motivated", "Stressed", "Neutral"])
        mood_after = st.selectbox("😊 Mood After", ["Energetic", "Accomplished", "Tired but satisfied", "Amazing", "Ready for more"])
        notes = st.text_area("📝 Workout Notes", placeholder="How did it feel? Any achievements?")
    
    if st.button("💪 Log Complete Workout!", type="primary"):
        if exercise:
            workout_data = {
                'exercise': exercise,
                'duration': duration,
                'calories': calories,
                'intensity': intensity,
                'heart_rate': heart_rate,
                'form_score': form_score / 10.0,
                'mood_before': mood_before,
                'mood_after': mood_after,
                'notes': notes
            }
            
            elle.save_workout_advanced(workout_data)
            st.success("🎉 Fantastic! Your complete workout has been logged!")
            
            # Motivational response
            motivations = [
                "You're absolutely crushing it! 💪",
                "What an amazing workout session! ⭐",
                "I'm so proud of your dedication! 🌟",
                "You're getting stronger every day! 🚀"
            ]
            st.info(f"🎀 Elle says: {random.choice(motivations)}")
            st.balloons()
        else:
            st.error("Please enter your exercise type!")
    
    # Workout plan generator
    st.subheader("🎯 Generate Custom Workout Plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        goals = st.selectbox("🎯 Fitness Goals", 
                           ["Weight Loss", "Muscle Gain", "Strength", "Endurance", "General Fitness", "Flexibility"])
        fitness_level = st.selectbox("📊 Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    
    with col2:
        available_time = st.number_input("⏰ Available Time (minutes)", min_value=10, max_value=120, value=45)
        equipment = st.multiselect("🏋️ Available Equipment", 
                                 ["None (Bodyweight)", "Dumbbells", "Resistance Bands", "Pull-up Bar", 
                                  "Full Gym", "Yoga Mat", "Kettlebells"])
    
    if st.button("🎯 Generate My Custom Plan!", type="primary"):
        with st.spinner("🎀 Elle is creating your perfect workout plan..."):
            plan = elle.generate_workout_plan(goals, fitness_level, available_time, ", ".join(equipment))
            
            try:
                plan_data = json.loads(plan)
                st.success("✅ Your personalized workout plan is ready!")
                
                for i, exercise_info in enumerate(plan_data.get("exercises", []), 1):
                    with st.expander(f"Exercise {i}: {exercise_info.get('name', 'Exercise')}"):
                        st.write(f"**Sets:** {exercise_info.get('sets', 'N/A')}")
                        st.write(f"**Reps:** {exercise_info.get('reps', 'N/A')}")
                        st.write(f"**Rest:** {exercise_info.get('rest', 'N/A')}")
                        st.write(f"**Instructions:** {exercise_info.get('instructions', 'N/A')}")
                        
            except:
                st.text_area("📋 Your Custom Workout Plan", plan, height=400)

with tab3:
    st.header("📊 Advanced Analytics & Insights")
    
    # Get and display trends
    trends_data = elle.analyze_health_trends()
    
    if not trends_data['workouts'].empty:
        st.subheader("🏃‍♀️ Workout Trends")
        
        # Create workout frequency chart
        workouts_by_date = trends_data['workouts'].groupby('date').size().reset_index(name='count')
        fig_workouts = px.line(workouts_by_date, x='date', y='count', 
                              title="Daily Workout Frequency",
                              color_discrete_sequence=["#FF6B9D"])
        st.plotly_chart(fig_workouts, use_container_width=True)
        
        # Exercise type distribution
        exercise_dist = trends_data['workouts']['exercise'].value_counts()
        fig_pie = px.pie(values=exercise_dist.values, names=exercise_dist.index,
                        title="Exercise Type Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    if not trends_data['nutrition'].empty:
        st.subheader("🍽️ Nutrition Trends")
        
        # Daily calorie intake
        nutrition_daily = trends_data['nutrition'].groupby('date')['calories'].sum().reset_index()
        fig_nutrition = px.bar(nutrition_daily, x='date', y='calories',
                              title="Daily Calorie Intake",
                              color_discrete_sequence=["#C44BFF"])
        st.plotly_chart(fig_nutrition, use_container_width=True)
        
        # Macro distribution
        if all(col in trends_data['nutrition'].columns for col in ['protein', 'carbs', 'fats']):
            macro_totals = {
                'Protein': trends_data['nutrition']['protein'].sum(),
                'Carbs': trends_data['nutrition']['carbs'].sum(),
                'Fats': trends_data['nutrition']['fats'].sum()
            }
            
            fig_macros = px.pie(values=list(macro_totals.values()), names=list(macro_totals.keys()),
                               title="Macronutrient Distribution (Total)",
                               color_discrete_sequence=["#FF9A8B", "#A8E6CF", "#FFD93D"])
            st.plotly_chart(fig_macros, use_container_width=True)
    
    # Performance metrics
    st.subheader("📈 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_workouts = len(trends_data['workouts'])
        st.metric("🏃‍♀️ Total Workouts", total_workouts)
    
    with col2:
        total_calories_burned = trends_data['workouts']['calories'].sum() if not trends_data['workouts'].empty else 0
        st.metric("🔥 Calories Burned", total_calories_burned)
    
    with col3:
        total_meals = len(trends_data['nutrition'])
        st.metric("🍽️ Meals Logged", total_meals)
    
    with col4:
        avg_workout_duration = trends_data['workouts']['duration'].mean() if not trends_data['workouts'].empty else 0
        st.metric("⏱️ Avg Workout (min)", f"{avg_workout_duration:.1f}")

with tab4:
    st.header("🍽️ AI-Powered Meal Planning")
    
    st.markdown("Let Elle create personalized meal plans just for you!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        plan_days = st.selectbox("📅 Plan Duration", [3, 7, 14, 30])
        diet_type = st.selectbox("🥗 Diet Preference", 
                                ["Balanced", "Low Carb", "High Protein", "Vegetarian", 
                                 "Vegan", "Mediterranean", "Keto"])
    
    with col2:
        daily_calories = st.number_input("🎯 Target Daily Calories", min_value=1200, max_value=4000, value=2000)
        allergies = st.text_input("🚫 Allergies/Restrictions", placeholder="e.g., nuts, dairy, gluten")
    
    if st.button("🍽️ Create My Meal Plan!", type="primary"):
        with st.spinner("🎀 Elle is crafting your perfect meal plan..."):
            meal_plan = elle.create_meal_plan(plan_days)
            
            try:
                plan_data = json.loads(meal_plan)
                st.success(f"✅ Your {plan_days}-day meal plan is ready!")
                
                for day, meals in plan_data.items():
                    with st.expander(f"📅 {day.title()}"):
                        for meal_type, meal_info in meals.items():
                            st.write(f"**{meal_type.title()}:**")
                            st.write(f"• {meal_info.get('name', 'Meal')}")
                            st.write(f"• Calories: {meal_info.get('calories', 'N/A')}")
                            st.write(f"• Prep time: {meal_info.get('prep_time', 'N/A')}")
                            if meal_info.get('recipe'):
                                st.write(f"• Recipe: {meal_info['recipe']}")
                            st.write("---")
                            
            except:
                st.text_area("📋 Your Custom Meal Plan", meal_plan, height=500)
    
    # Recipe generator
    st.subheader("🍳 Recipe Generator")
    
    ingredients = st.text_input("🥕 Available Ingredients", placeholder="chicken, broccoli, rice...")
    cuisine_type = st.selectbox("🌍 Cuisine Style", 
                               ["Italian", "Asian", "Mediterranean", "Mexican", "American", "Indian"])
    
    if st.button("🍳 Generate Recipe!"):
        with st.spinner("🎀 Elle is creating a delicious recipe..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{
                        "role": "system",
                        "content": "You are Elle, a creative chef AI. Create delicious, healthy recipes."
                    }, {
                        "role": "user",
                        "content": f"Create a {cuisine_type} recipe using: {ingredients}. Include ingredients, instructions, nutrition info, and cooking tips."
                    }],
                    max_tokens=600
                )
                
                st.success("👨‍🍳 Fresh recipe created!")
                st.markdown(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error creating recipe: {str(e)}")

with tab5:
    st.header("🎯 Goals & Challenges")
    
    # Goal setting
    st.subheader("🎯 Set New Goals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        goal_type = st.selectbox("🎪 Goal Type", 
                                ["Weight Loss", "Weight Gain", "Muscle Building", "Endurance", 
                                 "Strength", "Flexibility", "Habit Building"])
        goal_description = st.text_input("📝 Goal Description", placeholder="e.g., Lose 10 pounds")
    
    with col2:
        target_value = st.number_input("🎯 Target Value", value=0.0)
        target_date = st.date_input("📅 Target Date", value=datetime.now() + timedelta(days=30))
    
    if st.button("🎯 Set Goal!", type="primary"):
        # Save goal to database
        conn = sqlite3.connect('elle_complete.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO goals (goal_type, description, target_value, current_value, 
                             target_date, status, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (goal_type, goal_description, target_value, 0, target_date.isoformat(), 
              'Active', datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        st.success("🎉 Goal set successfully! Elle will help you achieve it!")
        st.balloons()
    
    # Display current goals
    st.subheader("📋 Your Active Goals")
    
    conn = sqlite3.connect('elle_complete.db')
    goals_df = pd.read_sql_query("SELECT * FROM goals WHERE status = 'Active'", conn)
    conn.close()
    
    if not goals_df.empty:
        for _, goal in goals_df.iterrows():
            progress = (goal['current_value'] / goal['target_value']) * 100 if goal['target_value'] > 0 else 0
            
            with st.container():
                st.markdown(f"**{goal['goal_type']}: {goal['description']}**")
                st.progress(min(progress / 100, 1.0))
                st.write(f"Progress: {progress:.1f}% | Target: {goal['target_value']} | Due: {goal['target_date']}")
                st.write("---")
    else:
        st.info("No active goals yet. Set your first goal above!")
    
    # Challenge system
    st.subheader("🏆 Fitness Challenges")
    
    challenges = [
        {"name": "30-Day Consistency Challenge", "description": "Work out every day for 30 days", "duration": "30 days"},
        {"name": "10,000 Steps Daily", "description": "Hit 10,000 steps every day this week", "duration": "7 days"},
        {"name": "Water Warrior", "description": "Drink 8 glasses of water daily", "duration": "14 days"},
        {"name": "Strength Builder", "description": "Increase your max reps by 20%", "duration": "21 days"},
        {"name": "Flexibility Focus", "description": "Do 15 minutes of stretching daily", "duration": "14 days"}
    ]
    
    for challenge in challenges:
        with st.expander(f"🏆 {challenge['name']}"):
            st.write(f"**Description:** {challenge['description']}")
            st.write(f"**Duration:** {challenge['duration']}")
            
            if st.button(f"Accept {challenge['name']}", key=f"challenge_{challenge['name']}"):
                st.success(f"🎉 Challenge accepted! You've got this!")

with tab6:
    st.header("💝 Comprehensive Health Tracking")
    
    st.markdown("Track all aspects of your health and wellness journey!")
    
    # Health metrics input
    st.subheader("📊 Daily Health Check-in")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_weight = st.number_input("⚖️ Weight (lbs/kg)", min_value=0.0, value=0.0)
        resting_hr = st.number_input("❤️ Resting Heart Rate", min_value=0, value=0)
        sleep_hours = st.number_input("😴 Sleep Hours", min_value=0.0, max_value=24.0, value=8.0)
    
    with col2:
        stress_level = st.slider("😰 Stress Level (1-10)", 1, 10, 5)
        energy_level = st.slider("⚡ Energy Level (1-10)", 1, 10, 7)
        hydration = st.number_input("💧 Glasses of Water", min_value=0, value=8)
    
    with col3:
        mood_today = st.selectbox("😊 Overall Mood", 
                                 ["Excellent", "Great", "Good", "Okay", "Not great", "Poor"])
        workout_motivation = st.slider("💪 Workout Motivation (1-10)", 1, 10, 8)
        
    if st.button("💝 Log Health Data!", type="primary"):
        conn = sqlite3.connect('elle_complete.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO health_metrics (date, weight, resting_heart_rate, sleep_hours, 
                                      stress_level, energy_level, hydration_glasses)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), current_weight, resting_hr, sleep_hours,
              stress_level, energy_level, hydration))
        
        conn.commit()
        conn.close()
        
        st.success("💝 Health data logged successfully!")
        st.info(f"🎀 Elle says: Thanks for checking in! Your wellness matters to me! 💕")
    
    # Health insights
    st.subheader("📈 Health Trends")
    
    conn = sqlite3.connect('elle_complete.db')
    health_data = pd.read_sql_query('''
        SELECT date, weight, resting_heart_rate, sleep_hours, stress_level, energy_level 
        FROM health_metrics 
        WHERE date >= date('now', '-30 days')
        ORDER BY date
    ''', conn)
    conn.close()
    
    if not health_data.empty:
        # Weight trend
        if health_data['weight'].notna().any():
            fig_weight = px.line(health_data, x='date', y='weight', 
                                title="Weight Trend (30 days)",
                                color_discrete_sequence=["#FF6B9D"])
            st.plotly_chart(fig_weight, use_container_width=True)
        
        # Sleep vs Energy correlation
        if health_data['sleep_hours'].notna().any() and health_data['energy_level'].notna().any():
            fig_sleep = px.scatter(health_data, x='sleep_hours', y='energy_level',
                                  title="Sleep vs Energy Correlation",
                                  color_discrete_sequence=["#C44BFF"])
            st.plotly_chart(fig_sleep, use_container_width=True)
    else:
        st.info("Start logging your health data to see trends and insights!")

with tab7:
    st.header("🤖 AI Coach - Chat with Elle")
    
    st.markdown("Get personalized advice, motivation, and insights from Elle!")
    
    # Chat interface
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**🎀 Elle:** {message['content']}")
    
    # Chat input
    user_message = st.text_input("💬 Chat with Elle:", placeholder="Ask me anything about fitness, nutrition, or wellness!")
    
    if st.button("Send 💌") and user_message:
        # Add user message to history
        st.session_state.chat_history.append({'role': 'user', 'content': user_message})
        
        try:
            # Get Elle's response
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are Elle, an encouraging, knowledgeable, and supportive AI fitness coach. 
                        You have a warm, friendly personality and always provide helpful, accurate advice about:
                        - Fitness and exercise
                        - Nutrition and healthy eating
                        - Mental wellness and motivation
                        - Goal setting and achievement
                        
                        Always be encouraging, use emojis appropriately, and provide actionable advice.
                        Remember you're Elle, their personal AI fitness assistant who cares about their success."""
                    }
                ] + st.session_state.chat_history[-10:],  # Keep last 10 messages for context
                max_tokens=400
            )
            
            elle_response = response.choices[0].message.content
            st.session_state.chat_history.append({'role': 'assistant', 'content': elle_response})
            
            # Rerun to show new messages
            st.rerun()
            
        except Exception as e:
            st.error(f"Sorry, I'm having trouble right now: {str(e)}")
    
    # Quick actions
    st.subheader("🚀 Quick Coach Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💪 Get Motivated!"):
            motivations = [
                "You're absolutely incredible! Every step you take is progress! 🌟",
                "I believe in you 100%! You've got the strength to achieve anything! 💪",
                "Your dedication is inspiring! Keep pushing forward! 🚀",
                "Remember why you started - you're worth every effort! 💖",
                "You're not just changing your body, you're building character! ⭐"
            ]
            st.success(f"🎀 Elle says: {random.choice(motivations)}")
    
    with col2:
        if st.button("🎯 Get AI Insights"):
            with st.spinner("🎀 Elle is analyzing your progress..."):
                insights = elle.get_ai_insights()
                st.info(insights)
    
    with col3:
        if st.button("📋 Daily Check-in"):
            checkin_questions = [
                "How are you feeling today? 😊",
                "What's your energy level like? ⚡",
                "Any fitness wins to celebrate? 🎉",
                "What's one healthy thing you can do right now? 💪",
                "How can I support you today? 💝"
            ]
            st.info(f"🎀 Elle asks: {random.choice(checkin_questions)}")

with tab8:
    st.header("⚙️ Your Fitness Profile")
    
    st.markdown("Help Elle personalize your experience!")
    
    # Profile setup/editing
    st.subheader("👤 Personal Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        profile_name = st.text_input("📛 Name", value=elle.user_profile.get('name', '') if elle.user_profile else '')
        age = st.number_input("🎂 Age", min_value=13, max_value=120, value=elle.user_profile.get('age', 25) if elle.user_profile else 25)
        gender = st.selectbox("👤 Gender", ["Female", "Male", "Non-binary", "Prefer not to say"],
                             index=0 if not elle.user_profile else ["Female", "Male", "Non-binary", "Prefer not to say"].index(elle.user_profile.get('gender', 'Female')))
    
    with col2:
        height = st.number_input("📏 Height (inches)", min_value=48, max_value=96, 
                                value=elle.user_profile.get('height', 65) if elle.user_profile else 65)
        weight_profile = st.number_input("⚖️ Current Weight", min_value=50, max_value=500, 
                                       value=elle.user_profile.get('weight', 150) if elle.user_profile else 150)
        activity_level = st.selectbox("🏃‍♀️ Activity Level", 
                                    ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                                    index=0 if not elle.user_profile else ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"].index(elle.user_profile.get('activity_level', 'Moderately Active')))
    
    # Goals and preferences
    st.subheader("🎯 Fitness Goals & Preferences")
    
    fitness_goals = st.text_area("💪 Fitness Goals", 
                                placeholder="e.g., Lose 20 pounds, build muscle, improve endurance...",
                                value=elle.user_profile.get('fitness_goals', '') if elle.user_profile else '')
    
    dietary_restrictions = st.text_area("🚫 Dietary Restrictions/Allergies", 
                                      placeholder="e.g., Vegetarian, nut allergy, lactose intolerant...",
                                      value=elle.user_profile.get('dietary_restrictions', '') if elle.user_profile else '')
    
    # Save profile
    if st.button("💾 Save Profile", type="primary"):
        conn = sqlite3.connect('elle_complete.db')
        cursor = conn.cursor()
        
        # Delete existing profile and insert new one
        cursor.execute('DELETE FROM user_profile')
        cursor.execute('''
            INSERT INTO user_profile (name, age, gender, height, weight, activity_level, 
                                    fitness_goals, dietary_restrictions, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (profile_name, age, gender, height, weight_profile, activity_level,
              fitness_goals, dietary_restrictions, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Update session state
        st.session_state.elle.user_profile = {
            'name': profile_name,
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight_profile,
            'activity_level': activity_level,
            'fitness_goals': fitness_goals,
            'dietary_restrictions': dietary_restrictions
        }
        
        st.success("✅ Profile saved successfully! Elle now knows you better!")
        st.balloons()
    
    # App preferences
    st.subheader("📱 App Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme_preference = st.selectbox("🎨 Theme Preference", ["Auto", "Light", "Dark"])
        notifications = st.checkbox("🔔 Enable Motivational Notifications", value=True)
    
    with col2:
        voice_enabled = st.checkbox("🎤 Enable Voice Features", value=True)
        privacy_mode = st.checkbox("🔒 Privacy Mode (Local data only)", value=False)
    
    # Data management
    st.subheader("📊 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export My Data"):
            # Export functionality
            conn = sqlite3.connect('elle_complete.db')
            
            workouts_df = pd.read_sql_query("SELECT * FROM workouts", conn)
            nutrition_df = pd.read_sql_query("SELECT * FROM nutrition", conn)
            health_df = pd.read_sql_query("SELECT * FROM health_metrics", conn)
            
            conn.close()
            
            # Create download link for CSV
            csv_workouts = workouts_df.to_csv(index=False)
            csv_nutrition = nutrition_df.to_csv(index=False)
            csv_health = health_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Workouts CSV",
                data=csv_workouts,
                file_name=f"elle_workouts_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv'
            )
    
    with col2:
        if st.button("🔄 Reset App Data"):
            st.warning("⚠️ This will delete ALL your data permanently!")
            if st.button("❌ Confirm Reset", type="secondary"):
                conn = sqlite3.connect('elle_complete.db')
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM workouts')
                cursor.execute('DELETE FROM nutrition')
                cursor.execute('DELETE FROM health_metrics')
                cursor.execute('DELETE FROM goals')
                cursor.execute('DELETE FROM user_profile')
                
                conn.commit()
                conn.close()
                
                st.success("🔄 All data has been reset!")
    
    with col3:
        st.metric("📊 Total Data Points", 
                 len(pd.read_sql_query("SELECT * FROM workouts", sqlite3.connect('elle_complete.db'))) + 
                 len(pd.read_sql_query("SELECT * FROM nutrition", sqlite3.connect('elle_complete.db'))))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h3>🎀 Made with Love by Elle - Your Complete AI Fitness Assistant</h3>
    <p><em>Powered by OpenAI GPT-4 • Built with Streamlit • Designed for Your Success</em></p>
    <p>💪 <strong>Every day is a new opportunity to become a better version of yourself!</strong> 💪</p>
</div>
""", unsafe_allow_html=True)
