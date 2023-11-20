import os
import logging
import subprocess
import jupytext
import shutil
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup


home_path = os.environ['HOME']
main_path = f'{home_path}/data-science-wiki/'



def remove_metadata(file_path_):
    # ファイルが存在する場合のみ実行
    if os.path.exists(file_path_):
        with open(file_path_, 'r') as file:
            data = json.load(file)

        # metadata.widgets を削除する
        if 'metadata' in data and 'widgets' in data['metadata']:
            del data['metadata']['widgets']

        # 同じファイルに上書き保存する
            with open(file_path_, 'w') as file:
                json.dump(data, file, indent=2)
        logging.info('remove metadata')
    else:
        logging.warning(f'File not found: {file_path_}')
    return


def edit_html(main_path_, html_path_):
    with open(html_path_, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # コードブロックをスクロールするためのタグを埋め込む
    head_end_index = html_content.find('</head>')
    style_to_add = """
    <style>
    .cm-editor.cm-s-jupyter .highlight pre {
        overflow-x: auto;
    }
    </style>
    """
    updated_html_content = html_content[:head_end_index] + style_to_add + html_content[head_end_index:]

    # SEO対策のためのタグを追加

    file_path = main_path_ + html_path_.replace(".html", ".ipynb")
    text = jupytext.read(file_path)
    title = text['cells'][0]['source'].replace('# ', '')
    description = text['cells'][1]['source']

    # タイトルタグ
    soup = BeautifulSoup(updated_html_content, 'html.parser')
    title_tag = soup.find('title')
    title_tag.string = f"{title} | データサイエンスのまとめサイト,200件以上の手法を紹介"

    # Descriptionタグ
    new_meta_tag = soup.new_tag('meta', attrs={"name": "description", "content": f"{description}"})
    soup.head.append(new_meta_tag)
    modified_html_content = str(soup)

    with open(html_path_, 'w', encoding='utf-8') as file:
        file.write(modified_html_content)

    logging.info('htmlファイルの編集')
    return


def ipynb_to_html(main_path_, ipynb_list):
    logging.info('---ipynb_to_html---')
    os.chdir(main_path)
    html_list = []
    dir_list = ['causalanalysis','cv','graph','multimodal','nlp','optimization','recommendation','rl','tabledata','timeseriesanalysis']
    # jupyterコマンドのパス
    jupyter = f'{home_path}/.cache/pypoetry/virtualenvs/data-science-wiki-274Wd7YI-py3.9/bin/jupyter'
    for ipynb_path in ipynb_list:
        for dir_name in dir_list:
            if ('ipynb' in ipynb_path) and (dir_name in ipynb_path):
                file_path = main_path + ipynb_path
                remove_metadata(file_path)
                logging.info(f'file path:{file_path}')
                html_result = subprocess.run([jupyter, 'nbconvert', '--to', 'html', file_path], capture_output=True, text=True)

                if html_result.returncode == 0:
                    logging.info(f'Successfully converted: {file_path} to HTML')
                    logging.info(f'Conversion stdout: {html_result.stdout}')
                else:
                    logging.error(f'Conversion failed: {file_path} to HTML')
                    logging.error(f'Conversion stdout: {html_result.stdout}')
                    logging.error(f'Conversion stderr: {html_result.stderr}')
                    continue  # optionally skip this iteration if the conversion failed

                html_path = ipynb_path.replace('ipynb', 'html')
                logging.info(f'Created file: {html_path}')

                edit_html(main_path_, html_path)

                html_list.append(html_path)

    logging.info(f'htmlリスト:{html_list}')
    return html_list






def ipynb_to_json(main_path_, html_list_):
    logging.info('---ipynb_to_json---')

    for html_path in html_list_:
        file_path = main_path_ + html_path.replace(".html", ".ipynb")
        try:
            logging.info(f'html file:{html_path}')
            text = jupytext.read(file_path)
            title = text['cells'][0]['source'].replace('# ', '')
            description = text['cells'][1]['source']

            utc_now = datetime.now(timezone.utc)
            iso_format = utc_now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            new_data = {
                "title": title,
                "overview": description,
                "path": '/' + html_path,
                "created_at": iso_format
            }

            with open('/home/ec2-user/efs/article_info.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            existing_entry = next((item for item in data if item["path"] == new_data["path"]), None)

            if existing_entry:
                # 既存のエントリを新しいデータで更新
                logging.info(f'update file:{html_path}')
                existing_entry.update(new_data)
            else:
                logging.info(f'append file:{html_path}')
                data.append(new_data)

            with open('/home/ec2-user/efs/article_info.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except FileNotFoundError:
            logging.exception(f'File not found, skip file:{file_path}')
            continue
        except Exception as e:
            logging.exception(f'An unexpected error occurred while processing file: {file_path}. Error: {str(e)}')
            continue
    return



def efs_uploader(html_list):
    logging.info('---efs_uploader---')

    for html_path in html_list:
        try:
            source_path = "/home/ec2-user/data-science-wiki/" + html_path
            destination_path = "/home/ec2-user/efs/article/" + html_path
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.move(source_path, destination_path)
            logging.info(f'destination path:{destination_path}')

        except FileNotFoundError:
            logging.exception(f'File not found, skip file:{html_path}')
            continue
        except Exception as e:
            logging.exception(f'An unexpected error occurred while processing file: {html_path}. Error: {str(e)}')
            continue

    return
