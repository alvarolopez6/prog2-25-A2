def list_users(exclude):
        contactos = [user for user in users if user != exclude]
        if contactos:
            return "\n".join(contactos) + "\n"
        else:
            return "No hay otros usuarios registrados.\n"

users=['hoo','sdf','fogtf','frjg']
print(list_users('hoo'))