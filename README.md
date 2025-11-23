Тестовое задание: обработка документов в PostgreSQL

Подготовка

1. Запустить скрипт data_filler.py для генерации тестовых данных.


2. Данные будут перенесены в базу через create_table.py.




---

Легенда

Таблица documents содержит условные документы, поступающие от клиентов.

Таблица data содержит объекты, которые могут встречаться в документах.

Связь между объектами осуществляется через поле parent:

Объект с заполненным parent считается дочерними.

Объект без parent считается материнским.




---

Создание таблиц в PostgreSQL

CREATE TABLE IF NOT EXISTS public.data

(

    object character varying(50) NOT NULL,
    
    status integer,
    
    level integer,
    
    parent character varying,
    
    owner character varying(14),
    
    CONSTRAINT data_pkey PRIMARY KEY (object)
    
);

CREATE TABLE IF NOT EXISTS public.documents

(

    doc_id character varying NOT NULL,
    
    recieved_at timestamp without time zone,
    
    document_type character varying,
    
    document_data jsonb,
    
    processed_at timestamp without time zone,
    
    CONSTRAINT documents_pkey PRIMARY KEY (doc_id)
    
);


---

Тестовое задание

Написать алгоритм обработки документов из таблицы documents по следующим условиям:

1. Выбрать один необработанный документ (processed_at IS NULL) с типом transfer_document, сортировка по recieved_at ASC.


2. Разобрать JSON документа:

Ключ objects — список материнских объектов в таблице data.

Ключ operation_details — операции изменения данных в таблице data.



3. Получить полный список объектов, учитывая дочерние элементы (связь по полю parent).


4. Обновить данные в таблице data, если значения соответствуют условиям operation_details:


"owner": {

    "new": "owner_4",
    
    "old": "owner_3"
    
}

5. После успешной обработки документа поставить отметку времени в processed_at.


6. Функция возвращает True, если обработка прошла успешно, иначе False.



Пример структуры JSON документа:

{

    "document_data": {
    
        "document_id": "25e91d56-696e-4be6-952c-4089593877a7",
        
        "document_type": "transfer_document"
        
    },
    
    "objects": [
    
        "p_effe6195-cc7f-44c2-a02c-46fc07dcd3e6",
        
        "p_8943e9fb-a2e7-4344-8c48-91d3a4fbdb0c"
        
    ],
    
    "operation_details": {
    
        "owner": {
        
            "new": "owner_4",
            
            "old": "owner_3"
            
        }
        
    }
    
}


---

Стек технологий

Python 3.12+

PostgreSQL

psycopg2 / psycopg2-binary

python-dotenv



---

Установка

pip install -r requirements.txt

.env файл

DB_HOST=localhost

DB_PORT=5432

DB_USER=your_username

DB_PASSWORD=your_password


---

Запуск

Перейти в папку test_task

1. Создание базы данных, запустить файл creat_base.py:

creat_base('postgres', 'test')

2. Создание таблиц и заполнение тестовыми данными, запустить файл create_insert_table.py:

create_table(new_base)

3. Обработка документов, запустить файл main:

main(new_base)

---


Особенности

Использовался комбинированый подход к решение. ООП + функуиональный подход.

Был создан класс для избежания дублирования, безапасного соединения и более удобного взоимодейсвтия с postgresSQL, происходит автоматический comit при выходе из контекстного мнеджера или rollback при исключение, файл Object_connect_base.py.

Основная логика разделена на функции, каждая выпоняющая только одну задачу, файл dal.py.

Индексация ключевых полей для ускорения запросов и избежания полного сканирования таблиц.

Обработака исключений блоком try except.

Генерация случайных данных для тестирования логики, файл data_filter.py.
