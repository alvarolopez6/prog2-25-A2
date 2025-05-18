import requests
from time import sleep

URL='http://127.0.0.1:5000'
def main() -> None:
    """
    Función principal que controla el menu, es necesario tener en ejecución el archivo 'main.py'
    """
    op: str = ''
    token: str | None = None

    while op != '0':
        sleep(2)
        print("MENU PRINCIPAL")
        print("1- Iniciar Sesion")
        print("2- Actualizar Datos")
        print("3- Registrar una nueva cuenta")
        print("4- Mostrar Datos de la sesion actual")
        print("5- Borrar la cuenta Actual")
        print("6- Cambiar el password")
        print("7- Cambiar el metodo de pago (Consumer)")
        print("8- Cerrar Sesión")
        print("9- Publicar Post (Freelancer)")
        print("10- Ver todos los posts publicados")
        print("11- Ver tus posts publicados(Freelancer)")
        print("12- Borrar Post (Freelancer)")
        print("13- Agregar Una Categoria a tus Posts")
        print("14- Contratar Servicio (Consumer)")
        print("15- Ver servicios contratados (Consumer)")
        print("16- Exportar perfil actual a CSV")
        print("17- Exportar post a CSV")
        print("18- Forza Borrar Una Cuenta (Admin)")
        print("19- Cancelar el contrato (Consumer)")
        print("0- Salir del programa")
        op=input("POR FAVOR ELIGE LA OPCION ")
        match op:
            case '1':
                # 1: Iniciar Sesion
                usuario_account=input("Introduce el usuario ")
                password_account=input("Introduce la contrasenya ")
                r=requests.get(
                    f'{URL}/login?usuario={usuario_account}'
                    f'&password={password_account}'
                )
                print(r.status_code)
                token=r.text
                print(token)

            case '2':
                # 2: Actualizar Datos
                nombre_account=input("INTRODUCE EL NUEVO NOMBRE ")
                email_account=input('INTRODUCE EL NUEVO EMAIL ' )
                telefono_account=input('INTRODUCE EL NUMERO DE TELEFONO ')
                r=requests.put(
                    f'{URL}/usuario?nombre={nombre_account}'
                    f'&email={email_account}'
                    f'&telefono={telefono_account}', headers={'Authorization': 'Bearer ' + token if token else '' }
                )
                print(r.status_code)
                print(r.text)

            case '3':
                # 3: Registrar una nueva cuenta
                r=requests.post(f"{URL}/signup?account={input('INTRODUCE EL USUARIO DE LA CUENTA ')}"
                                f"&password={input('INTRODUCE UNA CONTRASEÑA ')}"
                                f"&nombre={input('INTRODUCE UN NOMBRE ')}"
                                f"&email={input('INTRODUCE EL EMAIL ')}"
                                f"&tipo={input('INTRODUCE EL TIPO (Consumer/Freelancer) ')}")
                print(r.status_code)
                print(r.text)

            case '4':
                # 4: Mostrar datos del usuario
                r = requests.get(
                    f"{URL}/usuario", headers={'Authorization': 'Bearer ' + token if token else '' }
                )
                print(r.status_code)
                print(r.text)

            case '5':
                # 5: Borrar la cuenta actual
                r = requests.delete(
                    f"{URL}/usuario",headers={'Authorization': 'Bearer ' + token if token else '' }
                )
                token=None
                print(r.status_code)
                print(r.text)

            case '6':
                # 6: Cambiar contraseña
                oldpass=input("INTRODUCE TU PASSWORD ANTIGUO ")
                newpass=input("INTRODUCE TU NUEVO PASSWORD ")
                r = requests.put(
                    f'{URL}/password?oldpass={oldpass}'
                    f'&newpass={newpass}', headers={'Authorization': 'Bearer ' + token if token else '' }
                )
                print(r.status_code)
                print(r.text)

            case '7':
                # 7: Cambiar método de pago (solo consumers)
                metodo: int =0
                while metodo not in range(1,6):
                    print("ELIGE QUE METODO QUIERES")
                    print("1- VISA")
                    print("2- Paypal")
                    print("3- America Express")
                    print("4- Pocket")
                    print("5- Paysera")
                    metodo=int(input("Elige una de las opciones "))
                r = requests.put(f'{URL}/metodo_pago?metodo={metodo}',headers={'Authorization': 'Bearer ' + token if token else '' })
                print(r.status_code)
                print(r.text)

            case '8':
                # 8: Cerrar sesión
                if token is None:
                    print("No hay sesión iniciada")
                else:
                    r = requests.delete(f'{URL}/logout', headers={'Authorization': 'Bearer ' + token if token else '' })
                    print(r.status_code)
                    print(r.text)
                    token = None

            case '9':
                # Publicar Post(Freelancer)
                r=requests.post(f'{URL}/posts/offers?titulo={input("INTRODUCE EL TITULO DE LA PUBLICACION ")}'
                               f'&description={input("INTRODUCE LA DESCRIPCION ")}'
                               f'&price={input("INTRODUCE EL PRECIO ")}',  headers={'Authorization': 'Bearer ' + token if token else '' })
                print(r.status_code)
                print(r.text)

            case '10':
                # Ver Todos los Posts
                r=requests.get(f'{URL}/posts')
                if r.status_code == 200:
                    for i in r.text.split(";"):
                        print()
                        print(i)
                        input("Presiona Enter Para ver el Siguiente ")
                    print(r.status_code)
                else:
                    print(r.text)
                    print(r.status_code)

            case '11':
                # Ver Posts propios (Freelancer)
                r = requests.get(f'{URL}/posts/user', headers={'Authorization': 'Bearer ' + token if token else '' })
                if r.status_code == 200:
                    for i in r.text.split(";"):
                        print()
                        print(i)
                        input("Presiona Enter para ver el siguiente ")
                    print(r.status_code)
                else:
                    print(r.text)
                    print(r.status_code)

            case '12':
                # Borrar posts por titulo
                r = requests.delete(f'{URL}/posts/user?titulo={input("Introduce el titulo: ")}', headers={'Authorization': 'Bearer ' + token if token else '' })
                print(r.status_code)
                print(r.text)

            case '13':
                # Agregar Categoria
                r = requests.post(f'{URL}/posts/category?titulo={input("Introduce el titulo: ")}'
                                    f'&categoria={input("Introduce la categoria que quieres agregar ")}',
                                    headers={'Authorization': 'Bearer ' + token if token else ''})
                print(r.status_code)
                print(r.text)

            case '14':
                #Contratar Servicios
                r = requests.post(f'{URL}/usuario/hire?tuser={input("Introduzca el usuario del freelancer que quieres contratar ")}'
                                f'&titulo={input("Introduzca el titulo de la oferta que quieres contratar ")}', headers={'Authorization': 'Bearer ' + token if token else '' })
                print(r.status_code)
                print(r.text)

            case '15':
                # Ver servicios contratados (Consumer)
                r = requests.get(f'{URL}/usuario/hire', headers = {'Authorization': 'Bearer ' + token if token else ''})
                print(r.status_code)
                print(r.text)

            case '16':
                # Exportar perfil actual a CSV
                r = requests.get(f'{URL}/usuario/export', headers = {'Authorization': 'Bearer ' + token if token else ''})
                print(r.status_code)
                if r.status_code == 200:
                    with open('profile.csv', mode='wb') as f:
                        f.write(r.content)
                    print('Perfil exportado como "profile.csv"')

            case '17':
                # Exportar post a CSV
                r = requests.get(f'{URL}/posts/export?titulo={input("Introduzca el titulo del post: ")}', headers = {'Authorization': 'Bearer ' + token if token else ''})
                print(r.status_code)
                if r.status_code == 200:
                    with open('post.csv', mode='wb') as f:
                        f.write(r.content)
                    print('Post exportado como "post.csv"')
            case '18':
                #FORZA QUITAR UNA CUENTA
                r = requests.delete(f'{URL}/admin?user={input("INTRODUZCA EL USUARIO QUE QUIERES BORRAR: ")}', headers = {'Authorization': 'Bearer ' + token if token else ''})
                print(r.status_code)
                print(r.text)
            case '19':
                #Cancelar Un Contrato
                r = requests.delete(
                    f'{URL}/usuario/hire?tuser={input("Introduzca el usuario del freelancer que con quien quieres finalizar el contrato ")}'
                    f'&titulo={input("Introduzca el titulo de la oferta que quieres cancelar ")}',
                    headers={'Authorization': 'Bearer ' + token if token else ''})
                print(r.status_code)
                print(r.text)

main()