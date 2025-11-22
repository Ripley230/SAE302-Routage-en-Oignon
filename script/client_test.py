from client import get_route_from_master, send_message

if __name__ == "__main__":
    route = get_route_from_master("127.0.0.1", 8000)

    if route is None:
        print("Impossible de construire la route !")
    else:
        send_message("Bonjour, ceci est un test Onion !", route)
