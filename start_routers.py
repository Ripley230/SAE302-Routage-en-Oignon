import subprocess

for p in [5001, 5002, 5003]:
    subprocess.Popen(["python3", "router.py", str(p)])
    print("Router lancé sur", p)
