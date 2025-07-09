import requests
from bs4 import BeautifulSoup
import json
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import random

dominio_oficial = "www.caesb.df.gov.br"
keywords = [
    "Caesb", "Segunda Via da Conta", "Portal de Serviços",
    "Consultar Falta de Água", "Canais de Atendimento", "Carta de Serviços"
]

buscas = [
    "caesb segunda via",
    "portal caesb",
    "conta caesb",
    "caesb consultar falta de água"
]

def extrair_urls(busca):
     # Cria um diretório exclusivo para o perfil do Selenium
    pasta_perfil = os.path.join(os.getcwd(), "pbl08120gmail.com")
    os.makedirs(pasta_perfil, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={pasta_perfil}")  # Perfil isolado
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("✅ Navegador aberto com perfil isolado.")
        driver.get("https://www.google.com")
        time.sleep(random.uniform(2, 4))

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(busca)
        search_box.send_keys(Keys.RETURN)

        time.sleep(random.uniform(5, 7))

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        resultados = set() 

        for links in soup.find_all('a'):
            href = links.get('href')
            
            print(f"\turl encontrada: {href}")
            if href and "/url?q=" in href:
                link = href.split("/url?q=")[1].split("&")[0]
                resultados.add(link)  # Adiciona ao conjunto
    finally:
        driver.quit()

    return list(resultados)  # Retorna como lista

def analisar_urls(urls):
    suspeitas = []
    for url in urls:
        if dominio_oficial not in url:
            for palavra in keywords:
                if palavra.lower() in url.lower():
                    suspeitas.append(url)
                    break
    return list(set(suspeitas))  # remover duplicadas

def salvar_json(suspeitas):
    json_data = {
        "suspeitas_detectadas_em": time.strftime("%Y-%m-%d %H:%M:%S"),
        "urls_suspeitas": suspeitas,
        "dominio_oficial": dominio_oficial,
        "status": "anomalía_detectada" if suspeitas else "nenhuma_anomalia"
    }
    with open("urls_suspeitas.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

def chamar_powershell():
    subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "denunciar_rpa.ps1"])

def main():
    todas_urls = []
    for busca in buscas:
        urls = extrair_urls(busca)
        todas_urls.extend(urls)

    urls_suspeitas = analisar_urls(todas_urls)
    salvar_json(urls_suspeitas)

    if urls_suspeitas:
        print("URLs suspeitas encontradas. Chamando o robô...")
        #chamar_powershell()
    else:
        print("Nenhuma URL suspeita encontrada.")

if __name__ == "__main__":
    main()
