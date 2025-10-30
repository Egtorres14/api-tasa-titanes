from flask import Flask, jsonify
import time
from selenium import webdriver

# --- Importaciones de Selenium y WebDriver-Manager ---
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# --- Opciones CRÍTICAS para el servidor de Render [cite: 152-158] ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox") # CRÍTICO [cite: 155]
chrome_options.add_argument("--disable-dev-shm-usage") # CRÍTICO [cite: 157]
chrome_options.add_argument("--disable-gpu") # [cite: 158]
chrome_options.add_argument("--log-level=3")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
# --- Fin de las opciones críticas ---

@app.route('/obtener-tasa', methods=['GET'])
def get_rate():
    print(">>> Petición recibida en /obtener-tasa...")
    driver = None
    try:
        print(">>> Iniciando servicio de ChromeDriver (descargando)...")
        # webdriver-manager descarga el 'chromedriver' [cite: 159]
        service = Service(ChromeDriverManager().install())
        
        print(">>> Iniciando navegador Chrome (buscando binario en $PATH)...")
        # Selenium busca el binario de Chrome en el $PATH 
        # (que fue modificado por el startCommand de render.yaml) [cite: 160, 161]
        driver = webdriver.Chrome(service=service, options=chrome_options) [cite: 162]
        
        print(">>> Navegador iniciado. Abriendo página de Titanes...")
        driver.get("https://www.grupotitanes.com/#envio")
        
        wait = WebDriverWait(driver, 10)
        
        # 4. Interactuar con la página
        print(">>> Esperando que cargue el menú de origen...")
        wait.until(EC.presence_of_element_located((By.ID, 'pais1')))
        Select(driver.find_element(By.ID, 'pais1')).select_by_value('11') # EL SALVADOR
        
        print(">>> Esperando que cargue el menú de destino...")
        wait.until(EC.presence_of_element_located((By.ID, 'pais2')))
        Select(driver.find_element(By.ID, 'pais2')).select_by_value('6') # COLOMBIA
        
        # 5. Esperar el resultado
        print(">>> Países seleccionados. Esperando resultados de la tasa...")
        xpath_tasa = "//div[contains(text(), 'Mejor tasa disponible:')]/following-sibling::div[1]/b"
        wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath_tasa), 'EUR / COP'))
        
        # 6. Extraer los datos
        tasa = driver.find_element(By.XPATH, xpath_tasa).text
        xpath_comision = "//div[contains(text(), 'Comisión:')]/following-sibling::div[1]/b"
        comision = driver.find_element(By.XPATH, xpath_comision).text
        xpath_moneda = "//div[contains(text(), 'Moneda destino:')]/following-sibling::div[1]"
        moneda = driver.find_element(By.XPATH, xpath_moneda).text
        
        print(">>> ¡Datos extraídos con éxito!")
        
        # 7. Devolver los datos en formato JSON
        return jsonify(
            tasa_disponible=tasa,
            comision=comision,
            moneda_destino=moneda
        ), 200

    except Exception as e:
        print(f"XXX Ha ocurrido un error en Selenium: {e}") [cite: 173]
        return jsonify(
            error="No se pudieron obtener los datos.",
            detalle=str(e)
        ), 500

    finally:
        # 8. Cerrar el navegador
        if driver:
            driver.quit() [cite: 176]
            print(">>> Navegador cerrado.")

# Esta parte ('if __name__ ...') se ignora en Render 
# porque Gunicorn inicia 'app' directamente,
# pero es útil para pruebas locales.
if __name__ == '__main__':
    app.run(debug=True, port=5000)
