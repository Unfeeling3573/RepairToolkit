import customtkinter as ctk
import threading
import platform
import subprocess
import time
import os
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from datetime import datetime
import urllib.request
import json
import webbrowser
from fpdf import FPDF

# Importation conditionnelle pour éviter que le code ne crashe sur Mac
if platform.system() == "Windows":
    import winreg

# --- 1. Logique d'exécution (Le Backend) ---
class SystemRepairManager:
    def __init__(self):
        # Détection de l'OS (Mac vs Windows)
        self.is_windows = platform.system() == "Windows"

    def execute_command(self, command: list) -> str:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True,
                encoding='cp850'
            )
            if result.returncode != 0:
                return f"Erreur ({result.returncode}) : {result.stderr or result.stdout}"
            return result.stdout
        except Exception as e:
            return f"Erreur critique : {str(e)}"

    def get_hardware_info(self) -> str:
        if not self.is_windows:
            # Récupère les vraies infos du Mac pour le mode dev
            try:
                cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
                ram_bytes = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip()
                ram_gb = round(int(ram_bytes) / (1024**3))
                return f"💻 {cpu}\n🧠 {ram_gb} Go RAM (Mac)"
            except:
                return "💻 Système Mac (Mode Dev)\n🧠 RAM Simulée"
        try:
            cpu = self.execute_command(["powershell", "-Command", "(Get-CimInstance Win32_Processor).Name"]).strip()
            ram = self.execute_command(["powershell", "-Command", "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)"]).strip()
            cpu_clean = cpu.replace("(R)", "").replace("(TM)", "").replace("CPU", "").strip()
            return f"💻 {cpu_clean}\n🧠 {ram} Go RAM"
        except Exception:
            return "💻 Info Matériel Indisponible"

    def run_sfc_scan(self) -> str:
        if not self.is_windows:
            time.sleep(3) # Simule le temps d'attente pour voir l'effet sur l'interface Mac
            return "[Mac Mode] Simulation du scan SFC terminée. Aucune violation d'intégrité."
        return self.execute_command(["sfc", "/scannow"])

    def flush_dns(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Cache DNS vidé (simulation)."
        return self.execute_command(["ipconfig", "/flushdns"])

    def scan_suspicious_files(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation du scan de malware. Aucun fichier suspect trouvé."

        try:
            # Les PDF vérolés déposent souvent leur charge utile (payload) ici :
            temp_dir = os.environ.get('TEMP', '')
            downloads_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')

            directories_to_scan = [temp_dir, downloads_dir]
            suspicious_extensions = ['.exe', '.vbs', '.bat', '.ps1', '.js', '.scr', '.cmd']
            found_files = []

            for directory in directories_to_scan:
                if not directory or not os.path.exists(directory):
                    continue
                # Parcours des dossiers et sous-dossiers
                for root, _, files in os.walk(directory):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in suspicious_extensions):
                            found_files.append(os.path.join(root, file))

            if not found_files:
                return "Scan terminé : Aucun fichier exécutable/script suspect trouvé dans Temp ou Téléchargements."

            res = "⚠️ Fichiers suspects trouvés :\n" + "\n".join(f" - {f}" for f in found_files[:15])
            return res + (f"\n... et {len(found_files) - 15} autres." if len(found_files) > 15 else "")
        except Exception as e:
            return f"Erreur lors du scan : {str(e)}"

    def scan_leftover_pdf_traces(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation : Aucune trace de PDF malveillant trouvée après réinitialisation."

        try:
            user_profile = os.environ.get('USERPROFILE', '')
            app_data = os.environ.get('APPDATA', '')
            program_data = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')

            # On cible les dossiers conservés lors d'un reset "Conserver mes fichiers" + dossiers cachés
            directories_to_scan = [
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Downloads'),
                app_data,
                program_data
            ]

            suspicious_endings = ['.pdf.exe', '.pdf.vbs', '.pdf.bat', '.pdf.cmd', '.pdf.js', '.pdf.scr']
            found_traces = []

            for directory in directories_to_scan:
                if not directory or not os.path.exists(directory):
                    continue
                for root, _, files in os.walk(directory):
                    for file in files:
                        lower_file = file.lower()
                        if any(lower_file.endswith(ext) for ext in suspicious_endings):
                            found_traces.append(os.path.join(root, file) + " (Double extension détectée)")
                        elif lower_file.endswith('.pdf') and (app_data.lower() in root.lower() or program_data.lower() in root.lower()):
                            found_traces.append(os.path.join(root, file) + " (PDF caché dans un dossier système)")

            if not found_traces:
                return "Scan terminé : Aucune trace de PDF malveillant (double extension ou emplacement suspect) trouvée."

            res = "⚠️ Traces suspectes de PDF trouvées :\n" + "\n".join(f" - {f}" for f in found_traces[:15])
            return res + (f"\n... et {len(found_traces) - 15} autres." if len(found_traces) > 15 else "")
        except Exception as e:
            return f"Erreur lors de la recherche de traces : {str(e)}"

    def scan_registry_startup(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation : Registre analysé. Aucune entrée de démarrage suspecte."
        try:
            keys_to_check = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
            ]
            suspicious_paths = ['temp', 'appdata', 'downloads', 'programdata']
            suspicious_exts = ['.vbs', '.js', '.bat', '.ps1', '.cmd', '.scr', '.pdf.']
            found_issues = []

            for hkey_base, subkey_path in keys_to_check:
                try:
                    with winreg.OpenKey(hkey_base, subkey_path, 0, winreg.KEY_READ) as key:
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                value_lower = str(value).lower()
                                if any(p in value_lower for p in suspicious_paths) or any(ext in value_lower for ext in suspicious_exts):
                                    found_issues.append(f"[{name}] -> {value}")
                                i += 1
                            except OSError:
                                break
                except FileNotFoundError:
                    continue
            if not found_issues:
                return "Scan terminé : Aucune entrée de démarrage suspecte trouvée dans le Registre."
            return "⚠️ Entrées de démarrage suspectes détectées :\n" + "\n".join(f" - {f}" for f in found_issues)
        except Exception as e:
            return f"Erreur lors de l'analyse du Registre : {str(e)}"

    def run_dism_scan(self) -> str:
        if not self.is_windows:
            time.sleep(3)
            return "[Mac Mode] Simulation DISM : Image système Windows réparée."
        return self.execute_command(["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"])

    def clean_temp_files(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation : Fichiers temporaires nettoyés (1.2 Go libérés)."
        return self.execute_command(["cmd", "/c", "del /q/f/s %TEMP%\\*"])

    def clean_downloads_folder(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation : Dossier Téléchargements vidé (2.8 Go libérés)."
        return self.execute_command(["cmd", "/c", "del /q/f/s \"%USERPROFILE%\\Downloads\\*\""])

    def get_windows_license(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation : Clé de licence Windows (OEM) : VK7JG-NPHTM-C97JM-9MPGT-3V66T"
        try:
            cmd = ["powershell", "-Command", "(Get-WmiObject -query 'select * from SoftwareLicensingService').OA3xOriginalProductKey"]
            res = self.execute_command(cmd).strip()
            if not res:
                return "Information : Aucune clé OEM intégrée trouvée dans le BIOS/UEFI de cet ordinateur."
            return f"🔑 Clé de licence Windows (OEM) trouvée :\n{res}"
        except Exception as e:
            return f"Erreur lors de la récupération de la clé : {str(e)}"

    def check_disk_health(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation :\nNom         | Type | Statut | Santé\n----------------------------------------\nApple SSD   | SSD  | OK     | OK"
        try:
            cmd = ["powershell", "-Command", "Get-PhysicalDisk | Format-Table -Property FriendlyName, MediaType, OperationalStatus, HealthStatus -HideTableHeaders"]
            res = self.execute_command(cmd).strip()
            if not res:
                return "Impossible de récupérer l'état des disques."
            return f"💾 État de santé des disques (S.M.A.R.T) :\nNom | Type | Statut | Santé\n{'-'*40}\n{res}"
        except Exception as e:
            return f"Erreur lors de l'analyse des disques : {str(e)}"

    def execute_kill_switch(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation Kill Switch :\n- 3 processus suspects arrêtés\n- Fichiers malveillants purgés."
        try:
            # Termine de force tous les processus tournant depuis les dossiers Temp ou AppData via PowerShell
            ps_cmd = "Get-Process | Where-Object { $_.Path -match '\\\\Temp\\\\' -or $_.Path -match '\\\\AppData\\\\' } | Stop-Process -Force"
            self.execute_command(["powershell", "-Command", ps_cmd])
            # Purge agressive des fichiers temporaires
            self.execute_command(["cmd", "/c", "del /q/f/s %TEMP%\\*"])
            return "🚨 KILL SWITCH EXÉCUTÉ !\nLes processus suspects en arrière-plan ont été neutralisés et les dossiers temporaires purgés."
        except Exception as e:
            return f"Erreur lors du Kill Switch : {str(e)}"

    def check_and_restore_hosts(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation : Fichier HOSTS analysé et restauré avec ses valeurs par défaut."
        try:
            hosts_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32', 'drivers', 'etc', 'hosts')
            default_hosts = "# Copyright (c) 1993-2009 Microsoft Corp.\n#\n# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.\n#\n# localhost name resolution is handled within DNS itself.\n#\t127.0.0.1       localhost\n#\t::1             localhost\n"

            # Retire les attributs Lecture seule, Caché et Système (souvent ajoutés par les virus pour protéger le fichier)
            if os.path.exists(hosts_path):
                self.execute_command(["attrib", "-r", "-h", "-s", hosts_path])

            with open(hosts_path, 'w', encoding='utf-8') as f:
                f.write(default_hosts)

            return "🌐 Fichier HOSTS restauré avec succès. Les redirections malveillantes ont été supprimées."
        except Exception as e:
            return f"Erreur lors de la restauration du fichier HOSTS : {str(e)}"

    def create_restore_point(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation : Point de restauration système créé avec succès."
        try:
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", "Checkpoint-Computer -Description 'RepairToolkit_Backup' -RestorePointType 'MODIFY_SETTINGS'"]
            self.execute_command(cmd)
            return "🛡️ Point de restauration système créé avec succès."
        except Exception as e:
            return f"Erreur lors de la création du point de restauration : {str(e)}"

    def repair_explorer(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation : Processus explorer.exe redémarré."
        return self.execute_command(["cmd", "/c", "taskkill /f /im explorer.exe & start explorer.exe"])

    def generate_battery_report(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation : Rapport de batterie généré."
        try:
            report_path = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop', 'battery_report.html')
            self.execute_command(["cmd", "/c", f"powercfg /batteryreport /output \"{report_path}\""])
            return f"🔋 Rapport de batterie généré sur le Bureau :\n{report_path}"
        except Exception as e:
            return f"Erreur : {str(e)}"

    def reset_network(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation : Carte réseau réinitialisée (Winsock/IP)."
        try:
            res1 = self.execute_command(["netsh", "winsock", "reset"])
            self.execute_command(["ipconfig", "/renew"])
            return f"🌐 Réseau réinitialisé avec succès.\n{res1}\n(Un redémarrage peut être nécessaire)"
        except Exception as e:
            return f"Erreur lors de la réinitialisation réseau : {str(e)}"

    def get_detailed_sysinfo(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation :\nCarte Mère : Apple M-Series\nGPU : Apple Silicon 16-core"
        try:
            mobo = self.execute_command(["powershell", "-Command", "(Get-WmiObject win32_baseboard).Product"]).strip()
            gpu = self.execute_command(["powershell", "-Command", "(Get-WmiObject win32_VideoController).Name"]).strip()
            return f"📊 Informations Détaillées :\nCarte Mère : {mobo}\nCarte Graphique : {gpu}"
        except Exception as e:
            return f"Erreur lors de la récupération des infos : {str(e)}"

    def disable_telemetry(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation : Télémétrie et collecte de données désactivées."
        try:
            # Désactiver le service de télémétrie Windows
            self.execute_command(["sc", "config", "DiagTrack", "start=", "disabled"])
            self.execute_command(["sc", "stop", "DiagTrack"])
            # Clé de registre pour bloquer la télémétrie
            self.execute_command(["reg", "add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "/v", "AllowTelemetry", "/t", "REG_DWORD", "/d", "0", "/f"])
            return "🛑 Télémétrie Windows désactivée avec succès (Service DiagTrack arrêté)."
        except Exception as e:
            return f"Erreur lors de la désactivation de la télémétrie : {str(e)}"

    def disable_background_apps(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation : Applications en arrière-plan bloquées."
        try:
            self.execute_command(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications", "/v", "GlobalUserDisabled", "/t", "REG_DWORD", "/d", "1", "/f"])
            return "🛑 Exécution des applications en arrière-plan désactivée pour économiser les ressources."
        except Exception as e:
            return f"Erreur lors de la désactivation des apps en arrière-plan : {str(e)}"

# --- Configuration de l'application ---
APP_VERSION = "2.0-dev1"
UPDATE_URL = "https://api.github.com/repos/Unfeeling3573/RepairToolkit/releases/latest" # Remplacer TON_PSEUDO par ton vrai pseudo GitHub

# --- 2. Interface Graphique (Le Frontend) ---
class RepairApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.repair_manager = SystemRepairManager()

        # Configuration de la fenêtre principale
        self.title("Windows Repair Toolkit - Édition Pro")
        self.geometry("1000x700") # Fenêtre agrandie pour plus de confort
        ctk.set_appearance_mode("dark") # Thème sombre moderne
        ctk.set_default_color_theme("blue")

        # Configuration de la grille principale (2 colonnes, 3 lignes)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=3) # Zone des onglets
        self.grid_rowconfigure(1, weight=0) # Zone de statut (barre de chargement)
        self.grid_rowconfigure(2, weight=2) # Zone de console

        # -- Menu latéral (Sidebar) --
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(3, weight=1) # Espace vide poussant la version vers le bas

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Repair Toolkit", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 5))

        hw_info = self.repair_manager.get_hardware_info()
        self.hw_label = ctk.CTkLabel(self.sidebar_frame, text=hw_info, font=ctk.CTkFont(size=11), text_color="gray", justify="center")
        self.hw_label.grid(row=1, column=0, padx=10, pady=(0, 30))

        # Bouton utilitaire dans la sidebar
        self.btn_clear_log = ctk.CTkButton(self.sidebar_frame, text="🗑️ Effacer la console", command=self.clear_logs, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.btn_clear_log.grid(row=2, column=0, padx=20, pady=10)

        self.btn_export_log = ctk.CTkButton(self.sidebar_frame, text="💾 Exporter Rapport", command=self.export_report, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.btn_export_log.grid(row=3, column=0, padx=20, pady=10)

        self.btn_update = ctk.CTkButton(self.sidebar_frame, text="🔄 Mises à jour", command=self.check_update, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.btn_update.grid(row=4, column=0, padx=20, pady=10)

        # Switch Thème Clair/Sombre
        self.appearance_mode_switch = ctk.CTkSwitch(self.sidebar_frame, text="Mode Sombre", command=self.change_appearance_mode_event)
        self.appearance_mode_switch.grid(row=5, column=0, padx=20, pady=20)
        self.appearance_mode_switch.select() # Coché par défaut (Sombre)

        # Indicateur de version
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text=f"v{APP_VERSION} Pro Edition", font=ctk.CTkFont(size=10), text_color="#555555")
        self.version_label.grid(row=7, column=0, pady=20, sticky="s")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        # Raccourcis clavier (UX)
        self.bind("<Control-l>", self.clear_logs)
        self.bind("<Control-s>", self.export_report)

        # -- Zone principale : Les Onglets (Tabs) --
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=(10, 5), sticky="nsew")

        self.tab_sys = self.tabview.add("🛠️ Système")
        self.tab_opti = self.tabview.add("⚡ Optimisation")
        self.tab_sec = self.tabview.add("🛡️ Sécurité")
        self.tab_net = self.tabview.add("🌐 Réseau & Nettoyage")
        self.tab_utils = self.tabview.add("🧰 Utilitaires")

        # Layout des onglets
        self.tab_sys.grid_columnconfigure((0, 1, 2), weight=1)
        self.tab_opti.grid_columnconfigure((0, 1), weight=1)
        self.tab_sec.grid_columnconfigure((0, 1, 2), weight=1)
        self.tab_net.grid_columnconfigure((0, 1), weight=1)
        self.tab_utils.grid_columnconfigure((0, 1), weight=1)

        # Création des Cartes d'Actions (UI Premium)
        self.btn_sfc = self.create_action_card(self.tab_sys, 0, 0, "1. Scan SFC", "Vérifie l'intégrité et répare les fichiers système corrompus de Windows.", self.start_sfc_scan)
        self.btn_dism = self.create_action_card(self.tab_sys, 0, 1, "2. Réparer Image (DISM)", "Répare l'image système globale de Windows via Windows Update.", self.start_dism_scan)
        self.btn_restore = self.create_action_card(self.tab_sys, 0, 2, "3. Point Restauration", "Crée une sauvegarde système (recommandé avant réparation).", self.start_restore_point)
        self.btn_explorer = self.create_action_card(self.tab_sys, 1, 0, "Réparer Explorateur", "Redémarre l'explorateur Windows (Menu Démarrer bloqué, icônes invisibles).", self.start_repair_explorer, colspan=3)

        self.btn_telemetry = self.create_action_card(self.tab_opti, 0, 0, "Désactiver Télémétrie", "Bloque la collecte de données et le pistage par Microsoft (DiagTrack).", self.start_disable_telemetry, "#2C3E50", "#1A252F")
        self.btn_bg_apps = self.create_action_card(self.tab_opti, 0, 1, "Bloquer Apps Arrière-plan", "Empêche les applications inutiles de tourner en tâche de fond.", self.start_disable_background_apps, "#2C3E50", "#1A252F")

        self.btn_malware = self.create_action_card(self.tab_sec, 0, 0, "Scan Malware", "Recherche des scripts et exécutables cachés dans Temp et Downloads.", self.start_malware_scan, "#8B0000", "#5C0000")
        self.btn_pdf_trace = self.create_action_card(self.tab_sec, 0, 1, "Traces PDF Vérolé", "Détecte les doubles extensions et les faux PDF laissés par les virus.", self.start_pdf_trace_scan, "#8B0000", "#5C0000")
        self.btn_registry = self.create_action_card(self.tab_sec, 0, 2, "Scan Registre", "Vérifie les clés Run/RunOnce pour débusquer les virus au démarrage.", self.start_registry_scan, "#8B0000", "#5C0000")

        # Bouton Kill Switch (Prend toute la largeur de la ligne en dessous)
        self.btn_kill = self.create_action_card(self.tab_sec, 1, 0, "🚨 KILL SWITCH (Suppression)", "Arrêt d'urgence des processus suspects en mémoire et suppression forcée des charges utiles.", self.start_kill_switch, "#C0392B", "#922B21", colspan=3)

        self.btn_dns = self.create_action_card(self.tab_net, 0, 0, "Vider Cache DNS", "Résout la plupart des problèmes de connexion aux sites internet.", self.start_flush_dns)
        self.btn_hosts = self.create_action_card(self.tab_net, 0, 1, "Restaurer HOSTS", "Réinitialise le fichier HOSTS pour bloquer les redirections malveillantes.", self.start_hosts_restore)
        self.btn_temp = self.create_action_card(self.tab_net, 1, 0, "Nettoyage Temp", "Libère de l'espace disque en supprimant les fichiers temporaires inutiles.", self.start_clean_temp)
        self.btn_downloads = self.create_action_card(self.tab_net, 1, 1, "Vider Téléchargements", "Supprime définitivement le contenu du dossier Téléchargements.", self.start_clean_downloads)

        self.btn_net_reset = self.create_action_card(self.tab_net, 2, 0, "Réinitialiser Réseau", "Renouvelle l'adresse IP et réinitialise la carte réseau (Winsock).", self.start_network_reset, colspan=2)

        self.btn_license = self.create_action_card(self.tab_utils, 0, 0, "Clé de Licence", "Récupère la clé de produit Windows originale intégrée à la carte mère.", self.start_license_check)
        self.btn_disk = self.create_action_card(self.tab_utils, 0, 1, "Santé des Disques", "Vérifie l'état de santé S.M.A.R.T de vos disques durs et SSD.", self.start_disk_check)
        self.btn_battery = self.create_action_card(self.tab_utils, 1, 0, "Rapport Batterie", "Génère un rapport HTML complet sur l'état et l'usure de votre batterie.", self.start_battery_report, colspan=2)
        self.btn_sysinfo = self.create_action_card(self.tab_utils, 2, 0, "Infos Système", "Affiche des informations matérielles détaillées (Carte Mère, GPU).", self.start_detailed_sysinfo, colspan=2)

        # -- Zone de Statut et Barre de Progression (Nouvelle Feature UX) --
        self.status_frame = ctk.CTkFrame(self, height=30, fg_color="transparent")
        self.status_frame.grid(row=1, column=1, padx=20, pady=(5, 5), sticky="ew")

        self.status_label = ctk.CTkLabel(self.status_frame, text="✅ Prêt à analyser", font=ctk.CTkFont(weight="bold", size=13))
        self.status_label.pack(side="left", padx=5)

        self.progress_bar = ctk.CTkProgressBar(self.status_frame, mode="indeterminate", height=6)
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=(20, 5))
        self.progress_bar.set(0) # Cache la progression par défaut

        # -- Zone de texte (Console de logs) --
        self.console_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13), corner_radius=10, border_width=1, border_color="#333333")
        self.console_textbox.grid(row=2, column=1, padx=20, pady=(0, 20), sticky="nsew")

        # Configuration des couleurs de la console
        self.console_textbox.tag_config("info", foreground="#5DADE2")
        self.console_textbox.tag_config("success", foreground="#2ECC71")
        self.console_textbox.tag_config("warning", foreground="#F1C40F")
        self.console_textbox.tag_config("error", foreground="#E74C3C")

        self.log_message("Bienvenue dans Windows Repair Toolkit - Édition Pro.", "info")
        self.log_message("Initialisation terminée. Choisissez une action dans les onglets ci-dessus.\n" + "="*70, "success")

    # --- Fonctions UI/UX ---
    def create_action_card(self, parent, row, col, title, desc, command, btn_color=None, hover_color=None, colspan=1):
        """Crée une carte visuelle élégante pour contenir un bouton et sa description."""
        frame = ctk.CTkFrame(parent, corner_radius=8, border_width=1, border_color="#333333")
        frame.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")

        btn = ctk.CTkButton(frame, text=title, command=command, font=ctk.CTkFont(weight="bold"))
        if btn_color:
            btn.configure(fg_color=btn_color)
        if hover_color:
            btn.configure(hover_color=hover_color)
        btn.pack(pady=(15, 5), padx=15, fill="x")

        lbl = ctk.CTkLabel(frame, text=desc, font=ctk.CTkFont(size=11), text_color="#AAAAAA", wraplength=210, justify="center")
        lbl.pack(pady=(0, 15), padx=10, fill="both", expand=True)

        return btn

    def log_message(self, message: str, tag: str = None):
        """Ajoute un message dans la console, avec horodatage et sauvegarde."""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        full_message = f"{timestamp} {message}"

        if tag:
            self.console_textbox.insert("end", full_message + "\n\n", tag)
        else:
            self.console_textbox.insert("end", full_message + "\n\n")
        self.console_textbox.see("end")

        # Sauvegarde silencieuse dans un historique local
        try:
            with open("repair_history.log", "a", encoding="utf-8") as f:
                f.write(full_message + "\n\n")
        except:
            pass

    def clear_logs(self, event=None):
        self.console_textbox.delete("1.0", "end")
        self.log_message("Console effacée.\n" + "="*70, "info")

    def export_report(self, event=None):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Fichier PDF", "*.pdf"), ("Fichier Texte", "*.txt")],
            title="Sauvegarder le rapport",
            initialfile=f"Rapport_RepairToolkit_{datetime.now().strftime('%Y%m%d')}"
        )
        if file_path:
            try:
                content = self.console_textbox.get("1.0", "end")

                if file_path.endswith(".pdf"):
                    # Création du document PDF
                    pdf = FPDF()
                    pdf.add_page()

                    # En-tête
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, "Windows Repair Toolkit - Rapport d'intervention", ln=True, align='C')
                    pdf.ln(10)

                    # Corps du texte (Police type "machine à écrire" pour les logs)
                    pdf.set_font("Courier", size=10)

                    # FPDF standard ne gère pas les emojis, on les retire proprement pour le PDF
                    clean_content = content.encode('latin-1', 'ignore').decode('latin-1')

                    for line in clean_content.split('\n'):
                        pdf.multi_cell(0, 5, txt=line)

                    pdf.output(file_path)
                else:
                    # Sauvegarde texte classique si l'utilisateur choisit .txt
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                messagebox.showinfo("Succès", "Rapport exporté avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder le rapport : {e}")

    def check_update(self):
        """Vérifie si une nouvelle version est disponible sur GitHub."""
        self.log_message("Recherche de mises à jour en cours...", "info")
        self.btn_update.configure(state="disabled")

        def thread_target():
            try:
                req = urllib.request.Request(UPDATE_URL, headers={'User-Agent': 'RepairToolkit'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    latest_version = data.get("tag_name", "").replace("v", "")

                    if latest_version and latest_version != APP_VERSION:
                        if messagebox.askyesno("Mise à jour disponible", f"La version {latest_version} est disponible !\n\nVous utilisez actuellement la version {APP_VERSION}.\nVoulez-vous ouvrir la page de téléchargement ?"):
                            webbrowser.open(data.get("html_url", ""))
                            self.log_message(f"Ouverture du navigateur pour télécharger la v{latest_version}.", "success")
                    else:
                        self.log_message("Vous utilisez déjà la dernière version disponible.", "success")
            except Exception as e:
                self.log_message("Impossible de vérifier les mises à jour. Le repo est-il public ?", "error")
            self.btn_update.configure(state="normal")

        threading.Thread(target=thread_target, daemon=True).start()

    # --- 3. Mécanisme global d'exécution asynchrone (Refonte) ---
    def run_async_task(self, button, task_func, start_msg):
        """Gère l'UX complète d'une tâche : Désactivation, Barre de progression, Logs colorés."""
        self.log_message(f"-> {start_msg}", "info")
        button.configure(state="disabled")

        # Animations UI
        self.status_label.configure(text="⚙️ Analyse en cours...", text_color="#F1C40F")
        self.progress_bar.start()

        def thread_target():
            result = task_func()

            # Choix intelligent de la couleur selon le résultat
            res_lower = result.lower()
            tag = "success"
            if "erreur" in res_lower:
                tag = "error"
            elif "⚠️" in result or ("suspect" in res_lower and "aucun" not in res_lower):
                tag = "warning"

            self.log_message(result, tag)

            # Remise à zéro de l'UI
            button.configure(state="normal")
            self.status_label.configure(text="✅ Terminé", text_color="#2ECC71")
            self.progress_bar.stop()
            self.progress_bar.set(0)

        threading.Thread(target=thread_target, daemon=True).start()

    # --- Lancement des tâches ---
    def change_appearance_mode_event(self):
        if self.appearance_mode_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def start_sfc_scan(self):
        self.run_async_task(self.btn_sfc, self.repair_manager.run_sfc_scan, "Démarrage du scan SFC (Vérification des fichiers système)...")

    def start_dism_scan(self):
        self.run_async_task(self.btn_dism, self.repair_manager.run_dism_scan, "Démarrage de DISM (Réparation de l'image Windows)...")

    def start_restore_point(self):
        self.run_async_task(self.btn_restore, self.repair_manager.create_restore_point, "Création du point de restauration système...")

    def start_repair_explorer(self):
        self.run_async_task(self.btn_explorer, self.repair_manager.repair_explorer, "Redémarrage de l'explorateur Windows...")

    def start_flush_dns(self):
        self.run_async_task(self.btn_dns, self.repair_manager.flush_dns, "Vidage du cache DNS...")

    def start_clean_temp(self):
        self.run_async_task(self.btn_temp, self.repair_manager.clean_temp_files, "Nettoyage des fichiers temporaires (%TEMP%)...")

    def start_clean_downloads(self):
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir vider TOUT le dossier Téléchargements ?\n\nCette action est irréversible."):
            self.run_async_task(self.btn_downloads, self.repair_manager.clean_downloads_folder, "Nettoyage du dossier Téléchargements...")

    def start_malware_scan(self):
        self.run_async_task(self.btn_malware, self.repair_manager.scan_suspicious_files, "Recherche de scripts suspects (Temp & Downloads)...")

    def start_pdf_trace_scan(self):
        self.run_async_task(self.btn_pdf_trace, self.repair_manager.scan_leftover_pdf_traces, "Recherche de traces laissées par un PDF malveillant...")

    def start_registry_scan(self):
        self.run_async_task(self.btn_registry, self.repair_manager.scan_registry_startup, "Analyse des clés de démarrage du Registre...")

    def start_license_check(self):
        self.run_async_task(self.btn_license, self.repair_manager.get_windows_license, "Recherche de la clé de licence dans le BIOS/UEFI...")

    def start_disk_check(self):
        self.run_async_task(self.btn_disk, self.repair_manager.check_disk_health, "Analyse de la santé S.M.A.R.T des disques...")

    def start_battery_report(self):
        self.run_async_task(self.btn_battery, self.repair_manager.generate_battery_report, "Génération du rapport de batterie...")

    def start_kill_switch(self):
        if messagebox.askyesno("⚠️ ATTENTION ⚠️", "Le Kill Switch va forcer l'arrêt des processus d'arrière-plan suspects et purger les fichiers.\n\nVoulez-vous vraiment continuer ?"):
            self.run_async_task(self.btn_kill, self.repair_manager.execute_kill_switch, "Exécution du Kill Switch (Neutralisation des processus et malwares)...")

    def start_hosts_restore(self):
        self.run_async_task(self.btn_hosts, self.repair_manager.check_and_restore_hosts, "Restauration du fichier HOSTS de Windows...")

    def start_network_reset(self):
        self.run_async_task(self.btn_net_reset, self.repair_manager.reset_network, "Réinitialisation matérielle de la carte réseau...")

    def start_detailed_sysinfo(self):
        self.run_async_task(self.btn_sysinfo, self.repair_manager.get_detailed_sysinfo, "Analyse du matériel en cours...")

    def start_disable_telemetry(self):
        if messagebox.askyesno("Optimisation", "Désactiver la télémétrie bloquera l'envoi de vos données de diagnostic à Microsoft.\n\nVoulez-vous continuer ?"):
            self.run_async_task(self.btn_telemetry, self.repair_manager.disable_telemetry, "Désactivation de la télémétrie Windows (DiagTrack)...")

    def start_disable_background_apps(self):
        self.run_async_task(self.btn_bg_apps, self.repair_manager.disable_background_apps, "Désactivation globale des applications en arrière-plan...")

# Point d'entrée de l'application
if __name__ == "__main__":
    app = RepairApp()
    app.mainloop()
