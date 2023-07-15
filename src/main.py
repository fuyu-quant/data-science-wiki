import os
import logging
import subprocess
import boto3

s3 = boto3.client('s3')

home_path = os.environ['HOME']
main_path = f'{home_path}/vscode/data-science-wiki/'


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename= main_path + 'logs/app.log',
    filemode='w'
)


def update_check():
    result = subprocess.run(['ls'], capture_output=True)
    #result = subprocess.run(['git', 'diff', '--name-only', 'HEAD^'], capture_output=True, text=True)

    result = result.stdout.strip().decode('utf-8')
    result = str(result).split("\n")

    logging.info(result)
    return result


def ipynb_to_html(ipynb_list):
    html_list = []
    for i in ipynb_list:
        if 'ipynb' in i:
            ipynb_path = f'main_path + {i}'
            subprocess.run(['jupyter','nbconvert','--to','html',ipynb_path], capture_output=True)
            html_path = ipynb_path.replace('ipynb', 'html')
            html_list.append(html_path)
    return html_list


def s3_uploader(html_list):
    for j in html_list:
        s3.upload_file(file_path, bucket_name, 'file.txt')
        j
    return


if __name__ == "__main__":
    ipynb_list = update_check()

    html_list = ipynb_to_html(ipynb_list)