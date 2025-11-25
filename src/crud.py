
import datetime
from database import Base, engine, get_session
from data_filler import make_data, make_documents
from models import Data, Documents

from logger import get_logger

logger = get_logger(__name__)


# сначала удаляем старое значение потом переприсваиваем, что бы не добавлялись значения подряд
def create_table():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)



data = make_data()
data_tbl = list(data.values())
documents_tbl = make_documents(data)


def insert():
    with get_session() as session:

        insert_data = [Data(**i) for i in data_tbl]
        session.add_all(insert_data)

        insert_doc = [Documents(**i) for i in documents_tbl]
        session.add_all(insert_doc)
        session.commit()

        logger.info(f"Вставлено {len(insert_data)} данных и {len(insert_doc)} документов")




from sqlalchemy import select, and_, update, Index


def create_indexes():
    """Создание индексов для ускорения запросов"""

    # Комбинированный индекс для Documents (processed_at + document_type)
    Index(
        'idx_documents_processed_type',
        Documents.processed_at,
        Documents.document_type
    ).create(bind=engine)

    # Хэш-индекс для Data.parent (PostgreSQL поддерживает HASH)
    Index(
        'idx_data_parent_hash',
        Data.parent,
        postgresql_using='hash'
    ).create(bind=engine)

    # Комбинированный индекс для Data.owner + Data.status
    Index(
        'idx_data_owner_status',
        Data.owner,
        Data.status
    ).create(bind=engine)
    logger.info('Индексация полей завершина')


def select_one_doc(session):
    stmt = select(Documents.doc_id, Documents.document_data).where(
                and_(
                    Documents.processed_at == None,
                    Documents.document_type == 'transfer_document'
                )
            ).order_by(Documents.recieved_at.asc()).limit(1)

    row = session.execute(stmt).first()

    if row:
        logger.info(f'Выбран документ с id = {row[0][0]}')
    else:
        logger.info('Нет необработаных документов')

    return row


def parsing_data(row: tuple):
    """Разбираем картеж на doc_id, json, разбирам json на objects, operation_details"""
    doc_id, jsonb = row
    obj = jsonb['objects']
    operation_details = jsonb['operation_details']

    logger.debug(f'Документ {doc_id}, распарсен на {len(obj)} обьектов и {len(operation_details)} операций')

    return doc_id, obj, operation_details



def search_all_child(session, parent: list):
    """Поиск дочерних объектов"""

    stmt = select(Data.object).where(Data.parent.in_(parent))

    child = session.execute(stmt).scalars().all()

    parent_child = list(child)
    parent_child.extend(parent)

    logger.debug(f'Найдено {len(child)} дочерних  для родительских {parent}')
    return parent_child


def correct_data(session, all_parand_child: list, operation_details: dict[str, dict]):
    """Изменения старых значений на новые"""
    if operation_details:

        for operation, details in operation_details.items():
            new = details['new']
            old = details['old']

            collum = getattr(Data, operation)

            stmt = (update(Data).where(collum == old, Data.object.in_(all_parand_child)).values({operation: new}))

            session.execute(stmt)
            logger.info(f'Обнавлен поле {operation} с {old} на {new} для {len(all_parand_child)} обьектов')



def set_processing_time(session, doc_id: str):
    """Установка даты и времени для обработаных документов"""



    document = session.get(Documents, doc_id)
    document.processed_at = datetime.datetime.now()
    logger.info(f'Документ {doc_id} отмечен как обработанный')



def process_single_document(session):
    """Обработка одного документа"""

    logger.info('Начинает обработку одного документа')    

    row = select_one_doc(session)
    if not row:
        logger.info('Документов для обрабоатки нет')
        return None

    doc_id, object, operation_details = parsing_data(row)
    all_parand_child = search_all_child(session, object)

    correct_data(session, all_parand_child, operation_details)
    set_processing_time(session, doc_id)
    
    logger.info(f'Обработка докумнта {doc_id} завершина')

    return row




