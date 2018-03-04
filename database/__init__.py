import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from config import DATABASE_FILE

# get the absolute path of current directory
dir_path = os.path.dirname(os.path.realpath(__file__))
DATABASE_ADDRESS = "sqlite:///{}/{}".format(dir_path, DATABASE_FILE)

# reference: http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/

engine = create_engine(DATABASE_ADDRESS, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# for quick setup, this should be run to initialize the database for the first time
def init_db():
    # noinspection PyUnresolvedReferences
    import model.graph
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
