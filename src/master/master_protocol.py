from dataclasses import dataclass
from typing import Optional


@dataclass
class RouterInfo:
    """
    Représente un routeur tel qu'enregistré dans la base de données.
    """
    id: int
    name: str
    ip: str
    port: int
    n: int        # modulus clé publique
    e: int        # exposant clé publique
    enabled: bool


def row_to_router(row) -> RouterInfo:
    """
    Convertit une ligne SQL (SELECT ...) en RouterInfo.
    On suppose un SELECT dans l'ordre :
      id, name, ip, port, n, e, enabled
    """
    router_id, name, ip, port, n_str, e, enabled = row
    n_int = int(n_str)
    return RouterInfo(
        id=router_id,
        name=name,
        ip=ip,
        port=port,
        n=n_int,
        e=e,
        enabled=bool(enabled),
    )
