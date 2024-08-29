def limite_solicitudes(plan):
    if plan == "basico":
        return 100  # Ajusta este valor para permitir más solicitudes
    elif plan == "premium":
        return 1000
    else:
        return 10  # Valor por defecto
