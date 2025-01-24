from typing import Any

import psycopg2.errors
import pydapper
import os
from psycopg2.errors import UniqueViolation
from pydapper.exceptions import NoResultException
from data_base_models import *
from messagedto import MessageDto
import sqlite_init_commands as sql_stm


def map_to_strings_from_dictionary(values: list[dict[Any]]) -> list[str]:
    messages = []
    for d in values:
        for k, v in d.items():
            messages.append(v)
    return messages


def map_to_dto(src: Message) -> MessageDto:
    try:
        ts = f'{src.time_stamp.strftime("%H:%M")}'
    except Exception as e:
        print(e)
        ts = src.time_stamp
    return MessageDto(src.content, src.sender_fk, ts, src.id, src.channel_id)


def map_to_dtos(messages: list[Message]) -> list[MessageDto]:
    results = []
    for message in messages:
        dto = map_to_dto(message)
        results.append(dto)
    return results


def is_pg_database_build(cnx) -> bool:
    try:
        path = '../../dbinit/init.sql'
        with pydapper.connect(cnx) as commands:
            with open(path, 'w') as file:
                sql_init = file.read()
                commands.execute(sql_init)
                commands.execute(sql_stm.insert_global_channel)
    except Exception as e:
        print(e)
        return False
    return True


def is_sqlite_database_build(cnx) -> bool:
    try:
        file_name = 'messenger.sqlite'
        if os.path.exists(file_name):
            os.remove(file_name)
        file = open(file_name, 'w')
        file.close()
        with pydapper.connect(cnx) as commands:
            commands.execute(sql_stm.create_table_user_account)
            commands.execute(sql_stm.create_table_channel)
            commands.execute(sql_stm.create_table_user_account_in_channel)
            commands.execute(sql_stm.create_table_message)
            commands.execute(sql_stm.insert_global_channel)
    except Exception as e:
        print(e)
        return False
    return True



class MessengerRepository:
    def __init__(self):
        try:
            cnx = os.environ["POSTGRES_CONNECTION_STRING"]
            self.connection = cnx
        except KeyError:
            print("Es wurde kein Connectionstring in den Umgebungsvariablen gefunden.")
            self.connection = "postgresql+psycopg2://postgres:mysecretpassword@127.0.0.1:5432"
        self.init_database()

    def init_database(self):
        if not is_pg_database_build(self.connection):
            print("Keine Postgresdatenbank gefunden. Erstelle lokales sqlite Fallback.")
            self.connection = f"sqlite+sqlite3://messenger.sqlite"
            if not is_sqlite_database_build(self.connection):
                raise Exception("Die Erstellung der sqlite Datenbank ist fehlgeschlagen.")

    def is_new_user_created(self, user_name, password) -> bool:
        with pydapper.connect(self.connection) as commands:
            try:
                rowcount = commands.execute(
                    "insert into user_account (user_name, password) values (?1?, ?2?)",
                    param={"1": user_name, "2": password}
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

    def get_all_channels_by_user_name(self, user_name) -> list[str]:
        try:
            with pydapper.connect(self.connection) as commands:
                channels = commands.query(
                    """
                    select channel_fk 
                    from user_account_in_channel 
                    where user_account_fk=?1?;""",
                    param={"1": user_name})
            return channels
        except NoResultException:
            return []

    def get_all_messages_by_channel_name(self, channel_name) -> list[MessageDto]:
        try:
            with pydapper.connect(self.connection) as commands:
                messages = commands.query(
                    """
                    select content, time_stamp, sender_fk, id, channel_name_fk as channel_id
                    from message            
                    where channel_name_fk=?1?;
                    """,
                    param={"1": channel_name}, model=Message)
            return map_to_dtos(messages)
        except NoResultException:
            return []

    def is_message_found(self, message_id) -> (bool, MessageDto | None):
        try:
            with pydapper.connect(self.connection) as commands:
                message = commands.query_single(
                    """
                    select content, time_stamp, sender_fk, id, channel_name_fk as channel_id
                    from message
                    where id=?1?;
                    """,
                    param={"1": message_id}, model=Message)
            if message is not None:
                return True, map_to_dto(message)
        except NoResultException as e:
            print(e)
            return False, None

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

    def is_new_message_created(self, sender, content, chn=None, dm=None) -> (bool, MessageDto | None):
        with pydapper.connect(self.connection) as commands:
            result = commands.query_first(
                "insert into message (sender_fk, receiver_fk, channel_name_fk, content, id) "
                "values (?1?, ?2?, ?3?, ?4?, ?5?) RETURNING id;",
                param={"1": sender, "2": dm, "3": chn, "4": content, "5": str(uuid.UUID)}
            )
            message_id = result['id']
        if message_id is not None:
            return self.is_message_found(message_id)
        return False, None

    def is_message_deleted(self, message_id) -> bool:
        with pydapper.connect(self.connection) as commands:
            row_count = commands.execute(
                "delete from message where id = ?1?", param={"1":  message_id}
            )
            return row_count == 1

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

    def is_message_deleted_by_id(self, message_id) -> bool:
        with pydapper.connect(self.connection) as commands:
            try:
                commands.execute("delete from message where id=?1? ", param={"1": message_id})
                return True
            except Exception as e:
                print(e)
                return False
