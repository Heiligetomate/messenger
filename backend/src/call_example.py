from data_base_models import UserAccount
from messenger_repository import MessengerRepository

cnx = MessengerRepository()

users = cnx.get_all_users()
print(len(users))
is_user_created = cnx.is_new_user_created('neu', 'sicher')
print(is_user_created)
users = cnx.get_all_users()
print(len(users))


