import gradio as gr
import sqlite3
import os
from datetime import datetime
import requests

# Configuration de l'application
APP_NAME = "NutriTech Teranga"
CURRENCY = "XOF"
PREMIUM_PRICE = 5000  # 5000 FCFA
RECIPIENT_PHONE = "781492364"  # Votre numéro Wave/Orange Money
SUPPORT_EMAIL = "ibbidiallo7@gmail.com"
ADMIN_PHONE = "781492364"

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('nutritech.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_premium BOOLEAN DEFAULT 0,
        last_payment_date DATETIME
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_phone TEXT,
        amount INTEGER,
        method TEXT,
        transaction_id TEXT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT
    )
    ''')
    
    conn.commit()
    return conn

db = init_db()

# Services de paiement (simulés pour l'exemple)
class PaymentService:
    @staticmethod
    def process_payment(sender_phone: str, amount: int, method: str) -> bool:
        """Simule un paiement mobile avec enregistrement"""
        try:
            # En production, utiliser les vrais APIs:
            # - Wave: https://developer.wave.com/
            # - Orange Money: https://developer.orange.com/
            
            transaction_id = f"{method[:3]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor = db.cursor()
            cursor.execute('''
            INSERT INTO payments (user_phone, amount, method, transaction_id, status)
            VALUES (?, ?, ?, ?, ?)
            ''', (sender_phone, amount, method, transaction_id, "completed"))
            
            # Envoyer une notification (simulée)
            print(f"Notification: {amount}FCFA reçu de {sender_phone} via {method}")
            
            # Mettre à jour le statut premium si c'est le bon montant
            if amount >= PREMIUM_PRICE:
                cursor.execute('''
                UPDATE users SET is_premium=1, last_payment_date=CURRENT_TIMESTAMP
                WHERE phone=?
                ''', (sender_phone,))
            
            db.commit()
            return True
        
        except Exception as e:
            print(f"Erreur paiement: {e}")
            return False

# Interface utilisateur
def create_ui():
    with gr.Blocks(theme=gr.themes.Soft(), title=APP_NAME) as app:
        # Header
        gr.Markdown(f"""
        <div style="text-align:center">
            <h1>🌍 NutriTech Teranga</h1>
            <p>Votre coach nutritionnel sénégalais</p>
            <p><em>Par Ibrahima Diallo</em></p>
        </div>
        """)
        
        # Authentification
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🔐 Connexion")
                phone = gr.Textbox(label="Votre numéro (ex: 781234567)", placeholder="78XXXXXXX")
                login_btn = gr.Button("Se connecter", variant="primary")
                auth_status = gr.Markdown("")
            
            with gr.Column(scale=2, visible=False) as main_ui:
                # Calculateur nutritionnel
                gr.Markdown("## 🧮 Calculateur Nutritionnel")
                with gr.Row():
                    weight = gr.Slider(30, 150, value=65, label="Poids (kg)")
                    height = gr.Slider(140, 220, value=170, label="Taille (cm)")
                age = gr.Slider(15, 80, value=25, label="Âge")
                gender = gr.Radio(["Homme", "Femme"], label="Sexe")
                activity = gr.Dropdown([
                    "Sédentaire (peu d'activité)",
                    "Actif léger (1-3x/semaine)",
                    "Actif modéré (3-5x/semaine)",
                    "Sportif (6-7x/semaine)"
                ], label="Niveau d'activité")
                
                goal = gr.Radio([
                    "Perdre du poids",
                    "Maintenir mon poids",
                    "Prendre du poids"
                ], label="Objectif")
                
                calculate_btn = gr.Button("Calculer mes besoins", variant="primary")
                
                # Résultats
                with gr.Row():
                    bmr = gr.Number(label="Métabolisme de base (BMR)")
                    tdee = gr.Number(label="Dépense énergétique (TDEE)")
                advice = gr.Textbox(label="Nos conseils", lines=5, interactive=False)
                
                # Section Premium
                with gr.Column(visible=False) as premium_ui:
                    gr.Markdown("### 💎 Fonctionnalités Premium")
                    gr.Markdown("""
                    - Plan alimentaire personnalisé
                    - Suivi hebdomadaire
                    - Recettes locales saines
                    - Support prioritaire
                    """)
                    
                    payment_method = gr.Radio(
                        ["Wave", "Orange Money"],
                        label="Méthode de paiement"
                    )
                    
                    gr.Markdown(f"""
                    <div style="background:#f5f5f5;padding:15px;border-radius:8px">
                        <p>💰 Prix: <strong>{PREMIUM_PRICE} FCFA</strong></p>
                        <p>📞 Envoyer à: <strong>{RECIPIENT_PHONE}</strong></p>
                        <p>📧 Confirmation: <strong>{SUPPORT_EMAIL}</strong></p>
                    </div>
                    """)
                    
                    confirm_btn = gr.Button("J'ai effectué le paiement", variant="primary")
                    payment_status = gr.Markdown("")
        
        # Fonctions interactives
        def authenticate(phone):
            if not phone.isdigit() or len(phone) != 9:
                return {
                    auth_status: "❌ Numéro invalide. Exemple: 781234567",
                    main_ui: gr.Column.update(visible=False)
                }
            
            cursor = db.cursor()
            cursor.execute("SELECT is_premium FROM users WHERE phone=?", (phone,))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute("INSERT INTO users (phone) VALUES (?)", (phone,))
                db.commit()
                is_premium = False
            else:
                is_premium = user[0]
            
            return {
                auth_status: "",
                main_ui: gr.Column.update(visible=True),
                premium_ui: gr.Column.update(visible=not is_premium)
            }
        
        def calculate_needs(weight, height, age, gender, activity, goal):
            # Formule de Mifflin-St Jeor
            if gender == "Homme":
                bmr = 10*weight + 6.25*height - 5*age + 5
            else:
                bmr = 10*weight + 6.25*height - 5*age - 161
            
            # Facteur d'activité
            activity_map = {
                "Sédentaire (peu d'activité)": 1.2,
                "Actif léger (1-3x/semaine)": 1.375,
                "Actif modéré (3-5x/semaine)": 1.55,
                "Sportif (6-7x/semaine)": 1.725
            }
            
            tdee = bmr * activity_map.get(activity, 1.2)
            
            # Conseils adaptés
            if goal == "Perdre du poids":
                tdee -= 500
                conseils = """Conseils pour maigrir:
                - Réduire l'huile dans les plats
                - Manger plus de poisson grillé
                - Faire 30min de marche quotidienne
                - Boire beaucoup d'eau"""
            elif goal == "Prendre du poids":
                tdee += 500
                conseils = """Conseils pour grossir:
                - Augmenter les portions de riz
                - Consommer des arachides
                - Musculation 3x/semaine
                - Dormir suffisamment"""
            else:
                conseils = """Conseils de maintien:
                - Garder une alimentation équilibrée
                - Activité physique régulière
                - Contrôler son poids 1x/semaine"""
            
            return {
                bmr: round(bmr),
                tdee: round(tdee),
                advice: conseils
            }
        
        def confirm_payment(phone, method):
            success = PaymentService.process_payment(phone, PREMIUM_PRICE, method)
            
            if success:
                return {
                    payment_status: "✅ Paiement confirmé! Vous avez maintenant accès au Premium.",
                    premium_ui: gr.Column.update(visible=False)
                }
            else:
                return {
                    payment_status: "❌ Paiement non reconnu. Contactez le support au " + ADMIN_PHONE
                }
        
        # Liaisons des événements
        login_btn.click(
            authenticate,
            inputs=phone,
            outputs=[auth_status, main_ui, premium_ui]
        )
        
        calculate_btn.click(
            calculate_needs,
            inputs=[weight, height, age, gender, activity, goal],
            outputs=[bmr, tdee, advice]
        )
        
        confirm_btn.click(
            confirm_payment,
            inputs=[phone, payment_method],
            outputs=[payment_status, premium_ui]
        )
    
    return app

# Lancement de l'application
if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=False
    )
