from flask import Flask, jsonify
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Usaremos Chrome, el estándar en la nube ---
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# --- Opciones de Chrome para un servidor (Linux) ---
chrome_options = Options()
chrome_options.add_argument("--headless") # OBLIGATORIO para servidores
chrome_options.add_argument("--no-sandbox") # OBLIGATORIO
chrome_options.add_argument("--disable-dev-shm-usage") # OBLIGATORIO
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# --- Servidor de producción (Gunicorn) ---
# No usamos el 'if __name__ == "__main__":'
# Render y Gunicorn se encargan de iniciar 'app'

@app.route('/obtener-tasa', methods=['GET'])
def get_rate():
    print(">>> Petición recibida en /obtener-tasa...")
    driver = None
    try:
        # webdriver-manager descargará el driver correcto
        # para el servidor de Render (Linux)
        print(">>> Iniciando servicio de ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(">>> Navegador iniciado. Abriendo página de Titanes...")
        driver.get("https.www.grupotitanes.com/#envio")
        wait = WebDriverWait(driver, 10)
        
        # --- Lógica de Scraping (la misma de antes) ---
        print(">>> Esperando que cargue el menú de origen...")
        wait.until(EC.presence_of_element_located((By.ID, 'pais1')))
        Select(driver.find_element(By.ID, 'pais1')).select_by_value('11') # EL SALVADOR
        
        print(">>> Esperando que cargue el menú de destino...")
        wait.until(EC.presence_of_element_located((By.ID, 'pais2')))
        Select(driver.find_element(By.ID, 'pais2')).select_by_value('6') # COLOMBIA
        
        print(">>> Países seleccionados. Esperando resultados...")
        xpath_tasa = "//div[contains(text(), 'Mejor tasa disponible:')]/following-sibling::div[1]/b"
        wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath_tasa), 'EUR / COP'))
        
        print(">>> ¡Datos extraídos con éxito!")
        tasa = driver.find_element(By.XPATH, xpath_tasa).text
        comision = driver.find_element(By.XPATH, xpath_comision).text
        moneda = driver.find_element(By.XPATH, xpath_moneda).text
        
        return jsonify(
            tasa_disponible=tasa,
            comision=comision,
            moneda_destino=moneda
        ), 200

    except Exception as e:
        print(f"XXX Ha ocurrido un error en Selenium: {e}")
        return jsonify(error="No se pudieron obtener los datos.", detalle=str(e)), 500

    finally:
        if driver:
            driver.quit()
            print(">>> Navegador cerrado.")