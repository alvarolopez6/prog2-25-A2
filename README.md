# Sixerr
[//]: # (Incluid aquí la descripción de vuestra aplicación. Por cierto, así se ponen comentarios en Markdown)
Proyecto asignatura Programación 2 (GIIA).

Sixxer ofrece servicios para freelancers permitiendoles crear publicaciones ofreciendo diferentes servicios mientras que otros usuarios pueden contratarlos


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
* Guardará la información de los usuarios (consumer, freelancer, admin), las publicaciones (oferta, demanda) y las reseñas en una base de datos local. (Stefano)
* Permitirá la creación de perfiles y la verificación de identidad de los mismos para distintos tipos de usuarios como consumers que contratan servicios, freelancers y admins. (Younes)
* El freelancer tendrá la capacidad de subir publicaciones ofreciendo sus servicios y estas serán visibles para los usuarios. (Álvaro)
* Se dispondrá de una funcionalidad que nos permitirá ver de forma cómoda varias de las publicaciones. (Unai)
* Se desarrollará un sistema de búsqueda feed que ayuda a encontrar los servicios necesitados a partir de palabras clave y filtrando por categorías. (Unai)
* Se creará un sistema de reseñas que permite a los consumers valorar la experiencia al contratar servicios con freelancers. (Younes)
* Los freelancers recibirán pagos una vez que se contraten sus servicios. (Ismael)
* Permitirá a los consumers subir demandas, es decir, es el usuario el que publica una necesidad y un freelancer puede crear su oferta. (Álvaro)
* Permitirá la exportación de perfiles o publicaciones a diferentes formatos, como PDF, CSV o XML. (Ismael)
* Los administradores podrán borrar tanto perfiles como publicaciones en caso de considerarlo necesario.

## Instrucciones de instalación y ejecución
* Crear venv con el fichero _requirements.txt_
* Ejecutar app Flask desde _main.py_
* (Opcional) Probar usando _example.py_, mientras se mantiene _main.py_ en ejecución

## Resumen de la API

### Gestión de Usuarios
* Registrar una nueva cuenta
  * `POST /signup`
  * Parámetros: Nombre de usuario, Nombre, Contraseña, Email, Tipo de cuenta (`Consumer` / `Freelancer`)

* Actualizar datos del usuario
  * `PUT /usuario`
  * Requiere JWT
  * Parámetros: Nombre, Email, Teléfono

* Cambiar contraseña
  * `PUT /password`
  * Requiere JWT
  * Parámetros: Contraseña antigua, Nueva contraseña

* Cambiar método de pago, solo Consumers
  * `PUT /metodo_pago`
  * Requiere JWT (Consumer)
  * Parámetros: Método de pago (`1`=VISA, `2`=Paypal, `3`=AmEx, `4`=Pocket, `5`=Paysera)

* Depositar dinero en la cuenta de uno mismo
  * `PUT /money`
  * Requiere JWT
  * Parámetros: cantidad de dinero

* Borrar cuenta actual
  * `DELETE /usuario`
  * Requiere JWT


### Autenticación
* Iniciar sesión
  * `GET /login`
  * Parámetros: Nombre de usuario, Contraseña
  * Devuelve JWT y tipo de usuario (Consumer, Freelancer o Admin)

* Cerrar sesión
  * `DELETE /logout`
  * Requiere JWT


### Publicaciones y Posts
* Ver todos los posts
  * `GET /posts`
  * Público

* Publicar un nuevo post (Freelancer)
  * `POST /posts/offers`
  * Requiere JWT (Freelancer)
  * Parámetros: Título, Descripción, Precio

* Ver mis publicaciones (Freelancer)
  * `GET /posts/user`
  * Requiere JWT

* Borrar una publicación propia (Freelancer)
  * `DELETE /posts/user`
  * Requiere JWT
  * Parámetros: Título del post

* Añadir categoría a una publicación (Freelancer)
  * `POST /posts/category`
  * Requiere JWT
  * Parámetros: Título del post, Categoría

* Feed que permite ver y filtrar publicaciones
  * `GET /feed`


### Contrataciones (Solo Consumers)
* Contratar un servicio
  * `POST /usuario/hire`
  * Requiere JWT (Consumer)
  * Parámetros: Usuario del freelancer, Título del post

* Ver servicios contratados
  * `GET /usuario/hire`
  * Requiere JWT (Consumer)

* Cancelar un contrato
  * `DELETE /usuario/hire`
  * Requiere JWT (Consumer)
  * Parámetros: Usuario del freelancer, Título del post


### Exportación de Datos
* Exportar perfil actual a csv
  * `GET /usuario/export/csv`
  * Requiere JWT
  * Descarga `profile.pdf`

* Exportar perfil actual a pdf
  * `GET /usuario/export/pdf`
  * Requiere JWT
  * Descarga `profile.csv`

* Exportar perfil actual a xml
  * `GET /usuario/export/xml`
  * Requiere JWT
  * Descarga `profile.xml`

* Exportar perfil actual a zip
  * `GET /usuario/export/zip`
  * Requiere JWT
  * Descarga `profile.zip`

* Exportar post específico a csv
  * `GET /posts/export/csv`
  * Requiere JWT
  * Parámetros: Título del post
  * Descarga `post.csv`

* Exportar post específico a pdf
  * `GET /posts/export/pdf`
  * Requiere JWT
  * Parámetros: Título del post
  * Descarga `post.pdf`

* Exportar post específico a xml
  * `GET /posts/export/xml`
  * Requiere JWT
  * Parámetros: Título del post
  * Descarga `post.xml`

* Exportar post específico a zip
  * `GET /posts/export/zip`
  * Requiere JWT
  * Parámetros: Título del post
    * Descarga `post.zip`


### Funcionalidades Administrativas (Solo Admin)
* Forzar eliminación de una cuenta
  * `DELETE /admin`
  * Requiere JWT (Admin)
  * Parámetros: Usuario a eliminar

* Forzar eliminación de un post
  * 'adawda'
  * Requiere JWT (Admin)
  * Parámetros: Usuario del freelancer, nombre del post
