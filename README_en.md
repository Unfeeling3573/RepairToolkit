# 🛠️ Windows Repair Toolkit - Pro Edition

[![🇬🇧 English](https://img.shields.io/badge/Language-English-blue?style=for-the-badge)](README_en.md)
[![🇫🇷 Français](https://img.shields.io/badge/Langue-Français-red?style=for-the-badge)](README.md)

![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)
![OS](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20(Simulated)-lightgrey.svg)
![Build](https://img.shields.io/badge/Build-GitHub%20Actions-success.svg)

**Windows Repair Toolkit** is an all-in-one system utility with a modern and intuitive graphical interface. It allows you to diagnose, clean, secure, and repair Windows environments with a single click, without the need to type complex command lines.

---

## ✨ Main Features

The application is divided into several thematic tabs for simplified use:

### 🛠️ System
*   **SFC Scan**: Checks integrity and repairs corrupted system files.
*   **Repair Image (DISM)**: Restores the overall Windows system image via Windows Update.
*   **Restore Point**: Creates an instant system backup.
*   **Repair Explorer**: Restarts `explorer.exe` in case the Windows interface freezes.

### ⚡ Optimization
*   **Disable Telemetry**: Blocks data collection (DiagTrack) and tracking by Microsoft.
*   **Block Background Apps**: Prevents Windows applications from consuming background resources.
*   **Disable OneDrive**: Stops cloud synchronization and removes OneDrive from system startup.

### 🛡️ Security
*   **Malware Scan**: Searches for suspicious scripts and executables in temporary folders and downloads.
*   **Infected PDF Traces**: Detects malware using the double extension technique (`.pdf.exe`).
*   **Registry Scan**: Analyzes startup keys to identify persistent threats.
*   **🚨 KILL SWITCH**: Emergency stop of suspicious processes and aggressive purge of temporary files.

### 🌐 Network & Cleanup
*   **Flush DNS Cache**: Resolves connection issues related to cached domains.
*   **Restore HOSTS**: Resets the Windows HOSTS file to block malicious redirects.
*   **Clean Temp**: Frees up disk space by purging the `%TEMP%` folder.
*   **Empty Downloads**: Quick and permanent deletion of the Downloads folder.

### 🧰 Utilities
*   **License Key**: Retrieves the original Windows product key (OEM) embedded in the BIOS/UEFI.
*   **Disk Health**: Displays the physical health status (S.M.A.R.T.) of SSDs/HDDs.
*   **Battery Report**: Generates a comprehensive HTML report on battery wear (for laptops).
*   **System Info**: Displays detailed hardware information (Motherboard, GPU).
*   **Install Software**: Integrated interactive catalog to batch install software (silently) via Winget (Chrome, VLC, 7-Zip, etc.).

### 🎨 Interface & Customization
*   **Dark / Light Mode**: Premium modern theme (CustomTkinter) with instant toggle.
*   **Multi-language (i18n)**: On-the-fly translation with dynamic download of language packs from GitHub.
*   **UI Architecture**: The interface is specified and managed via the `ui_spec.json` file.

---

## 🚀 Installation & Usage

### For Users (Compiled Version)
1. Go to the **Releases** section of this GitHub repository.
2. Download the `Mon_Logiciel_Windows.zip` (or Mac) file.
3. Extract the archive on your computer.
4. Run the executable file **`Windows_Repair_Toolkit.exe`** as an administrator.

*Note for Mac users: A macOS version is compiled to test the graphical interface. Since repair actions are specific to Windows, they are simulated on Mac (Dev Mode).*

### For Developers (Source Code)
Make sure you have Python 3.11+ installed.

```bash
# 1. Clone the repository
git clone https://github.com/Unfeeling3573/RepairToolkit.git
cd RepairToolkit

# 2. Create a virtual environment (Optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
.venv\Scripts\activate     # On Windows

# 3. Install dependencies
pip install customtkinter pyinstaller fpdf

# 4. Run the application
python main.py
```
