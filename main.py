
from tz_sql.tz_alchemy.crud import create_table, insert, process_single_document

from tz_sql.tz_alchemy.database import get_session

create_table()
insert()

def main():
    try:
        with get_session() as session:
            while True:
                row = process_single_document(session)

                if not row:
                    break

                session.commit()
        return True
    except Exception as e:
        return False


if __name__ == '__main':

    print(main())