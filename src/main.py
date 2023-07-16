import os
import logging
import subprocess
import jupytext
import boto3
from dotenv import load_dotenv

load_dotenv('../.env')

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )

home_path = os.environ['HOME']
main_path = f'{home_path}/data-science-wiki/'


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename= main_path + 'logs/app.log',
    filemode='w'
)


def update_check():
    #result = subprocess.run(['ls'], capture_output=True)
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD^'], capture_output=True, text=True)

    result = result.stdout.strip().decode('utf-8')
    result = str(result).split("\n")

    logging.info(result)
    return result


def ipynb_to_html(ipynb_list):
    html_list = []
    for ipynb_path in ipynb_list:
        if 'ipynb' in ipynb_path:
            file_path = main_path + ipynb_path
            subprocess.run(['jupyter','nbconvert','--to','html',file_path], capture_output=True)
            html_path = ipynb_path.replace('ipynb', 'html')
            html_list.append(html_path)
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
    ipynb_list = update_check()

    #ipynb_list = ['tabledata/clustering/t-means.ipynb']
    ipynb_to_text(ipynb_list)
    html_list = ipynb_to_html(ipynb_list)
    s3_uploader(html_list)