import os
import logging
import subprocess

from make_html import (
    ipynb_to_html,
    ipynb_to_json,
    efs_uploader
    )

home_path = os.environ['HOME']
main_path = f'{home_path}/data-science-wiki/'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename= main_path + 'logs/crontab.log',
    filemode='w'
)


def github_ipynb_retriever():
    """
    check github update
    """
    logging.info('---update_check---')
    os.chdir(main_path)
    result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
    logging.info(f'git pull:{result}')
    changelog = subprocess.run(['git', 'diff', '--name-only', 'HEAD^'], capture_output=True, text=True)
    logging.info(f'変更:{changelog}')
    changelog = changelog.stdout.strip()#.decode('utf-8')
    change_ipynb_path_list_ = str(changelog).split("\n")

    logging.info(f'変更のあるipynbのファイル:{change_ipynb_path_list_}')

    # 検索するディレクトリ名
    directory_names = [
        'causalanalysis',
        'cv',
        'graph',
        'materials_informatics',
        'mathmatical_optimization',
        'multimodal',
        'nlp',
        'recommendation',
        'rl',
        'simulation',
        'statistics',
        'tabledata',
        'timeseriesanalysis'
        ]

    ipynb_path_list_ = []
    for file_name in change_ipynb_path_list_:
        for dir_name in directory_names:
            if dir_name in file_name:
                if '.ipynb' in file_name:
                    directory_path = f'{home_path}/data-science-wiki/{file_name}'
                    print(directory_path)
                    ipynb_path_list_.append(directory_path)

    logging.info(f'ipynbのファイル数:{len(ipynb_path_list_)}')
    print(ipynb_path_list_)
    return ipynb_path_list_


if __name__ == "__main__":
    home_path = os.environ['HOME']
    main_path = f'{home_path}/data-science-wiki/'
    ipynb_path_list = github_ipynb_retriever()
    html_list = ipynb_to_html(main_path, ipynb_list)
    ipynb_to_json(main_path, html_list)
    efs_uploader(html_list)
