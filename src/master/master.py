import sys
import traceback

from src.master.master_handler import MasterHandler

try:
    from PyQt5.QtWidgets import QApplication
    from src.gui.master_gui import MasterMainWindow  # à créer si pas encore fait
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def run_cli(handler: MasterHandler) -> None:
    """
    Petit mode texte de secours pour gérer les routeurs
    si la GUI n'est pas disponible.
    """
    print("=== MASTER (mode CLI) ===")
    while True:
        print("\n1. Lister les routeurs")
        print("2. Ajouter un routeur")
        print("3. Activer / Désactiver un routeur")
        print("4. Quitter")
        choice = input("> ").strip()

        if choice == "1":
            routers = handler.list_routers()
            if not routers:
                print("Aucun routeur enregistré.")
            else:
                for r in routers:
                    status = "ON" if r.enabled else "OFF"
                    print(f"[{r.id}] {r.name} {r.ip}:{r.port} enabled={status}")
        elif choice == "2":
            name = input("Nom du routeur (ex: R1): ").strip()
            ip = input("IP du routeur: ").strip()
            port = int(input("Port du routeur: ").strip())
            bits = int(input("Taille clé (ex: 512): ").strip() or "512")
            r = handler.add_router(name, ip, port, bits=bits)
            print(f"Routeur ajouté : {r}")
        elif choice == "3":
            rid = int(input("ID du routeur: ").strip())
            enabled_input = input("Activer (1) ou Désactiver (0): ").strip()
            enabled = enabled_input == "1"
            handler.set_router_enabled(rid, enabled)
            print("OK.")
        elif choice == "4":
            break
        else:
            print("Choix invalide.")


def main() -> int:
    try:
        handler = MasterHandler("config/config_master.json")
    except Exception as e:
        print("Erreur à l'initialisation du Master:")
        print(e)
        traceback.print_exc()
        return 1

    if GUI_AVAILABLE:
        app = QApplication(sys.argv)
        window = MasterMainWindow(handler)
        window.show()
        ret = app.exec_()
        handler.close()
        return ret
    else:
        print("PyQt5 ou master_gui non disponible, passage en mode CLI.")
        run_cli(handler)
        handler.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
