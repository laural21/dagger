FROM python:3.7-slim

ARG AIRFLOW_VERSION
ENV AIRFLOW_HOME /usr/local/airflow

ARG PYTHON_VERSION
ENV PYTHON_VERSION 3.7

# Configure environment
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV AIRFLOW_GPL_UNIDECODE yes
ENV BUILD_DEPS='python3-dev libkrb5-dev libsasl2-dev libssl-dev libffi-dev build-essential liblapack-dev libpq-dev'
ENV CONSTRAINTS="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Install build dependencies & utilities
RUN apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        apt-utils \
        freetds-bin \
        libsasl2-modules \
        locales \
        lsb-release \
        sasl2-bin \
        sqlite3 \
        unixodbc \
        $BUILD_DEPS \
        python3-pip \
        python3-requests \
        curl \
        netcat \
        net-tools \
        sudo \
        vim \
        htop \
        procps \
        less \
        jq \
        ssh \
        git \
        zip unzip

# Install aws cli 2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

# Install python libraries & cleanup
RUN pip install -U pip setuptools wheel pytest-runner
RUN pip install --use-deprecated legacy-resolver \
    authlib==0.15.4 \
    requests==2.25.1 \
    apache-airflow[slack,postgres,s3,statsd]==$AIRFLOW_VERSION --constraint $CONSTRAINTS \
    && apt-get purge --auto-remove -yqq $BUILD_DEPS \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

# Setup airflow user
RUN useradd --user-group --no-log-init -m -d $AIRFLOW_HOME --shell /bin/bash airflow \
    && chown -R airflow: $AIRFLOW_HOME \
    && echo airflow:airflow | chpasswd \
    && echo "airflow ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/airflow \
    && chmod 0440 /etc/sudoers.d/airflow

USER airflow

# Install additional python libraries
COPY requirements.txt $AIRFLOW_HOME/requirements.txt
RUN /usr/local/bin/pip install --user -r  $AIRFLOW_HOME/requirements.txt

# Add files
COPY docker-entrypoint.sh $AIRFLOW_HOME/docker-entrypoint.sh
COPY airflow.cfg $AIRFLOW_HOME/airflow.cfg

WORKDIR $AIRFLOW_HOME
ENTRYPOINT ["./docker-entrypoint.sh"]