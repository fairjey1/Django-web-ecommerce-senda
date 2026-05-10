from decimal import Decimal
from .models import ConfiguracionEnvio

def calcular_costo_envio(carrito):
    """
    Recibe el objeto carrito y devuelve el costo de envío final.
    """
    config = ConfiguracionEnvio.load()
    total_compra = carrito.get_total_precio()
    
    # 1. Regla de Envío Gratis
    if total_compra >= config.minimo_compra_envio_gratis:
        return Decimal('0.00')

    # 2. Cálculo por peso
    peso_total = sum(
        Decimal(str(item['variante'].peso_kg or 0)) * item['cantidad'] 
        for item in carrito
    )

    # Fórmula: Base + (Peso Total * Costo por KG)
    costo_final = config.costo_base + (peso_total * config.costo_por_kg_extra)
    
    return costo_final.quantize(Decimal('0.01'))  # Redondear a 2 decimales