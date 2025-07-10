import requests
from bs4 import BeautifulSoup
import json
import subprocess
import os
import time
import random
import logging
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# ========= CONFIGURAÇÃO DO LOGGER =========

def configurar_logger(nivel='INFO'):
    niveis = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    nivel_log = niveis.get(nivel.upper(), logging.WARNING)

    os.makedirs('log', exist_ok=True)

    logging.basicConfig(
        level=nivel_log,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('log/detector.log', encoding='utf-8')
        ],
        force=True
    )

    return logging.getLogger(__name__)

logger = configurar_logger('INFO')

# ========= VARIÁVEIS =========

dominio_oficial = "www.caesb.df.gov.br"

buscas = [
    "caesb segunda via",
    "portal caesb",
    "conta caesb",
    "caesb consultar falta de água"
]

# ========= FUNÇÃO DE EXTRAÇÃO DOS ANÚNCIOS =========

def extrair_anuncios(busca):
    pasta_perfil = os.path.join(os.getcwd(), "pbl08120gmail.com")
    os.makedirs(pasta_perfil, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={pasta_perfil}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    anuncios_encontrados = []
    try:
        logger.info(f" Buscando: {busca}")
        driver.get("https://www.google.com")
        time.sleep(random.uniform(2, 4))

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(busca)
        search_box.send_keys(Keys.RETURN)

        time.sleep(random.uniform(5, 7))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        anuncios = soup.find_all('span', string=lambda s: s and 'Anúncio' in s)

        for anuncio in anuncios:
            link_tag = anuncio.find_parent('div')
            if link_tag:
                a_tag = link_tag.find('a', href=True)
                if a_tag:
                    href = a_tag['href']
                    if "/url?q=" in href:
                        url_final = href.split("/url?q=")[1].split("&")[0]
                        dominio = urlparse(url_final).netloc
                        anuncios_encontrados.append({
                            "url": url_final,
                            "dominio": dominio
                        })
                        logger.info(f" Anúncio encontrado: {dominio} -> {url_final}")

    except Exception as e:
        logger.error(f"Erro ao extrair anúncios: {e}")
    finally:
        driver.quit()

    return anuncios_encontrados

# ========= JSON, POWERSHELL e MAIN =========

def salvar_json(anuncios):
    json_data = {
        "busca_realizada_em": time.strftime("%Y-%m-%d %H:%M:%S"),
        "anuncios_encontrados": anuncios,
        "status": "ok" if anuncios else "nenhum_resultado"
    }
    with open("anuncios_detectados.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
    logger.info("Arquivo JSON salvo com os PATROCINADOS encontrados.")

def chamar_powershell():
    try:
        subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "denunciar_rpa.ps1"])
        logger.info("Script PowerShell executado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao executar PowerShell: {e}")

def main():
    todos_anuncios = []
    for busca in buscas:
        anuncios = extrair_anuncios(busca)
        todos_anuncios.extend(anuncios)

    salvar_json(todos_anuncios)

    if todos_anuncios:
        logger.warning("Anúncios patrocinados encontrados:")
        for item in todos_anuncios:
            logger.warning(f"    - {item['dominio']} -> {item['url']}")
        logger.warning("Chamando robô de denúncia...")
        # chamar_powershell()
    else:
        logger.info("Nenhum anúncio patrocinado encontrado.")

if __name__ == "__main__":
    main()
