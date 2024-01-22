import psycopg2
from psycopg2 import Error
# import os
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pprint


class PostgresDb:

    user = 'postgres'
    password = 'postgres'
    host = '127.0.0.1'
    port = '5432'
    name_db = 'clients'

    @staticmethod
    def postgres_db_info():
        """ Функция для получения информации о PostgreSQL """
        try:
            with psycopg2.connect(user=PostgresDb.user,
                                  password=PostgresDb.password,
                                  host=PostgresDb.host,
                                  port=PostgresDb.port) as conn:
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
        """ Функция для создания базы данных на PostgreSQL"""
        conn = psycopg2.connect(user=PostgresDb.user,
                                password=PostgresDb.password,
                                host=PostgresDb.host,
                                port=PostgresDb.port)
        cur = conn.cursor()
        conn.autocommit = True
        sql_create_database = f'CREATE DATABASE {PostgresDb.name_db};'
        cur.execute(sql_create_database)
        cur.close()
        conn.close()
        return f'База данных "{PostgresDb.name_db}" создана'

    @staticmethod
    def postgres_db_drop():
        """ Функция для удаления созданной базы данных на PostgreSQL"""
        conn = psycopg2.connect(user=PostgresDb.user,
                                password=PostgresDb.password,
                                host=PostgresDb.host,
                                port=PostgresDb.port)
        cur = conn.cursor()
        conn.autocommit = True
        sql_create_database = f'DROP DATABASE IF EXISTS {PostgresDb.name_db};'
        cur.execute(sql_create_database)
        cur.close()
        conn.close()
        return f'База данных "{PostgresDb.name_db}" удалена'

    @staticmethod
    def create_db_structure():
        """ Функция для создания структуры базы данных 'clients'.
        Создаются две таблицы 'client' и 'client_phone' связанные по 'id_client' """
        with psycopg2.connect(database=PostgresDb.name_db,
                              user=PostgresDb.user,
                              password=PostgresDb.password,
                              host=PostgresDb.host,
                              port=PostgresDb.port) as conn:
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
        """ Функция для наполнения таблиц 'client' и 'client_phone' """
        with psycopg2.connect(database=PostgresDb.name_db,
                              user=PostgresDb.user,
                              password=PostgresDb.password,
                              host=PostgresDb.host,
                              port=PostgresDb.port) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                           INSERT INTO client(
                                  first_name,
                                  second_name,
                                  email_address)
                           VALUES (%s, %s, %s)
                        RETURNING id_client''', (first_name, second_name, email_address))
                id_client = cur.fetchone()[0]
                if len(client_phone) == 0:
                    cur.execute('''
                    INSERT INTO client_phone(phone_number, id_client)
                    VALUES (%s, %s)''', (None, id_client))
                else:
                    for i in range(len(client_phone)):
                        cur.execute('''
                        INSERT INTO client_phone(phone_number, id_client) 
                        VALUES (%s, %s)''', (client_phone[i], id_client))
                conn.commit()

    def add_phone_number(self, id_client, client_phone):
        """ Функция для добавления телефона клиента по его ID """
        with psycopg2.connect(database=PostgresDb.name_db,
                              user=PostgresDb.user,
                              password=PostgresDb.password,
                              host=PostgresDb.host,
                              port=PostgresDb.port) as conn:
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
        """ Функция для Удаления телефона (телефонов) клиента по его ID """
        with psycopg2.connect(database=PostgresDb.name_db,
                              user=PostgresDb.user,
                              password=PostgresDb.password,
                              host=PostgresDb.host,
                              port=PostgresDb.port) as conn:
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

    def del_client(self, id_client):
        """ Функция для удаления клиента по его ID """
        with psycopg2.connect(database=PostgresDb.name_db,
                              user=PostgresDb.user,
                              password=PostgresDb.password,
                              host=PostgresDb.host,
                              port=PostgresDb.port) as conn:
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

    def find_client(self, param_search):
        """ Функция для поиска клиентов по подстроке """
        # result = {}
        # sql_text_for_select = ''
        # str_search = ''
        str_many_search = []
        sql_text_for_many_select = []
        if param_search == {}:
            return f'Параметры поиска клиента в базе данных не заданы'
        # Если задан только одни параметр поиска и это не поиск по всем полям и не поиск по всей базе
        elif (len(param_search) == 1 and
              f'{list(*param_search.items())[0]}' != '*' and
              f'{list(*param_search.items())[0]}' != '**'):
            sql_text_for_select = f'{list(*param_search.items())[0]} LIKE %s;'
            str_search = '%' + list(*param_search.items())[1] + '%'
            with psycopg2.connect(database=PostgresDb.name_db,
                                  user=PostgresDb.user,
                                  password=PostgresDb.password,
                                  host=PostgresDb.host,
                                  port=PostgresDb.port) as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                                SELECT client.id_client,
                                       first_name,
                                       second_name,
                                       email_address,
                                       phone_number
                                  FROM client JOIN client_phone
                                    ON client.id_client = client_phone.id_client
                                 WHERE ''' + sql_text_for_select, (str_search,))
                    result = cur.fetchall()
            return print(result)
        # Если задан один параметр поиска подстроки и это поиск по всей базе на любые совпадения по всем полям
        elif len(param_search) == 1 and f'{list(*param_search.items())[0]}' == '*':
            with psycopg2.connect(database=PostgresDb.name_db,
                                  user=PostgresDb.user,
                                  password=PostgresDb.password,
                                  host=PostgresDb.host,
                                  port=PostgresDb.port) as conn:
                with conn.cursor() as cur:
                    str_search = '%' + f'{list(*param_search.items())[1]}' + '%'
                    cur.execute('''
                            SELECT client.id_client,
                                   first_name,
                                   second_name,
                                   email_address,
                                   phone_number
                              FROM client JOIN client_phone
                                ON client.id_client = client_phone.id_client
                             WHERE first_name LIKE %s OR
                                   second_name LIKE %s OR
                                   email_address LIKE %s OR
                                   phone_number LIKE %s;''', (str_search, str_search, str_search, str_search))
                    result = cur.fetchall()
            if result:
                return result
            else:
                return f'Данные по подстроке "{str_search}"не найдены'
        # Если задан один параметр поиска и это ВСЕЙ информации из базы
        elif len(param_search) == 1 and f'{list(*param_search.items())[0]}' == '**':
            sql_text_for_select = f'{list(*param_search.items())[1]}'
            with psycopg2.connect(database=PostgresDb.name_db,
                                  user=PostgresDb.user,
                                  password=PostgresDb.password,
                                  host=PostgresDb.host,
                                  port=PostgresDb.port) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_text_for_select)
                    result = cur.fetchall()
            return result
        # Если задано несколько параметров поиска в базе
        else:
            for k, v in list(param_search.items()):
                sql_text_for_many_select.append(k)
                str_many_search.append('%' + v + '%')
            sql_text_for_select = ' LIKE %s AND '.join(sql_text_for_many_select) + ' LIKE %s;'
            with psycopg2.connect(database=PostgresDb.name_db,
                                  user=PostgresDb.user,
                                  password=PostgresDb.password,
                                  host=PostgresDb.host,
                                  port=PostgresDb.port) as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                                SELECT client.id_client,
                                       first_name,
                                       second_name,
                                       email_address,
                                       phone_number
                                  FROM client JOIN client_phone
                                    ON client.id_client = client_phone.id_client
                                 WHERE ''' + sql_text_for_select, str_many_search)
                    result = cur.fetchall()
            return result

    def find_info(self):
        """ Функция для формирования блока запроса информации о клиентах
            Пользователю необходимо будет выбрать один или несколько параметров поиска,
            после чего ввести "0"
            Если выбрать поиск подстроки по всей базе, или вывод всей информации из базы,
            то, соответственно запрос по нескольким параметрам не работает"""
        # os.system('cls' if os.name == 'nt' else 'clear')
        print('\033c', end='')
        ch = ''
        search_bar = ''
        result = {}
        while ch not in ('q', 'Q'):
            print('*' * 86)
            print(f'* Поиск будет осуществлен по:{search_bar}')
            print('*' * 86)
            print('* Для поиска информации в базе данных нажмите: ')
            print('*')
            print('* "1" - поиск по имени клиента: ')
            print('* "2" - поиск по фамилии клиента: ')
            print('* "3" - поиск по электронной почте клиента: ')
            print('* "4" - поиск по телефону клиента: ')
            print('* "5" - поиск по всем полям базы данных: ')
            print('* "6" - вывод информации по всем клиентам в базе данных: ')
            print('* "0" - Для начала поиска: ')
            print('*')
            print('*' * 86)
            print('* Для выхода нажмите "q"')
            print('*' * 86)
            ch = input('Введите один или несколько пунктов и нажмите "0": ')
            if ch not in ('1', '2', '3', '4', '5', '6', '0', 'q', 'Q'):
                print('\033c', end='')
                print('\033[31m ДАННОГО ПУНКТА НЕТ В МЕНЮ! \033[0m')
                search_bar = ''
                result = {}
            elif ch == '0' and search_bar == '':
                print('\033c', end='')
                print('\033[31m НЕ ВЫБРАНО НИ ОДНОГО ВАРИАНТА ПОИСКА! \033[0m')
            elif ch == '0' and search_bar != '':
                print('\033c', end='')
                print('*' * 86)
                print('Введите строки поиска. Поиск осуществляется по "маске". Регистр имеет значение.')
                print('*' * 86)
                for key, volume in result.items():
                    match key:
                        case 'first_name':
                            result[key] = input('Введите значение для поиска по имени: ')
                        case 'second_name':
                            result[key] = input('Введите значение для поиска по фамилии: ')
                        case 'email_address':
                            result[key] = input('Введите значение для поиска по электронной почте: ')
                        case 'phone_number':
                            result[key] = input('Введите значение для поиска по телефону: ')
                        case '*':
                            result[key] = input('Введите подстроку для поиска: ')
                        case '**':
                            result[key] = '''SELECT client.id_client,
                                                    first_name,
                                                    second_name,
                                                    email_address,
                                                    phone_number
                                               FROM client JOIN client_phone
                                                 ON client.id_client = client_phone.id_client'''
                print('*' * 86)
                return result
            else:
                print('\033c', end='')
                match ch:
                    case '1':
                        if search_bar == '':
                            search_bar += '\033[33m  по имени\033[0m'
                            result['first_name'] = ''
                        else:
                            if '*' or '**' in result:
                                result.clear()
                                search_bar = '\033[33m  по имени\033[0m'
                                result['first_name'] = ''
                            elif 'first_name' not in result:
                                search_bar += '\033[33m , по имени\033[0m'
                                result['first_name'] = ''
                    case '2':
                        if search_bar == '':
                            search_bar += '\033[33m  по фамилии\033[0m'
                            result['second_name'] = ''
                        else:
                            if '*' or '**' in result:
                                result.clear()
                                search_bar = '\033[33m  по фамилии\033[0m'
                                result['second_name'] = ''
                            elif 'second_name' not in result:
                                search_bar += '\033[33m , по фамилии\033[0m'
                                result['second_name'] = ''
                    case '3':
                        if search_bar == '':
                            search_bar += '\033[33m  по электронной почте\033[0m'
                            result['email_address'] = ''
                        else:
                            if '*' or '**' in result:
                                result.clear()
                                search_bar = '\033[33m  по электронной почте\033[0m'
                                result['email_address'] = ''
                            elif 'email_address' not in result:
                                search_bar += '\033[33m , по электронной почте\033[0m'
                                result['email_address'] = ''
                    case '4':
                        if search_bar == '':
                            search_bar += '\033[33m  по телефону\033[0m'
                            result['phone_number'] = ''
                        else:
                            if '*' or '**' in result:
                                result.clear()
                                search_bar = '\033[33m  по телефону\033[0m'
                                result['phone_number'] = ''
                            elif 'phone_number' not in result:
                                search_bar += '\033[33m , по телефону\033[0m'
                                result['phone_number'] = ''
                    case '5':
                        search_bar = '\033[33m  ПОИСК ПОДСТРОКИ ПО ВСЕЙ БАЗЕ ДАННЫХ\033[0m'
                        result.clear()
                        result['*'] = ''
                    case '6':
                        search_bar = '\033[33m  ВЫВОД ВСЕЙ ИНФОРМАЦИИ О КЛИЕНТАХ\033[0m'
                        result.clear()
                        result['**'] = ''
        result = {}
        return result

    def modify_info(self):
        """ Функция для формирования блока запроса информации на изменение в базе данных.
         Запрашивается ID клиента, информацию о котором необходимо исправить и
         поля, в которые необходимо внести изменения.
         Результатом работы функции является ID клиента и словарь с именами полей и новыми значениями"""
        # os.system('cls' if os.name == 'nt' else 'clear')
        print('\033c', end='')
        ch = ''
        search_bar = ''
        result = {}
        id_modify_client = None
        while ch not in ('q', 'Q'):
            print('*' * 86)
            if id_modify_client is None:
                id_modify_client = input('Введите ID клиента, данные которого необходимо изменить: ')
            if id_modify_client in ('q', 'Q'):
                id_modify_client = None
                break
            elif id_modify_client.isnumeric():
                print('*' * 86)
                print(f'* Изменить данные клиента c ID {id_modify_client}:{search_bar}')
                print('*' * 86)
                print('* Укажите, какую именно информацию необходимо изменить: ')
                print('*')
                print('* "1" - имя клиента: ')
                print('* "2" - фамилию клиента: ')
                print('* "3" - электронную почту клиента: ')
                print('* "4" - телефон клиента: ')
                print('* "0" - для начала внесения изменений: ')
                print('*')
                print('*' * 86)
                print('* Для выхода нажмите "q"')
                print('*' * 86)
                ch = input('Введите один или несколько пунктов и нажмите "0": ')                
                if ch not in ('1', '2', '3', '4', '0', 'q', 'Q'):
                    print('\033c', end='')
                    print('\033[31m ДАННОГО ПУНКТА НЕТ В МЕНЮ! \033[0m')
                    search_bar = ''
                    result = {}
                elif ch == '0' and search_bar == '':
                    print('\033c', end='')
                    print('*' * 86)
                    print('\033[31m НЕ ВЫБРАНО НИ ОДНОГО ПАРАМЕТРА ДЛЯ ИЗМЕНЕНИЯ! \033[0m')
                elif ch == '0' and search_bar != '':
                    print('\033c', end='')
                    print('*' * 86)
                    print('Введите измененные данные.')
                    print('*' * 86)
                    for key, volume in result.items():
                        match key:
                            case 'first_name':
                                result[key] = input('Введите новое именя клиента: ')
                            case 'second_name':
                                result[key] = input('Введите новую фамилию клиента: ')
                            case 'email_address':
                                result[key] = input('Введите новую электронную почту клиента: ')
                            case 'phone_number':
                                result[key] = input('Введите новый телефон клиента: ')
                    print('*' * 86)
                    return id_modify_client, result
                else:
                    print('\033c', end='')
                    match ch:
                        case '1':
                            if search_bar == '':
                                search_bar += '\033[33m  имя\033[0m'
                                result['first_name'] = ''
                            else:
                                if 'first_name' not in result:
                                    search_bar += '\033[33m , имя\033[0m'
                                    result['first_name'] = ''
                        case '2':
                            if search_bar == '':
                                search_bar += '\033[33m  фамилию\033[0m'
                                result['second_name'] = ''
                            else:
                                if 'second_name' not in result:
                                    search_bar += '\033[33m , фамилию\033[0m'
                                    result['second_name'] = ''
                        case '3':
                            if search_bar == '':
                                search_bar += '\033[33m  электронную почту\033[0m'
                                result['email_address'] = ''
                            else:
                                if 'email_address' not in result:
                                    search_bar += '\033[33m , электронную почту\033[0m'
                                    result['email_address'] = ''
                        case '4':
                            if search_bar == '':
                                search_bar += '\033[33m  телефон\033[0m'
                                result['phone_number'] = ''
                            else:
                                if 'phone_number' not in result:
                                    search_bar += '\033[33m , телефон\033[0m'
                                    result['phone_number'] = ''
            else:
                print('\033c', end='')
                print('*' * 86)
                print('\033[31m КЛИЕНТА С ТАКИМ ID НЕТ \033[0m')
                id_modify_client = None
                search_bar = ''
                result = {}
        return id_modify_client, result

    def modifi_client(self, id_modify_client, param_modify):
        """ Функция для изменения информации о клиенте в базе данных.
         Получилось громоздко.... (( """
        str_many_modify = []
        sql_text_for_many_modify = []
        with psycopg2.connect(database=PostgresDb.name_db,
                              user=PostgresDb.user,
                              password=PostgresDb.password,
                              host=PostgresDb.host,
                              port=PostgresDb.port) as conn:
            with conn.cursor() as cur:
                cur.execute('''SELECT client.id_client,
                                      phone_number,
                                      client_phone.id_phone
                                 FROM client JOIN client_phone
                                   ON client.id_client = client_phone.id_client
                                WHERE client.id_client=%s;''', id_modify_client)
                quantity_of_phones = cur.fetchall()
        if param_modify == {}:
            return f'Параметры изменения данных клиента не заданы'
        # Если пораметр для изменения один и телефон у клиента один
        elif len(param_modify) == 1 and len(quantity_of_phones) == 1:
            if f'{list(*param_modify.items())[0]}' in ('first_name', 'second_name', 'email_address'):
                tabe_name = 'client'
            else:
                tabe_name = 'client_phone'
            sql_text_for_modify = f"{list(*param_modify.items())[0]}=%s WHERE {tabe_name}.id_client=%s;"
            with psycopg2.connect(database=PostgresDb.name_db,
                                  user=PostgresDb.user,
                                  password=PostgresDb.password,
                                  host=PostgresDb.host,
                                  port=PostgresDb.port) as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE " + tabe_name + " SET " + sql_text_for_modify, 
                                (list(*param_modify.items())[1], id_modify_client))
        # Если пораметров для изменения много и телефон у клиента один
        elif len(param_modify) > 1 and len(quantity_of_phones) == 1:
            for k, v in list(param_modify.items()):
                sql_text_for_many_modify.append(k)
                str_many_modify.append(v)
            for i in range(len(sql_text_for_many_modify)):
                if sql_text_for_many_modify[i] in ('first_name', 'second_name', 'email_address'):
                    tabe_name = 'client'
                else:
                    tabe_name = 'client_phone'
                with psycopg2.connect(database=PostgresDb.name_db,
                                      user=PostgresDb.user,
                                      password=PostgresDb.password,
                                      host=PostgresDb.host,
                                      port=PostgresDb.port) as conn:
                    with conn.cursor() as cur:
                        cur.execute("UPDATE " + tabe_name + " SET " + sql_text_for_many_modify[i] + 
                                    "=%s WHERE " + tabe_name + ".id_client=%s;", 
                                    (str_many_modify[i], id_modify_client))
        # Если пораметр для изменения один и телефонов у клиента много
        elif len(param_modify) == 1 and len(quantity_of_phones) > 1:
            if f'{list(*param_modify.items())[0]}' in ('first_name', 'second_name', 'email_address'):
                tabe_name = 'client'
            else:
                tabe_name = 'client_phone'
            print(quantity_of_phones)
            id_phone_client = input('Введите ID телефона, которые необходимо изменить: ')
            sql_text_for_modify = f'''{list(*param_modify.items())[0]}=%s WHERE 
                                      {tabe_name}.id_client=%s AND 
                                      {tabe_name}.id_phone=%s;'''
            with psycopg2.connect(database=PostgresDb.name_db,
                                  user=PostgresDb.user,
                                  password=PostgresDb.password,
                                  host=PostgresDb.host,
                                  port=PostgresDb.port) as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE " + tabe_name + " SET " + sql_text_for_modify, 
                                (list(*param_modify.items())[1], id_modify_client, id_phone_client))
        # Если пораметр для изменения много и телефонов у клиента много
        elif len(param_modify) > 1 and len(quantity_of_phones) > 1:
            for k, v in list(param_modify.items()):
                sql_text_for_many_modify.append(k)
                str_many_modify.append(v)
            print(quantity_of_phones)
            id_phone_client = input('Введите ID телефона, которые необходимо изменить: ')
            for i in range(len(sql_text_for_many_modify)):
                if sql_text_for_many_modify[i] in ('first_name', 'second_name', 'email_address'):
                    tabe_name = 'client'
                else:
                    tabe_name = 'client_phone'
                with psycopg2.connect(database=PostgresDb.name_db,
                                      user=PostgresDb.user,
                                      password=PostgresDb.password,
                                      host=PostgresDb.host,
                                      port=PostgresDb.port) as conn:
                    # Пока не получилось одним запросом обновить данные в двух таблицах, пришлось делать
                    # два запроса...
                    with conn.cursor() as cur:
                        if tabe_name == 'client':
                            cur.execute("UPDATE " + tabe_name + " SET " + sql_text_for_many_modify[i] + 
                                        "=%s WHERE " + tabe_name +
                                        ".id_client=%s;",
                                        (str_many_modify[i], id_modify_client))
                        else:
                            cur.execute("UPDATE " + tabe_name + " SET " + sql_text_for_many_modify[i] + 
                                        "=%s WHERE " + tabe_name +
                                        ".id_client=%s AND " + tabe_name + ".id_phone=%s;",
                                        (str_many_modify[i], id_modify_client, id_phone_client))
        with psycopg2.connect(database=PostgresDb.name_db,
                              user=PostgresDb.user,
                              password=PostgresDb.password,
                              host=PostgresDb.host,
                              port=PostgresDb.port) as conn:
            with conn.cursor() as cur:
                cur.execute('''SELECT client.id_client,
                                      first_name,
                                      second_name,
                                      email_address,
                                      phone_number
                                 FROM client JOIN client_phone
                                   ON client.id_client = client_phone.id_client
                                WHERE client.id_client=%s;''', id_modify_client)
                result = cur.fetchall()
        return result
       

# Создаем объект класса
db_pg = PostgresDb()
# Запрос информации по клиентам
pprint.pprint(db_pg.find_client(db_pg.find_info()))
# Модификация информации клиента
# pprint.pprint(db_pg.modifi_client(*db_pg.modify_info()))

# Вывод информации о сервере Postgres
# pprint.pprint(db_pg.postgres_db_info())

# Создание базы данных "clients" на сервере Postgres
# print(db_pg.postgres_db_create())

# Можно удалить созданную базу данных "clients"
# print(db_pg.postgres_db_drop())

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
# db_pg.del_phone_number(id_client=4)

# Поиск данных в базе по подстроке
# pprint.pprint(db_pg.find_client(input('Введите искомые данные: ')))

# Удаление клиента по его ID
# pprint.pprint(del_client(input('Введите ID Клиента, которого необходимо удалить: ')))
