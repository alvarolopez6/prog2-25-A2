import re
class User:
    pass

class ChatUser:
    pass

class Chat(ChatUser):
    #@database_decorador
    def __init__(self, user1: User, user2: User, msg: str) -> None:
        # Validación de tipos
        if not isinstance(user1, User) or not isinstance(user2, User) or not isinstance(msg, str):
            raise TypeError('Incorrect type of arguments')
        # Validar que no sea el mismo usuario
        if user1.username == user2.username:
            raise ValueError("Remitente y destinatario no pueden ser el mismo usuario")
        # Limpieza básica del mensaje
        self.msg = self._sanitize_message(msg)
        self.user1 = user1
        self.user2 = user2

    def _sanitize_sql(self, text: str) -> str:
        """Sanitización profunda contra SQL Injection.
        Escapa caracteres peligrosos, bloques lógicos y palabras clave maliciosas."""
        # 1. Eliminar caracteres de control y nulos
        text = re.sub(r"[\x00-\x1F\x7F]", "", text)  # ASCII 0-31 y 127 (DEL)

        # 2. Palabras clave peligrosas (regex insensible a mayúsculas/minúsculas)
        dangerous_keywords = [
            r"\bDROP\b", r"\bDELETE\b", r"\bINSERT\b", r"\bUPDATE\b",
            r"\bTRUNCATE\b", r"\bEXEC\b", r"\bXP_CMDSHELL\b", r"\bUNION\b",
            r"\bSELECT\b", r"\bOR\b", r"\bAND\b", r"\bNOT\b", r"\bWHERE\b"
        ]
        for keyword in dangerous_keywords:
            text = re.sub(keyword, "", text, flags=re.IGNORECASE)

        # 3. Operadores lógicos y caracteres especiales
        replacements = {
            "'": "''",  # Escapa comillas simples
            "\"": "\"\"",  # Escapa comillas dobles
            ";": "",  # Elimina ejecución múltiple
            "--": "",  # Elimina comentarios
            "/*": "", "*/": "",  # Bloques comentarios
            "=": "",  # Operador de comparación (opcional)
            "|": "", "&": "",  # Operadores bitwise
            "!": "",  # Operador NOT (alternativo)
            "%": "\%", "_": "\_"  # Escapa comodines LIKE
        }
        for key, value in replacements.items():
            text = text.replace(key, value)

        # 4. Normalizar espacios múltiples (evita bypass con espacios/tabs)
        text = re.sub(r"\s+", " ", text).strip()

        return text