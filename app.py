import gradio as gr
import os
import datetime
import json
from pathlib import Path

# ---------------------- Base de connaissances ----------------------
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

# ---------------------- IA Nutritionnelle ----------------------
def assistant_ia(prompt):
    prompt_lower = prompt.lower()
    if "calorie" in prompt_lower or "besoin énergétique" in prompt_lower:
        return ("Le besoin calorique journalier dépend de votre âge, sexe, poids, taille et activité physique.\n"
                "On utilise souvent la formule de Mifflin-St Jeor pour estimer le métabolisme de base (BMR), puis on ajuste selon le niveau d’activité pour obtenir le total des dépenses énergétiques (TDEE).")
    elif "perdre du poids" in prompt_lower:
        return ("Pour perdre du poids, il est recommandé de créer un déficit calorique d'environ 500 kcal par jour, accompagné d'une activité physique régulière, notamment du cardio.")
    elif "gagner du poids" in prompt_lower or "prise de masse" in prompt_lower:
        return ("Pour gagner du poids, un surplus calorique d'environ 500 kcal par jour est conseillé, associé à un entraînement de musculation pour favoriser la prise de masse musculaire.")
    elif "tension" in prompt_lower:
        return ("Une bonne tension artérielle se maintient grâce à une alimentation pauvre en sel, la gestion du stress, une activité physique régulière, et un suivi médical. Valeurs idéales : entre 90/60 et 120/80 mmHg.")
    elif "glycémie" in prompt_lower or "diabète" in prompt_lower:
        return ("Surveillez votre glycémie régulièrement, suivez un régime à index glycémique bas et évitez les sucres rapides. Glycémie à jeun idéale : 0,70 à 1,00 g/L.")
    elif "alimentation équilibrée" in prompt_lower or "nutrition" in prompt_lower:
        return ("Une alimentation équilibrée comprend des protéines, glucides, lipides, fibres, vitamines et minéraux. Il est important de privilégier des aliments variés et non transformés.")
    else:
        return "Voici quelques informations générales sur la nutrition :\n\n" + document_connaissances

# ---------------------- Calculs caloriques ----------------------
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
    save_history({"calories": cal, "sport": sport, "menu": menu, "date": str(datetime.datetime.now())})
    return f"{cal} kcal/jour", sport, menu

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

        with gr.TabItem("🏠 Accueil"):
            gr.Markdown("""
🚀 **SanatioTech : La Révolution Technologique pour une Santé Plus Intelligente !**

Bienvenue chez SanatioTech 🌟 – où l’innovation rencontre les soins de santé pour créer un avenir plus sûr, plus connecté et plus humain.

💡 **Pourquoi SanatioTech ?**

Nous repoussons les limites de la médecine grâce à des solutions high-tech intelligentes, conçues pour les professionnels exigeants comme pour les patients éclairés. Notre mission ? Vous offrir des outils qui anticipent, simplifient et améliorent votre quotidien.

✨ **Nos Atouts Incontournables**

🔹 Innovation de Pointe : IA médicale, diagnostics assistés, gestion optimisée des données… La santé de demain, aujourd’hui.  
🔹 Sécurité Impeccable 🔒 : Vos données sont protégées avec des protocoles ultra-sécurisés, conformes aux normes internationales.  
🔹 Simplicité d’Usage : Des interfaces intuitives pour une prise en main immédiate, sans compromis sur la performance.  
🔹 Impact Réel : Des solutions qui améliorent concrètement les résultats médicaux et le confort des patients.

🌍 **Rejoignez la Révolution SanatioTech !**

Que vous soyez médecin, établissement de santé, ou particulier, nos technologies sur-mesure vous accompagnent pour une santé plus précise, proactive et personnalisée.

👉 Découvrez nos solutions et transformez votre approche des soins !

#SantéConnectée #InnovationMédicale #FuturDeLaSanté
            """)

        with gr.TabItem("📊 NutriTech"):
            with gr.Tabs():
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

                with gr.TabItem("📈 Historique"):
                    hist_btn = gr.Button("Afficher l'historique")
                    hist_out = gr.Textbox(label="Derniers calculs", lines=12)
                    def show_history():
                        data = load_history()
                        return "\n\n".join([f"{h['date']} : {h['calories']} kcal | {h['sport']} | {h['menu']}" for h in data[-10:]])
                    hist_btn.click(show_history, outputs=hist_out)

                with gr.TabItem("🧠 Assistant IA"):
                    prompt = gr.Textbox(label="Posez votre question nutritionnelle")
                    rep = gr.Textbox(label="Réponse de l'IA", lines=8)
                    gr.Button("Envoyer").click(assistant_ia, inputs=prompt, outputs=rep)

                with gr.TabItem("📅 Présentation"):
                    gr.Markdown("""
🌿 **NutriTech 🧠 – L’intelligence de la nutrition au service de votre santé**

NutriTech est une application web innovante d’intelligence artificielle nutritionnelle, conçue pour aider chaque individu à mieux comprendre son corps, ses besoins caloriques et à recevoir des conseils personnalisés pour améliorer son mode de vie.

🚀 **Fonctionnalités principales**  
✨ Calcul intelligent des besoins caloriques journaliers  
🎯 Basé sur la formule Mifflin-St Jeor, adaptée pour les hommes et les femmes  

🥗 **Conseils nutritionnels personnalisés**  
En fonction de vos objectifs :  
✅ Perte de poids  
💪 Prise de masse  
⚖️ Maintien de forme  

🧪 **Analyse des facteurs de mode de vie**  
✓ Activité physique  
✓ Objectif santé  

🧬 **Technologies utilisées**  
Python + scikit-learn pour les calculs et l’IA  
Gradio pour une interface interactive simple et intuitive  
Google Colab pour l’hébergement temporaire  
Préparation future du déploiement avec Flask + Render ou HuggingFace Spaces  

🎯 **Objectif du projet**  
NutriTech a été développé dans le cadre d’un projet personnel visant à :  
🌍 Rendre la nutrition accessible et compréhensible à tous  
🤖 Montrer comment l’IA peut éduquer et prévenir les maladies  
🚀 Construire une preuve de concept solide pour un futur produit de santé numérique à impact  

👤 **Auteur**  
Ibrahima Diallo  
Lycéen passionné d’intelligence artificielle médicale & de santé préventive  
📧 ibbidiallo7@gmail.com 🌐 GitHub : ibrahima-med-ai
                    """)

port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port)

