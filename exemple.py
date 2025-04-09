import requests
URL='http://127.0.0.1:5000'
def main()-> None:
    op:str=''
    token: str | None = None

    while op != '0':
        print("MENU PRINCIPAL")
        print("1- Inciar Session")
        print("2- Actualizar Datos")
        print("3- Registrar una nueva cuenta")
        print("4- Mostrar Datos de la session actual")
        print("5- Borrar La cuenta Actual")
        print("6- Cambiar el password")
        print("7- Cambiar el metodo de pago (Consumer)")
        op=input("POR FAVOR ELIGE LA OPCION ")
        match op:
            case '1':
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
                r=requests.post(f"{URL}/signup?account={input('INTRODUCE EL USUARIO DE LA CUENTA ')}"
                                f"&password={input('INTRODUCE UNA CONTRASEÑA ')}"
                                f"&nombre={input('INTRODUCE UN NOMBRE ')}"
                                f"&email={input('INTRODUCE EL EMAIL ')}"
                                f"&tipo={input('INTRODUCE EL TIPO (Consumer/Freelancer) ')}")
                print(r.status_code)
                print(r.text)


            case '4':
                r = requests.get(
                    f"{URL}/usuario", headers={'Authorization': 'Bearer ' + token if token else '' }
                )
                print(r.status_code)
                print(r.text)
            case '5':
                r = requests.delete(
                    f"{URL}/usuario",headers={'Authorization': 'Bearer ' + token if token else '' }
                )
                token=None
                print(r.status_code)
                print(r.text)
            case '6':
                oldpass=input("INTRODUCE TU PASSWORD ANTIGUO ")
                newpass=input("INTRODUCE TU NUEVO PASSWORD ")
                r = requests.put(
                    f'{URL}/password?oldpass={oldpass}'
                    f'&newpass={newpass}', headers={'Authorization': 'Bearer ' + token if token else '' }
                )
                print(r.status_code)
                print(r.text)

            case '7':
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


main()