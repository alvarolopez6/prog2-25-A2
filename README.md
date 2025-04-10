# Sixerr
[//]: # (Incluid aquí la descripción de vuestra aplicación. Por cierto, así se ponen comentarios en Markdown)

## Autores

* (Coordinador) [Álvaro López Agulló](https://github.com/alvarolopez6)
* [Ismael Escribano Orts](https://github.com/Ismael-Escribano)
* [Younes Laihi](https://github.com/youneslaihi744)
* [Stefano Bia Carrasco](https://github.com/Stefano-UA)
* [Oussama Samrani El Fetouaki](https://github.com/Samrani205)
* [Unai Harvey Gutiérrez](https://github.com/unaiua)

## Profesor
[//]: # (Dejad a quien corresponda)
[Miguel A. Teruel](https://github.com/materuel-ua)

## Requisitos
[//]: # (Indicad aquí los requisitos de vuestra aplicación, así como el alumno responsable de cada uno de ellos)
* Se creará una base de datos de ámbito general. (Stefano)
* Guardará la información de los usuarios (consumer, freelancer, admin), las publicaciones (oferta, demanda), las reseñas y los chats en una base de datos local. (Stefano)
* Permitirá la creación de perfiles y la verificación de identidad de los mismos para distintos tipos de usuarios como consumers que contratan servicios, freelancers y admins.(Younes)
* El freelancer tendrá la capacidad de subir publicaciones ofreciendo sus servicios y estas serán visibles para los usuarios. (Álvaro)
* Implementación de un chat que permitirá la comunicación entre un freelancer y un consumidor.(Samrani)
* Se dispondrá de un modelo ‘Feed’ en el que podremos ver de forma cómoda varias de las publicaciones. (Unai)
* Se desarrollará un sistema de búsqueda que ayuda a encontrar los servicios necesitados a partir de palabras clave y filtrando por categorías. (Unai)
* Se creará un sistema de reseñas que permite a los consumers valorar la experiencia al contratar servicios con freelancers. (Younes)
* Permitirá a los usuarios “Freelancer” entregar los trabajos pedidos de forma directa y recibir un pago a cambio. (Ismael)
* Permitirá a los consumers subir demandas, es decir, es el usuario el que publica una necesidad y un freelancer lo contacta. (Álvaro)
* Permitirá la exportación de perfiles o publicaciones a diferentes formatos, como PDF, CSV o XML. (Ismael)
* Permitirá la importación de publicaciones en formato CSV o XML. (Ismael)

## Instrucciones de instalación y ejecución
[//]: # (Indicad aquí qué habría que hacer para ejecutar vuestra aplicación)

## Resumen de la API

### Autenticación
* Login (Opción 1)
  * GET /login
  * Parámetros: Nombre de usuario, contraseña

* Logout (Opción 8)
  * DELETE /logout
  * Requiere JWT

### Gestión de Usuarios
* Registrar una nueva cuenta (Opción 3)
  * POST /signup
  * Parámetros: Nombre de usuario, Nombre, Contraseña, Email, tipo de cuenta

* Actualizar Datos del usuario (Opción 2)
  * PUT /usuario
  * Requiere JWT
  * Parámetros: Nombre, Email, teléfono

* Cambiar contraseña (Opción 6)
  * PUT /password
  * Requiere JWT
  * Parámetros: Contraseña antigua, Nueva contraseña

* Cambiar método de pago, solo Consumers (Opción 7)
  * PUT /metodo_pago
  * Requiere JWT (Consumer)
  * Parámetros: Método de pago

* Borrar cuenta actual (Opción 5)
  * DELETE /usuario
  * Requiere JWT

### Informes y Exportación
* Mostrar datos del usuario actual (Opción 4)
  * GET /usuario
  * Requiere JWT
