import subprocess

def main():
    base_port = 5001

    count_str = input("Combien de routeurs veux-tu lancer ? ")
    try:
        count = int(count_str)
    except ValueError:
        count = 1

    if count < 1:
        count = 1

    index = 0
    while index < count:
        port = base_port + index
        # Lance "python router.py <port>" dans un nouveau processus
        subprocess.Popen(["python3", "router.py", str(port)])
        print("Routeur lancé sur le port", port)
        index = index + 1

if __name__ == "__main__":
    main()
