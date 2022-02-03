import datetime
import os
import pathlib
from typing import List

import requests
from bs4 import BeautifulSoup


def prepare_packages_names(packages_names: List[str]) -> List[str]:
    if 'ettercap' in packages_names:
        packages_names.append('ettercap-graphical')
        packages_names.remove('ettercap')
    return packages_names


def get_packages_names() -> List[str]:
    website = 'https://www.kali.org/tools/'
    response = requests.get(website)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content)
            cards = soup.select('.card')
            packages_names = []
            for card in cards:
                card_packages = [
                    a_tag.get_text().replace('\n', '').replace('$', '')
                    for a_tag in card.select('.card > ul > li > a')
                ]
                packages_names += card_packages
            packages_names = prepare_packages_names(packages_names)
            return packages_names
        except BaseException as ex:
            raise Exception('Unable to parse kali tools website:', ex)
    else:
        raise Exception(f'Website {website} returned {response.status_code}')


def write_packages_names(lib_dir, packages_names: List[str]):
    timestamp = int(datetime.datetime.now().timestamp() * 100)
    packages_lists_dir = os.path.join(lib_dir, 'packages-lists')
    if not os.path.exists(packages_lists_dir):
        os.makedirs(packages_lists_dir)
    with open(os.path.join(packages_lists_dir, f'package-list-{timestamp}.txt'), 'w') as file_writer:
        file_writer.writelines('\n'.join(packages_names))


def collect_packages_names(lib_dir):
    packages_names = get_packages_names()
    write_packages_names(lib_dir, packages_names)


def get_collected_packages_names(lib_dir) -> List[str]:
    def find_latest_list_file_dir() -> str:
        max_timestamp = 0
        for filename in os.listdir(os.path.join(lib_dir, 'packages-lists')):
            filename_timestamp = int(filename.replace('.txt', '').split('-')[-1])
            if filename_timestamp > max_timestamp:
                max_timestamp = filename_timestamp
        if max_timestamp:
            return os.path.join(lib_dir, 'packages-lists', f'package-list-{max_timestamp}.txt')
        else:
            raise Exception('No packages lists found')

    latest_list_file_dir = find_latest_list_file_dir()
    packages_names = []
    with open(latest_list_file_dir, 'r') as file_reader:
        for line in file_reader.readlines():
            packages_names.append(line.strip())

    return packages_names


if __name__ == '__main__':
    lib_dir = pathlib.Path(__file__).parent.resolve()
    collect_packages_names(lib_dir)