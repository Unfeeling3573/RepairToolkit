import platform
import subprocess
import time
import os
import shutil

if platform.system() == "Windows":
    import winreg

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

    def quarantine_suspicious_files(self) -> str:
        if not self.is_windows:
            time.sleep(2)
            return "[Mac Mode] Simulation : 3 fichiers suspects mis en quarantaine avec succès."

        try:
            temp_dir = os.environ.get('TEMP', '')
            downloads_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')

            # Création du dossier de quarantaine à la racine (C:\RepairToolkit_Quarantine)
            system_drive = os.environ.get('SystemDrive', 'C:')
            quarantine_dir = os.path.join(system_drive + '\\', 'RepairToolkit_Quarantine')

            if not os.path.exists(quarantine_dir):
                os.makedirs(quarantine_dir)
                # Cache le dossier pour éviter que l'utilisateur ne clique dessus par erreur
                self.execute_command(["attrib", "+h", "+s", quarantine_dir])

            directories_to_scan = [temp_dir, downloads_dir]
            suspicious_extensions = ['.exe', '.vbs', '.bat', '.ps1', '.js', '.scr', '.cmd']
            quarantined_count = 0

            for directory in directories_to_scan:
                if not directory or not os.path.exists(directory):
                    continue
                for root, _, files in os.walk(directory):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in suspicious_extensions):
                            file_path = os.path.join(root, file)
                            try:
                                # On déplace et on ajoute ".locked" pour casser l'extension d'origine
                                safe_name = file + ".locked"
                                dest_path = os.path.join(quarantine_dir, safe_name)
                                shutil.move(file_path, dest_path)
                                quarantined_count += 1
                            except Exception:
                                pass # Le fichier est peut-être utilisé par le système

            if quarantined_count == 0:
                return "Scan terminé : Aucun fichier exécutable suspect à mettre en quarantaine."

            return f"🛡️ Quarantaine réussie : {quarantined_count} fichier(s) neutralisé(s) et isolé(s) dans {quarantine_dir}."
        except Exception as e:
            return f"Erreur lors de la mise en quarantaine : {str(e)}"

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

    def disable_onedrive(self) -> str:
        if not self.is_windows:
            time.sleep(1)
            return "[Mac Mode] Simulation : OneDrive désactivé."
        try:
            # Arrêter le processus
            self.execute_command(["taskkill", "/f", "/im", "OneDrive.exe"])
            # Désactiver via le Registre (Stratégie de groupe)
            self.execute_command(["reg", "add", "HKLM\\Software\\Policies\\Microsoft\\Windows\\OneDrive", "/v", "DisableFileSyncNGSC", "/t", "REG_DWORD", "/d", "1", "/f"])
            self.execute_command(["reg", "delete", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/v", "OneDrive", "/f"])
            return "☁️🚫 OneDrive a été arrêté et désactivé du système."
        except Exception as e:
            return f"Erreur lors de la désactivation de OneDrive : {str(e)}"

    def install_software_list(self, software_ids: list) -> str:
        if not self.is_windows:
            time.sleep(2)
            return f"[Mac Mode] Simulation : {len(software_ids)} logiciel(s) installé(s) avec succès."

        results = []
        for sw_id in software_ids:
            try:
                # Commande Winget pour une installation silencieuse avec acceptation auto des licences
                command = ["winget", "install", "--id", sw_id, "--silent", "--accept-package-agreements", "--accept-source-agreements"]
                res = self.execute_command(command)
                if "Aucun package" in res or "No package" in res or "n'a pas été reconnu" in res:
                    results.append(f"⚠️ Introuvable : {sw_id}")
                else:
                    results.append(f"✅ Installé : {sw_id}")
            except Exception as e:
                results.append(f"❌ Erreur ({sw_id}) : {str(e)}")

        return "📦 Rapport d'installation Winget :\n" + "\n".join(results)
