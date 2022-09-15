CREATE TABLE player_status (
    name VARCHAR(100),
    hitting BOOLEAN,
    hr VARCHAR(15)
);

CREATE TABLE users (
    name VARCHAR(100),
    phone_number VARCHAR(15)
);

INSERT INTO player_status (
    name,
    hitting,
    hr
)
VALUES (
    'a. pujols',
    false,
    695
);

INSERT INTO users (
    name,
    phone_number
)
VALUES (
    'Logan Roach',
    '9188845288'
),
(
    'Freddie Baldwin',
    '3123614099'
),
(
    'Jon Broun',
    '3146517579'
);