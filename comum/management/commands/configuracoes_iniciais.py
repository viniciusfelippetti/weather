import datetime
import shutil

import pandas as pd
from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import zipfile
import os
from comum.models import Estacao, HistoricoEstacao


def convert_utc_to_time(utc_string):
    # Remove o sufixo UTC e espaços extras
    utc_string = utc_string.replace('UTC', '').strip()
    utc_string = utc_string.replace(':', '').strip()

    # Verifica se o valor contém segundos (formato HH:MM:SS)
    if len(utc_string) > 5 and ':' in utc_string:
        # Se for formato HH:MM:SS, divide e extrai horas, minutos e segundos
        parts = utc_string.split(':')
        print(parts)
        hour = parts[0].zfill(2)
        minute = parts[1].zfill(2)
    else:
        # Se for formato HH:MM, divide e extrai horas e minutos  # Obter a parte HHMM
        hour = int(utc_string[:2])
        minute = int(utc_string[2:])
        return datetime.time(hour, minute)

    # Retorna o tempo formatado como uma string
    return datetime.time(hour, minute)


def converter_para_float(value):
    # Remove espaços em bran
    value = value.strip()

    # Verifica se o valor está vazio
    if not value:
        return 0

    # Se o valor começa com uma vírgula, adiciona um zero antes da vírgula
    if value.startswith(','):
        value = '0' + value

    # Substitui vírgulas por pontos
    value = value.replace(',', '.')

    # Tenta converter o valor para float
    try:
        return float(value)
    except ValueError:
        return 0  # Retorna 0 se a conversão falhar


def ajuste_valor(value):
    # Converte o valor para string
    value_str = str(value).strip()

    # Substitui valores vazios por '-9999'
    if value_str == '':
        return '-9999'
    else:
        return value_str

def all_values_minus9999(values):
    # Verifica se todos os valores são -9999 ou -9999.0
    return all(value == -9999 or value == -9999.0 for value in values)

def ajuste_data_formato(date_string):
        try:
            # Converte a data de YYYY/MM/DD para YYYY-MM-DD manipulando a string
            return date_string.replace('/', '-')
        except ValueError:
            return date_string


class Command(BaseCommand):
    help = 'Importação dos beneficiários'

    def handle(self, *args, **options):

        options = Options()
        # Configura o diretório de download
        prefs = {
            "download.default_directory": "/home/vinif",  # Substitua pelo caminho desejado
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }  # Substitua pelo caminho desejado
        options.add_experimental_option("prefs", prefs)

        # Inicializa o navegador
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        browser.get('https://portal.inmet.gov.br/dadoshistoricos')

        # Aguarda o link estar presente
        wait = WebDriverWait(browser, 10)

        link_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@href='https://portal.inmet.gov.br/uploads/dadoshistoricos/2024.zip']")))
        link_element.click()
        time.sleep(20)

        link_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@href='https://portal.inmet.gov.br/uploads/dadoshistoricos/2023.zip']")))
        link_element.click()
        time.sleep(20)

        link_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@href='https://portal.inmet.gov.br/uploads/dadoshistoricos/2022.zip']")))
        link_element.click()
        time.sleep(20)

        link_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@href='https://portal.inmet.gov.br/uploads/dadoshistoricos/2021.zip']")))
        link_element.click()
        time.sleep(20)
        link_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@href='https://portal.inmet.gov.br/uploads/dadoshistoricos/2020.zip']")))
        link_element.click()
        time.sleep(20)
        # #
        zip_dir = ''
        extract_dir = '/extracted_files'  # Substitua pelo caminho desejado
        # #
        # Verifique se o diretório de destino existe e crie-o se necessário
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)
            print(f"Criado o diretório: {extract_dir}")

        # Liste todos os arquivos ZIP no diretório
        zip_files = [f for f in os.listdir(zip_dir) if f.endswith('.zip')]

        # Descompacte cada arquivo ZIP
        for zip_file in zip_files:
            zip_file_path = os.path.join(zip_dir, zip_file)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                print(f"Arquivos de {zip_file} descompactados em: {extract_dir}")
        #
        # print("Todos os arquivos ZIP foram descompactados com sucesso.")
        extracted_files = os.listdir(extract_dir)
        #
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Mover apenas se o arquivo não estiver já no diretório de destino
                if os.path.abspath(root) != os.path.abspath(extract_dir):
                    shutil.move(file_path, extract_dir)
                    print(f"Movendo {file_path} para {extract_dir}")

        for csv_file in extracted_files:
            if csv_file.startswith('INMET_NE_RN') and csv_file.endswith('.CSV'):

                csv_file_path = os.path.join(extract_dir, csv_file)
                print(csv_file_path)
                df = pd.read_csv(csv_file_path, encoding='ISO-8859-1', sep='delimiter')
                # print(f"Lendo dados de: {csv_file_path}")
                # print(df.head())
                estacao = df.iloc[1, 0].split(';')[1].strip()
                codigo = df.iloc[2, 0].split(';')[1].strip()
                latitude = df.iloc[3, 0].split(';')[1].strip()
                longitude = df.iloc[4, 0].split(';')[1].strip()
                if not Estacao.objects.filter(nome_estacao=estacao).exists():
                    Estacao.objects.create(nome_estacao=estacao, latitude=latitude, longitude=longitude, id=codigo)

                for i in range(8, len(df)):
                    # Sanitize and extract values
                    data = ajuste_data_formato(df.iloc[i, 0].split(';')[0].strip())
                    hora = convert_utc_to_time(df.iloc[i, 0].split(';')[1].strip())
                    precipitacao = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[2].strip()))
                    pressao = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[3].strip()))
                    pressao_maxima = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[4].strip()))
                    pressao_minima = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[5].strip()))
                    radiacao = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[6].strip()))
                    temperatura = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[7].strip()))
                    temperatura_minima = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[10].strip()))
                    temperatura_maxima = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[9].strip()))
                    umidade = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[13].strip()))
                    umidade_minima = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[14].strip()))
                    umidade_maxima = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[15].strip()))
                    vento_rajada_maxima = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[17].strip()))
                    vento_velocidade_horaria = converter_para_float(ajuste_valor(df.iloc[i, 0].split(';')[18].strip()))

                    # List of all values to check if they are all zero
                    values = [
                        precipitacao, pressao, pressao_maxima, pressao_minima, radiacao,
                        temperatura, temperatura_minima, temperatura_maxima, umidade,
                        umidade_minima, umidade_maxima, vento_rajada_maxima, vento_velocidade_horaria
                    ]

                    # Check if all values are zero, if not, create the HistoricoEstacao object
                    if not all_values_minus9999(values):
                        HistoricoEstacao.objects.create(
                            estacao_id=codigo,
                            data=data,
                            hora=hora,
                            precipitacao=precipitacao,
                            pressao=pressao,
                            pressao_maxima=pressao_maxima,
                            pressao_minima=pressao_minima,
                            radiacao=radiacao,
                            temperatura=temperatura,
                            temperatura_minima=temperatura_minima,
                            temperatura_maxima=temperatura_maxima,
                            umidade=umidade,
                            umidade_minima=umidade_minima,
                            umidade_maxima=umidade_maxima,
                            vento_rajada_maxima=vento_rajada_maxima,
                            vento_velocidade_horaria=vento_velocidade_horaria
                        )

        # # Feche o navegador
        # browser.quit()
