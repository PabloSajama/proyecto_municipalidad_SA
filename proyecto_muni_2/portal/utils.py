from .models import HistorialActividadEvento # Asegúrate de que el nombre del modelo sea correcto

def registrar_historial(user, accion, tabla, detalles, objeto_id=None):
    """
    Registra una acción realizada por un usuario en el sistema.
    """
    try:
        HistorialActividadEvento.objects.create(
            user=user,
            accion=accion,
            tabla=tabla,
            info_operador=detalles
        )
    except Exception as e:
        # Esto evita que si el historial falla, se detenga la operación principal
        print(f"Error al registrar historial: {e}")