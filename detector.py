from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import random

def salvar_html_google(busca):
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
        with open("resultado_google.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ HTML salvo.")
    finally:
        driver.quit()

# Execução
if __name__ == "__main__":
    salvar_html_google("caesb segunda via")
