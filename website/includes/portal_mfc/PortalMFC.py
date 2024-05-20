import pathlib

import requests
import re
import uuid
from bs4 import BeautifulSoup

class Portal():
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.path = str(pathlib.Path().resolve())
        self.pattern = r'file_id=(\d+)'
        self.regex_num_order = r"modelId/(\d+)"
        self.session = requests.Session()
        self.orig_http = "https://www.mfc61.ru"
        self.url_download_files = "https://www.mfc61.ru/Order/getFile?files_ids={0}"
        self.url_auth = "https://www.mfc61.ru/user/manager"
        self.url_order= "https://www.mfc61.ru/Order/list"

    def auth(self):
        params = {
            'UserLoginForm[username]': self.login,
            'UserLoginForm[password]': self.password
        }
        response = self.session.post(self.url_auth , data=params)
        if "Вы успешно вошли" in response.text:
            return True
        else:
            return False

    def InfoOrder(self, url_order, theme_order):
        get = self.session.get(url_order)
        bs = BeautifulSoup(get.text, "html.parser")
        class_date = bs.select(".tablet-green.vmid")
        date_in = class_date[0].text
        date_out = class_date[1].text

        surname = bs.select(".bp-surname")[0].text if len(bs.select(".bp-surname")) > 0 else "Нет"
        names = bs.select(".bp-names")[0].text if len(bs.select(".bp-names")) > 0 else "Нет"
        occupation = bs.select(".bp-occupation")[0].text if len(bs.select(".bp-occupation")) > 0 else "Нет"
        email = bs.select(".bp-email .straight")[0].text if len(bs.select(".bp-email .straight")) > 0 else "Нет"
        cellphone = bs.select(".bp-cellphone .straight")[0].text if len(bs.select(".bp-cellphone .straight")) > 0 else "Нет"

        mfc_section_body = bs.select(".mfc-section-body")[0].text

        order_files = bs.select(".msp-file-attachment.nomargin .mfac-row")

        image_urls = [img['src'] for img in bs.find_all('img')]

        # Загрузка изображений и сохранение их на диск или передача как часть ответа
        images = []
        for url in image_urls:
            # Загрузка изображения
            image_response = requests.get(url)
            if image_response.status_code == 200:
                # Сохранение изображения на диск
                file_path = self.path + "\\website\\files\\portal_mfc\\images\\" + str(uuid.uuid4()) + ".jpg"
                with open(file_path, 'wb') as image_file:
                    image_file.write(image_response.content)
                    images.append(file_path)
                print('Изображение {} сохранено.'.format(url))
            else:
                print('Ошибка при загрузке изображения {}.'.format(url))

        file_zip = self.GetAllFiles(order_files)

        return {"date_in": date_in, "date_out": date_out, "surname": surname,
                "names": names, "occupation": occupation, "email": email,
                "cellphone": cellphone, "mfc_section_body": mfc_section_body,
                "file_zip": file_zip, "images": images, "theme_order": theme_order}
    def GetAllFiles(self, order_files):
        files_num = []
        for order_file in order_files:
            match = re.search(self.pattern, str(order_file))
            files_num.append(match.group(1))
        nums = ','.join(files_num)
        download_file = self.session.get(self.url_download_files.format(nums))
        if download_file.status_code == 200:
            # Открываем файл для записи в бинарном режиме
            gen_name = str(uuid.uuid4()) + ".zip"
            file_path = self.path + "\\website\\files\\portal_mfc\\documents\\" + gen_name
            with open(file_path, 'wb') as file:
                # Записываем содержимое файла из ответа в файл на диске
                file.write(download_file.content)
            return file_path
        return None

    def getAllOrder(self):
        get = self.session.get(self.url_order)
        bs = BeautifulSoup(get.text, "html.parser")
        find_table = bs.select(".mfc-table-restyling-offers tbody tr td.envelope a")

        arr_information = []
        for table in find_table:
            theme_order = table.parent.parent.select("td")[4].text.strip()
            print(theme_order)
            url_order = self.InfoOrder(self.orig_http + table.get("href"), theme_order)
            match = re.search(self.regex_num_order, self.orig_http + table.get("href"))
            number = match.group(1)

            arr_information.append({"number_order": number, "info": url_order})
        return arr_information