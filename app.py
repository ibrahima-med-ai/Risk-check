import gradio as gr
import os
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

# Texte de connaissances nutritionnelles intégrées (inchangé)
document_connaissances = """
Nutrition et santé :

1. Le besoin calorique journalier dépend de plusieurs facteurs : âge, sexe, poids, taille, niveau d'activité physique.
2. La formule de Mifflin-St Jeor est une méthode reconnue pour estimer le métabolisme de base (BMR).
3. Le total des dépenses énergétiques journalières (TDEE) est le BMR multiplié par un facteur d'activité.
4. Pour perdre du poids, un déficit calorique d'environ 500 kcal/jour est recommandé.
5. Pour gagner du poids, un surplus calorique d'environ 500 kcal/jour avec entraînement de musculation est efficace.
6. Une alimentation équilibrée doit contenir protéines, glucides, lipides, fibres, vitamines et minéraux.
7. L’hydratation est essentielle au bon fonctionnement du métabolisme.
8. L’activité physique régulière améliore la composition corporelle et la santé cardiovasculaire.
9. Les régimes drastiques ou déséquilibrés sont à éviter pour préserver la santé.
10. Les besoins nutritionnels peuvent varier en fonction de pathologies, grossesse, etc.
"""

def assistant_ia(prompt):
    prompt_lower = prompt.lower()
    if "calorie" in prompt_lower or "besoin énergétique" in prompt_lower:
        return ("Le besoin calorique journalier dépend de votre âge, sexe, poids, taille et activité physique.\n"
                "On utilise souvent la formule de Mifflin-St Jeor pour estimer le métabolisme de base (BMR), "
                "puis on ajuste selon le niveau d’activité pour obtenir le total des dépenses énergétiques (TDEE).")
    elif "perdre du poids" in prompt_lower:
        return ("Pour perdre du poids, il est recommandé de créer un déficit calorique d'environ 500 kcal par jour, "
                "accompagné d'une activité physique régulière, notamment du cardio.")
    elif "gagner du poids" in prompt_lower or "prise de masse" in prompt_lower:
        return ("Pour gagner du poids, un surplus calorique d'environ 500 kcal par jour est conseillé, "
                "associé à un entraînement de musculation pour favoriser la prise de masse musculaire.")
    elif "alimentation équilibrée" in prompt_lower or "nutrition" in prompt_lower:
        return ("Une alimentation équilibrée comprend des protéines, glucides, lipides, fibres, vitamines et minéraux. "
                "Il est important de privilégier des aliments variés et non transformés.")
    else:
        return "Voici quelques informations générales sur la nutrition:\n\n" + document_connaissances

def calc_bmr(weight, height, age, gender):
    if gender == "Homme":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calc_tdee(bmr, activity_level):
    levels = {
        "Sédentaire (peu ou pas d'exercice)": 1.2,
        "Légèrement actif (1-3 jours/semaine)": 1.375,
        "Modérément actif (3-5 jours/semaine)": 1.55,
        "Très actif (6-7 jours/semaine)": 1.725,
        "Extrêmement actif": 1.9
    }
    return bmr * levels.get(activity_level, 1.2)

def recommandations(weight, height, age, gender, activity, goal):
    bmr = calc_bmr(weight, height, age, gender)
    tdee = round(calc_tdee(bmr, activity))
    cal = tdee
    if goal == "Perdre du poids":
        cal -= 500
        sport = "45 min de cardio 5x/semaine"
        menu = "Avoine, poulet, légumes, soupes légères."
    elif goal == "Gagner du poids":
        cal += 500
        sport = "Musculation + surplus calorique"
        menu = "Œufs, riz complet, smoothie protéiné."
    else:
        sport = "Activité modérée régulière"
        menu = "Régime équilibré avec variété d'aliments."
    return f"{cal} kcal/jour", sport, menu

# ------------------- Interface Gradio --------------------

BANNER_URL = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"

with gr.Blocks(theme=gr.themes.Base()) as gradio_app:
    with gr.Tabs():
        with gr.TabItem("🏠 Accueil"):
            gr.Image(value=BANNER_URL, show_label=False, interactive=False)
            gr.Markdown("🚀 **SanatioTech : La Révolution Technologique pour une Santé Plus Intelligente !**\n\n[...]")

        with gr.TabItem("📊 NutriTech"):
            with gr.Tabs():
                with gr.TabItem("📅 Présentation"):
                    gr.Markdown("🌿 **NutriTech 🧠 – L’intelligence de la nutrition au service de votre santé**\n\n[...]")
                with gr.TabItem("🔢 Calcul & conseils"):
                    with gr.Row():
                        with gr.Column():
                            w = gr.Slider(30, 200, value=70, label="Poids (kg)")
                            h = gr.Slider(100, 220, value=170, label="Taille (cm)")
                            a = gr.Slider(10, 100, value=25, label="Âge")
                            g = gr.Radio(["Homme", "Femme"], label="Sexe")
                            act = gr.Dropdown(label="Activité", choices=[
                                "Sédentaire (peu ou pas d'exercice)",
                                "Légèrement actif (1-3 jours/semaine)",
                                "Modérément actif (3-5 jours/semaine)",
                                "Très actif (6-7 jours/semaine)",
                                "Extrêmement actif"
                            ])
                            obj = gr.Radio(["Perdre du poids", "Maintenir le poids", "Gagner du poids"], label="Objectif")
                            btn = gr.Button("Calculer")
                        with gr.Column():
                            out1 = gr.Textbox(label="Calories (kcal/jour)")
                            out2 = gr.Textbox(label="Sport conseillé")
                            out3 = gr.Textbox(label="Menu conseillé", lines=6)
                    btn.click(recommandations, inputs=[w, h, a, g, act, obj], outputs=[out1, out2, out3])
                with gr.TabItem("🧠 Assistant IA"):
                    prompt = gr.Textbox(label="Posez votre question nutritionnelle")
                    rep = gr.Textbox(label="Réponse de l'IA", lines=8)
                    gr.Button("Envoyer").click(assistant_ia, inputs=prompt, outputs=rep)
                with gr.TabItem("🚀 À venir"):
                    gr.Markdown("### Prochaines fonctionnalités NutriTech\n- Suivi glycémique\n- Dashboard interactif\n[...]")

        with gr.TabItem("🚀 Autres projets"):
            gr.Markdown("### Projets IA santé à venir sur SanatioTech\n- CardioPredict\n- SleepOptima\n[...]")

# ------------------- Intégration FastAPI --------------------

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

app = FastAPI()

# Sert le fichier de vérification Google placé dans ./public/
app.mount("/", StaticFiles(directory="public", html=True), name="static")

# Sert l'interface Gradio sur /app
app = gr.mount_gradio_app(app, gradio_app, path="/app")

