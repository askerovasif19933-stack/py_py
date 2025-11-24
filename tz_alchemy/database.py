from sqlalchemy.orm import sessionmaker , DeclarativeBase
from sqlalchemy import create_engine
from config import host, password, user
from basse_tz import new_base



# движок для подключения
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{new_base}")
print(engine)

# базовый класс от которого наследуемся
class Base(DeclarativeBase):
    pass


# создаем фабрику сессий
get_session = sessionmaker(engine)






