import logging
import glob
import os

home_path = os.environ['HOME']
main_path = f'{home_path}/data-science-wiki/'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename= main_path + 'logs/recreate.log',
    filemode='w'
)

def ipynb_retriever():
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
    for name in directory_names:
        directory_path = f'{home_path}/data-science-wiki/{name}/'
        notebook_paths_list = glob.glob(os.path.join(directory_path, '**/*.ipynb'), recursive=True)
        ipynb_path_list_.extend(notebook_paths_list)
    logging.info(f'ipynbのファイル数:{len(ipynb_path_list_)}')
    return ipynb_path_list_




if __name__ == "__main__":
    ipynb_path_list = ipynb_retriever()
