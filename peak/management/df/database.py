import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.reflection import Inspector

import config


engine = sqlalchemy.create_engine(config.database_url, echo=config.debug)
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Agent(Base):
    __tablename__ = 'agent'

    jid = sqlalchemy.Column(sqlalchemy.String(255), primary_key=True)
    mas = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)
    player_type = sqlalchemy.Column(sqlalchemy.String(10000), nullable=False)

    def __repr__(self):
        return f'<Agent {self.jid}>'

    @classmethod
    def find_all(cls):
        return session.query(cls).all() 

    @classmethod
    def find(cls, jid: str):
        return session.query(cls).filter_by(jid=jid).first()

    @classmethod
    def find_by_mas(cls, mas: str):
        return session.query(cls).filter_by(mas=mas).all()

    @classmethod
    def add(cls, jid: str, mas: str, player_type: str):
        entity = cls.find(jid)
        if not entity:
            entity = cls(jid=jid, mas=mas, player_type=player_type)
            session.add(entity)
        else:
            entity.player_type = player_type
            entity.mas = mas
        session.commit()

if sqlalchemy.inspect(engine).has_table(table_name=Agent.__table__):
    Agent.__table__.drop(engine)

Base.metadata.create_all(engine)