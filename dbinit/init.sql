create table user_account
(
    user_name varchar(20)  default 'DEFAULT'::character varying not null
        constraint user_account_pk
            primary key,
    password  varchar(128) default ''::character varying        not null
);

alter table user_account
    owner to postgres;

create table channel
(
    channel_name varchar(20)  default 'GLOBAL'::character varying not null
        constraint channel_pk
            primary key,
    password     varchar(128) default ''::character varying       not null,
    is_public    boolean      default true                        not null
);

alter table channel
    owner to postgres;

create table user_account_in_channel
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

alter table user_account_in_channel
    owner to postgres;

create table message
(
    id              uuid                     default gen_random_uuid()     not null
        constraint message_pk
            primary key,
    time_stamp      timestamp with time zone default CURRENT_TIMESTAMP     not null,
    sender_fk       varchar(20)                                            not null
        constraint message_user_account_user_name_fk
            references user_account
            on delete cascade,
    content         varchar(8096)            default ''::character varying not null,
    receiver_fk     varchar(20)
        constraint message_user_account_user_name_fk_2
            references user_account
            on delete cascade,
    channel_name_fk varchar(20)
        constraint message_channel_channel_name_fk
            references channel
            on delete cascade
);

alter table message
    owner to postgres;

