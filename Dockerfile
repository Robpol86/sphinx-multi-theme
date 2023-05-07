FROM readthedocs/build:ubuntu-20.04-2023.05.03
ENV READTHEDOCS_VIRTUALENV_PATH=/home/docs/checkouts/readthedocs.org/user_builds/sphinx-multi-theme/envs/40
WORKDIR /home/docs/checkouts/readthedocs.org/user_builds/sphinx-multi-theme/checkouts/40

RUN asdf install python 3.10.8
RUN asdf global python 3.10.8

ENV PATH=/home/docs/checkouts/readthedocs.org/user_builds/sphinx-multi-theme/envs/40/bin:/home/docs/.asdf/shims:/home/docs/.asdf/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN asdf plugin add poetry
RUN asdf install poetry latest
RUN asdf global poetry latest
RUN ln -s $READTHEDOCS_VIRTUALENV_PATH .venv

RUN python -mvenv $READTHEDOCS_VIRTUALENV_PATH
RUN python -m pip install --upgrade --no-cache-dir pip setuptools
RUN python -m pip install --upgrade --no-cache-dir pillow mock==1.0.1 "alabaster>=0.7,<0.8,!=0.7.5" commonmark==0.9.1 recommonmark==0.5.0 sphinx sphinx-rtd-theme "readthedocs-sphinx-ext<2.3"

ADD . .

RUN poetry install
RUN sphinx-build -W --keep-going -q -b linkcheck -d _build/doctrees docs/ _build/linkcheck
