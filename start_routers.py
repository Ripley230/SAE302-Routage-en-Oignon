# start_routers.py
import subprocess
import time

processus_routeurs = []  # stocke les Popen

def main():
    global processus_routeurs

    nb = int(input("Combien de routeurs lancer ? "))
    processus_routeurs = []

    port_depart = 5001

    for i in range(nb):
        port = port_depart + i
        print(f"Routeur lancé sur {port}")

        # lance "python router.py <port>"
        p = subprocess.Popen(
            ["python", "router.py", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        processus_routeurs.append(p)
        time.sleep(0.2)


def stop():
    """
    Arrête proprement tous les routeurs lancés.
    """
    global processus_routeurs

    print("Arrêt des routeurs...")

    for p in processus_routeurs:
        try:
            p.terminate()  # demande d'arrêt
        except:
            pass

    # Attendre un peu
    time.sleep(0.5)

    processus_routeurs = []


if __name__ == "__main__":
    main()
