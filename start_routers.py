import subprocess

def main():
    base = 5001
    txt = input("Combien de routeurs lancer ? ")
    try:
        nb = int(txt)
    except:
        nb = 1

    if nb < 1:
        nb = 1

    i = 0
    while i < nb:
        port = base + i
        subprocess.Popen(["python3", "router.py", str(port)])
        print("Routeur lancé sur", port)
        i = i + 1

if __name__ == "__main__":
    main()
