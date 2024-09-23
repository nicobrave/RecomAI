from database import insertar_contrato

def insertar_contrato_prueba():
    contrato_data = {
        "number": "ABCD1234",  # Número del contrato
        "provider": "Empresa XYZ",  # Proveedor
        "amount": 100000,  # Monto total de la factura
        "description": "Servicios de Consultoría",  # Glosa
        "order_number": "6789",  # Número de orden de compra
        "start_date": "01/09/2024",  # Fecha de emisión de la factura
        "due_date": "30/09/2024",  # Fecha de vencimiento de la factura
        "ito_email": "nico@recomai.cl"  # Email del ITO encargado de revisar la factura
    }

    # Inserta un único contrato
    insertar_contrato(contrato_data)

# Llamar a la función para insertar el contrato
insertar_contrato_prueba()
