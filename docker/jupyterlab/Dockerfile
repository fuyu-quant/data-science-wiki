FROM python:3.9.7-buster
#USER root
ARG DEBIAN_FRONTEND=noninteractive

# 環境系
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9

# パッケージの追加とタイムゾーンの設定
# 必要に応じてインストールするパッケージを追加してください
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    jq \
    locales \
    tree \
    procps \
    vim \
    git \
    sudo \
&&  localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 \ 
&&  ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
# apt-getのキャッシュを削除するためのコード
# https://nykergoto.hatenablog.jp/entry/2020/07/25/%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92%E3%81%AAdockerfile%E3%82%92%E6%9B%B8%E3%81%8F%E3%81%A8%E3%81%8D%E3%81%AB%E6%B0%97%E3%82%92%E3%81%A4%E3%81%91%E3%81%A8%E3%81%8F%E3%81%A8%E8%89%AF%E3%81%84%E3%81%93
&&  apt-get autoremove -y \
&&  apt-get clean \
# この下はどっちが必要か分からない
&&  rm -rf /var/lib/apt/lists/* \  
&&  rm -rf /usr/local/src/*


RUN curl -sL https://deb.nodesource.com/setup_18.x |bash - \
    && apt-get install -y --no-install-recommends \
        nodejs \
        yarn \
&&  apt-get autoremove -y \
&&  apt-get clean \
# この下はどっちが必要か分からない
&&  rm -rf /var/lib/apt/lists/* \  
&&  rm -rf /usr/local/src/*   



# JupyterLab関連のパッケージ（いくつかの拡張機能を含む）
# 必要に応じて、JupyterLabの拡張機能などを追加してください
RUN python3 -m pip install --upgrade pip \
&&  pip install --no-cache-dir \
    jupyterlab \
    jupyterlab_code_formatter black isort autopep8 \
    jupyterlab_execute_time \
    jupyterlab-git \
    jupyterlab_widgets \
    jupyterlab_autoscrollcelloutput \
    ipywidgets \
    jupyterlab-language-pack-ja-JP \
    import-ipynb

RUN jupyter labextension install \
      @jupyter-widgets/jupyterlab-manager \
      plotlywidget \
      jupyterlab-plotly 


# GitHubからsshでcloneするための設定
# 参考になったサイト
# https://github.com/yuiki-iwayama/JupyterLab-Docker
ARG GITHUB_USER
ARG GITHUB_EMAIL
RUN mkdir -p ~/.ssh  && \
  git config --global user.name "fuyu-quant" && \
  git config --global user.email fuyufuyu@gamil.com
#COPY ./jupyterlab/utils/config /root/.ssh
#COPY ./jupyterlab/utils/init.sh /usr/bin



#COPY /Users/tanakatouma/vscode/kaggle-Learning-Equality/${LOCAL_DIR}/requirements.txt /${PROJECT_DIR}/
# パッケージのインストール
# requirements.txtの場所(参考リンク：https://zuma-lab.com/posts/docker-python-settings)
# 適当な場所に移動する
COPY requirements.txt /root
WORKDIR /root
RUN pip install --no-cache-dir -r requirements.txt