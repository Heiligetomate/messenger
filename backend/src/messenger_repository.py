from typing import Any

import psycopg2.errors
import pydapper
from psycopg2.errors import UniqueViolation
from pydapper.exceptions import NoResultException

from backend.src import channel
from data_base_models import *


def map_to_strings_from_dictionary(values: list[dict[Any]]) -> list[str]:
    messages = []
    for d in values:
        for k, v in d.items():
            messages.append(v)
    return messages


class MessengerRepository:
    def __init__(self):
        self.connection = "postgresql+psycopg2://postgres:mysecretpassword@127.0.0.1:5433"

    def is_new_user_created(self, user_name, password) -> bool:
        with pydapper.connect(self.connection) as commands:
            try:
                rowcount = commands.execute(
                    "insert into user_account (user_name, password) values (?1?, ?2?)",
                    param={"1": password, "2": user_name}
                )
                if rowcount == 1:
                    rowcount = commands.execute(
                        "insert into user_account_in_channel (user_account_fk, channel_fk) values (?1?, 'global')",
                        param={"1": user_name}
                    )
            except UniqueViolation as e:
                print(e)
                return False

        return rowcount == 1

    def is_new_channel_created(self, channel_name: str, password: str, is_public: bool) -> bool:
        try:
            with pydapper.connect(self.connection) as commands:
                rowcount = commands.execute(
                    "insert into channel (channel_name, password, is_public) values (?1?, ?2?, ?3?)",
                    param={"1": channel_name, "2": password, "3": is_public}
                )
                return rowcount == 1
        except UniqueViolation as e:
            print(e)
            return False

    def is_joined_channel(self, channel_name: str, user_name: str) -> bool:
        try:
            with pydapper.connect(self.connection) as commands:
                rowcount = commands.execute(
                    "insert into user_account_in_channel (channel_fk, user_account_fk) values (?1?, ?2?)",
                    param={"1": channel_name, "2": user_name}
                )
                return True
        except NoResultException:
            return False

    def get_all_users(self) -> list[UserAccount]:
        with pydapper.connect(self.connection) as commands:
            users = commands.query("select user_name, password from user_account;", model=UserAccount)
        return users

    def get_all_users_by_channel(self, channel_name) -> list[str]:
        try:
            with pydapper.connect(self.connection) as commands:
                users = commands.query("select user_account_fk from user_account_in_channel where channel_fk=?1?;",
                                       param={"1": channel_name})
            return map_to_strings_from_dictionary(users)
        except NoResultException:
            return []

    def is_user_found(self, user_name) -> (bool, UserAccount | None):
        with pydapper.connect(self.connection) as commands:
            try:
                user = commands.query_single("select user_name, password from user_account where user_name=?1?;",
                                             model=UserAccount, param={"1": user_name})
                return True, user
            except NoResultException:
                return False, None

    def is_channel_found(self, channel_name) -> (bool, Channel | None):
        with pydapper.connect(self.connection) as commands:
            try:
                channel = commands.query_single("select channel_name, password, is_public from channel "
                                                "where channel_name=?1?;", model=Channel, param={"1": channel_name})
                return True, channel
            except NoResultException:
                return False, None

    def is_new_message_created(self, sender, content, channel=None, dm=None) -> bool:
        with pydapper.connect(self.connection) as commands:
            rowcount = commands.execute(
                "insert into message (sender_fk, receiver_fk, channel_name_fk, content) "
                "values (?1?, ?2?, ?3?, ?4?)", param={"1": sender, "2": dm, "3": channel, "4": content}
            )
        return rowcount == 1

    def is_user_in_channel(self, user_name, channel_name) -> bool:
        with pydapper.connect(self.connection) as commands:
            try:
                commands.query_single("select channel_fk from user_account_in_channel where user_account_fk=?1? "
                                      "and channel_fk=?2?;", param={"1": user_name, "2": channel_name})
                return True
            except NoResultException:
                return False

    def is_user_joined_in_channel(self, user_name, channel_name) -> bool:
        is_user_in_channel = self.is_user_in_channel(user_name, channel_name)
        if is_user_in_channel:
            return True
        try:
            with pydapper.connect(self.connection) as commands:
                rowcount = commands.execute(
                    "insert into user_account_in_channel (user_account_fk, channel_fk) "
                    "values (?1?, ?2?)", param={"1": user_name, "2": channel_name}
                )
                return rowcount == 1
        except psycopg2.errors.ForeignKeyViolation as e:
            print(e)
            return False
