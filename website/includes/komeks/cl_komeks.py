import os
import pathlib
import re
import uuid
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from website import database
from website.includes.database.database_models import KomeksUpdatesNames, KomeksUpdateFiles


class Komeks:
    def __init__(self, login, password):
        self.url = "https://azovkomeks.ru/update/lk.php"
        self.url_orig = "https://azovkomeks.ru"
        self.login = login
        self.password = password
        self.path = str(pathlib.Path().resolve())
        self.session = requests.Session()
    def get_html(self):
        return self.session.get(self.url, auth=(self.login, self.password))
    def parse_html(self, html):
        html_text = html.text.replace("Версия<tr>", "Версия</tr><tr>").replace("<tr>", "</tr><tr>")
        return BeautifulSoup(html_text, "html.parser")
    def extract_update_info(self, soup):
        find_table = soup.find_all('table')[0]
        rows = find_table.find_all('tr')

        for row in rows[1:]:
            columns = row.find_all('td')
            title = columns[0].text.strip()
            links = [{"name": link.text, "url": link["href"]} for link in columns[1].find_all('a')]
            try:
                version = columns[2].text.strip()
            except Exception as err:
                version = "Нет"

            yield title, links, version
    def download_and_save_file(self, url):
        filename = os.path.basename(url)
        response = requests.get(url, auth=(self.login, self.password))
        if response.status_code == 200:
            uuid_name = str(uuid.uuid4())
            file_path = os.path.join(self.path, "website", "files", "updates", f"{uuid_name}_{filename}")
            with open(file_path, 'wb') as update_file:
                update_file.write(response.content)
            return file_path
        return None
    def process_updates(self, app):
        html = self.get_html()
        soup = self.parse_html(html)

        with app.app_context():
            list_names_update = KomeksUpdatesNames.query.all()

            for title, links, version in self.extract_update_info(soup):
                for names in list_names_update:
                    if names.name_orig in title:
                        for link in links:
                            new_add_komeks_update_files = KomeksUpdateFiles.query.filter(
                                KomeksUpdateFiles.win_types == link['name'],
                                KomeksUpdateFiles.id_komeks_updates_names == names.id,
                                KomeksUpdateFiles.version == version
                            ).first()
                            if not new_add_komeks_update_files:
                                file_path = self.download_and_save_file(self.url_orig + link['url'])
                                if file_path:
                                    new_add_komeks_update_files = KomeksUpdateFiles(
                                        win_types=link['name'],
                                        update_on=datetime.now(),
                                        id_komeks_updates_names=names.id,
                                        href_download=file_path,
                                        version=version
                                    )
                                    database.session.add(new_add_komeks_update_files)
                                    database.session.commit()
