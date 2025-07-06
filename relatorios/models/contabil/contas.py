from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CtContas(Base):
    __tablename__ = "ctcontas"
    __table_args__ = {"schema": "bethadba"}

    codi_emp = Column()
    codi_cta = Column(Integer, primary_key=True)
    nome_cta = Column(String)
    clas_cta = Column(String)
    tipo_cta = Column(String)
    data_cta = Column(Date)
    situacao_cta = Column(String)
    data_cta = Column(Date)
