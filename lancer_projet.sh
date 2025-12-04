#!/bin/bash

# Script d'aide au lancement pour le projet Routage Oignon
# A placer dans le même dossier que les fichiers .py

echo "=== Lancement du Projet Routage Oignon ==="

# Vérification des fichiers
if [ ! -f "directory_node.py" ]; then
    echo "Erreur : Fichiers introuvables. Placez ce script avec les fichiers .py"
    exit 1
fi

echo "[1/3] Lancement de l'Annuaire (Master)..."
# On essaie de lancer dans un nouveau terminal
if command -v x-terminal-emulator > /dev/null; then
    x-terminal-emulator -e "python3 directory_node.py" &
elif command -v gnome-terminal > /dev/null; then
    gnome-terminal -- python3 directory_node.py &
elif command -v konsole > /dev/null; then
    konsole -e "python3 directory_node.py" &
else
    echo "Pas de terminal détecté, lancement en arrière plan (logs mélangés)"
    python3 directory_node.py &
fi

sleep 2

echo "[2/3] Lancement de 3 Routeurs..."
for i in {1..3}
do
    if command -v x-terminal-emulator > /dev/null; then
        x-terminal-emulator -e "python3 onion_router.py" &
    elif command -v gnome-terminal > /dev/null; then
        gnome-terminal -- python3 onion_router.py &
    elif command -v konsole > /dev/null; then
        konsole -e "python3 onion_router.py" &
    else
        python3 onion_router.py &
    fi
    sleep 1
done

echo "[3/3] Lancement du Client..."
echo "Le client va se lancer dans cette fenêtre."
python3 client.py
