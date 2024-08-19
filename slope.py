from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
import mysql.connector
from mysql.connector import Error
from kivy.app import App
from kivy.uix.textinput import TextInput
from datetime import datetime

# Supprimer l'importation de Toast
# from kivymd.uix.toast import Toast

import logging

logging.basicConfig(level=logging.DEBUG)

# Définir la taille de la fenêtre
Window.size = (310, 580)

class MainScreen(Screen):
    pass

class StartScreen(Screen):
    pass

class AppointmentScreen(Screen):
    def submit_appointment(self):
        # Récupérer les valeurs des champs de texte
        nom = self.ids.nom_field.text
        phone = self.ids.phone_field.text
        date = self.ids.date_field.text
        heure = self.ids.heure_field.text

        # Validation basique
        if not nom or not phone or not date or not heure:
            print("Tous les champs doivent être remplis.")
            return
        
        # Appel de la méthode pour insérer les données dans la base de données
        app = Slope.get_running_app()
        app.insert_patient(nom, phone, date, heure)

        # Afficher un message de succès
        print("Rendez-vous enregistré avec succès !")

        # Réinitialiser les champs après enregistrement
        self.ids.nom_field.text = ""
        self.ids.phone_field.text = ""
        self.ids.date_field.text = ""
        self.ids.heure_field.text = ""

class LoginScreen(Screen):
    def show_error_dialog(self, message):
        dialog = MDDialog(
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def login(self, email, password):
        if not email or not password:
            self.show_error_dialog("Veuillez remplir tous les champs.")
            return
        
        logging.debug("Méthode login appelée avec email: %s", email)
        app = App.get_running_app()
        connection = app.connect_to_database()
        
        if connection:
            logging.debug("Connexion à la base de données réussie dans login.")
            try:
                cursor = connection.cursor()
                
                query = "SELECT * FROM doctor WHERE email = %s AND password = %s"
                cursor.execute(query, (email, password))
                doctor = cursor.fetchone()
                
                if doctor:
                    print("Connexion réussie en tant que docteur")
                    self.manager.current = 'admin'
                else:
                    query = "SELECT * FROM users WHERE email = %s AND password = %s"
                    cursor.execute(query, (email, password))
                    patient = cursor.fetchone()
                    
                    if patient:
                        print("Connexion réussie en tant que patient")
                        self.manager.current = 'appointment'
                    else:
                        self.show_error_dialog("Adresse e-mail ou mot de passe incorrect.")
                
                cursor.close()
            except Error as e:
                logging.error(f"Erreur SQL dans login: {e}")
            finally:
                connection.close()
        else:
            self.show_error_dialog("Adresse e-mail ou mot de passe incorrect.")

class SignupScreen(Screen):
    # Méthodes pour l'inscription des utilisateurs
    pass

class SigDocScreen(Screen):
    # Méthodes pour l'inscription des docteurs
    pass

class PatientScreen(Screen):
    def close_nav_drawer(self):
        if 'nav_drawer' in self.ids:
            self.ids.nav_drawer.set_state("close")
        else:
            print("Erreur : 'nav_drawer' n'a pas été trouvé.")

class AdminScreen(Screen):
    pass

class Slope(MDApp):
    def connect_to_database(self):
        try:
            print("Tentative de connexion à la base de données...")
            connection = mysql.connector.connect(
                host='localhost',
                database='gestion_hopital',
                user='root',
                password=''
            )
            if connection.is_connected():
                print("Connecté à la base de données MySQL")
                return connection
            else:
                print("Connexion non établie.")
        except Error as e:
            print(f"Erreur lors de la connexion à la base de données: {e}")
            return None
        
    def build(self):
        screen_manager = ScreenManager()
       
        Builder.load_file('main.kv')
        Builder.load_file('start.kv')
        Builder.load_file("login.kv")
        Builder.load_file("signup.kv")
        Builder.load_file("signD.kv")
        Builder.load_file("patient.kv")
        Builder.load_file("admin.kv")
        Builder.load_file("appointment.kv")  # Charger le fichier KV pour l'écran des rendez-vous
        
        screen_manager.add_widget(MainScreen(name="main"))
        screen_manager.add_widget(StartScreen(name="start"))
        screen_manager.add_widget(LoginScreen(name="login"))
        screen_manager.add_widget(SignupScreen(name="signup"))
        screen_manager.add_widget(SigDocScreen(name="signD"))
        screen_manager.add_widget(PatientScreen(name="patient"))
        screen_manager.add_widget(AdminScreen(name="admin"))
        screen_manager.add_widget(AppointmentScreen(name="appointment"))  # Ajout correct de l'écran des rendez-vous

        connection = self.connect_to_database()
        if connection:
            print("Connexion réussie depuis la méthode build.")
        else:
            print("La connexion a échoué depuis la méthode build.")
        
        return screen_manager
    
    def insert_patient(self, nom, phone, date, heure):
        connection = self.connect_to_database()

        # Valider et formater la date et l'heure
        try:
            formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
            formatted_time = datetime.strptime(heure, "%H:%M").strftime("%H:%M:%S")
        except ValueError:
            print("Erreur : Date ou heure au format incorrect.")
            return

        if connection:
            try:
                cursor = connection.cursor()
                query = "INSERT INTO patient (nom, phone, dates, heure) VALUES (%s, %s, %s, %s)"
                values = (nom, phone, formatted_date, formatted_time)
                cursor.execute(query, values)
                connection.commit()
                print("Patient inséré avec succès.")
            except Error as e:
                print(f"Erreur lors de l'insertion du patient: {e}")
            finally:
                cursor.close()
                connection.close()
        else:
            print("Impossible de se connecter à la base de données.")
if __name__ == "__main__":
    LabelBase.register(name="MBarlow", fn_regular="fonts/Barlow-Medium.ttf")
    LabelBase.register(name="SBarlow", fn_regular="fonts/Barlow-SemiBold.ttf")
    Slope().run()
