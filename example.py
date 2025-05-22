import requests
from feed import feed

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
            metodo = int(input("Elige una de las OPCIÓNes "))
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

    def publicar_offer():
        # Publicar Post(Freelancer)
        r = requests.post(f'{URL}/posts?titulo={input("INTRODUCE EL TITULO DE LA PUBLICACION ")}'
                          f'&description={input("INTRODUCE LA DESCRIPCION ")}'
                          f'&price={input("INTRODUCE EL PRECIO ")}',
                          headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def publicar_demand():
        # Publicar Post(Consumer)
        r = requests.post(f'{URL}/posts?titulo={input("INTRODUCE EL TITULO DE LA PUBLICACION ")}'
                          f'&description={input("INTRODUCE LA DESCRIPCION ")}'
                          f'&urgency={input("INTRODUCE LA URGENCIA (1, 5) ")}',
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

    def mostrar_post_feed():
        # Iniciar feed
        r = requests.get(f'{URL}/feed')
        if r.status_code == 200:
            feed(r.json())
        else:
            print(r.json())
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

    def exportar_perfil():
        # Exportar perfil actual a CSV, PDF, XML o ZIP
        while True:
            export_opc = input(f'Elija a que formato quiere exportar su perfil:\n'
                               f'1.- Archivo CSV\n'
                               f'2.- Archivo PDF\n'
                               f'3.- Archivo XML\n'
                               f'4.- Archivo ZIP (contiene todos los anteriores)\n')
            match export_opc:
                case '1':
                    r = requests.get(f'{URL}/usuario/export/csv', headers={'Authorization': 'Bearer ' + token if token else ''})
                    extension = '.csv'
                    break
                case '2':
                    r = requests.get(f'{URL}/usuario/export/pdf', headers={'Authorization': 'Bearer ' + token if token else ''})
                    extension = '.pdf'
                    break
                case '3':
                    r = requests.get(f'{URL}/usuario/export/xml', headers={'Authorization': 'Bearer ' + token if token else ''})
                    extension = '.xml'
                    break
                case '4':
                    r = requests.get(f'{URL}/usuario/export/zip', headers={'Authorization': 'Bearer ' + token if token else ''})
                    extension = '.zip'
                    break
                case _:
                    print('Opción no válida')

        print(r.status_code)
        if r.status_code == 200:
            with open(f'profile{extension}', mode='wb') as f:
                f.write(r.content)
            print(f'Perfil exportado como "profile{extension}"')

    def exportar_post_csv():
        # Exportar post a CSV, PDF, XML o ZIP
        while True:
            export_opc = input(f'Elija a que formato quiere exportar el post:\n'
                               f'1.- Archivo CSV\n'
                               f'2.- Archivo PDF\n'
                               f'3.- Archivo XML\n'
                               f'4.- Archivo ZIP (contiene todos los anteriores)\n')
            match export_opc:
                case '1':
                    r = requests.get(f'{URL}/posts/export/csv?titulo={input("Introduzca el titulo del post: ")}',
                                     headers={'Authorization': 'Bearer ' + token if token else ''})
                    extension = '.csv'
                    break
                case '2':
                    r = requests.get(f'{URL}/posts/export/pdf?titulo={input("Introduzca el titulo del post: ")}',
                                     headers={'Authorization': 'Bearer ' + token if token else ''})
                    extension = '.pdf'
                    break
                case '3':
                    r = requests.get(f'{URL}/posts/export/xml?titulo={input("Introduzca el titulo del post: ")}',
                                     headers={'Authorization': 'Bearer ' + token if token else ''})
                    extension = '.xml'
                    break
                case '4':
                    r = requests.get(f'{URL}/posts/export/zip?titulo={input("Introduzca el titulo del post: ")}',
                                     headers={'Authorization': 'Bearer ' + token if token else ''})
                    extension = '.zip'
                    break
                case _:
                    print('Opción no válida')
        print(r.status_code)
        if r.status_code == 200:
            with open(f'post{extension}', mode='wb') as f:
                f.write(r.content)
            print(f'Post exportado como "post{extension}"')

    def forza_quitar_cuenta():
        # FORZA QUITAR UNA CUENTA
        r = requests.delete(f'{URL}/admin?user={input("INTRODUZCA EL USUARIO QUE QUIERES BORRAR: ")}',
                            headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def forzar_borrar_post():
        # Borrar un post
        r = requests.delete(f'')
        r = requests.delete(f'{URL}/admin/post?user={input("INTRODUZCA EL USUARIO DEL OWNER DEL POST: ")}'
                            f'&titulo={input("INTRODUCE EL TITULO DEL POST ")}',
                            headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)

    def cancelar_un_contrato():
        # Cancelar Un Contrato
        r = requests.delete(
            f'{URL}/usuario/hire?tuser={input("Introduzca el usuario del freelancer que con quien quieres finalizar el contrato: ")}'
            f'&titulo={input("Introduzca el titulo de la oferta que quieres cancelar: ")}'
            f'&valoracion={input("Introduzca una valoracion del FreeLancer: ")}',
            headers={'Authorization': 'Bearer ' + token if token else ''})
        print(r.status_code)
        print(r.text)
    
    def depositar_dinero():
        # Depositar Dinero
        r = requests.put(
            f'{URL}/money?number={input("INTRODUZCA EL NUMERO DE TARJETA: ")}'
            f'&cvv={input("INTRODUZCA EL CVV: ")}'
            f'&exp={input("INTRODUCA EL EXP: ")}'
            f'&quantity={input("INTRODUCA LA CANTIDAD: ")}',
            headers={'Authorization': 'Bearer ' + token if token else ''}
        )
        print(r.status_code)
        print(r.text)

    op: str = ''
    token: str | None = None

    while op != '5':
        print("MENU PRINCIPAL")
        print("1- Iniciar Sesion")
        print("2- Registrar una nueva cuenta")
        print("3- Ver todos los posts publicados")
        print("4- Iniciar feed")
        print("5- Salir")
        op = input("POR FAVOR ELIGE LA OPCIÓN ")
        match op:
            case "1":
                # 1: Iniciar Sesion
                token, status_code = iniciar_sesion()
                while token is not None and status_code == 200:
                    print("**********HAS INICIADO SESSION COMO CONSUMER**********")
                    print("1- Actualizar Datos")
                    print("2- Mostrar Datos de la sesion actual")
                    print("3- Borrar la cuenta Actual")
                    print("4- Cambiar el password")
                    print("5- Ver todos los posts publicados")
                    print("6- Iniciar Feed")
                    print("7- Depositar Dinero En Cuenta")
                    print("8- Exportar perfil actual")
                    print("9- Exportar post")
                    print("10- Cambiar el metodo de pago (Consumer)")
                    print("11- Contratar Servicio (Consumer)")
                    print("12- Ver servicios contratados (Consumer)")
                    print("13- Cancelar el contrato (Consumer)")
                    print("14- Publicar Demanda (Consumer)")
                    print("15- Cerrar Sesión")
                    opconsum= input("POR FAVOR ELIGE LA OPCIÓN ")
                    match opconsum:
                        case "1":
                            # Consumer.1: Actualizar Datos
                            actualizar_datos()
                        case "2":
                            # Consumer.2: Mostrar datos del usuario
                            mostrar_datos_usuario()
                        case "3":
                            # Consumer.3: Borrar la cuenta actual
                            borrar_cuenta_actual()
                            token = None
                        case "4":
                            # Consumer.4: Cambiar contraseña
                            cambiar_password()
                        case "5":
                            # Consumer.5: Ver Todos los Posts
                            mostrar_todos_posts()
                        case "6":
                            # Consumer.6: Iniciar feed
                            mostrar_post_feed()
                        case "7":
                            # Consumer.7: Dipositar dinero
                            depositar_dinero()
                        case "8":
                            # Consumer.8: Exportar perfil actual Csv
                            exportar_perfil()
                        case "9":
                            # Consumer.9: Exportar Post Csv
                            exportar_post_csv()
                        case "10":
                            # Consumer.10: Cambiar metodo de pago
                            cambiar_metodo_pago()
                        case "11":
                            # Consumer.11:Contratar Servicios
                            contratar_servicio()
                        case "12":
                            # Consumer.12:Ver servicios contratados
                            ver_servicio_contratado()
                        case "13":
                            # Consumer.13: Cancelar Un Contrato
                            cancelar_un_contrato()
                        case "14":
                            # Consumer.14: Publicar Demanda
                            publicar_demand()
                        case "15":
                            # Consumer.15: Cerrar sesión
                            cerrar_session()
                            token = None
                            break
                        case _:
                            print("POR FAVOR INTRODUCE UNA OPCIÓN CORRECTA")

                while token is not None and status_code == 201:
                    print("**********HAS INICIADO SESSION COMO FREELANCER**********")
                    print("1- Actualizar Datos")
                    print("2- Mostrar Datos de la sesion actual")
                    print("3- Borrar la cuenta Actual")
                    print("4- Cambiar el password")
                    print("5- Ver todos los posts publicados")
                    print("6- Iniciar feed")
                    print("7- Dipositar Dinero")
                    print("8- Exportar perfil actual")
                    print("9- Exportar post")
                    print("10- Publicar Offer (Freelancer)")
                    print("11- Ver tus posts publicados(Freelancer)")
                    print("12- Borrar Post (Freelancer)")
                    print("13- Agregar Una Categoria a tus Posts(Freelancer)")
                    print("14- Cerrar Session")
                    oplancer = input("POR FAVOR ELIGE LA OPCIÓN ")
                    match oplancer:
                        case "1":
                            # Freelancer.1: Actualizar Datos
                            actualizar_datos()
                        case "2":
                            # Freelancer.2: Mostrar datos del usuario
                            mostrar_datos_usuario()
                        case "3":
                            # Freelancer.3: Borrar la cuenta actual
                            borrar_cuenta_actual()
                            token = None
                        case "4":
                            # Freelancer.4: Cambiar contraseña
                            cambiar_password()
                        case "5":
                            # Freelancer.5: Ver Todos los Posts
                            mostrar_todos_posts()
                        case "6":
                            # Freelancer.6: Iniciar feed
                            mostrar_post_feed()
                        case "7":
                            # Freelancer.7: Dipositar dinero
                            depositar_dinero()
                        case "8":
                            # Freelancer.8: Exportar Perfil Csv
                            exportar_perfil()
                        case "9":
                            # Freelancer.9: Exportar Post Csv
                            exportar_post_csv()
                        case "10":
                            # Freelancer.10: Publicar Post(Freelancer)
                            publicar_offer()
                        case "11":
                            # Freelancer.11: Ver Posts propios (Freelancer)
                            mostrar_propios_posts()
                        case "12":
                            # Freelancer.12: Borrar Posts Propios
                            borrar_propios_posts()
                        case '13':
                            # Freelancer.13: Agregar Categoria
                            agregar_propia_categoria()
                        case "14":
                            # Freelancer.14: Cerrar sesión
                            cerrar_session()
                            token = None
                            break
                        case _:
                            print("POR FAVOR INTRODUCE UNA OPCIÓN CORRECTA")

                while token is not None and status_code == 202:
                    print("**********HAS INICIADO SESSION COMO ADMIN**********")
                    print("1- Actualizar Datos")
                    print("2- Mostrar Datos de la session actual")
                    print("3- Borrar la cuenta Actual")
                    print("4- Cambiar el password")
                    print("5- Ver todos los posts publicados")
                    print("6- Iniciar feed")
                    print("7- Exportar perfil actual")
                    print("8- Exportar post")
                    print("9- Forzar Borrar Una Cuenta (Admin)")
                    print("10- Forzar borrado de una publicación")
                    print("11- Cerrar Session")
                    opladmin = input("POR FAVOR ELIGE LA OPCIÓN ")
                    match opladmin:
                        case "1":
                            # Admin.1: Actualizar Datos
                            actualizar_datos()
                        case "2":
                            # Admin.2: Mostrar datos del usuario
                            mostrar_datos_usuario()
                        case "3":
                            # Admin.3: Borrar la cuenta actual
                            borrar_cuenta_actual()
                            token = None
                        case "4":
                            # Admin.4: Cambiar contraseña
                            cambiar_password()
                        case "5":
                            # Admin.5: Ver Todos los Posts
                            mostrar_todos_posts()
                        case "6":
                            # Admin.6: Iniciar feed
                            mostrar_post_feed()
                        case "7":
                            # Admin.7: Exportar Perfil Csv
                            exportar_perfil()
                        case "8":
                            # Admin.8: Exportar Post Csv
                            exportar_post_csv()
                        case "9":
                            # Admin.9: Forzar Borrar una cuenta
                            forza_quitar_cuenta()
                        case "10":
                            # Admin.10: Forzar borrar una publicación
                            forzar_borrar_post()
                        case "11":
                            # Admin.11: Cerrar sesión
                            cerrar_session()
                            token = None
                            break
            case "2":
                # 2: Registrar una cuenta
                registrar_cuenta()
            case "3":
                # 3: Ver todos los posts
                mostrar_todos_posts()
            case "4":
                # 4: Iniciar feed
                mostrar_post_feed()
            case _:
                print("POR FAVOR INTRODUCE UNA DE LAS OPCIÓNES ")

if __name__=='__main__':
    main()