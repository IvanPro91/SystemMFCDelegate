from collections import defaultdict
from datetime import datetime, timedelta, time
from marshmallow import post_dump, fields
from sqlalchemy.dialects.postgresql import JSONB
from ...extensions import database
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, desc, text, and_
from sqlalchemy.orm import joinedload
from flask_login import UserMixin
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID, NUMERIC, SMALLINT, BYTEA, TEXT, DATE, TIMESTAMP, BOOLEAN


# Просмотр настроенных документов
class SpZapros(database.Model):
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных
    __tablename__ = 'sp_zapros'
    __table_args__ = {'schema': 'eldoc'}  # Указываем схему, если она используется

    id = database.Column(database.Integer(), primary_key=True, autoincrement=True)
    id_doc = database.Column(database.Integer, database.ForeignKey('docs.spdoc.id', onupdate='NO ACTION'))
    id_isp = database.Column(database.Integer())
    numdocz = database.Column(database.String())
    ftzapros = database.Column(database.String())
    fz = database.Column(database.String())
    id_alg = database.Column(database.Integer())
    id_elalg = database.Column(database.Integer())
    adr_service = database.Column(database.String())
    srok = database.Column(database.Integer(), default=0)
    smev_func = database.Column(database.String())
    kr_day = database.Column(SMALLINT, default=2)
    smev_mnemonic = database.Column(database.String())
    sirmo = database.Column(database.Integer())
    reestr = database.Column(NUMERIC(1, 0))
    guid = database.Column(UUID)
    folder_out = database.Column(database.String())
    folder_in = database.Column(database.String())
    period_query = database.Column(database.Integer())
    period_query_first = database.Column(database.Integer())
    sign_ext = database.Column(database.String())
    attachment_ext = database.Column(database.String())

    # Дополнительно, если нужно, можно определить отношения
    doc = database.relationship("SpDoc", backref="sp_zaproses", foreign_keys=[id_doc])


# Пример других классов для связи, если их нужно явно определить:
class SpDoc(database.Model):
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных
    __tablename__ = 'spdoc'
    __table_args__ = {'schema': 'docs'}
    id = database.Column(database.Integer(), primary_key=True, autoincrement=True)
    naz = database.Column(database.String())

class Zapros(database.Model):
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных
    __tablename__ = 'zapros'
    __table_args__ = {'schema': 'eldoc'}  # Указываем схему, если она используется

    id = database.Column(database.Integer(), primary_key=True, autoincrement=True)
    id_delo = database.Column(database.Integer(), database.ForeignKey('delo.delo.id', ondelete='SET NULL', onupdate='NO ACTION'))
    id_in = database.Column(database.Integer())
    id_out = database.Column(database.Integer())
    id_spzapros = database.Column(database.Integer, database.ForeignKey('eldoc.sp_zapros.id', ondelete='RESTRICT', onupdate='NO ACTION'))
    query_number = database.Column(database.String())
    stat = database.Column(database.Integer(), default=0, nullable=False)
    primech = database.Column(database.String())
    chk = database.Column(database.Integer(), default=0, nullable=False)
    tn_send = database.Column(database.Integer())
    naz_filein = database.Column(database.String())
    adr_z = database.Column(database.String())
    error_counter = database.Column(database.Integer())
    test = database.Column(BOOLEAN)
    smev3_adr_type = database.Column(database.String())
    id_delo_doc = database.Column(database.Integer(), database.ForeignKey('delo.delo_doc.id', ondelete='SET NULL', onupdate='NO ACTION'))
    test_scenario = database.Column(database.Integer())
    id_adapter = database.Column(database.Integer())
    business_status = database.Column(database.String())
    naz_fileout = database.Column(database.String())
    error_count_receiving = database.Column(database.Integer(), default=0)
    version_namespaces = database.Column(database.Integer())

    # Определение отношений, если необходимо
    delo = database.relationship("Delo", backref="zaproses", foreign_keys=[id_delo])
    sp_zapros = database.relationship("SpZapros", backref="zaproses", foreign_keys=[id_spzapros])
    delo_doc = database.relationship("DeloDoc", backref="zaproses", foreign_keys=[id_delo_doc])


# Пример других классов для связи, если их нужно явно определить:
class Delo(database.Model):
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных
    __tablename__ = 'delo'
    __table_args__ = {'schema': 'delo'}
    id = database.Column(database.Integer, primary_key=True)
    dat = database.Column(DATE)
    cl = database.Column(NUMERIC(1, 0))

class DeloDoc(database.Model):
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных
    __tablename__ = 'delo_doc'
    __table_args__ = {'schema': 'delo'}  # Указываем схему, если она используется

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    id_delo = database.Column(database.Integer, database.ForeignKey('delo.delo.id', ondelete='CASCADE', onupdate='RESTRICT'))
    id_spdoc = database.Column(database.Integer, database.ForeignKey('docs.spdoc.id', ondelete='RESTRICT', onupdate='RESTRICT'))
    idf = database.Column(database.Integer, database.ForeignKey('clients.zakf.idf', ondelete='CASCADE', onupdate='NO ACTION'))
    pres = database.Column(NUMERIC(1, 0), nullable=False, default=0)
    need = database.Column(NUMERIC(1, 0))
    doc_from = database.Column(SMALLINT)
    kol_doc_podl = database.Column(SMALLINT)
    kol_doc_cop = database.Column(SMALLINT)
    list_podl = database.Column(SMALLINT)
    list_cop = database.Column(SMALLINT)
    idy = database.Column(database.Integer, database.ForeignKey('clients.zaky.idy', ondelete='RESTRICT', onupdate='NO ACTION'))
    tn = database.Column(database.Integer)
    iscopy = database.Column(SMALLINT)
    primech = database.Column(TEXT)
    datv = database.Column(DATE)
    daysposob = database.Column(database.Integer)
    srok = database.Column(database.Integer)
    avt = database.Column(NUMERIC(1, 0), nullable=False, default=0)
    opisprn = database.Column(NUMERIC(1, 0), nullable=False, default=1)
    is_vid = database.Column(NUMERIC(1, 0))
    elobrdoc_val = database.Column(database.Integer)

    # Определение отношений, если необходимо
    delo = database.relationship("Delo", backref="delo_docs", foreign_keys=[id_delo])
    spdoc = database.relationship("SpDoc", backref="delo_docs", foreign_keys=[id_spdoc])
    zakf = database.relationship("Zakf", backref="delo_docs", foreign_keys=[idf])
    zaky = database.relationship("Zaky", backref="delo_docs", foreign_keys=[idy])


class Zakf(database.Model):
    __tablename__ = 'zakf'
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных
    __table_args__ = {'schema': 'clients'}  # Указываем схему, если она используется

    idf = database.Column(database.Integer, primary_key=True, autoincrement=True)
    fam = database.Column(TEXT, nullable=False, default='')
    nam = database.Column(TEXT, nullable=False, default='')
    otch = database.Column(TEXT, nullable=False, default='')
    pol = database.Column(database.CHAR(1), nullable=False, default='')
    dr = database.Column(DATE)
    cnils = database.Column(database.CHAR(14), nullable=False, default='')
    inn = database.Column(database.CHAR(12), nullable=False, default='')
    tel = database.Column(TEXT, nullable=False, default='')
    email = database.Column(TEXT, nullable=False, default='')
    adr = database.Column(TEXT, nullable=False, default='')
    codenp = database.Column(database.CHAR(11), default='')
    kul = database.Column(SMALLINT, nullable=False, default=0)
    nd = database.Column(TEXT, nullable=False, default='')
    nk = database.Column(TEXT, nullable=False, default='')
    telmob = database.Column(TEXT)
    p_num = database.Column(TEXT)
    dvidp = database.Column(DATE)
    kem = database.Column(TEXT)
    kpodr = database.Column(database.CHAR(10))
    passw = database.Column(database.CHAR(10))
    ogrip = database.Column(database.CHAR(15))
    raigor = database.Column(database.Integer)
    p_ser = database.Column(TEXT)
    docum = database.Column(database.Integer, nullable=False, default=8)
    isself = database.Column(NUMERIC(1, 0), nullable=False, default=0)
    famrod = database.Column(TEXT)
    namrod = database.Column(TEXT)
    otchrod = database.Column(TEXT)
    fadr = database.Column(TEXT)
    fcodenp = database.Column(database.CHAR(11))
    fkul = database.Column(SMALLINT)
    fnd = database.Column(TEXT)
    fnk = database.Column(TEXT)
    fraigor = database.Column(database.Integer)
    active = database.Column(NUMERIC(1, 0), default=1)
    is_sms = database.Column(NUMERIC(1, 0), default=1)
    is_email = database.Column(NUMERIC(1, 0), default=1)
    uuid = database.Column(UUID, default=database.text('uuid_generate_v4()'))
    family = database.Column(database.Integer)
    citizenship = database.Column(database.Integer, default=643)
    birth_place = database.Column(TEXT)
    p_code = database.Column(TEXT)
    ocenka = database.Column(database.Integer)
    birth_place_data = database.Column(TEXT)
    esia_oid = database.Column(TEXT)
    regtype = database.Column(database.Integer, default=1)
    tnch = database.Column(database.Integer)
    is_msp = database.Column(database.Integer)
    anonim = database.Column(database.Integer)
    email_subscription = database.Column(NUMERIC(1, 0))
    primech = database.Column(TEXT)
    birth_place_pfr = database.Column(TEXT)
    birth_place_data_pfr = database.Column(TEXT)
    born_act_num = database.Column(TEXT)
    born_act_date = database.Column(DATE)
    rai_ua = database.Column(SMALLINT, nullable=False, default=0)
    date_reg = database.Column(DATE)
    date_tb_reg = database.Column(DATE)
    date_te_reg = database.Column(DATE)
    drspecial = database.Column(TEXT)
    born_act_kem = database.Column(TEXT)
    business_data = database.Column(TEXT)
    fs_id_agreement = database.Column(TEXT)
    dt_agreement = database.Column(TIMESTAMP)
    tn_create = database.Column(database.Integer)
    fs_id_digital_signature = database.Column(TEXT)
    created = database.Column(TIMESTAMP)
    updated = database.Column(TIMESTAMP)
    npd_date = database.Column(DATE)
    dul_valid = database.Column(DATE)
    is_auto_kvit_fns = database.Column(database.Integer, nullable=False, default=1)


class QueueStat(database.Model):
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных
    __tablename__ = 'stat'
    __table_args__ = {'schema': 'queue'}  # Указываем схему, если она используется

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    fio = database.Column(TEXT)
    tn = database.Column(database.Integer)
    idf = database.Column(database.Integer, database.ForeignKey('clients.zakf.idf', ondelete='CASCADE', onupdate='NO ACTION'))
    idy = database.Column(database.Integer, database.ForeignKey('clients.zaky.idf', ondelete='CASCADE', onupdate='NO ACTION'))
    dat_p = database.Column(DATE)
    dat_v = database.Column(DATE)
    dat_e = database.Column(DATE)
    updated_at = database.Column(DATE)
    timzapis = database.Column(DATE)
    id_delo = database.Column(database.Integer)

class Zaky(database.Model):
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных
    __tablename__ = 'zaky'
    __table_args__ = {'schema': 'clients'}  # Указываем схему, если она используется

    idy = database.Column(database.Integer, primary_key=True, autoincrement=True)
    naz = database.Column(database.CHAR(200), nullable=False)
    opf = database.Column(database.Integer)
    inn = database.Column(database.CHAR(12))
    kpp = database.Column(database.CHAR(9))
    ogrn = database.Column(database.CHAR(15))
    tel = database.Column(TEXT, default='')
    email = database.Column(TEXT)
    adr = database.Column(TEXT)
    naz_full = database.Column(TEXT)
    codenp = database.Column(database.CHAR(11))
    kul = database.Column(SMALLINT)
    nd = database.Column(TEXT)
    nk = database.Column(TEXT)
    raigor = database.Column(database.Integer)
    active = database.Column(NUMERIC(1, 0), default=1)
    is_sms = database.Column(NUMERIC(1, 0), nullable=False, default=1)
    is_email = database.Column(NUMERIC(1, 0), nullable=False, default=1)
    telmob = database.Column(TEXT)
    reg_doc = database.Column(database.Integer)
    reg_ser = database.Column(TEXT)
    reg_num = database.Column(TEXT)
    reg_dat = database.Column(DATE)
    reg_isp = database.Column(TEXT)
    reg_dat_vid = database.Column(DATE)
    reg_isp_vid = database.Column(TEXT)
    tip = database.Column(database.Integer, default=1)
    tip_sub = database.Column(TEXT)
    country = database.Column(TEXT)
    fadr = database.Column(TEXT)
    fcodenp = database.Column(database.CHAR(11))
    fkul = database.Column(SMALLINT)
    fnd = database.Column(TEXT)
    fnk = database.Column(TEXT)
    fraigor = database.Column(database.Integer)
    kio = database.Column(TEXT)
    nazr = database.Column(TEXT)
    is_msp = database.Column(database.Integer)
    email_subscription = database.Column(NUMERIC(1, 0))
    primech = database.Column(TEXT)
    reg_number = database.Column(TEXT)
    business_data = database.Column(TEXT)
    tn_create = database.Column(database.Integer)


class Userst(database.Model):
    __tablename__ = 'userst'
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных

    fio = database.Column(database.CHAR(50), nullable=False, default='')
    id_passw = database.Column(database.CHAR(10), nullable=False, default='')
    gr = database.Column(database.Integer, nullable=False, default=0)
    tn = database.Column(database.Integer, primary_key=True, nullable=False)
    ima = database.Column(database.CHAR(50), default='')
    validbefore = database.Column(database.Date)
    cnils = database.Column(TEXT)
    tel = database.Column(TEXT)
    job = database.Column(TEXT)
    id_isp = database.Column(database.Integer, default=1)
    password = database.Column(BYTEA)
    fio_rl = database.Column(TEXT)
    status_ch = database.Column(database.TIMESTAMP)
    date_ch_pass = database.Column(database.Date, nullable=False, default='2000-01-01')
    elplat_id = database.Column(TEXT)
    login = database.Column(TEXT)
    laravel_password = database.Column(TEXT)
    tn_out = database.Column(TEXT)
    outer_system_id = database.Column(TEXT)
    operator_oid = database.Column(TEXT)
    type_rab = database.Column(database.Integer)


class Usersgr(database.Model):
    __tablename__ = 'usersgr'
    __bind_key__ = 'mfc'  # Указываем, что эта модель связана с другой базой данных

    gr = database.Column(database.Integer, primary_key=True, nullable=False)
    ngr = database.Column(database.VARCHAR(50), nullable=False)
    fullque = database.Column(database.SmallInteger)

