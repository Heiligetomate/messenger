create_table_user_account = """
create table if not exists user_account
(
    user_name varchar(20)  default '' not null
        constraint user_account_pk
            primary key,
    password  varchar(128) default ''       not null
);
"""

create_table_channel = """
create table if not exists channel
(
    channel_name varchar(20)  default '' not null
        constraint channel_pk
            primary key,
    password     varchar(128) default ''      not null,
    is_public    boolean      default true                        not null
);
"""

create_table_user_account_in_channel = """
create table if not exists user_account_in_channel
(
    user_account_fk varchar(20) not null
        constraint user_account_in_channel_user_account_user_name_fk
            references user_account
            on delete cascade,
    channel_fk      varchar(20) not null
        constraint user_account_in_channel_channel_channel_name_fk
            references channel
            on delete cascade
);
"""

create_table_message = """
create table if not exists message
(
    id              varchar(36)                         not null
        constraint message_pk
            primary key,
    time_stamp      timestamp with time zone default CURRENT_TIMESTAMP     not null,
    sender_fk       varchar(20)                                            not null
        constraint message_user_account_user_name_fk
            references user_account
            on delete cascade,
    content         varchar(8096)            default '' not null,
    receiver_fk     varchar(20)
        constraint message_user_account_user_name_fk_2
            references user_account
            on delete cascade,
    channel_name_fk varchar(20)
        constraint message_channel_channel_name_fk
            references channel
            on delete cascade
);
"""

insert_global_channel = "insert into channel (channel_name, is_public) VALUES ('global', true);"