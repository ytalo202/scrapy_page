from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
import os
# from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import chromedriver_binary  # Adds chromedriver binary to path

def ask_sunat(ruc, serie, number, sun_document, sun_user, sun_password):
    # chrome_options = webdriver.ChromeOptions()
    # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # options.add_argument('--start-maximized')
    # options.add_argument('--headless')
    # options.add_argument('--disable-extensions')
    # options.add_argument("--no-sandbox")
    # options.add_experimental_option('excludeSwitches', ['enable-automation'])

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("window-size=1024,768")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(chrome_options=chrome_options)

    # driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    driver.set_window_position(2000, 0)
    driver.maximize_window()
    time.sleep(0.5)

    driver.get(
        'https://api-seguridad.sunat.gob.pe/v1/clientessol/4f3b88b3-d9d6-402a-b85d-6a0bc857746a/oauth2/loginMenuSol?originalUrl=https://e-menu.sunat.gob.pe/cl-ti-itmenu/AutenticaMenuInternet.htm&state=rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAx3CAAAABAAAAADdAAEZXhlY3B0AAZwYXJhbXN0AEsqJiomL2NsLXRpLWl0bWVudS9NZW51SW50ZXJuZXQuaHRtJmI2NGQyNmE4YjVhZjA5MTkyM2IyM2I2NDA3YTFjMWRiNDFlNzMzYTZ0AANleGVweA==')

    # ruc = '20501493156'
    # serie = 'F005'
    # number = '75298'
    #
    # sun_document = '20601732751'
    # sun_user = 'WECLUB20'
    # sun_password = 'iV123456789'

    # login
    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'input#txtRuc'))) \
        .send_keys(sun_document)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'input#txtUsuario'))) \
        .send_keys(sun_user)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'input#txtContrasena'))) \
        .send_keys(sun_password)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'button#btnAceptar'))) \
        .click()

    # menu principal    
    try:
        WebDriverWait(driver, 8) \
            .until(EC.element_to_be_clickable((By.ID,
                                               'divOpcionServicio2'))) \
            .click()
    except Exception:
        return {"type": 3, "reason_id": 1}  # autentificacion

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.ID,
                                           'nivel1_11'))) \
        .click()

    try:
        WebDriverWait(driver, 5) \
            .until(EC.element_to_be_clickable((By.ID,
                                               'nivel2_11_9'))) \
            .click()
    except Exception:
        return {"type": 3, "reason_id": 2}
    
    try:
        WebDriverWait(driver, 5) \
            .until(EC.element_to_be_clickable((By.ID,
                                               'nivel3_11_9_5'))) \
            .click()
    except Exception:
        return {"type": 3, "reason_id": 2}

    try:
        WebDriverWait(driver, 5) \
            .until(EC.element_to_be_clickable((By.ID,
                                               'nivel4_11_9_5_1_1'))) \
            .click()
    except Exception:
        return {"type": 3, "reason_id": 2}

    # formulario de busqueda de comprobante

    try:
        WebDriverWait(driver, 13) \
            .until(EC.element_to_be_clickable((By.XPATH,
                                               '//*[@id="iframeApplication"]')))
        driver.switch_to.frame(driver.find_element_by_id("iframeApplication"))
    except Exception:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    WebDriverWait(driver, 8) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//*[@id="criterio.tipoConsulta"]'))) \
        .clear()

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//*[@id="criterio.tipoConsulta"]'))) \
        .send_keys('FE Recibidas')

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '/html/body/div[1]/table/tbody/tr/td/div/div/form/table/tbody/tr/td/table/tbody/tr/td/table[4]/tbody/tr/td/table/tbody/tr[2]/td[3]/div/div/div[3]/input'))) \
        .send_keys('')

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//*[@id="criterio.ruc"]'))) \
        .send_keys(ruc)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '/html/body/div[1]/table/tbody/tr/td/div/div/form/table/tbody/tr/td/table/tbody/tr/td/table[4]/tbody/tr/td/table/tbody/tr[3]/td[3]/div/div/div[3]/input'))) \
        .send_keys(serie)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '/html/body/div[1]/table/tbody/tr/td/div/div/form/table/tbody/tr/td/table/tbody/tr/td/table[4]/tbody/tr/td/table/tbody/tr[4]/td[3]/div/div/div[3]/input'))) \
        .send_keys(number)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//*[@id="criterio.btnContinuar"]'))) \
        .click()

    try:
        WebDriverWait(driver, 12) \
            .until(EC.element_to_be_clickable((By.XPATH,
                                               '//*[@id="recibido.facturasGrid-page-0"]/div/table/tbody/tr/td[2]/a'))) \
            .click()
    except Exception:
        return {"type": 2, "reason_id": 0}  # documento no encontrado

    time.sleep(1)

    if len(driver.window_handles) == 1:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    driver.switch_to.window(driver.window_handles[1])

    if check_exists_by_xpath(driver,
                             '/html/body/center/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]'):
        date = driver.find_element_by_xpath(
            '/html/body/center/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]') \
            .text.replace(' ', '').replace(':', '')
    else:
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    if check_exists_by_xpath(driver,
                             '/html/body/center/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[5]'):
        currency = driver.find_element_by_xpath(
            '/html/body/center/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[5]') \
            .text.replace(' ', '').replace(':', '')
    else:
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    if check_exists_by_xpath(driver, '/html/body/center/table/tbody/tr/td/table/tbody/tr[9]/td/table/tbody//tr/td'):
        lines = driver.find_elements_by_xpath(
            '/html/body/center/table/tbody/tr/td/table/tbody/tr[9]/td/table/tbody//tr/td')
    else:
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    items = []
    for i in range(0, len(lines), 8):
        if i != 0:
            items.append({
                "quantity": float(lines[i].text),
                "unit": lines[i + 1].text,
                "name": lines[i + 3].text,
                "unit_price": float(lines[i + 5].text),
            })

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        driver.close()

    return {"type": 1, "data": {"date": date, 'currency': currency, 'items': items}, "reason_id": 0}


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return False
    return True


def check_exists_by_css_selector(driver, id):
    try:
        driver.find_elements_by_css_selector(id)
    except NoSuchElementException:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return False
    return True


def check_exists_by_id(driver, id):
    try:
        driver.find_element_by_id(id)
    except Exception:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return False
    return True
