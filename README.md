**Сущности БД музыкального сайта:**

genre - таблица с именами жанров

artist - таблица с именами артистов

album - таблица с названиями альбомов

song - таблица с названиями песен

collection - таблица со сборниками

artist_genre - таблица для связи артистов и жанров (многие ко многим)

artist_album - таблица для связи артистов и альбомов (многие ко многим)

collection_song - таблица для связи сборников и песен (многие ко многим)

**Сущности БД "Сотрудники":**

department - таблица с названиями отделов

employee - таблица с сотрудниками. Аргумент department_ID - внешний ключ на department_ID таблицы department (отдел, где сотрудник работает)

boss - таблица для хранения информации о сотрудниках, являющихся начальниками отделов. В данном варианте один сотрудник может быть начальником более, чем в 2-х отделах. Если необходимо учитывать, что одни сотрудник не может совмещать должность начальника другого отдела, то для employee_ID должно быть ограничение UNIQUE

