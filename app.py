import gradio as gr
import sqlite3
import os
from datetime import datetime
import hashlib

# Configuration
RECIPIENT_PHONE = "781492364"
PREMIUM_PRICE = 3000  # 3000 FCFA
SUPPORT_EMAIL = "ibbidiallo7@gmail.com"
DB_NAME = "nutritech.db"

# Initialisation DB
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        phone TEXT UNIQUE,
        password TEXT,
        is_premium BOOLEAN DEFAULT 0,
        reg_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    return conn

db = init_db()

# Services de paiement (simulés)
class PaymentService:
    @staticmethod
    def process_payment(phone, method):
        """Simule un paiement mobile"""
        print(f"📲 Paiement reçu: {method} de {phone}")
        cursor = db.cursor()
        cursor.execute("UPDATE users SET is_premium=1 WHERE phone=?", (phone,))
        db.commit()
        return True

# Interface Gradio
with gr.Blocks(title="NutriTech Teranga", theme=gr.themes.Soft()) as app:
    # State
    current_user = gr.State(None)
    
    # Authentification
    with gr.Tab("🔐 Compte"):
        phone = gr.Textbox(label="Votre numéro (ex: 781234567)")
        password = gr.Textbox(label="Mot de passe", type="password")
        login_btn = gr.Button("Se connecter")
        reg_btn = gr.Button("S'inscrire")
        auth_status = gr.Markdown()
    
    # Calculateur (visible après connexion)
    with gr.Tab("🧮 Nutrition", visible=False) as calc_tab:
        gr.Markdown(f"### 💡 Bienvenue sur NutriTech Teranga Premium")
        
        # Champs de saisie
        weight = gr.Slider(30, 150, label="Poids (kg)")
        height = gr.Slider(140, 220, label="Taille (cm)")
        age = gr.Slider(15, 80, label="Âge")
        gender = gr.Radio(["Homme", "Femme"], label="Sexe")
        activity = gr.Dropdown(["Sédentaire", "Actif", "Sportif"], label="Activité")
        
        # Boutons
        calculate_btn = gr.Button("Calculer", variant="primary")
        
        # Résultats
        bmr = gr.Number(label="Métabolisme de base (BMR)")
        tdee = gr.Number(label="Besoin calorique (TDEE)")
        advice = gr.Textbox(label="Conseils", lines=4)
        
        # Paiement Premium
        with gr.Accordion("💎 Devenir Premium (3000 FCFA)", open=False):
            gr.Markdown(f"""
            **Envoyez {PREMIUM_PRICE} FCFA à:**  
            📞 **{RECIPIENT_PHONE}** via:
            - Wave: *123*{RECIPIENT_PHONE}*3000#
            - Orange: *144*{RECIPIENT_PHONE}*3000#
            """)
            payment_method = gr.Radio(["Wave", "Orange Money"], label="Méthode")
            confirm_btn = gr.Button("J'ai payé")
            payment_status = gr.Markdown()

    # Fonctions
    def register(phone, password):
        try:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, hashed))
            db.commit()
            return {"auth_status": "✅ Enregistré!", "current_user": (1, phone, hashed, 0)}
        except sqlite3.IntegrityError:
            return {"auth_status": "❌ Numéro déjà utilisé"}

    def login(phone, password):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE phone=? AND password=?", (phone, hashed))
        user = cursor.fetchone()
        if user:
            return {
                "auth_status": "✅ Connecté!",
                "calc_tab": gr.Tabs.update(visible=True),
                "current_user": user
            }
        return {"auth_status": "❌ Identifiants incorrects"}

    def confirm_payment(user, method):
        if PaymentService.process_payment(user[1], method):
            return {"payment_status": "✅ Premium activé!"}
        return {"payment_status": "❌ Paiement non reconnu"}

    # Événements
    reg_btn.click(register, [phone, password], [auth_status, current_user])
    login_btn.click(login, [phone, password], [auth_status, calc_tab, current_user])
    confirm_btn.click(confirm_payment, [current_user, payment_method], [payment_status])

# Déploiement Render
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=False
    )
