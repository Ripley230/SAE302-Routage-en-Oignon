from src.client.client import get_route_from_master, send_message

if __name__ == "__main__":
    route = get_route_from_master("127.0.0.1", 8000)

    if route is None:
        print("Impossible de construire la route !")
    else:
        print("\n=== ROUTE UTILISÉE PAR LE CLIENT ===")
        for hop in route:
            print(hop)
        print("====================================\n")

        # 🔥 Demander à l'utilisateur d'entrer un message
        message = input("Entrez le message à envoyer : ")

        send_message(message, route)
        print("Message envoyé !")
