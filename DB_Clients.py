import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pprint


class Postgres_DB:

    user = 'postgres'
    password = 'postgres'
    host = '127.0.0.1'
    port = '5432'
    name_db = 'clients'

    @staticmethod
    def postgres_db_info():
        ''' Функция для получения информации о PostgreSQL'''
        try:
            with psycopg2.connect(user=Postgres_DB.user,
                                  password=Postgres_DB.password,
                                  host=Postgres_DB.host,
                                  port=Postgres_DB.port) as conn:
                with conn.cursor() as cur:
                    connected_db_info = f'Информация о сервере PostgreSQL: {conn.get_dsn_parameters()}'
                    # Выполнение SQL-запроса для получения информации о версии БД
                    cur.execute("SELECT version();")
                    record = cur.fetchone()
        except (Exception, Error) as error:
            return f'Ошибка при работе с PostgreSQL, {error}'
        finally:
            return connected_db_info + f'\n"Вы подключены к - {record}'

    @staticmethod
    def postgres_db_create():
        ''' Функция для создания базы данных на PostgreSQL'''
        conn = psycopg2.connect(user=Postgres_DB.user,
                              password=Postgres_DB.password,
                              host=Postgres_DB.host,
                              port=Postgres_DB.port)
        cur =  conn.cursor()
        conn.autocommit = True
        sql_create_database = f'CREATE DATABASE {Postgres_DB.name_db};'
        cur.execute(sql_create_database)
        cur.close()
        conn.close()
        return f'База данных "{Postgres_DB.name_db}" создана'

    @staticmethod
    def postgres_db_drop():
        ''' Функция для удаления созданной базы данных на PostgreSQL'''
        conn = psycopg2.connect(user=Postgres_DB.user,
                                password=Postgres_DB.password,
                                host=Postgres_DB.host,
                                port=Postgres_DB.port)
        cur = conn.cursor()
        conn.autocommit = True
        sql_create_database = f'DROP DATABASE IF EXISTS {Postgres_DB.name_db};'
        cur.execute(sql_create_database)
        cur.close()
        conn.close()
        return f'База данных "{Postgres_DB.name_db}" удалена'

    @staticmethod
    def create_db_structure():
        ''' Функция для создания структуры базы данных 'clients'.
        Создаются две таблицы 'client' и 'client_phone' связанные по 'id_client' '''
        with psycopg2.connect(database=Postgres_DB.name_db,
                              user=Postgres_DB.user,
                              password=Postgres_DB.password,
                              host=Postgres_DB.host,
                              port=Postgres_DB.port) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                            CREATE TABLE IF NOT EXISTS client(
                                   id_client SERIAL PRIMARY KEY,
                                   first_name VARCHAR(40) NOT NULL,
                                   second_name VARCHAR(40) NOT NULL,
                                   email_address VARCHAR(40)
                                   );
                            ''')
                cur.execute('''
                            CREATE TABLE IF NOT EXISTS client_phone(
                                   id_phone SERIAL PRIMARY KEY,
                                   phone_number VARCHAR(20),
                                   id_client INTEGER REFERENCES client(id_client)
                                   );
                            ''')
                conn.commit()
        return f'Таблицы "client" и "client_phone" созданы'


    def insert_db_value(self,
                        first_name,
                        second_name,
                        email_address,
                        client_phone):
        ''' Функция для наполнения таблиц 'client' и 'client_phone' '''
        with psycopg2.connect(database=Postgres_DB.name_db,
                              user=Postgres_DB.user,
                              password=Postgres_DB.password,
                              host=Postgres_DB.host,
                              port=Postgres_DB.port) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                           INSERT INTO client(
                                  first_name,
                                  second_name,
                                  email_address)
                           VALUES (%s, %s, %s)
                        RETURNING id_client''', (first_name, second_name, email_address));
                id_client = cur.fetchone()[0]
                if len(client_phone) == 0:
                    cur.execute('''
                    INSERT INTO client_phone(phone_number, id_client)
                    VALUES (%s, %s)''', (None, id_client))
                else:
                    for i in range(len(client_phone)):
                        cur.execute('''
                        INSERT INTO client_phone(phone_number, id_client) VALUES (%s, %s)''', (client_phone[i], id_client))
                conn.commit()


    def add_phone_number(self, id_client, client_phone):
        ''' Функция для добавления телефона клиента по его ID '''
        with psycopg2.connect(database=Postgres_DB.name_db,
                              user=Postgres_DB.user,
                              password=Postgres_DB.password,
                              host=Postgres_DB.host,
                              port=Postgres_DB.port) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                            SELECT phone_number 
                              FROM client_phone 
                             WHERE id_client=%s;''', (id_client,))
                if cur.fetchone()[0] is None:
                    cur.execute('''
                                UPDATE client_phone 
                                   SET phone_number=%s 
                                 WHERE id_client=%s;''', (*client_phone, id_client))
                else:
                    cur.execute('''
                                INSERT INTO client_phone(phone_number, id_client) 
                                VALUES (%s, %s)''', (*client_phone, id_client))
                conn.commit()


    def del_phone_number(self, id_client):
        ''' Функция для Удаления телефона (телефонов) клиента по его ID '''
        with psycopg2.connect(database=Postgres_DB.name_db,
                              user=Postgres_DB.user,
                              password=Postgres_DB.password,
                              host=Postgres_DB.host,
                              port=Postgres_DB.port) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                            SELECT phone_number 
                              FROM client_phone 
                             WHERE id_client=%s;''', (id_client,))
                if len(cur.fetchall()) == 1:
                    cur.execute('''
                                UPDATE client_phone 
                                   SET phone_number=%s 
                                 WHERE id_client=%s;''', (None, id_client))
                else:
                    cur.execute('''
                                SELECT phone_number, id_phone 
                                  FROM client_phone 
                                 WHERE id_client=%s;''', (id_client,))
                    first_phone_id = cur.fetchall()[0][1]
                    cur.execute('''
                                DELETE FROM client_phone 
                                 WHERE id_phone!=%s 
                                       AND id_client=%s;''', (first_phone_id, id_client))
                    cur.execute('''
                                UPDATE client_phone 
                                   SET phone_number=%s 
                                 WHERE id_client=%s;''', (None, id_client))
                conn.commit()

    def find_client(self, str_search):
        ''' Функция для поиска клиентов по подстроке '''
        with psycopg2.connect(database=Postgres_DB.name_db,
                              user=Postgres_DB.user,
                              password=Postgres_DB.password,
                              host=Postgres_DB.host,
                              port=Postgres_DB.port) as conn:
            with conn.cursor() as cur:
                str_search = '%' + str_search + '%'
                cur.execute('''
                            SELECT first_name AS Имя,
                                   second_name AS Фамилия,
                                   email_address AS email,
                                   phone_number AS Телефон
                              FROM client JOIN client_phone
                                ON client.id_client = client_phone.id_client
                             WHERE first_name LIKE %s OR
                                   second_name LIKE %s OR
                                   email_address LIKE %s OR
                                   phone_number LIKE %s;''', (str_search, str_search, str_search, str_search))
                result = cur.fetchall()
                if result != []:
                    return result
                else:
                    return f'Данные по подстроке "{str_search}"не найдены'


    def del_client(self, id_client):
        ''' Функция для удаления клиента по его ID '''
        with psycopg2.connect(database=Postgres_DB.name_db,
                              user=Postgres_DB.user,
                              password=Postgres_DB.password,
                              host=Postgres_DB.host,
                              port=Postgres_DB.port) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                            SELECT first_name,
                                   second_name
                              FROM client
                             WHERE id_client=%s;''', (id_client,))
                result = cur.fetchone()
                if result is not None:
                    cur.execute('''
                                DELETE FROM client_phone
                                 WHERE id_client=%s;''', (id_client,))
                    cur.execute('''
                                DELETE FROM client
                                 WHERE id_client=%s;''', (id_client,))
                    conn.commit()
                    return f'Клиент {result} успешно удален'
                else:
                    return f'Клиент c ID: "{id_client}" не найден'


# Создаем объект класса
db_pg = Postgres_DB()

# Вывод информации о сервере Postgres
# pprint.pprint(db_pg.postgres_db_info())

# Создание базы данных "clients" на сервере Postgres
#print(db_pg.postgres_db_create())

# Можно удалить созданную базу данных "clients"
#print(db_pg.postgres_db_drop())

# Создание структуры базы данных "clients"
# print(db_pg.create_db_structure())

# Наполняем созданные таблицы данными (4 клиента)
# db_pg.insert_db_value(first_name='Иван',
#                       second_name='Иванов',
#                       email_address='ivan@yandex.ru',
#                       client_phone=['+7(915)081-21-21'])
# db_pg.insert_db_value(first_name='Василий',
#                       second_name='Сидоров',
#                       email_address='sidorov@yandex.ru',
#                       client_phone=['+7(925)280-21-21'])
# db_pg.insert_db_value(first_name='Илья',
#                       second_name='Петров',
#                       email_address='petrov@yandex.ru',
#                       client_phone=['+7(914)081-22-22', '+7(924) 155-01-01'])
# db_pg.insert_db_value(first_name='Алексей',
#                       second_name='Алексеев',
#                       email_address='alekseev@yandex.ru',
#                       client_phone=[])

# Добавляем номера телефонов клиентов с ID "3" и "4"
# db_pg.add_phone_number(id_client=4, client_phone=['+7(900)100-11-11'])
# db_pg.add_phone_number(id_client=3, client_phone=['+7(999)111-22-33'])

# Удаляем телефон (телефоны) у клиента с ID "4"
#db_pg.del_phone_number(id_client=4)

# Поиск данных в базе по подстроке
# pprint.pprint(db_pg.find_client(input('Введите искомые данные: ')))

# Удаление клиента по его ID
# pprint.pprint(del_client(input('Введите ID Клиента, которого необходимо удалить: ')))