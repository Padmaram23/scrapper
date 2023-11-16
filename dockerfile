FROM apache/airflow:2.7.1
COPY ./requirements.txt /requirements.txt
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install --upgrade selenium

USER root
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unzip

RUN apt install wget
RUN apt-get install -yqq unzip
# install chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
    
ENV CHROMEDRIVER_VERSION=118.0.5993.70

RUN mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION 
RUN curl -sS -o /tmp/chromedriver_linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/linux64/chromedriver-linux64.zip 
RUN unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION 
RUN rm /tmp/chromedriver_linux64.zip 
RUN chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver-linux64/chromedriver
RUN ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

RUN  mkdir -p /home/airflow/.cache/selenium 
RUN chmod -R 777 /home/airflow/.cache/selenium 