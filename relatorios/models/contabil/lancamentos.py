from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CtLancto(Base):
    __tablename__ = "ctlancto"
    __table_args__ = {"schema": "bethadba"}

    codi_emp = Column(Integer, primary_key=True, comment="Código da empresa")
    nume_lan = Column(Integer, primary_key=True)
    codi_his = Column(Integer)
    chis_lan = Column(String)
    orig_lan = Column(Integer)
    codi_lote = Column(Integer)
    fili_lan = Column(Integer)
    origem_reg = Column(Integer)
    cdeb_lan = Column(
        Integer,
        ForeignKey("bethadba.ctcontas.codi_cta"),
        comment="Código da conta de débito",
    )
    ccre_lan = Column(
        Integer,
        ForeignKey("bethadba.ctcontas.codi_cta"),
        comment="Código da conta de crédito",
    )
    vlor_lan = Column(Numeric(15, 2), comment="Valor do lançamento")
    data_lan = Column(Date, comment="Data do lançamento")
