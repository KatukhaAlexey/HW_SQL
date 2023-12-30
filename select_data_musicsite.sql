/* Самая продолжительная песня */
SELECT song_name AS Название_песни, 
       song_duration AS Продолжительность_с, 
       song_duration/60 + (MOD(CAST(song_duration AS DECIMAL), 60)/100) AS Продолжительность_мин
  FROM song
 WHERE song_duration = (SELECT MAX(song_duration) FROM song);

/* Треки продолжительностью 3.5 минут (210 секунд) и более */
SELECT song_name AS Название_песни, 
       song_duration/60+(MOD(CAST(song_duration AS DECIMAL), 60)/100) AS Продолжительность_мин
  FROM song
 WHERE song_duration >= 210;

/* Название сборников, вышедших в период с 2018 по 2020 год включительно */
SELECT collection_name, 
       date_collection
  FROM collection
 WHERE date_collection >= '2018-01-01' AND date_collection <= '2020-01-01';

/* Исполнители, чьё имя состоит не из одного слова. В данном запросе найдем "Никнейм" исполнителя, состоящий не из одного слова */
SELECT nickname AS Ник
  FROM artist
 WHERE nickname NOT LIKE '% %';

/* Название треков, которые содержат слово "мой" ("моя") или "my" */
SELECT song_name AS Название_песни
  FROM song
 WHERE song_name LIKE 'my %' 
       OR song_name LIKE 'мой %' 
       OR song_name LIKE 'моя %'
       OR song_name LIKE '% my'
       OR song_name LIKE '% мой'
       OR song_name LIKE '% моя';

/* Количество исполнителей в каждом жанре */
SELECT genre.genre_name AS Жанр, 
       COUNT(genre.genre_name) AS Количество_исполнителей
  FROM artist 
       INNER JOIN artist_genre 
       ON artist.artist_id = artist_genre.artist_id
       INNER JOIN genre 
       ON genre.genre_id = artist_genre.genre_id
 GROUP BY genre.genre_name;

/* Количество треков, вошедших в альбомы 2019-2020 годов */
SELECT COUNT(song.song_name) AS Количество_треков
  FROM song 
       INNER JOIN artist_album 
       ON song.album_id = artist_album.album_id
       INNER JOIN album 
       ON artist_album.album_id = album.album_id
 WHERE date_album >= '2019-01-01' AND date_album <= '2020-01-01';

/* Средняя продолжительность треков по каждому альбому */
SELECT album.album_name AS Альбом,
       ROUND(AVG(song.song_duration), 2) AS Средняя_продолжительность_трека
  FROM album
       INNER JOIN song
       ON album.album_id = song.album_id
 GROUP BY Альбом

/* Все исполнители, которые не выпустили альбомы в 2020 году */
SELECT CONCAT(artist.first_name, ' ', artist.last_name) AS Исполнитель
  FROM artist
 WHERE CONCAT(artist.first_name, ' ', artist.last_name) NOT IN --Находим исполнителя, который выпускал альбом в 2020 году
       (SELECT CONCAT(artist.first_name, ' ', artist.last_name) AS Исполнитель
          FROM artist
               INNER JOIN artist_album
               ON artist_album.artist_id = artist.artist_id
               INNER JOIN album
               ON album.album_id = artist_album.album_id
         WHERE album.date_album >= '2020-01-01' AND album.date_album <= '2020-12-31'
        )
 GROUP BY Исполнитель;
    
/* Названия сборников, в которых присутствует конкретный исполнитель (по выбору). Ищем 'Ляпис Трубецкой'*/
SELECT collection.collection_name AS Сборник
  FROM collection
       INNER JOIN collection_song
       ON collection_song.collection_id = collection.collection_id
       INNER JOIN song
       ON song.song_id = collection_song.song_id
       INNER JOIN album
       ON album.album_id = song.album_id
       INNER JOIN artist_album
       ON artist_album.album_id = album.album_id
       INNER JOIN artist
       ON artist.artist_id = artist_album.album_id
       WHERE artist.nickname LIKE 'Ляпис Трубецкой'
 GROUP BY Сборник;

/* Названия альбомов, в которых присутствуют исполнители более чем одного жанра */
SELECT album.album_name AS Альбом
  FROM album
       INNER JOIN artist_album
       ON artist_album.album_id = album.album_id
       INNER JOIN artist
       ON artist.artist_id = artist_album.album_id
       INNER JOIN artist_genre 
       ON artist.artist_id = artist_genre.artist_id
       INNER JOIN genre 
       ON genre.genre_id = artist_genre.genre_id
 GROUP BY Альбом
 HAVING COUNT(genre.genre_name) > 1;

/* Наименования треков, которые не входят в сборники */
SELECT song.song_name AS Трек
  FROM song 
 WHERE song.song_name NOT IN 
       (SELECT song.song_name AS Трек
          FROM song 
               INNER JOIN collection_song
               ON collection_song.song_id = song.song_id
               INNER JOIN collection
               ON collection.collection_id = collection_song.collection_id)     
               
/* Исполнитель или исполнители, написавшие самый короткий по продолжительности трек */
SELECT CONCAT(artist.first_name, ' ', artist.last_name) AS Исполнитель
  FROM artist
       INNER JOIN artist_album
       ON artist_album.artist_id = artist.artist_id
       INNER JOIN album
       ON album.album_id = artist_album.album_id
       INNER JOIN song
       ON album.album_id = song.album_id
 WHERE song.song_duration = 
       (SELECT MIN(song.song_duration) FROM song)
 
/* Названия альбомов, содержащих наименьшее количество треков */
 SELECT Альбом, MIN(Количество_треков)
   FROM (SELECT album.album_name AS Альбом, COUNT(song.song_name) AS Количество_треков
          FROM album
         INNER JOIN song
               ON album.album_id = song.album_id
         GROUP BY album.album_name)
  GROUP BY Альбом
