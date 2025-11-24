
from crud import create_table, insert, process_single_document

from database import get_session
from sqlalchemy import select
from models import Data, Documents



def main():
    try:
        with get_session() as session:
            old = select(Data.status, Data.owner)
            old_ex = session.execute(old).all()


            while True:
                row = process_single_document(session)

                if not row:
                    break

                session.commit()
            new = select(Data.status, Data.owner)
            new_ex = session.execute(new).all()


            for k,v in zip(old_ex, new_ex):
                print(k== v)

        return True
    except Exception as e:
        return False


create_table()
insert()
print(main())