from collections import defaultdict
from datetime import datetime, timedelta, time
from marshmallow import post_dump, fields
from sqlalchemy.dialects.postgresql import JSONB
from ...extensions import database, marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, desc, text, and_
from sqlalchemy.orm import joinedload
from flask_login import UserMixin
from sqlalchemy import event



class Regions(database.Model):
    '''
    Регионы МФЦ которые есть в шаблоне
    '''
    __tablename__ = "regions"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
    update_on = database.Column(database.DateTime(), comment="Дата обновления МФЦ")
    name_region = database.Column(database.String(), comment="Названия региона МФЦ")
    ip_ais = database.Column(database.String(), comment="IP сервера ИИС")
    ip_smev3 = database.Column(database.String(), comment="IP сервера ЭДО")
    ip_doctransformer = database.Column(database.String(), comment="IP ДОКТРАНСФОРМЕР")
    ip_signer2 = database.Column(database.String(), comment="IP СИГНЕР2")
    ip_edo = database.Column(database.String(), comment="IP сервера ЭДО")
    ip_site = database.Column(database.String(), comment="IP Сайт")

    portal_login = database.Column(database.String(), comment="портал логин")
    portal_password = database.Column(database.String(), comment="портал пароль")

    vipnet_login = database.Column(database.String(), comment="vipnet логин")
    vipnet_password = database.Column(database.String(), comment="vipnet пароль")

    active_portal = database.Column(database.Boolean(), comment="Включить парсинг портала", default=False)
    active_edit_photo = database.Column(database.Boolean(), comment="Включить обработка фото", default=False)
    active_inventory = database.Column(database.Boolean(), comment="Включить инвентаризацию", default=False)
    active_download_updates = database.Column(database.Boolean(), comment="Включить скачивание обновлений", default=False)
    active_vipnet = database.Column(database.Boolean(), comment="Включить получение статусов vipnet", default=False)
    active_view_camera = database.Column(database.Boolean(), comment="Включить отображение камер", default=False)

    @classmethod
    def addRegion(self, name_region):
        new_region = Regions.query.filter(Regions.name_region == name_region).first()
        if not new_region:
            addRegion = Regions(name_region=name_region, update_on=datetime.now())
            database.session.add(addRegion)
            database.session.commit()
            database.session.flush()

            addAdmin = Users(id_region=addRegion.id, user_login="Администратор", id_role=1)
            database.session.add(addAdmin)
            database.session.commit()
            database.session.flush()
            addAdmin.set_password("admin")
            return True
        return False

class RoleUserMFC(database.Model):
    __tablename__ = "role_user_mfc"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
    name_role = database.Column(database.String(), comment="Роли МФЦ")

    @classmethod
    def addRoleUserMFC(self, name_role):
        new_role = RoleUserMFC.query.filter(RoleUserMFC.name_role == name_role).first()
        if not new_role:
            new_role = RoleUserMFC(name_role=name_role)
            database.session.add(new_role)
            database.session.commit()
            return True
        return False
class Users(database.Model, UserMixin):
    '''
    Сотрудники МФЦ
    '''
    __tablename__ = "users"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
    id_region = database.Column(database.Integer(), database.ForeignKey("regions.id"), comment="ОИВ")
    id_role = database.Column(database.Integer(), database.ForeignKey("role_user_mfc.id"), comment="Роль")

    tn = database.Column(database.Integer(), comment="Номер пользователя в ИИС")
    job = database.Column(database.String(), comment="Название должности")

    user_login = database.Column(database.String(), comment="Названия региона МФЦ")
    user_password = database.Column(database.String(), comment="Названия региона МФЦ")

    role = database.relationship(RoleUserMFC, primaryjoin="and_(RoleUserMFC.id == Users.id_role)")
    region = database.relationship(Regions, primaryjoin="and_(Regions.id == Users.id_region)")

    def set_password(self, password):
        self.user_password = generate_password_hash(password)
        database.session.commit()

    def check_password(self, password):
        return check_password_hash(self.user_password, password)


# Нам нужны справочники для шаблонов
class ListOIV(database.Model):
    '''
    Органы исполнительной власти
    '''
    __tablename__ = 'list_oiv'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_oiv = database.Column(database.String(), comment="Название ОИВ")

# Настройка списка камер для отображения данных на основном экране
class ListCameraMFC(database.Model):
    '''
    Камеры МФЦ
    '''
    __tablename__ = 'list_camera_mfc'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    id_region = database.Column(database.Integer(), database.ForeignKey("regions.id"), comment="Регион")
    name_camera_mfc = database.Column(database.String(), comment="Название Камеры")
    url_camera_mfc = database.Column(database.String(), comment="URL Камеры")


class TypeMFC(database.Model):
    '''
    Тип МФЦ - есть 2-ва типа (МФЦ или ТОСП)
    '''
    __tablename__ = 'type_mfc'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    type_name_mfc = database.Column(database.String(), comment="МФЦ, ТОСП")


class ProfileMFC(database.Model):
    '''
    Профиль МФЦ указывается в шаблоне (Универсальный, для бизнеса и т.п.)
    '''
    __tablename__ = 'profile_mfc'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    profile_name_mfc = database.Column(database.String(), comment="Для бизнеса, Универсальный и т.п.")


class TypesTemplate(database.Model):
    '''
    Тип шаблона Федеральные, Окна, Муниципальные, Региональные и т.п.
    '''
    __tablename__ = "types_template"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_type = database.Column(database.String(), comment="Типы шаблонов (Федеральные, Окна, Муницип...)")


class UslugiTemplate(database.Model):
    '''
    Справочник услуг из шаблона
    '''
    __tablename__ = 'uslugi_template'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    update_on = database.Column(database.DateTime(), comment="Дата обновления услуги")
    name_uslugi = database.Column(database.String(), comment="Название услуги")
    organ_vlasti = database.Column(database.Integer(), database.ForeignKey("list_oiv.id"), comment="ОИВ")
    file_template = database.Column(database.String(), comment="Название файла в котором нашли услугу")
    new_usluga = database.Column(database.Boolean(), comment="Отметка, новая ли услуга")


class ListMFC(database.Model):
    '''
    Список Добавленных с шаблона МФЦ/ТОСП
    '''
    __tablename__ = "list_mfc"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
    update_on = database.Column(database.DateTime(), comment="Дата обновления МФЦ")
    num_aismrs = database.Column(database.String(), comment="Номер в АИС МРС")
    address = database.Column(database.String(), comment="Адрес")
    id_profile_mfc = database.Column(database.Integer(), database.ForeignKey("profile_mfc.id"))
    id_type_mfc = database.Column(database.Integer(), database.ForeignKey("type_mfc.id"))
    region_mfc = database.Column(database.Integer(), database.ForeignKey("regions.id"), comment="Регион МФЦ")
    new_mfc = database.Column(database.Boolean(), comment="Добавлен новый МФЦ/ТОСП")


class FilesTemplates(database.Model):
    '''
    Файлы шаблонов АИС МРС
    '''
    __tablename__ = 'files_templates'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    update_on = database.Column(database.DateTime(), comment="Дата загрузки файла")
    type_template = database.Column(database.Integer(), database.ForeignKey("types_template.id"), comment="Тип шаблона")
    filename = database.Column(database.String(), comment="Название файла шаблона")


# *********************** Справочник названий модулей и обновлений *********************************
class KomeksUpdatesNames(database.Model):
    __tablename__ = 'komeks_updates_names'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_orig = database.Column(database.String(), comment="Названия на странице обновлений")
    name_update = database.Column(database.String(), comment="Названия как в модуле")

    @classmethod
    def addKomeksUpdatesNames(self, names):
        for key, values in names.items():
            new_KomeksUpdates = KomeksUpdatesNames.query.filter(KomeksUpdatesNames.name_orig == key,
                                                                KomeksUpdatesNames.name_update == values).first()
            if not new_KomeksUpdates:
                new_KomeksUpdates = KomeksUpdatesNames(name_orig=key, name_update=values)
                database.session.add(new_KomeksUpdates)
                database.session.commit()
        return True


class KomeksUpdateFiles(database.Model):
    __tablename__ = 'komeks_update_files'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    update_on = database.Column(database.DateTime(), comment="Дата загрузки файла")
    win_types = database.Column(database.String(), comment="Тип платформы")
    id_komeks_updates_names = database.Column(database.Integer(), database.ForeignKey("komeks_updates_names.id"))
    href_download = database.Column(database.String(), comment="ссылка для локального скачивание")
    version = database.Column(database.String(), comment="Версия обновления")

# *********************** Настройки парсинга портала МФЦ *********************************
class PortalSettings(database.Model):
    '''
    Сохранение настроек портала МФЦ
    '''
    __tablename__ = 'portal_settings'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    region_mfc = database.Column(database.Integer(), database.ForeignKey("regions.id"), comment="Регион МФЦ")
    login_portal = database.Column(database.String(), comment="Логин руководителя портала")
    password_portal = database.Column(database.String(), comment="Пароль руководителя портала")
    async_seconds = database.Column(database.String(), comment="Время опроса поручений", default=360)
    region = database.relationship(Regions, backref="portal_settings", viewonly=True)

class PortalImages(database.Model):
    '''
    Сохранение ссылок на файлы
    '''
    __tablename__ = 'portal_images'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    id_portal_orders = database.Column(database.Integer(), database.ForeignKey("portal_orders.id"))
    filename = database.Column(database.String(), comment="Имя файла картинки что в основном тексте")

class DelegateOrderUser(database.Model):
    __tablename__ = "delegate_order_user"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
    id_order = database.Column(database.Integer(), database.ForeignKey("portal_orders.id"))
    id_user = database.Column(database.Integer(), database.ForeignKey("users.id"))
    id_region = database.Column(database.Integer(), database.ForeignKey("regions.id"))
    notify = database.Column(database.Boolean(), default=False)
    status = database.Column(database.Boolean(), default=False)

    user = database.relationship(Users, primaryjoin="and_(DelegateOrderUser.id_user == Users.id)")

class PortalOrders(database.Model):
    '''
    Сохранение настроек портала МФЦ
    '''
    __tablename__ = 'portal_orders'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    region_mfc = database.Column(database.Integer(), database.ForeignKey("regions.id"), comment="Регион МФЦ")
    id_order = database.Column(database.Integer(), comment="Номер поручения")
    date_in = database.Column(database.DateTime(), comment="Дата начала")
    date_out = database.Column(database.DateTime(), comment="Дата окончания")
    surname = database.Column(database.String(), comment="Фамилия координатора")
    names = database.Column(database.String(), comment="Имя координатора")
    occupation = database.Column(database.String(), comment="Должность координатора")
    email = database.Column(database.String(), comment="email координатора")
    cellphone = database.Column(database.String(), comment="телефон координатора")
    theme_order = database.Column(database.String(), comment="Тема поручения")
    mfc_section_body = database.Column(database.String(), comment="Тело поручения координатора")
    file_zip = database.Column(database.String(), comment="Ссылка на архив")
    images = database.relationship(PortalImages, backref="orders", viewonly=True)
    delegate_order = database.relationship(DelegateOrderUser, backref="orders", viewonly=True)
    new_order = database.Column(database.Boolean(), comment="Статус поручения", default=False)





# Сначала забираем все данные с шаблонов(так что бы было автозаполнения по новым данным + обновлялась дата обновленных)

'''
class RoleUserMFC(database.Model):
    __tablename__ = "role_user_mfc"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
    name_role = database.Column(database.String(), comment="Роли МФЦ")


# Модель пользователей
class Users(UserMixin, database.Model):
    __tablename__ = 'users'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
    created_on = database.Column(database.DateTime(), comment="Дата создания пользователя")
    user_surname = database.Column(database.String(), comment="Фамилия")
    user_name = database.Column(database.String(), comment="Имя")
    user_patronymic = database.Column(database.String(), comment="Отчество")
    id_mfc = database.Column(database.Integer(), database.ForeignKey("list_mfc.id"))
    id_role_mfc = database.Column(database.Integer(), database.ForeignKey("role_user_mfc.id"))
    telegram_id = database.Column(database.String(), comment="Идентификатор Телеграмм")
    user_password = database.Column(database.String(), comment="Пароль пользователя(в случае невозможности зайти в телеграмм)")
    user_photo = database.Column(database.String(), comment="Ссылка на фото")
    telegram_bot_id = database.Column(database.String(), comment="ID Телеграмм (для связи с ботом)")
    access_blocked = database.Column(database.Boolean(), comment="Блокировка доступа")
    user_supervisor = database.Column(database.Boolean(), comment="Руководитель")
    user_administrator = database.Column(database.Boolean(), comment="Администратор (создается единожды и не меняется)")

    role = database.relationship(RoleUserMFC, primaryjoin="and_(RoleUserMFC.id == Users.id_role_mfc)")
    def set_password(self, password):
        self.user_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.user_password, password)

    def __repr__(self):
        return f'<User{self.user_surname} {self.user_name} {self.user_patronymic}>'

#************************* Справочники **************************

class Rooms(database.Model):
    __tablename__ = "rooms"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_room = database.Column(database.String(), comment="Название помещения")

class Devices(database.Model):
    __tablename__ = "devices_mfc"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_device = database.Column(database.String(), comment="Название устройства")

class Options(database.Model):
    __tablename__ = "options"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_options = database.Column(database.String(), comment="Название опции, например Windows, Роутер и т.д.")

class Measure(database.Model):
    __tablename__ = "measure"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_measure = database.Column(database.String(), comment="Название ед. измерения")

#************************* /Справочники **************************

# Заполняем каждой группе свои параметры на заполнение
class DevicesOptions(database.Model):
    __tablename__ = "device_options"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    id_device = database.Column(database.Integer(), database.ForeignKey("devices_mfc.id"))
    id_options = database.Column(database.Integer(), database.ForeignKey("options.id"))
    id_measure = database.Column(database.Integer(), database.ForeignKey("measure.id"))

# Все МФЦ и ТОСПы указываются в одной таблице и тут же указывается child МФЦ/ТОСП

class UsersMFC(database.Model):
    __tablename__ = "users_mfc"
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
    update_on = database.Column(database.DateTime(), comment="Дата добавления")
    id_mfc = database.Column(database.Integer(), database.ForeignKey("list_mfc.id"))
    id_user = database.Column(database.Integer(), database.ForeignKey("users.id"))
    id_role = database.Column(database.Integer(), database.ForeignKey("role_user_mfc.id"))
    username = database.Column(database.String(), comment="ФИО пользователя")
    director = database.Column(database.Boolean(), comment="Руководитель или пользователя", default=False)

class FilesUpdates(database.Model):
    __tablename__ = 'files_updates'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    update_on = database.Column(database.DateTime(), comment="Дата загрузки файла")
    type_file = database.Column(database.Integer(), database.ForeignKey("types_updates_file.id"), comment="Тип файла обновления")
    filename = database.Column(database.String(), comment="Название файла обновления")
    download = database.Column(database.Integer(), comment="Количество скачиваний")
    like = database.Column(database.Integer(), comment="Количество понравившихся")
    dislike = database.Column(database.Integer(), comment="Количество не понравившихся")
    comment = database.Column(database.String(), comment="Комментарий к неисправности")



class UslugiMFC(database.Model):
    __tablename__ = 'uslugi_mfc'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    id_uslugi_mfc = database.Column(database.Integer(), comment="Номер услуги в БД ИИС")
    name_uslugi_mfc = database.Column(database.String(), comment="Название услуги в БД ИИС")
    id_mfc = database.Column(database.Integer(), database.ForeignKey("list_mfc.id"))
    id_uslugi_template = database.Column(database.Integer(), database.ForeignKey("uslugi_template.id"))

class AssignmentFiles(database.Model):
    __tablename__ = 'assignment_files'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    filename = database.Column(database.String(), comment="Название файла в поручении")

class UserControlUMFC(database.Model):
    __tablename__ = 'user_control_umfc'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_assignment = database.Column(database.String(), comment="ФИО ответственного УМФЦ")

class Assignment(database.Model):
    __tablename__ = 'assignment'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_assign = database.Column(database.String(), comment="Название поручения")
    text_assign = database.Column(database.String(), comment="Текст поручения")
    user_umfc_control = database.Column(database.Integer(), database.ForeignKey("user_control_umfc.id"))
    files = database.Column(database.Integer(), database.ForeignKey("assignment_files.id"))

class UserControlMFC(database.Model):
    __tablename__ = 'user_control_mfc'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")
    name_assignment = database.Column(database.String(), comment="ФИО ответственного МФЦ")
    id_assignment = database.Column(database.Integer(), database.ForeignKey("assignment.id"))
    id_users_mfc = database.Column(database.Integer(), database.ForeignKey("users_mfc.id"))

class UserMfcAssignment(database.Model):
    __tablename__ = 'user_mfc_assignment'
    id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер")



# Модель рабочего места
class UserWorkplace(database.Model):
	__tablename__ = 'user_workplace'
	id = database.Column(database.Integer(), primary_key=True, comment="Уникальный номер рабочего места")
	name_workplace = database.Column(database.String(), comment="Название рабочего места")
	view = database.Column(database.Boolean(), comment="Отображение отчета", default=False)
	queue = database.Column(database.Integer(), comment="Очередь отображения", default=0)
	create_date = database.Column(database.DateTime(), comment="Дата создания изделия(новинка)")
	opt_price = database.Column(database.Numeric(), comment="Цена оптовая", default=0)
	operation = database.relationship(OperationsProducts,
									  primaryjoin="and_(OperationsProducts.id_product == Products.id)",
									  cascade="all, delete")
									  
	back_user = database.relationship(HistoryAuthUser, backref="user_info", viewonly=True)
	user_workplace = database.relationship(UserWorkplace, primaryjoin="and_(UserWorkplace.id == Users.workplace_user)")
	
	def __repr__(self):
		return "<{}:{}>".format(self.id, self.name_workplace)

'''
