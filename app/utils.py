"""
Funções genéricas utilizadas no sistema.
"""

def parse_tags(tags_str):
    """Retorna lista de tags padronizadas."""
    if not tags_str:
        return []
    return [t.strip().upper() for t in tags_str.split(",") if t.strip()]
