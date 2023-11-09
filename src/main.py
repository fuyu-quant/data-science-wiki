import os
import logging
import subprocess
import jupytext
import shutil
import json
from datetime import datetime, timezone


home_path = os.environ['HOME']
main_path = f'{home_path}/data-science-wiki/'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename= main_path + 'logs/app.log',
    filemode='w'
)


def update_check():
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
    changelog_list = str(changelog).split("\n")

    logging.info(f'変更リスト:{changelog_list}')
    return changelog_list




def ipynb_to_html(ipynb_list):
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

                # スタイルの追加
                with open(html_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                head_end_index = html_content.find('</head>')
                style_to_add = """
                <style>
                .cm-editor.cm-s-jupyter .highlight pre {
                    overflow-x: auto;
                }
                </style>
                """
                updated_html_content = html_content[:head_end_index] + style_to_add + html_content[head_end_index:]
                with open(html_path, 'w', encoding='utf-8') as file:
                    file.write(updated_html_content)

                logging.info('スタイルの追加')
                html_list.append(html_path)

    logging.info(f'htmlリスト:{html_list}')
    return html_list






def ipynb_to_json(html_list_):
    logging.info('---ipynb_to_json---')

    for html_path in html_list_:
        file_path = main_path + html_path.replace(".html", ".ipynb")
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



if __name__ == "__main__":
    # gitのコマンドを実行する上で必要
    os.chdir(main_path)
    ipynb_list = update_check()
    html_list = ipynb_to_html(ipynb_list)
    ipynb_to_json(html_list)
    efs_uploader(html_list)
