import sys
import ctypes
import platform
from gui import RepairApp

def is_admin():
    """Vérifie si le programme possède les droits Administrateur sous Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Point d'entrée de l'application
if __name__ == "__main__":
    # --- Bouclier Administrateur (UAC) ---
    if platform.system() == "Windows" and not is_admin():
        # Relance le programme avec les droits administrateur
        if getattr(sys, 'frozen', False):
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1)
        sys.exit() # Ferme l'instance actuelle non-administrateur

    app = RepairApp()
    app.mainloop()
