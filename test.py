from post import Offer, import_post_csv
from user import Consumer, Freelancer, Admin


x = Admin('Admin', 'Admin', 'lionel_messi', 'cr7@messi.com', '656565888')
y = Freelancer('Freelancer','Ismael', 'tiktok_is_my_life', 'younes@gmail.com', -1, opiniones=[9,8,6])
z = Consumer('Consumer', 'Consumer', 'alvaro', 'unai@gmail.com', -1)



from db import SixerrDB

db = SixerrDB()
db.sinit()

db.store(x)
db.store(y)
db.store(z)


for user in db.retrieve(Admin):
    print(user, '\n')

for user in db.retrieve(Freelancer):
    print(user, '\n')

for user in db.retrieve(Consumer):
    print(user, '\n')


# a =  Offer('Titulo1', 'Descripcion1', 'lunes', None, 50.99)
# a.export_post_csv('data/')
#
# b = import_post_csv('data/Post.csv')
# print(b.display_information())