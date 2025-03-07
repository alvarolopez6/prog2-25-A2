from publicaciones import Publicacion
from oferta import Oferta
from demanda import Demanda

post1 = Oferta('a','a','a','a', 20, True)
print(post1.mostrar_informacion())

dem2 = Demanda('a','a','a','a', 20)
print(dem2.mostrar_informacion())