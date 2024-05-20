import os
import pathlib
from datetime import datetime

from website import create_app
from website.extensions import *
from website.includes.VipNet.vipnet_class import VipNet
from website.includes.database.database_mfc import SpZapros, Zapros
from website.includes.database.database_models import Regions, PortalSettings, PortalOrders, PortalImages, \
    KomeksUpdatesNames, RoleUserMFC
from website.includes.komeks.cl_komeks import Komeks
from website.includes.portal_mfc.PortalMFC import Portal
from apscheduler.schedulers.background import BackgroundScheduler

path = str(pathlib.Path().resolve())

app = create_app()
with app.app_context():
    database.create_all()

    all_regions = ["г. Азов", "г. Батайск", "г. Волгодонск", "г. Гуково",
                   "г. Донецк", "г. Зверево", "г. Каменск-Шахтинский", "г. Новочеркасск",
                   "г. Новошахтинск", "г. Ростов-на-Дону", "г. Таганрог", "г. Шахты",
                   "Азовский район", "Аксайский район", "Багаевский район", "Белокалитвинский район",
                   "Боковский район", "Верхнедонской район", "Веселовский район", "Волгодонской район",
                   "Дубовский район", "Егорлыкский район", "Заветинский район", "Зерноградский район",
                   "Зимовниковский район", "Кагальницкий район", "Каменский район", "Кашарский район",
                   "Константиновский район", "Красносулинский район", "Куйбышевский район", "Мартыновский район",
                   "Матвеево-Курганский район", "Миллеровский район", "Милютинский район", "Морозовский район",
                   "Мясниковский район", "Неклиновский район", "Обливский район", "Октябрьский район",
                   "Орловский район", "Песчанокопский район", "Пролетарский район", "Ремонтненский район",
                   "Родионово-Несветайский район", "Сальский район", "Семикаракорский район", "Советский район",
                   "Тарасовский район", "Тацинский район", "Усть-Донецкий район", "Целинский район",
                   "Цимлянский район", "Чертковский район", "Шолоховский район"]

    names_update = [
            {"Архив обновления программы": "ИИС"},
            {"Архив обновления сервера ЭДО": "ЭДО"},
            {"Модуль СМЭВ 2": "Модуль СМЭВ 2"},
            {"Программа для преобразовании печати документов": "Программа для преобразовании печати документов"},
            {"Веб-сервис ЕПГУ": "Веб-сервис ЕПГУ"},
            {"Веб-сервис пердварительной записи с ЕПГУ": "Веб-сервис пердварительной записи с ЕПГУ"},
            {"Сервис Минтруда РО": "Сервис Минтруда РО"},
            {"СМЭВ 3 на java 17": "СМЭВ 3 на java 17"},
            {"Signer 2": "Signer 2"},
            {"Сервис хранения файлов": "Сервис хранения файлов"},
            {"Сервер электронной очереди": "Сервер электронной очереди"}
        ]

    roles = ["Администратор", "Пользователь"]

    for role in roles: RoleUserMFC.addRoleUserMFC(role)
    #for region in all_regions: Regions.addRegion(region)
    for names in names_update: KomeksUpdatesNames.addKomeksUpdatesNames(names)

def AsyncVipNetPaskageMfc():
    with app.app_context():
        regions = Regions.query.all()
        for region in regions:
            if region.active_portal:
                vipnet = VipNet(user=region.vipnet_login, password=region.vipnet_password)
                data = vipnet.getTransportMFTP()
                print(data)
                pass



def AsyncPortalMfc():
    with app.app_context():
        regions = Regions.query.all()
        for region in regions:
            if region.active_portal:
                print("Проверка поручений", region.name_region)
                p_mfc = Portal(region.portal_login, region.portal_password)
                p_mfc.auth()
                info = p_mfc.getAllOrder()
                for order in info:
                    #theme_order
                    findOrder = PortalOrders.query.filter(PortalOrders.id_order == order['number_order']).first()
                    if not findOrder:
                        data = order['info']
                        add_new = PortalOrders(region_mfc=region.id,
                                               id_order=order['number_order'],
                                               date_in=datetime.strptime(data['date_in'], '%d.%m.%Y'),
                                               date_out=datetime.strptime(data['date_out'], '%d.%m.%Y'),
                                               surname=data['surname'],
                                               theme_order=data['theme_order'],
                                               names=data['names'],
                                               occupation=data['occupation'],
                                               email=data['email'],
                                               cellphone=data['cellphone'],
                                               mfc_section_body=data['mfc_section_body'],
                                               file_zip=data['file_zip'])
                        database.session.add(add_new)
                        database.session.commit()
                        database.session.flush()

                        for image in data['images']:
                            database.session.add(PortalImages(id_portal_orders=order['number_order'], filename=image))
                            database.session.commit()
                    else:
                        try:
                            os.remove(order['info']['file_zip'])
                        except Exception as err:
                            pass

def AsyncKomeksUpdate():
    updates = Komeks("tatsin", "VC47U")
    updates.process_updates(app)

# Запускаем сохранение файлов обновлений и поручения на портале

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(AsyncPortalMfc, trigger='interval', seconds=360)
scheduler.add_job(AsyncVipNetPaskageMfc, trigger='interval', seconds=360)
#scheduler.add_job(AsyncKomeksUpdate, trigger='interval', seconds=360)
scheduler.start()

if __name__ == '__main__':
    #adsdasasd
    vipnet = VipNet()
    data = vipnet.getTransportMFTP()
    print(data)
    print("Запуск модуля, внутреннего сайта, без обновления данных.")
    #app.run(host='0.0.0.0', port=8999, debug=True)
