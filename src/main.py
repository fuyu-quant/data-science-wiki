import os
import logging
import subprocess
import jupytext
import boto3
from dotenv import load_dotenv


home_path = os.environ['HOME']
main_path = f'{home_path}/data-science-wiki/'

load_dotenv(f'{main_path}/.env')


s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )



logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename= main_path + 'logs/app.log',
    filemode='w'
)


def update_check():
    os.chdir(main_path)
    result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
    logging.info(f'git pull:{result}')
    changelog = subprocess.run(['git', 'diff', '--name-only', 'HEAD^'], capture_output=True, text=True)
    logging.info(f'変更:{changelog}')
    changelog = changelog.stdout.strip()#.decode('utf-8')
    changelog_list = str(changelog).split("\n")

    logging.info(f'変更リスト:{changelog_list}')
    return changelog_list


def ipynb_to_html(ipynb_list):
    os.chdir(main_path)
    html_list = []
    dir_list = ['causalanalysis','cv','graph','multimodal','nlp','recommendation','rl','tabledata','timeseriesanalysis']
    # jupyterコマンドのパス
    jupyter = f'{home_path}/.cache/pypoetry/virtualenvs/data-science-wiki-274Wd7YI-py3.9/bin/jupyter'
    for ipynb_path in ipynb_list:
        for dir_name in dir_list:
            if ('ipynb' in ipynb_path) and (dir_name in ipynb_path):
                file_path = main_path + ipynb_path
                logging.info(f'file path:{file_path}')
                html_result = subprocess.run([jupyter,'nbconvert','--to','html', file_path], capture_output=True, text=True)
                logging.info(f'変換結果:{html_result}')
                html_path = ipynb_path.replace('ipynb', 'html')
                logging.info(f'作成ファイル:{html_path}')
                html_list.append(html_path)

    logging.info(f'htmlリスト:{html_list}')
    return html_list


def s3_uploader(html_list):
    for html_path in html_list:
        bucket_name = 'ds-wiki-html'
        local_path = main_path + html_path
        s3_path = html_path
        s3.upload_file(local_path, bucket_name, s3_path)
        if os.path.isfile(local_path):
            os.remove(local_path)
    return


def ipynb_to_text(ipynb_list):
    for ipynb_path in ipynb_list:
        file_path = main_path + ipynb_path
        text = jupytext.read(file_path)
        title = text['cells'][0]['source'].replace(' ', '').replace('#', '')
        description = text['cells'][1]['source']
        logging.info(title)
        logging.info(description)
    return 


if __name__ == "__main__":
    # gitのコマンドを実行する上で必要
    os.chdir(main_path)
    ipynb_list = update_check()
    #ipynb_to_text(ipynb_list)
    html_list = ipynb_to_html(ipynb_list)
    s3_uploader(html_list)