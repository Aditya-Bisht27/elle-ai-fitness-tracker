import streamlit as st
import openai
import sqlite3
import datetime
import base64
from PIL import Image
from io import BytesIO
import json

# Page config
st.set_page_config(
    page_title="Elle - AI Fitness Tracker", 
    page_icon="🎀", 
    layout="wide"
)

# Initialize OpenAI
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

class ElleTracker:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect('elle_fitness.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY,
                date TEXT,
                exercise TEXT,
                duration INTEGER,
                calories INTEGER,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition (
                id INTEGER PRIMARY KEY,
                date TEXT,
                meal_type TEXT,
                food_items TEXT,
                calories INTEGER,
                analysis TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_food(self, image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Hi! I'm Elle, your AI fitness assistant! 🎀
                            
Let me analyze this food photo for you and estimate:
- Food items I can identify
- Portion sizes
- Total calories
- Protein, carbs, and fats

Format as JSON:
{
    "food_items": ["item1", "item2"],
    "total_calories": number,
    "protein": number,
    "carbs": number,
    "fats": number,
    "elle_says": "Encouraging analysis from Elle"
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"image/jpeg;base64,{img_base64}"}
                        }
                    ]
                }],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f'{{"elle_says": "Sorry! I\'m having trouble analyzing this photo right now. Error: {str(e)}"}}'
    
    def save_workout(self, exercise, duration, calories, notes=""):
        conn = sqlite3.connect('elle_fitness.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO workouts (date, exercise, duration, calories, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.datetime.now().isoformat(), exercise, duration, calories, notes))
        conn.commit()
        conn.close()
    
    def save_nutrition(self, meal_type, food_items, calories, analysis):
        conn = sqlite3.connect('elle_fitness.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO nutrition (date, meal_type, food_items, calories, analysis)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.datetime.now().isoformat(), meal_type, food_items, calories, analysis))
        conn.commit()
        conn.close()
    
    def get_recent_workouts(self):
        conn = sqlite3.connect('elle_fitness.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM workouts ORDER BY date DESC LIMIT 10')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_recent_nutrition(self):
        conn = sqlite3.connect('elle_fitness.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM nutrition ORDER BY date DESC LIMIT 10')
        results = cursor.fetchall()
        conn.close()
        return results

# Initialize Elle
if 'elle' not in st.session_state:
    st.session_state.elle = ElleTracker()

elle = st.session_state.elle

# Main App Interface
st.title("🎀 Elle - Your AI Fitness Assistant")
st.markdown("### *Hi! I'm Elle, your personal AI fitness coach! Let's track your health journey together!* 💪✨")

# Check API key
if "OPENAI_API_KEY" not in st.secrets:
    st.error("🔑 Please add your OpenAI API key in Streamlit Cloud secrets!")
    st.info("Go to your app settings → Secrets → Add: OPENAI_API_KEY = 'your-key-here'")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📸 Food Analysis", "💪 Workout Tracker", "📊 Dashboard", "🎯 Elle's Insights"])

with tab1:
    st.header("📸 Food Photo Analysis with Elle")
    st.markdown("*Upload a photo of your meal and I'll analyze it for you!* 🍽️")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader("📱 Take or Upload Food Photo", type=['png', 'jpg', 'jpeg'])
        meal_type = st.selectbox("🍽️ What meal is this?", ["Breakfast", "Lunch", "Dinner", "Snack"])
    
    with col2:
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Food Photo", use_column_width=True)
            
            if st.button("🔍 Let Elle Analyze This!", type="primary"):
                with st.spinner("🎀 Elle is analyzing your food..."):
                    analysis = elle.analyze_food(image)
                    
                    try:
                        data = json.loads(analysis)
                        
                        st.success("✅ Analysis Complete!")
                        
                        # Display results
                        st.subheader("🎀 Elle Says:")
                        st.info(data.get("elle_says", "Great choice!"))
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("🔥 Total Calories", data.get("total_calories", "N/A"))
                            st.metric("🥩 Protein (g)", data.get("protein", "N/A"))
                        with col_b:
                            st.metric("🍞 Carbs (g)", data.get("carbs", "N/A"))
                            st.metric("🥑 Fats (g)", data.get("fats", "N/A"))
                        
                        # Save data
                        food_list = ", ".join(data.get("food_items", []))
                        elle.save_nutrition(meal_type, food_list, data.get("total_calories", 0), analysis)
                        st.success("💾 Saved to your nutrition log!")
                        
                    except:
                        st.text_area("📝 Raw Analysis", analysis, height=200)

with tab2:
    st.header("💪 Workout Tracker")
    st.markdown("*Tell me about your workout and I'll log it for you!* 🏃‍♀️")
    
    col1, col2 = st.columns(2)
    
    with col1:
        exercise = st.text_input("🏋️ Exercise Type", placeholder="e.g., Running, Yoga, Weight lifting")
        duration = st.number_input("⏱️ Duration (minutes)", min_value=1, value=30)
    
    with col2:
        calories = st.number_input("🔥 Calories Burned (estimate)", min_value=1, value=200)
        notes = st.text_area("📝 How did it feel?", placeholder="Great session! Felt energetic...")
    
    if st.button("💪 Log My Workout!", type="primary"):
        if exercise:
            elle.save_workout(exercise, duration, calories, notes)
            st.success("🎉 Awesome! I've logged your workout. Keep up the great work!")
            st.balloons()
        else:
            st.error("Please tell me what exercise you did!")

with tab3:
    st.header("📊 Your Fitness Dashboard")
    st.markdown("*Here's how you're doing! I'm so proud of your progress!* 📈")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏃‍♀️ Recent Workouts")
        workouts = elle.get_recent_workouts()
        if workouts:
            for workout in workouts[:5]:
                date = workout[1][:10]  # Just the date part
                st.write(f"**{workout[2]}** - {workout[3]} min, {workout[4]} cal ({date})")
        else:
            st.info("No workouts yet! Ready to start? 💪")
    
    with col2:
        st.subheader("🍽️ Recent Meals")
        nutrition = elle.get_recent_nutrition()
        if nutrition:
            for meal in nutrition[:5]:
                date = meal[1][:10]
                st.write(f"**{meal[2]}**: {meal[3]} - {meal[4]} cal ({date})")
        else:
            st.info("No meals logged yet! Upload a food photo to start! 📸")

with tab4:
    st.header("🎯 Elle's Personal Insights")
    st.markdown("*Let me give you some personalized advice!* 💡")
    
    if st.button("🤖 Get Elle's Recommendations", type="primary"):
        workouts = elle.get_recent_workouts()
        nutrition = elle.get_recent_nutrition()
        
        workout_count = len(workouts)
        nutrition_count = len(nutrition)
        
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are Elle, an encouraging AI fitness coach. Be supportive, personal, and motivating."
                }, {
                    "role": "user",
                    "content": f"I've logged {workout_count} workouts and {nutrition_count} meals recently. Give me personalized fitness and nutrition advice as Elle, my encouraging AI coach."
                }],
                max_tokens=300
            )
            
            st.success("🎀 Elle's Personal Message for You:")
            st.info(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Sorry, I'm having trouble generating insights right now: {str(e)}")
    
    # Motivational section
    st.subheader("🌟 Daily Motivation")
    motivational_quotes = [
        "You're stronger than you think! 💪",
        "Every workout counts, no matter how small! 🌟",
        "Progress, not perfection! You've got this! 🚀",
        "Your body can do it. It's your mind you need to convince! 🧠",
        "The only bad workout is the one you didn't do! ✨"
    ]
    
    import random
    quote = random.choice(motivational_quotes)
    st.success(f"🎀 Elle says: {quote}")

# Footer
st.markdown("---")
st.markdown("🎀 *Made with love by Elle - Your AI Fitness Assistant* | Powered by OpenAI GPT-4")
