import customtkinter as ctk
import threading
import time
import os
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from datetime import datetime
import urllib.request
import json
import webbrowser
import re
from fpdf import FPDF
import ssl

from backend import SystemRepairManager

# --- Configuration de l'application ---
APP_VERSION = "2.0-dev10"

# --- Interface Gestionnaire de Quarantaine ---
class QuarantineManagerWindow(ctk.CTkToplevel):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.title("Gestionnaire de Quarantaine")
        self.geometry("600x400")
        self.attributes("-topmost", True)
        self.backend = backend
        self.parent_app = parent

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        lbl = ctk.CTkLabel(self, text="Fichiers isolés en Quarantaine", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.grid(row=0, column=0, pady=(20,10))

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.refresh_list()

    def refresh_list(self):
        # Nettoie la liste actuelle avant de la recharger
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        files = self.backend.get_quarantined_files()
        if not files:
            lbl = ctk.CTkLabel(self.scroll_frame, text="La quarantaine est vide. Aucun fichier suspect.", text_color="gray")
            lbl.pack(pady=20)
            return

        for f in files:
            frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)

            lbl = ctk.CTkLabel(frame, text=f, font=ctk.CTkFont(weight="bold"))
            lbl.pack(side="left", padx=10)

            btn_del = ctk.CTkButton(frame, text="Détruire", width=80, fg_color="#E74C3C", hover_color="#C0392B", command=lambda name=f: self.delete_file(name))
            btn_del.pack(side="right", padx=5)

            btn_res = ctk.CTkButton(frame, text="Restaurer", width=80, fg_color="#F39C12", hover_color="#D68910", command=lambda name=f: self.restore_file(name))
            btn_res.pack(side="right", padx=5)

    def delete_file(self, filename):
        if messagebox.askyesno("Confirmer", f"Voulez-vous supprimer DÉFINITIVEMENT {filename} ?"):
            res = self.backend.delete_quarantined_file(filename)
            self.parent_app.log_message(res, "info")
            self.refresh_list()

    def restore_file(self, filename):
        if messagebox.askyesno("Attention", f"Voulez-vous vraiment restaurer {filename} sur le Bureau ?\nAssurez-vous qu'il ne s'agit pas d'un virus !"):
            res = self.backend.restore_quarantined_file(filename)
            self.parent_app.log_message(res, "warning")
            self.refresh_list()

# --- Interface Catalogue de Logiciels ---
class SoftwareCatalogWindow(ctk.CTkToplevel):
    def __init__(self, parent, install_callback):
        super().__init__(parent)
        self.title("Catalogue de Logiciels (Winget)")
        self.geometry("550x650")
        self.attributes("-topmost", True) # Garde la fenêtre au premier plan
        self.install_callback = install_callback

        self.catalog = {
            "🌐 Navigateurs": {
                "Google Chrome": "Google.Chrome",
                "Mozilla Firefox": "Mozilla.Firefox",
                "Brave Browser": "Brave.Brave",
                "Opera GX": "Opera.OperaGX"
            },
            "🎬 Multimédia": {
                "VLC Media Player": "VideoLAN.VLC",
                "Spotify": "Spotify.Spotify",
                "OBS Studio": "OBSProject.OBSStudio"
            },
            "🛠️ Utilitaires": {
                "7-Zip": "7zip.7zip",
                "WinRAR": "RARLab.WinRAR",
                "Notepad++": "Notepad++.Notepad++",
                "Rufus": "Rufus.Rufus",
                "PowerToys": "Microsoft.PowerToys"
            },
            "⚙️ Utilitaires Avancés": {
                "HWMonitor": "CPUID.HWMonitor",
                "CrystalDiskInfo": "CrystalDewWorld.CrystalDiskInfo",
                "PuTTY": "PuTTY.PuTTY"
            },
            "💬 Communication": {
                "Discord": "Discord.Discord",
                "WhatsApp": "WhatsApp.WhatsApp",
                "Zoom": "Zoom.Zoom",
                "Telegram": "Telegram.TelegramDesktop"
            },
            "📡 Contrôle à distance": {
                "AnyDesk": "AnyDeskSoftwareGmbH.AnyDesk",
                "TeamViewer": "TeamViewer.TeamViewer"
            },
            "☁️ Cloud & Stockage": {
                "Google Drive": "Google.Drive",
                "Dropbox": "Dropbox.Dropbox"
            },
            "🎮 Gaming": {
                "Steam": "Valve.Steam",
                "Epic Games Launcher": "EpicGames.EpicGamesLauncher"
            },
            "📄 Bureautique & Dev": {
                "LibreOffice": "TheDocumentFoundation.LibreOffice",
                "Acrobat Reader": "Adobe.Acrobat.Reader.64-bit",
                "VS Code": "Microsoft.VisualStudioCode",
                "Python 3.11": "Python.Python.3.11",
                "Git": "Git.Git",
                "Docker Desktop": "Docker.DockerDesktop"
            }
        }

        self.checkboxes = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text="Sélectionnez les logiciels à installer :", font=ctk.CTkFont(size=16, weight="bold"))
        self.label.grid(row=0, column=0, pady=(20, 10))

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        row_idx = 0
        for category, softwares in self.catalog.items():
            cat_label = ctk.CTkLabel(self.scrollable_frame, text=category, font=ctk.CTkFont(size=14, weight="bold"), text_color="#5DADE2")
            cat_label.grid(row=row_idx, column=0, sticky="w", pady=(15, 5), padx=10)
            row_idx += 1

            for name, winget_id in softwares.items():
                var = ctk.StringVar(value="")
                cb = ctk.CTkCheckBox(self.scrollable_frame, text=name, variable=var, onvalue=winget_id, offvalue="")
                cb.grid(row=row_idx, column=0, sticky="w", pady=5, padx=30)
                self.checkboxes[name] = var
                row_idx += 1

        self.lbl_custom = ctk.CTkLabel(self.scrollable_frame, text="Autre (ID Winget personnalisé) :", font=ctk.CTkFont(size=14, weight="bold"), text_color="#5DADE2")
        self.lbl_custom.grid(row=row_idx, column=0, sticky="w", pady=(15, 5), padx=10)
        row_idx += 1

        self.entry_custom = ctk.CTkEntry(self.scrollable_frame, placeholder_text="ex: GitHub.GitHubDesktop", width=250)
        self.entry_custom.grid(row=row_idx, column=0, sticky="w", pady=5, padx=30)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, pady=20)

        self.btn_install = ctk.CTkButton(self.btn_frame, text="Installer la sélection", command=self.confirm_install, fg_color="#2ECC71", hover_color="#27AE60")
        self.btn_install.pack(side="left", padx=10)

        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="Annuler", command=self.destroy, fg_color="#E74C3C", hover_color="#C0392B")
        self.btn_cancel.pack(side="left", padx=10)

    def confirm_install(self):
        selected_ids = [var.get() for var in self.checkboxes.values() if var.get() != ""]
        custom_id = self.entry_custom.get().strip()
        if custom_id:
            selected_ids.append(custom_id)

        if not selected_ids:
            messagebox.showwarning("Sélection vide", "Veuillez sélectionner au moins un logiciel ou entrer un ID personnalisé.")
            return

        self.destroy()
        self.install_callback(selected_ids)

# --- 2. Interface Graphique (Le Frontend) ---
class RepairApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.repair_manager = SystemRepairManager()

        # --- Système de Langue ---
        self.config = {"lang": "fr"}
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except:
                pass

        self.translations = {}
        lang_file = f"langs/{self.config['lang']}.json"
        if os.path.exists(lang_file):
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
            except:
                pass

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

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Repair Toolkit", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 5))

        hw_info = self.repair_manager.get_hardware_info()
        self.hw_label = ctk.CTkLabel(self.sidebar_frame, text=hw_info, font=ctk.CTkFont(size=11), text_color="gray", justify="center")
        self.hw_label.grid(row=1, column=0, padx=10, pady=(0, 30))

        # Bouton utilitaire dans la sidebar
        self.btn_clear_log = ctk.CTkButton(self.sidebar_frame, text=self._("🗑️ Effacer la console"), command=self.clear_logs, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.btn_clear_log.grid(row=2, column=0, padx=20, pady=10)

        self.btn_export_log = ctk.CTkButton(self.sidebar_frame, text=self._("💾 Exporter Rapport"), command=self.export_report, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.btn_export_log.grid(row=3, column=0, padx=20, pady=10)

        self.btn_update = ctk.CTkButton(self.sidebar_frame, text=self._("🔄 Mises à jour"), command=self.check_update, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.btn_update.grid(row=4, column=0, padx=20, pady=10)

        # Switch Thème Clair/Sombre
        self.appearance_mode_switch = ctk.CTkSwitch(self.sidebar_frame, text=self._("Mode Sombre"), command=self.change_appearance_mode_event)
        self.appearance_mode_switch.grid(row=5, column=0, padx=20, pady=20)
        self.appearance_mode_switch.select() # Coché par défaut (Sombre)

        # Menu de Sélection de la Langue
        current_lang = "Français" if self.config.get("lang", "fr") == "fr" else "English"
        self.btn_lang = ctk.CTkOptionMenu(self.sidebar_frame, values=["Français", "English"], command=self.change_language_event)
        self.btn_lang.set(current_lang)
        self.btn_lang.grid(row=6, column=0, padx=20, pady=10)

        # Indicateur de version
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text=f"v{APP_VERSION} Pro Edition", font=ctk.CTkFont(size=10), text_color="#555555")
        self.version_label.grid(row=8, column=0, pady=20, sticky="s")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Raccourcis clavier (UX)
        self.bind("<Control-l>", self.clear_logs)
        self.bind("<Control-s>", self.export_report)

        # -- Zone principale : Les Onglets (Tabs) --
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=(10, 5), sticky="nsew")

        self.tab_sys = self.tabview.add(self._("🛠️ Système"))
        self.tab_opti = self.tabview.add(self._("⚡ Optimisation"))
        self.tab_sec = self.tabview.add(self._("🛡️ Sécurité"))
        self.tab_net = self.tabview.add(self._("🌐 Réseau & Nettoyage"))
        self.tab_utils = self.tabview.add(self._("🧰 Utilitaires"))

        # Layout des onglets
        self.tab_sys.grid_columnconfigure((0, 1, 2), weight=1)
        self.tab_opti.grid_columnconfigure((0, 1), weight=1)
        self.tab_sec.grid_columnconfigure((0, 1, 2), weight=1)
        self.tab_net.grid_columnconfigure((0, 1), weight=1)
        self.tab_utils.grid_columnconfigure((0, 1), weight=1)

        # Thèmes de couleurs des cartes extraits de ui_spec.json
        card_themes = {
            "dark_theme": {"btn_color": "#2C3E50", "hover_color": "#1A252F"},
            "danger": {"btn_color": "#8B0000", "hover_color": "#5C0000"},
            "kill_switch": {"btn_color": "#C0392B", "hover_color": "#922B21"}
        }

        # Création des Cartes d'Actions (UI Premium)
        self.btn_sfc = self.create_action_card(self.tab_sys, 0, 0, "1. Scan SFC", "Vérifie l'intégrité et répare les fichiers système corrompus de Windows.", self.start_sfc_scan)
        self.btn_dism = self.create_action_card(self.tab_sys, 0, 1, "2. Réparer Image (DISM)", "Répare l'image système globale de Windows via Windows Update.", self.start_dism_scan)
        self.btn_restore = self.create_action_card(self.tab_sys, 0, 2, "3. Point Restauration", "Crée une sauvegarde système (recommandé avant réparation).", self.start_restore_point)
        self.btn_explorer = self.create_action_card(self.tab_sys, 1, 0, "Réparer Explorateur", "Redémarre l'explorateur Windows (Menu Démarrer bloqué, icônes invisibles).", self.start_repair_explorer, colspan=3)

        self.btn_telemetry = self.create_action_card(self.tab_opti, 0, 0, "Désactiver Télémétrie", "Bloque la collecte de données et le pistage par Microsoft (DiagTrack).", self.start_disable_telemetry, **card_themes["dark_theme"])
        self.btn_bg_apps = self.create_action_card(self.tab_opti, 0, 1, "Bloquer Apps Arrière-plan", "Empêche les applications inutiles de tourner en tâche de fond.", self.start_disable_background_apps, **card_themes["dark_theme"])

        self.btn_onedrive = self.create_action_card(self.tab_opti, 1, 0, "Désactiver OneDrive", "Arrête la synchronisation et retire OneDrive du démarrage.", self.start_disable_onedrive, **card_themes["dark_theme"], colspan=2)

        self.btn_malware = self.create_action_card(self.tab_sec, 0, 0, "Scan Malware", "Recherche des scripts et exécutables cachés dans Temp et Downloads.", self.start_malware_scan, **card_themes["danger"])
        self.btn_pdf_trace = self.create_action_card(self.tab_sec, 0, 1, "Traces PDF Vérolé", "Détecte les doubles extensions et les faux PDF laissés par les virus.", self.start_pdf_trace_scan, **card_themes["danger"])
        self.btn_registry = self.create_action_card(self.tab_sec, 0, 2, "Scan Registre", "Vérifie les clés Run/RunOnce pour débusquer les virus au démarrage.", self.start_registry_scan, **card_themes["danger"])

        self.btn_quarantine = self.create_action_card(self.tab_sec, 1, 0, "Mise en Quarantaine", "Isole et désactive les exécutables suspects dans un dossier sécurisé.", self.start_quarantine, **card_themes["danger"], colspan=2)
        self.btn_manage_quarantine = self.create_action_card(self.tab_sec, 1, 2, "Gérer Quarantaine", "Consulter, restaurer ou supprimer les fichiers isolés.", self.open_quarantine_manager, **card_themes["dark_theme"])

        # Bouton Kill Switch (Prend toute la largeur de la ligne en dessous)
        self.btn_kill = self.create_action_card(self.tab_sec, 2, 0, "🚨 KILL SWITCH (Suppression)", "Arrêt d'urgence des processus suspects en mémoire et suppression forcée des charges utiles.", self.start_kill_switch, **card_themes["kill_switch"], colspan=3)

        self.btn_dns = self.create_action_card(self.tab_net, 0, 0, "Vider Cache DNS", "Résout la plupart des problèmes de connexion aux sites internet.", self.start_flush_dns)
        self.btn_hosts = self.create_action_card(self.tab_net, 0, 1, "Restaurer HOSTS", "Réinitialise le fichier HOSTS pour bloquer les redirections malveillantes.", self.start_hosts_restore)
        self.btn_temp = self.create_action_card(self.tab_net, 1, 0, "Nettoyage Temp", "Libère de l'espace disque en supprimant les fichiers temporaires inutiles.", self.start_clean_temp)
        self.btn_downloads = self.create_action_card(self.tab_net, 1, 1, "Vider Téléchargements", "Supprime définitivement le contenu du dossier Téléchargements.", self.start_clean_downloads)

        self.btn_net_reset = self.create_action_card(self.tab_net, 2, 0, "Réinitialiser Réseau", "Renouvelle l'adresse IP et réinitialise la carte réseau (Winsock).", self.start_network_reset, colspan=2)

        self.btn_license = self.create_action_card(self.tab_utils, 0, 0, "Clé de Licence", "Récupère la clé de produit Windows originale intégrée à la carte mère.", self.start_license_check)
        self.btn_disk = self.create_action_card(self.tab_utils, 0, 1, "Santé des Disques", "Vérifie l'état de santé S.M.A.R.T de vos disques durs et SSD.", self.start_disk_check)
        self.btn_battery = self.create_action_card(self.tab_utils, 1, 0, "Rapport Batterie", "Génère un rapport HTML complet sur l'état et l'usure de votre batterie.", self.start_battery_report)
        self.btn_sysinfo = self.create_action_card(self.tab_utils, 1, 1, "Infos Système", "Affiche des informations matérielles détaillées (Carte Mère, GPU).", self.start_detailed_sysinfo)
        self.btn_install_software = self.create_action_card(self.tab_utils, 2, 0, "Installer Logiciel", "Installe silencieusement une application via Winget (ex: VLC, Chrome, 7zip).", self.start_software_install, colspan=2)

        # -- Zone de Statut et Barre de Progression (Nouvelle Feature UX) --
        self.status_frame = ctk.CTkFrame(self, height=30, fg_color="transparent")
        self.status_frame.grid(row=1, column=1, padx=20, pady=(5, 5), sticky="ew")

        self.status_label = ctk.CTkLabel(self.status_frame, text=self._("✅ Prêt à analyser"), font=ctk.CTkFont(weight="bold", size=13))
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

        self.log_message(self._("Bienvenue dans Windows Repair Toolkit - Édition Pro."), "info")
        self.log_message(self._("Initialisation terminée. Choisissez une action dans les onglets ci-dessus.\n======================================================================"), "success")

        # --- Téléchargement silencieux si la langue par défaut n'est pas installée ---
        if not os.path.exists(lang_file):
            self.log_message(f"Téléchargement du pack de langue par défaut ({self.config['lang']}) en arrière-plan...", "info")
            self.download_language_pack(self.config['lang'], quiet=True)

    # --- Fonctions UI/UX ---
    def _(self, text):
        """Fonction de traduction à la volée. Renvoie le texte d'origine si non trouvé."""
        return self.translations.get(text, text)

    def create_action_card(self, parent, row, col, title, desc, command, btn_color=None, hover_color=None, colspan=1):
        """Crée une carte visuelle élégante pour contenir un bouton et sa description."""
        frame = ctk.CTkFrame(parent, corner_radius=8, border_width=1, border_color="#333333")
        frame.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")

        btn = ctk.CTkButton(frame, text=self._(title), command=command, font=ctk.CTkFont(weight="bold"))
        if btn_color:
            btn.configure(fg_color=btn_color)
        if hover_color:
            btn.configure(hover_color=hover_color)
        btn.pack(pady=(15, 5), padx=15, fill="x")

        lbl = ctk.CTkLabel(frame, text=self._(desc), font=ctk.CTkFont(size=11), text_color="#AAAAAA", wraplength=210, justify="center")
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
                # Contournement de l'erreur de certificat SSL (très fréquente sur macOS)
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                # Lecture directe du code source sur GitHub (mis à jour pour pointer vers gui.py)
                RAW_URL = f"https://raw.githubusercontent.com/Unfeeling3573/RepairToolkit/v2-dev/gui.py?nocache={int(time.time())}"
                req = urllib.request.Request(RAW_URL, headers={'User-Agent': 'RepairToolkit'})

                with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
                    content = response.read().decode('utf-8')

                    # Extraction intelligente du numéro de version dans le code distant
                    match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        remote_version = match.group(1)
                        if remote_version != APP_VERSION:
                            if messagebox.askyesno("Mise à jour disponible", f"Une nouveauté a été détectée sur GitHub (v{remote_version}) !\n\nVous avez la v{APP_VERSION}.\nVoulez-vous ouvrir la page du projet ?"):
                                webbrowser.open("https://github.com/Unfeeling3573/RepairToolkit")
                                self.log_message("Ouverture de GitHub pour la mise à jour.", "success")
                        else:
                            self.log_message("Vous utilisez déjà la dernière version.", "success")
                    else:
                        self.log_message("Impossible de lire la version sur GitHub.", "error")
            except Exception as e:
                self.log_message(f"Erreur réseau : {str(e)}", "error")
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
    def change_language_event(self, new_lang_name):
        lang_map = {"Français": "fr", "English": "en"}
        lang_code = lang_map.get(new_lang_name, "fr")

        if lang_code == self.config.get("lang", "fr") and os.path.exists(f"langs/{lang_code}.json"):
            return

        self.btn_lang.configure(state="disabled")
        self.log_message(f"Téléchargement du pack de langue '{lang_code}' depuis GitHub...", "info")
        self.download_language_pack(lang_code, quiet=False)

    def download_language_pack(self, lang_code, quiet=False):
        def thread_target():
            try:
                if not os.path.exists("langs"):
                    os.makedirs("langs")

                url = f"https://raw.githubusercontent.com/Unfeeling3573/RepairToolkit/v2-dev/langs/{lang_code}.json?nocache={int(time.time())}"
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                req = urllib.request.Request(url, headers={'User-Agent': 'RepairToolkit'})
                with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
                    data = response.read().decode('utf-8')
                    with open(f"langs/{lang_code}.json", "w", encoding="utf-8") as f:
                        f.write(data)

                self.config["lang"] = lang_code
                with open("config.json", "w", encoding="utf-8") as f:
                    json.dump(self.config, f)

                if not quiet:
                    self.log_message(f"Pack de langue '{lang_code}' appliqué ! Veuillez redémarrer l'application.", "success")
                    messagebox.showinfo("Redémarrage requis", "Le kit de langue a été téléchargé avec succès.\n\nVeuillez redémarrer l'application pour appliquer la traduction.")
                else:
                    self.log_message(f"Le pack de langue '{lang_code}' a été téléchargé avec succès en arrière-plan.", "success")
            except Exception as e:
                if not quiet:
                    self.log_message(f"Erreur de téléchargement : {str(e)}\nLe fichier 'langs/{lang_code}.json' existe-t-il sur GitHub ?", "error")
                else:
                    self.log_message(f"Impossible de télécharger la langue par défaut : {str(e)}", "warning")
            finally:
                if not quiet and hasattr(self, 'btn_lang'):
                    self.btn_lang.configure(state="normal")

        threading.Thread(target=thread_target, daemon=True).start()

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

    def start_quarantine(self):
        if messagebox.askyesno("Mise en Quarantaine", "Cette action va neutraliser et déplacer les exécutables suspects des dossiers Temp/Téléchargements vers C:\\RepairToolkit_Quarantine.\n\nVoulez-vous continuer ?"):
            self.run_async_task(self.btn_quarantine, self.repair_manager.quarantine_suspicious_files, "Mise en quarantaine des menaces...")

    def open_quarantine_manager(self):
        QuarantineManagerWindow(self, self.repair_manager)

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

    def start_disable_onedrive(self):
        if messagebox.askyesno("Optimisation", "Voulez-vous vraiment désactiver complètement OneDrive ?\n\nVos fichiers locaux ne seront plus synchronisés avec le cloud."):
            self.run_async_task(self.btn_onedrive, self.repair_manager.disable_onedrive, "Désactivation de Microsoft OneDrive...")

    def start_software_install(self):
        SoftwareCatalogWindow(self, self._execute_software_install)

    def _execute_software_install(self, software_ids):
        msg = f"Téléchargement et installation de {len(software_ids)} logiciel(s) en arrière-plan..."
        self.run_async_task(self.btn_install_software, lambda: self.repair_manager.install_software_list(software_ids), msg)
