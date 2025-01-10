import pydapper
from data_base_models import UserAccount


class MessengerRepository:
    def __init__(self):
        self.connection = "postgresql+psycopg2://postgres:mysecretpassword@127.0.0.1:5433"

    def get_all_users(self) -> list[UserAccount]:
        with pydapper.connect(self.connection) as commands:
            users = commands.query("select user_name, password from user_account;", model=UserAccount)
        return users

    def is_change_password_success(self, user_name, new_password) -> bool:
        with pydapper.connect(self.connection) as commands:
            rowcount = commands.execute(
                "update user_account set password = ?1? where user_name = ?2?",
                param={"1": new_password, "2": user_name}
            )
        return rowcount == 1

    def is_new_user_created(self, user_name, password) -> bool:
        with pydapper.connect(self.connection) as commands:
            rowcount = commands.execute(
                "insert into user_account (user_name, password) values (?1?, ?2?)",
                param={"1": password, "2": user_name}
            )
        return rowcount == 1
