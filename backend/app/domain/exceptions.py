"""
Excepciones de dominio y reglas de negocio del sistema Tracker UP.
"""

class DomainException(Exception):
    """Excepción base para violaciones de reglas del dominio."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidEmailDomainException(DomainException):
    """Lanzada cuando un usuario intenta autenticarse o registrarse con un correo no institucional UP."""
    def __init__(self, email: str):
        super().__init__(
            f"El correo '{email}' no pertenece al dominio institucional permitido (@alum.up.edu.pe o @up.edu.pe)."
        )


class UserAlreadyExistsException(DomainException):
    def __init__(self, email: str):
        super().__init__(f"El usuario con correo '{email}' ya se encuentra registrado.")


class EntityNotFoundException(DomainException):
    def __init__(self, entity_name: str, identifier: str | int):
        super().__init__(f"No se encontró el recurso {entity_name} con identificador '{identifier}'.")


class InvalidAcademicRecordException(DomainException):
    def __init__(self, detail: str):
        super().__init__(f"Registro académico inválido: {detail}")

