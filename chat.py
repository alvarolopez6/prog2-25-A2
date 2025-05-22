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

'''
Las funciones que podemos anadir al flask
    # Diccionario para almacenar mensajes (temporal, en producción usarías una base de datos)
    chat_messages = {}

    @app.flask.route('/chat/send', methods=['POST'])
    @jwt_required()
    def send_message() -> tuple[str, int]:
        """
        Envía un mensaje de un usuario a otro.
        
        Requiere:
        - recipient: nombre de usuario del destinatario
        - message: contenido del mensaje
        
        Returns:
        - 200: Mensaje enviado con éxito
        - 404: Usuario destinatario no encontrado
        - 400: Error en los datos proporcionados
        """
        current_user = get_jwt_identity()
        recipient = request.args.get('recipient')
        message = request.args.get('message')
        
        try:
            # Verificar que el destinatario existe
            if recipient not in User.usuarios:
                return f'Usuario {recipient} no encontrado', 404
                
            # Crear el mensaje
            chat = Chat(User.usuarios[current_user], User.usuarios[recipient], message)
            
            # Almacenar el mensaje (en producción usarías una base de datos)
            if (current_user, recipient) not in chat_messages:
                chat_messages[(current_user, recipient)] = []
            chat_messages[(current_user, recipient)].append(chat.msg)
            
            return 'Mensaje enviado con éxito', 200
            
        except ValueError as e:
            return str(e), 400
        except TypeError as e:
            return str(e), 400


    @app.flask.route('/chat/history', methods=['GET'])
    @jwt_required()
    def get_chat_history() -> tuple[Union[str, list], int]:
        """
        Obtiene el historial de chat entre dos usuarios.
        
        Requiere:
        - other_user: nombre de usuario del otro participante del chat
        
        Returns:
        - 200: Lista de mensajes
        - 404: No hay mensajes con ese usuario
        """
        current_user = get_jwt_identity()
        other_user = request.args.get('other_user')
        
        # Buscar en ambos sentidos (A->B y B->A)
        key1 = (current_user, other_user)
        key2 = (other_user, current_user)
        
        messages = []
        if key1 in chat_messages:
            messages.extend([f"{current_user}: {msg}" for msg in chat_messages[key1]])
        if key2 in chat_messages:
            messages.extend([f"{other_user}: {msg}" for msg in chat_messages[key2]])
        
        if not messages:
            return 'No hay mensajes con este usuario', 404
            
        # Ordenar cronológicamente (en producción usarías timestamps)
        return messages, 200
        
            @app.flask.route('/chat/users', methods=['GET'])
    @jwt_required()
    def get_chat_users() -> tuple[list, int]:
        """
        Obtiene la lista de usuarios con los que has intercambiado mensajes.
        
        Returns:
        - 200: Lista de usuarios
        - 404: No hay chats
        """
        current_user = get_jwt_identity()
        users = set()
        
        for (sender, recipient), messages in chat_messages.items():
            if sender == current_user:
                users.add(recipient)
            elif recipient == current_user:
                users.add(sender)
                
        if not users:
            return 'No has chateado con nadie aún', 404
            
        return list(users), 200
'''