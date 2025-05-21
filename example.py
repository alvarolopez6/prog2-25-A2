import requests

URL='http://127.0.0.1:5000'
def main() -> None:
    """
    Función principal que controla el menu, es necesario tener en ejecución el archivo 'main.py'
    """
    def iniciar_sesion():
        # 1: Iniciar Sesion
        usuario_account = input("Introduce el usuario ")
        password_account = input("Introduce la contrasenya ")
        r = requests.get(
            f'{URL}/login?usuario={usuario_account}'
            f'&password={password_account}'
        )
        print(r.status_code)
        print(r.text)
        return None if r.status_code==401 else r.text,r.status_code

    def actualizar_datos():
        # 2: Actualizar Datos
        nombre_account = input("INTRODUCE EL NUEVO NOMBRE ")
        email_account = input('INTRODUCE EL NUEVO EMAIL ')
        telefono_account = input('INTRODUCE EL NUMERO DE TELEFONO ')
        r = requests.put(
            f'{URL}/usuario?nombre={nombre_account}'
            f'&email={email_account}'
            f'&telefono={telefono_account}', headers={'Authorization': 'Bearer ' + token if token else ''}
        )
        print(r.status_code)
        print(r.text)

    def registrar_cuenta():
        # 3: Registrar una nueva cuenta
        r = requests.post(f"{URL}/signup?account={input('INTRODUCE EL USUARIO DE LA CUENTA ')}"
                          f"&password={input('INTRODUCE UNA CONTRASEÑA ')}"
                          f"&nombre={input('INTRODUCE UN NOMBRE ')}"
                          f"&email={input('INTRODUCE EL EMAIL ')}"
                          f"&tipo={input('INTRODUCE EL TIPO (Consumer/Freelancer) ')}")
        print(r.status_code)
        print(r.text)

    def mostrar_datos_usuario():
        # 4: Mostrar datos del usuario
        r = requests.get(
            f"{URL}/usuario", headers={'Authorization': 'Bearer ' + token if token else ''}
        )
        print(r.status_code)
        print(r.text)

    def borrar_cuenta_actual():
        # 5: Borrar la cuenta Actual
        r = requests.delete(
            f"{URL}/usuario", headers={'Authorization': 'Bearer ' + token if token else ''}
        )
        print(r.status_code)
        print(r.text)

    def cambiar_password():
        # 6: Cambiar Contraseña
        oldpass = input("INTRODUCE TU PASSWORD ANTIGUO ")
        newpass = input("INTRODUCE TU NUEVO PASSWORD ")
        r = requests.put(
            f'{URL}/password?oldpass={oldpass}'
            f'&newpass={newpass}', headers={'Authorization': 'Bearer ' + token if token else ''}
        )
        print(r.status_code)
        print(r.text)

    def cambiar_metodo_pago():
        # 7: Cambiar metodo de Pago
        metodo: int = 0
        while metodo not in range(1, 6):
            print("ELIGE QUE METODO QUIERES")
            print("1- VISA")
            print("2- Paypal")
            print("3- America Express")
            print("4- Pocket")
            print("5- Paysera")
            metodo = int(input("Elige una de las opciones "))
        r = requests.put(f'{URL}/metodo_pago?metodo={metodo}',
                         headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def cerrar_session():
        #8: Cerrar Session
        if token is None:
            print("No hay sesión iniciada")
        else:
            r = requests.delete(f'{URL}/logout', headers={'Authorization': 'Bearer ' + token if token else ''})
            print(r.status_code)
            print(r.text)

    def publicar_post():
        # Publicar Post(Freelancer)
        r = requests.post(f'{URL}/posts/offers?titulo={input("INTRODUCE EL TITULO DE LA PUBLICACION ")}'
                          f'&description={input("INTRODUCE LA DESCRIPCION ")}'
                          f'&price={input("INTRODUCE EL PRECIO ")}',
                          headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def mostrar_todos_posts():
        # Ver Todos los Posts
        r = requests.get(f'{URL}/posts')
        if r.status_code == 200:
            for i in r.text.split(";"):
                print()
                print(i)
                input("Presiona Enter Para ver el Siguiente ")
            print(r.status_code)
        else:
            print(r.text)
            print(r.status_code)

    def mostrar_propios_posts():
        #Mostrar Propios Posts
        r = requests.get(f'{URL}/posts/user', headers={'Authorization': 'Bearer ' + token if token else ''})
        if r.status_code == 200:
            for i in r.text.split(";"):
                print()
                print(i)
                input("Presiona Enter para ver el siguiente ")
            print(r.status_code)
        else:
            print(r.text)
            print(r.status_code)

    def borrar_propios_posts():
        # Borrar posts por titulo
        r = requests.delete(f'{URL}/posts/user?titulo={input("Introduce el titulo: ")}',
                            headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def agregar_propia_categoria():
        # Agregar Categoria
        r = requests.post(f'{URL}/posts/category?titulo={input("Introduce el titulo: ")}'
                          f'&categoria={input("Introduce la categoria que quieres agregar ")}',
                          headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def contratar_servicio():
        # Contratar Servicios
        r = requests.post(
            f'{URL}/usuario/hire?tuser={input("Introduzca el usuario del freelancer que quieres contratar ")}'
            f'&titulo={input("Introduzca el titulo de la oferta que quieres contratar ")}',
            headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def ver_servicio_contratado():
        # Ver servicios contratados (Consumer)
        r = requests.get(f'{URL}/usuario/hire', headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def exportar_perfil_csv():
        # Exportar perfil actual a CSV
        r = requests.get(f'{URL}/usuario/export', headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        if r.status_code == 200:
            with open('profile.csv', mode='wb') as f:
                f.write(r.content)
            print('Perfil exportado como "profile.csv"')

    def exportar_post_csv():
        # Exportar post a CSV
        r = requests.get(f'{URL}/posts/export?titulo={input("Introduzca el titulo del post: ")}',
                         headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        if r.status_code == 200:
            with open('post.csv', mode='wb') as f:
                f.write(r.content)
            print('Post exportado como "post.csv"')

    def forza_quitar_cuenta():
        # FORZA QUITAR UNA CUENTA
        r = requests.delete(f'{URL}/admin?user={input("INTRODUZCA EL USUARIO QUE QUIERES BORRAR: ")}',
                            headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def forzar_borrar_post():
        # Borrar una cuenta
        r = requests.delete(f'{URL}/admin?user={input("INTRODUZCA EL USUARIO DEL QUE QUIERES BORRAR LA PUBLICACIÓN: ")}?post={input('INTRODUCE EL TÍTULO DEL POST A BORRAR: ')}',
                            headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def cancelar_un_contrato():
        # Cancelar Un Contrato
        r = requests.delete(
            f'{URL}/usuario/hire?tuser={input("Introduzca el usuario del freelancer que con quien quieres finalizar el contrato ")}'
            f'&titulo={input("Introduzca el titulo de la oferta que quieres cancelar ")}',
            headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    op: str = ''
    token: str | None = None

    while op != '3':
        print("MENU PRINCIPAL")
        print("1- Iniciar Sesion")
        print("2- Registrar una nueva cuenta")
        print("3- Salir")
        op = input("POR FAVOR ELIGE LA OPCION ")
        match op:
            case "1":
                # 1: Iniciar Sesion
                token,status_code = iniciar_sesion()
                while token is not None and status_code==200:
                    print("**********HAS INICIADO SESSION COMO CONSUMER**********")
                    print("1- Actualizar Datos")
                    print("2- Mostrar Datos de la sesion actual")
                    print("3- Borrar la cuenta Actual")
                    print("4- Cambiar el password")
                    print("5- Ver todos los posts publicados")
                    print("6- Exportar perfil actual a CSV")
                    print("7- Exportar post a CSV")
                    print("8- Cambiar el metodo de pago (Consumer)")
                    print("9- Contratar Servicio (Consumer)")
                    print("10- Ver servicios contratados (Consumer)")
                    print("11- Cancelar el contrato (Consumer)")
                    print("12- Cerrar Sesión")
                    opconsum= input("POR FAVOR ELIGE LA OPCION ")
                    match opconsum:
                        case "1":
                            # 1: Actualizar Datos
                            actualizar_datos()
                        case "2":
                            # 2: Mostrar datos del usuario
                            mostrar_datos_usuario()
                        case "3":
                            # 3: Borrar la cuenta actual
                            borrar_cuenta_actual()
                            token = None
                        case "4":
                            # 4: Cambiar contraseña
                            cambiar_password()
                        case "5":
                            # 5: Ver Todos los Posts
                            mostrar_todos_posts()
                        case "6":
                            # 6: Exportar Perfil Csv
                            exportar_perfil_csv()
                        case "7":
                            # 7: Exportar Post Csv
                            exportar_post_csv()
                        case "8":
                            # 8: Cambiar metodo de pago
                            cambiar_metodo_pago()
                        case "9":
                            # 9:Contratar Servicios
                            contratar_servicio()
                        case "10":
                            # 10:Ver servicios contratados
                            ver_servicio_contratado()
                        case "11":
                            # 11: Cancelar Un Contrato
                            cancelar_un_contrato()
                        case "12":
                            # 12: Cerrar sesión
                            cerrar_session()
                            token = None
                            break
                        case _:
                            print("POR FAVOR INTRODUCE UNA OPCION CORRECTA")

                while token is not None and status_code == 201:
                    print("**********HAS INICIADO SESSION COMO FREELANCER**********")
                    print("1- Actualizar Datos")
                    print("2- Mostrar Datos de la sesion actual")
                    print("3- Borrar la cuenta Actual")
                    print("4- Cambiar el password")
                    print("5- Ver todos los posts publicados")
                    print("6- Exportar perfil actual a CSV")
                    print("7- Exportar post a CSV")
                    print("8- Publicar Post (Freelancer)")
                    print("9- Ver tus posts publicados(Freelancer)")
                    print("10- Borrar Post (Freelancer)")
                    print("11- Agregar Una Categoria a tus Posts(Freelancer)")
                    print("12- Cerrar Session")
                    oplancer = input("POR FAVOR ELIGE LA OPCION ")
                    match oplancer:
                        case "1":
                            # 1: Actualizar Datos
                            actualizar_datos()
                        case "2":
                            # 2: Mostrar datos del usuario
                            mostrar_datos_usuario()
                        case "3":
                            # 3: Borrar la cuenta actual
                            borrar_cuenta_actual()
                            token = None
                        case "4":
                            # 4: Cambiar contraseña
                            cambiar_password()
                        case "5":
                            # 5: Ver Todos los Posts
                            mostrar_todos_posts()
                        case "6":
                            # 6: Exportar Perfil Csv
                            exportar_perfil_csv()
                        case "7":
                            # 7: Exportar Post Csv
                            exportar_post_csv()
                        case "8":
                            # 8: Publicar Post(Freelancer)
                            publicar_post()
                        case "9":
                            # 9: Ver Posts propios (Freelancer)
                            mostrar_propios_posts()
                        case "10":
                            # 10: Borrar Posts Propios
                            borrar_propios_posts()
                        case '11':
                            #Agregar Categoria
                            agregar_propia_categoria()
                        case "12":
                            # 12: Cerrar sesión
                            cerrar_session()
                            token = None
                            break
                        case _:
                            print("POR FAVOR INTRODUCE UNA OPCION CORRECTA")

                while token is not None and status_code == 202:
                    print("**********HAS INICIADO SESSION COMO ADMIN*********")
                    print("1- Actualizar Datos")
                    print("2- Mostrar Datos de la sesion actual")
                    print("3- Borrar la cuenta Actual")
                    print("4- Cambiar el password")
                    print("5- Ver todos los posts publicados")
                    print("6- Exportar perfil actual a CSV")
                    print("7- Exportar post a CSV")
                    print("8- Forza borrado de una cuenta")
                    print("9- Forza borrado de una publicación")
                    print("10- Cerrar sesión")
                    opladmin = input("POR FAVOR ELIGE LA OPCION: ")
                    match opladmin:
                        case "1":
                            actualizar_datos()
                        case "2":
                            mostrar_datos_usuario()
                        case "3":
                            borrar_cuenta_actual()
                            token = None
                        case "4":
                            cambiar_password()
                        case "5":
                            mostrar_todos_posts()
                        case "6":
                            exportar_perfil_csv()
                        case "7":
                            exportar_post_csv()
                        case "8":
                            forza_quitar_cuenta()
                        case '9':
                            forzar_borrar_post()
                        case "10":
                            #Cerrar sesión
                            cerrar_session()
                            token = None
                            break
            case "2":
                #2: Registrate una cuenta
                registrar_cuenta()
            case _:
                print("POR FAVOR INTRODUCE UNA DE LAS OPCIONES ")






















if __name__=='__main__':
    main()