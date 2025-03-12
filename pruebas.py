from publicaciones import Publicacion
from oferta import Oferta
from demanda import Demanda

post1 = Oferta('a','a','a','a', 20, True)
print(post1.mostrar_informacion())

dem2 = Demanda('a','a','a','a', 20)
print(dem2.mostrar_informacion())

post1.agregar_categoria('Ciencias')
post1.agregar_categoria('Física')
post1.eliminar_categoria('Ciencias')
print(post1.obtener_categorias())
post1.eliminar_categoria('Física')

print(post1.mostrar_informacion())
