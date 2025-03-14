from generic_posts import *
from offer import *
from demand import *

post1 = Offer('Title1','Description1','User1','Image1', 1)
print(post1.display_information())
print(type(post1.publication_date))
print(type(post1.title))
