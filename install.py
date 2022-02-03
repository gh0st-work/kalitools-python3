import os
import pathlib
import subprocess

from collect_packages_names import get_collected_packages_names


def install_package(package_name: str):
    try:
        stdout = subprocess.getoutput(f'sudo dpkg -s {package_name}')
        if 'Status: install ok installed' in stdout:
            return {
                'success': True,
                'info': 'already installed',
            }
        else:
            os.system(f'sudo apt install -y {package_name}')
            stdout = subprocess.getoutput(f'sudo dpkg -s {package_name}')
            if 'Status: install ok installed' in stdout:
                return {
                    'success': True,
                    'info': 'ok',
                }
            else:
                return {
                    'success': False,
                    'info': 'not installed',
                }
    except BaseException as ex:
        return {
            'success': False,
            'info': str(ex),
        }


def install():
    if os.geteuid() != 0:
        raise Exception('Please run with sudo privileges')
    lib_dir = pathlib.Path(__file__).parent.resolve()
    packages_names = get_collected_packages_names(lib_dir)
    results = [
        {
            'package_name': packages_name,
            **install_package(packages_name)
        }
        for packages_name in packages_names
    ]
    max_package_name_len = max(list(map(lambda result: len(result['package_name']), results)))
    max_status_len = max(len('SUCCESS'), len('FAILURE'))
    print('\n\n\n')
    for result in results:
        result_package_name_text = result['package_name'].ljust(max_package_name_len)
        result_status_text = ('SUCCESS' if result['success'] else 'FAILURE').ljust(max_status_len)
        result_info_text = result['info']
        print(f'{result_package_name_text}: {result_status_text} ({result_info_text})')
    success_installed_count = len(list(filter(lambda result: result['success'], results)))
    all_packages_count = len(results)
    success_percent = round(success_installed_count / all_packages_count * 100, 2)
    print()
    print(f'Installed {success_installed_count}/{len(results)} ({success_percent}%) kali tools on your machine')
