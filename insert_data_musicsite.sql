INSERT INTO artist(first_name, last_name, nickname)
VALUES ('Михаил', 'Горшенёв', 'Горшок'),
       ('Сергей', 'Шнуров', 'Шнур'),
       ('Игорь', 'Сукачёв', NULL),
       ('Сергей', 'Михалок', 'Ляпис Трубецкой');
	   
INSERT INTO genre(genre_name)
VALUES ('рок'),
       ('панк-рок'),
       ('Фолк-рок'),
       ('поп-рок');
	   
INSERT INTO collection(collection_name, date_collection)
VALUES ('Сборник русского рока', TO_DATE('2000', 'YYYY')),
       ('Лучшее из Ленинграда', TO_DATE('2019', 'YYYY')),
       ('Лирическое', TO_DATE('2000', 'YYYY')),
       ('Сборник для вечеринки', TO_DATE('2000', 'YYYY'));
	   
INSERT INTO album(album_name, date_album)
VALUES ('Король и Шут. Акустический альбом', TO_DATE('1999', 'YYYY')),
       ('Как в старой сказке', TO_DATE('2020', 'YYYY')),
	   ('Театръ демона', TO_DATE('2010', 'YYYY')),
       ('Дачники', TO_DATE('2000', 'YYYY')),
       ('Пираты XXI века', TO_DATE('2002', 'YYYY')),
	   ('Перезвоны', TO_DATE('2005', 'YYYY')),
	   ('Реки', TO_DATE('1993', 'YYYY')),
	   ('Ты кинула', TO_DATE('1998', 'YYYY')),
	   ('Всем девченкам нравится...', TO_DATE('2000', 'YYYY'));
	   
INSERT INTO song(song_name, song_duration, date_song, album_id)
VALUES ('Кукла колдуна', 202, TO_DATE('1999', 'YYYY'), 1),
       ('Прыгну со скалы', 191, TO_DATE('1999', 'YYYY'), 1),
       ('Ели мясо мужики', 133, TO_DATE('1999', 'YYYY'), 1),
       ('Проклятый старый дом', 257, TO_DATE('2020', 'YYYY'), 2),
	   ('Воспоминания о былой любви', 295, TO_DATE('2020', 'YYYY'), 2),
	   ('Танец злобного гения', 235, TO_DATE('2010', 'YYYY'), 3),
	   ('Дачники', 130, TO_DATE('2000', 'YYYY'), 4),
	   ('Когда нет денег', 178, TO_DATE('2000', 'YYYY'), 4),
	   ('Терминатор', 235, TO_DATE('2000', 'YYYY'), 4),
	   ('Космос', 101, TO_DATE('2000', 'YYYY'), 4),
	   ('WWW', 187, TO_DATE('2002', 'YYYY'), 5),
	   ('У меня есть всё', 267, TO_DATE('2002', 'YYYY'), 5),
	   ('Люди не летают', 164, TO_DATE('2002', 'YYYY'), 5),
	   ('Перезвоны', 202, TO_DATE('2005', 'YYYY'), 6),
	   ('Я милого узнаю по походке', 215, TO_DATE('2005', 'YYYY'), 6),
	   ('Белый колпак', 310, TO_DATE('1993', 'YYYY'), 7),
	   ('Дорожная', 314, TO_DATE('1993', 'YYYY'), 7),
	   ('На перекрестке Луны', 402, TO_DATE('1993', 'YYYY'), 7),
	   ('Ау', 234, TO_DATE('1998', 'YYYY'), 8),
	   ('Ты кинула', 237, TO_DATE('1998', 'YYYY'), 8),
	   ('Облака', 298, TO_DATE('1998', 'YYYY'), 8),
	   ('Любовь повернулась ко мне задом', 242, TO_DATE('2000', 'YYYY'), 9),
	   ('Крошка моя', 204, TO_DATE('2000', 'YYYY'), 9);
	   
INSERT INTO artist_album(artist_ID, album_ID)
VALUES (1, 1),
       (1, 2),
       (1, 3),
	   (2, 4),
	   (2, 5),
	   (3, 6),
	   (3, 7),
	   (4, 8),
	   (4, 9);
	   
INSERT INTO collection_song(collection_ID, song_ID)
VALUES (1, 1),
       (1, 2),
       (1, 3),
	   (1, 11),
	   (1, 20),
	   (2, 7),
	   (2, 8),
	   (2, 9),
	   (2, 10),
	   (2, 11),
	   (2, 12),
	   (3, 16),
       (3, 17),
	   (4, 3),
	   (4, 6),
	   (4, 9),
	   (4, 12),
	   (4, 19),
       (4, 20);
	   
INSERT INTO artist_genre(artist_ID, genre_ID)
VALUES (1, 1),
       (1, 2),
       (1, 3),
	   (2, 1),
	   (2, 4),
	   (3, 1),
	   (3, 4),
	   (4, 4);