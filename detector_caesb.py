import requests
from bs4 import BeautifulSoup
import json
import subprocess
import time

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
    query = "+".join(busca.split())
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resposta = requests.get(url, headers=headers)
    soup = BeautifulSoup(resposta.text, 'html.parser')

    resultados = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and "/url?q=" in href:
            href_limpo = href.split("/url?q=")[1].split("&")[0]
            resultados.append(href_limpo)
    return resultados

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
        print("[!] URLs suspeitas encontradas. Chamando o robô...")
        chamar_powershell()
    else:
        print("[✓] Nenhuma URL suspeita encontrada.")

if __name__ == "__main__":
    main()
