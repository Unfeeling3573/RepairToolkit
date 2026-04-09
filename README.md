# 🛠️ Windows Repair Toolkit - Édition Pro

![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)
![OS](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20(Simulé)-lightgrey.svg)
![Build](https://img.shields.io/badge/Build-GitHub%20Actions-success.svg)

**Windows Repair Toolkit** est un utilitaire système tout-en-un doté d'une interface graphique moderne et intuitive. Il permet de diagnostiquer, nettoyer, sécuriser et réparer des environnements Windows en un seul clic, sans avoir besoin de taper des lignes de commande complexes.

---

## ✨ Fonctionnalités Principales

L'application est divisée en plusieurs onglets thématiques pour une utilisation simplifiée :

### 🛠️ Système
*   **Scan SFC** : Vérifie l'intégrité et répare les fichiers système corrompus.
*   **Réparer Image (DISM)** : Restaure l'image système globale de Windows via Windows Update.
*   **Point de Restauration** : Crée une sauvegarde système instantanée.
*   **Réparer Explorateur** : Redémarre `explorer.exe` en cas de blocage de l'interface Windows.

### 🛡️ Sécurité
*   **Scan Malware** : Recherche de scripts et d'exécutables suspects dans les dossiers temporaires et les téléchargements.
*   **Traces PDF Vérolé** : Détecte les malwares utilisant la technique de la double extension (`.pdf.exe`).
*   **Scan Registre** : Analyse les clés de démarrage pour identifier des menaces persistantes.
*   **🚨 KILL SWITCH** : Arrêt d'urgence des processus suspects et purge agressive des fichiers temporaires.

### 🌐 Réseau & Nettoyage
*   **Vider Cache DNS** : Résout les problèmes de connexion liés aux domaines mis en cache.
*   **Restaurer HOSTS** : Réinitialise le fichier HOSTS de Windows pour bloquer les redirections malveillantes.
*   **Nettoyage Temp** : Libère de l'espace disque en purgeant le dossier `%TEMP%`.
*   **Vider Téléchargements** : Suppression rapide et définitive du dossier Téléchargements.

### 🧰 Utilitaires
*   **Clé de Licence** : Récupère la clé de produit Windows (OEM) ancrée dans le BIOS/UEFI.
*   **Santé des Disques** : Affiche l'état de santé physique (S.M.A.R.T.) des disques SSD/HDD.
*   **Rapport Batterie** : Génère un rapport HTML complet sur l'usure de la batterie (pour PC portables).

---

## 🚀 Installation & Utilisation

### Pour les utilisateurs (Version Compilée)
1. Rendez-vous dans la section **Releases** de ce dépôt GitHub.
2. Téléchargez le fichier `Mon_Logiciel_Windows.zip` (ou Mac).
3. Extrayez l'archive sur votre ordinateur.
4. Lancez le fichier exécutable **`Windows_Repair_Toolkit.exe`** en tant qu'administrateur.

*Note pour les utilisateurs Mac : Une version macOS est compilée pour tester l'interface graphique. Les actions de réparation étant spécifiques à Windows, elles sont simulées sur Mac (Mode Dev).*

### Pour les développeurs (Code Source)
Assurez-vous d'avoir Python 3.11+ installé.

```bash
# 1. Cloner le dépôt
git clone https://github.com/Unfeeling3573
/RepairToolkit.git
cd RepairToolkit

# 2. Créer un environnement virtuel (Optionnel mais recommandé)
python -m venv .venv
source .venv/bin/activate  # Sur Linux/Mac
.venv\Scripts\activate     # Sur Windows

# 3. Installer les dépendances
pip install customtkinter pyinstaller fpdf

# 4. Lancer l'application
python main.py
