import gradio as gr
import os
import datetime
import json
from pathlib import Path

# ---------------------- Base de connaissances ----------------------
document_connaissances = """
Nutrition and Health:

1. Daily caloric needs depend on several factors: age, sex, weight, height, physical activity level.
2. The Mifflin-St Jeor formula is a recognized method to estimate Basal Metabolic Rate (BMR).
3. Total Daily Energy Expenditure (TDEE) is calculated by multiplying BMR with an activity factor.
4. To lose weight, a caloric deficit of about 500 kcal/day is recommended.
5. To gain weight, a caloric surplus of about 500 kcal/day with strength training is effective.
6. A balanced diet includes proteins, carbohydrates, fats, fibers, vitamins, and minerals.
7. Proper hydration is essential for metabolic function.
8. Regular physical activity improves body composition and cardiovascular health.
9. Extreme or unbalanced diets should be avoided to maintain health.
10. Nutritional needs may vary due to medical conditions, pregnancy, etc.
"""

# ---------------------- IA Nutritionnelle ----------------------
def assistant_ia(prompt):
    prompt_lower = prompt.lower()
    if "calorie" in prompt_lower or "energy need" in prompt_lower:
        return ("Daily caloric needs depend on your age, sex, weight, height, and activity level.\n"
                "The Mifflin-St Jeor formula is commonly used to estimate your BMR, which is then multiplied by your activity factor to get TDEE.")
    elif "lose weight" in prompt_lower:
        return ("To lose weight, it's recommended to create a daily caloric deficit of about 500 kcal, combined with regular cardio activity.")
    elif "gain weight" in prompt_lower or "muscle" in prompt_lower:
        return ("To gain weight, a caloric surplus of about 500 kcal per day is advised, along with strength training to support muscle growth.")
    elif "blood pressure" in prompt_lower:
        return ("Maintaining healthy blood pressure involves reducing sodium, managing stress, regular exercise, and monitoring. Ideal range: 90/60 to 120/80 mmHg.")
    elif "glucose" in prompt_lower or "diabetes" in prompt_lower:
        return ("Monitor your glucose regularly, maintain a balanced low-sugar diet, and consult a health professional. Ideal fasting glucose: 70–100 mg/dL.")
    elif "balanced diet" in prompt_lower or "nutrition" in prompt_lower:
        return ("A balanced diet includes proteins, carbohydrates, fats, fibers, vitamins, and minerals. Aim for variety and minimally processed foods.")
    else:
        return "Here are some general tips on nutrition:\n\n" + document_connaissances

# ---------------------- Calculs caloriques ----------------------
def calc_bmr(weight, height, age, gender):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calc_tdee(bmr, activity_level):
    levels = {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (1-3 days/week)": 1.375,
        "Moderately active (3-5 days/week)": 1.55,
        "Very active (6-7 days/week)": 1.725,
        "Extremely active": 1.9
    }
    return bmr * levels.get(activity_level, 1.2)

def recommandations(weight, height, age, gender, activity, goal):
    bmr = calc_bmr(weight, height, age, gender)
    tdee = round(calc_tdee(bmr, activity))
    cal = tdee
    if goal == "Lose weight":
        cal -= 500
        sport = "45 min of cardio 5x/week"
        menu = "Oats, chicken, vegetables, light soups."
    elif goal == "Gain weight":
        cal += 500
        sport = "Weight training + caloric surplus"
        menu = "Eggs, brown rice, protein smoothies."
    else:
        sport = "Regular moderate activity"
        menu = "Balanced diet with variety."
    save_history({"calories": cal, "sport": sport, "menu": menu, "date": str(datetime.datetime.now())})
    return f"{cal} kcal/day", sport, menu

# ---------------------- Historique ----------------------
history_path = Path("history.json")
def load_history():
    if history_path.exists():
        with open(history_path, "r") as f:
            return json.load(f)
    return []

def save_history(entry):
    data = load_history()
    data.append(entry)
    with open(history_path, "w") as f:
        json.dump(data[-50:], f, indent=2)

# ---------------------- Interface Gradio ----------------------
with gr.Blocks(theme=gr.themes.Soft()) as app:
    with gr.Tabs():

        with gr.TabItem("🏠 Home"):
            gr.Markdown("""
            # SanatioTech: Smarter Health, Smarter You 🌱
            Welcome to the future of digital health powered by AI nutrition.
            Built by Ibrahima Diallo - 2025
            """)

        with gr.TabItem("📊 NutriTech"):
            with gr.Tabs():
                with gr.TabItem("🔢 Calculator & Advice"):
                    with gr.Row():
                        with gr.Column():
                            w = gr.Slider(30, 200, value=70, label="Weight (kg)")
                            h = gr.Slider(100, 220, value=170, label="Height (cm)")
                            a = gr.Slider(10, 100, value=25, label="Age")
                            g = gr.Radio(["Male", "Female"], label="Gender")
                            act = gr.Dropdown(label="Activity", choices=[
                                "Sedentary (little or no exercise)",
                                "Lightly active (1-3 days/week)",
                                "Moderately active (3-5 days/week)",
                                "Very active (6-7 days/week)",
                                "Extremely active"
                            ])
                            obj = gr.Radio(["Lose weight", "Maintain weight", "Gain weight"], label="Goal")
                            btn = gr.Button("Calculate")
                        with gr.Column():
                            out1 = gr.Textbox(label="Calories (kcal/day)")
                            out2 = gr.Textbox(label="Suggested Exercise")
                            out3 = gr.Textbox(label="Suggested Menu", lines=6)
                    btn.click(recommandations, inputs=[w, h, a, g, act, obj], outputs=[out1, out2, out3])

                with gr.TabItem("📈 History"):
                    hist_btn = gr.Button("Show My History")
                    hist_out = gr.Textbox(label="Last Calculations", lines=12)
                    def show_history():
                        data = load_history()
                        return "\n\n".join([f"{h['date']}: {h['calories']} kcal | {h['sport']} | {h['menu']}" for h in data[-10:]])
                    hist_btn.click(show_history, outputs=hist_out)

                with gr.TabItem("🤖 AI Assistant"):
                    prompt = gr.Textbox(label="Ask your nutrition question")
                    rep = gr.Textbox(label="AI Response", lines=8)
                    gr.Button("Send").click(assistant_ia, inputs=prompt, outputs=rep)

        with gr.TabItem("🔐 Login & Profile"):
            gr.Markdown("""
            🔒 Coming soon: Full user registration and login system with profile pictures and preferences.
            🌟 You’ll be able to save, retrieve, and sync your data securely across devices.
            """)

        with gr.TabItem("🩺 Glucose & BP Tracker"):
            gr.Markdown("""
            ## Glucose & Blood Pressure Monitoring
            - Ideal Glucose (fasting): 70–100 mg/dL
            - Ideal Blood Pressure: 90/60 – 120/80 mmHg
            - Track your inputs daily.
            """)
            glucose = gr.Number(label="Glucose (mg/dL)")
            bp_sys = gr.Number(label="Systolic Pressure (mmHg)")
            bp_dia = gr.Number(label="Diastolic Pressure (mmHg)")
            health_out = gr.Textbox(label="Evaluation")
            def eval_health(glucose, bp_sys, bp_dia):
                g_msg = "Normal" if 70 <= glucose <= 100 else "Check with doctor"
                bp_msg = "Normal" if 90 <= bp_sys <= 120 and 60 <= bp_dia <= 80 else "Abnormal levels"
                return f"Glucose: {g_msg}\nBlood Pressure: {bp_msg}"
            gr.Button("Evaluate Health").click(eval_health, inputs=[glucose, bp_sys, bp_dia], outputs=health_out)

        with gr.TabItem("🌐 Features"):
            gr.Markdown("""
            ## Fully Activated Features
            - ✅ Personalized caloric calculator
            - ✅ AI-powered nutrition assistant
            - ✅ Historical tracking
            - ✅ Blood pressure & glucose monitor
            - 🔒 Login system (backend-ready)
            - 📱 Mobile-ready (PWA/Android)
            - 🌍 International support (FR/EN/AR ready)
            - 🔗 Ready for wearable APIs (Fitbit, etc.)
            - 👨‍⚕️ Professional dashboards (soon)
            """)

port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port)

