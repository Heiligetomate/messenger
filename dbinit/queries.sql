-- Create, Read, Update, Delete - CRUD Operations
INSERT INTO user_account (user_name, password) VALUES ('Matti', 'password');

SELECT user_name, password
FROM user_account;

UPDATE user_account
SET user_name = 'Juri'
WHERE user_name = 'juri';

DELETE FROM user_account WHERE user_name = 'Juri';


INSERT INTO message (sender_fk, content, receiver_fk) VALUES ('Matti', 'Hello World', 'Hannes');
INSERT INTO message (sender_fk, content, receiver_fk) VALUES ('Matti', 'Hello World', 'Juri');
INSERT INTO message (sender_fk, content, receiver_fk) VALUES ('Juri', 'Hello World', 'Matti');
INSERT INTO message (sender_fk, content, receiver_fk) VALUES ('Juri', 'Hello World', 'Hannes');
INSERT INTO message (sender_fk, content, receiver_fk) VALUES ('Hannes', 'Hello World', 'Juri');
INSERT INTO message (sender_fk, content, receiver_fk) VALUES ('Hannes', 'Hello World', 'Matti');


INSERT INTO message (sender_fk, content, channel_name_fk) VALUES ('Hannes', 'Hello World', 'Gurke');
INSERT INTO message (sender_fk, content, channel_name_fk) VALUES ('Hannes', 'Hello World', 'Gurke');
INSERT INTO message (sender_fk, content, channel_name_fk) VALUES ('Hannes', 'Hello World', 'Gurke');
INSERT INTO message (sender_fk, content, channel_name_fk) VALUES ('Juri', 'Hello World', 'Salat');
INSERT INTO message (sender_fk, content, channel_name_fk) VALUES ('Juri', 'Hello World', 'Gurke');
INSERT INTO message (sender_fk, content, channel_name_fk) VALUES ('Juri', 'Hello World', 'Gurke');
INSERT INTO message (sender_fk, content, channel_name_fk) VALUES ('Juri', 'Hello World', 'Salat');
INSERT INTO message (sender_fk, content, channel_name_fk) VALUES ('Juri', 'Hello World', 'Gurke');

INSERT INTO channel (channel_name, password, is_public) VALUES ('Tomate', '123kartoffel', false);

INSERT INTO user_account_in_channel (user_account_fk, channel_fk) values ('Hannes', 'Tomate');
INSERT INTO user_account_in_channel (user_account_fk, channel_fk) values ('Hannes', 'Salat');


INSERT INTO user_account_in_channel (user_account_fk, channel_fk) values ('Juri', 'Tomate');
INSERT INTO user_account_in_channel (user_account_fk, channel_fk) values ('Juri', 'Salat');
INSERT INTO user_account_in_channel (user_account_fk, channel_fk) values ('Juri', 'Gurke');
INSERT INTO user_account_in_channel (user_account_fk, channel_fk) values ('Matti', 'Gurke');


SELECT channel_fk, id as MessageId, time_stamp, sender_fk, content
FROM user_account_in_channel
JOIN message on user_account_in_channel.channel_fk = message.channel_name_fk
WHERE user_account_in_channel.user_account_fk = 'Juri';


SELECT * FROM message where channel_name_fk = 'Gurke';


SELECT distinct channel_fk, is_public
FROM user_account_in_channel uac
JOIN channel c ON uac.channel_fk = c.channel_name
WHERE user_account_fk='123';

insert into user_account_in_channel (user_account_fk, channel_fk) values ('123', 'juris-kanal');


SELECT * FROM channel;
SELECT id, time_stamp FROM message WHERE time_stamp < CURRENT_TIMESTAMP;

SELECT id, time_stamp, sender_fk, content, receiver_fk
FROM message
WHERE channel_name_fk IS NOT NULL
  AND message.receiver_fk IS NOT NULL;

SELECT id, time_stamp, sender_fk, content, channel_name_fk FROM message WHERE channel_name_fk IS NOT NULL;

INSERT INTO user_account (password, user_name) VALUES ('123', 'Keule');



alter table public.message
drop constraint message_user_account_user_name_fk_2,
add constraint message_user_account_user_name_fk_2
   foreign key (receiver_fk)
   references user_account(user_name)
   on delete cascade;



