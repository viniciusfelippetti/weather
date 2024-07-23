FROM python:3.10.12

# set work directory
WORKDIR /weather

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Adicionar chave e repositório do Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

# Instalar o Google Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Instalar o ChromeDriver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/91.0.4472.101/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]