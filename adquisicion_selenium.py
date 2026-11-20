import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


URLS_AEROPUERTOS = {
    "VLC": "https://www.airportia.com/spain/valencia-airport/departures/",
    "MAD": "https://www.airportia.com/spain/madrid-barajas-international-airport/departures/",
    "BCN": "https://www.airportia.com/spain/barcelona-international-airport/departures/",
    "LHR": "https://www.airportia.com/united-kingdom/london-heathrow-airport/departures/",
    "CDG": "https://www.airportia.com/france/charles-de-gaulle-international-airport/departures/",
    "AMS": "https://www.airportia.com/netherlands/amsterdam-schiphol-airport/departures/",
    "FRA": "https://www.airportia.com/germany/frankfurt-am-main-international-airport/departures/",
    "FCO": "https://www.airportia.com/italy/leonardo-da-vinci/departures/",
}


def iniciar_driver(headless=False):
    opciones = Options()
    opciones.page_load_strategy = "eager"
    if headless:
        opciones.add_argument("--headless=new")

    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-blink-features=AutomationControlled")
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option("useAutomationExtension", False)
    opciones.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=opciones)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver


def formatear_hora(texto_hora):
    """Convierte '09:50' al formato 'YYYY-MM-DD HH:MM' que espera explorar.py."""
    limpio = texto_hora.strip()
    if not re.match(r"^\d{2}:\d{2}$", limpio):
        return None
    hoy = datetime.now().strftime("%Y-%m-%d")
    return f"{hoy} {limpio}"


def normalizar_estado(texto_estado):
    """Unifica el estado (en inglés o español) al formato de explorar.py."""
    t = texto_estado.lower()
    if "landed" in t or "aterrizado" in t:
        return "landed"
    if "en route" in t or "en ruta" in t or "en el aire" in t or "airborne" in t:
        return "active"
    if "delayed" in t or "retrasado" in t:
        return "delayed"
    if "cancelled" in t or "cancelado" in t:
        return "cancelled"
    if "scheduled" in t or "programado" in t:
        return "scheduled"
    return t or None


def obtener_vuelos(aeropuerto, driver=None):
    url = URLS_AEROPUERTOS.get(aeropuerto.upper())
    if not url:
        print(f"[{aeropuerto}] aeropuerto sin URL configurada")
        return None

    cerrar_al_final = False
    if driver is None:
        driver = iniciar_driver(headless=False)
        cerrar_al_final = True

    vuelos = []
    try:
        driver.get(url)
        time.sleep(2)

        # Intentar cerrar banner de cookies si aparece
        try:
            btn_cookies = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "button#onetrust-accept-btn-handler, button.fc-cta-consent, [aria-label*='Aceptar'], [aria-label*='Accept']"
                ))
            )
            btn_cookies.click()
        except TimeoutException:
            pass

        # Esperar a que cargue la tabla de vuelos
        WebDriverWait(driver, 25).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.flights tbody tr"))
        )

        filas = driver.find_elements(By.CSS_SELECTOR, "table.flights tbody tr")

        for fila in filas:
            celdas = fila.find_elements(By.TAG_NAME, "td")
            if len(celdas) < 6 or "num" not in (celdas[0].get_attribute("class") or ""):
                continue

            enlaces_vuelo = celdas[0].find_elements(By.TAG_NAME, "a")
            flight_iata = enlaces_vuelo[0].text.strip() if enlaces_vuelo else None

            texto_destino = celdas[1].text.strip()
            match_iata = re.search(r"\b([A-Z]{3})\b$", texto_destino)
            arr_iata = match_iata.group(1) if match_iata else None

            dep_time = formatear_hora(celdas[3].text)
            dep_actual = formatear_hora(celdas[4].text)

            dep_delayed = None
            if dep_time and dep_actual:
                t_prog = datetime.strptime(dep_time, "%Y-%m-%d %H:%M")
                t_real = datetime.strptime(dep_actual, "%Y-%m-%d %H:%M")
                dep_delayed = int((t_real - t_prog).total_seconds() / 60)

            spans_estado = celdas[5].find_elements(By.CSS_SELECTOR, "span.label")
            texto_estado = " ".join(s.text.strip() for s in spans_estado if s.text.strip())
            status = normalizar_estado(texto_estado)

            vuelos.append({
                "flight_iata": flight_iata,
                "dep_iata": aeropuerto.upper(),
                "cs_flight_iata": None,
                "arr_iata": arr_iata,
                "status": status,
                "dep_time": dep_time,
                "arr_time": None,
                "arr_actual": None,
                "delayed": dep_delayed,
                "dep_delayed": dep_delayed,
                "arr_delayed": None,
            })

    except TimeoutException:
        print(f"[{aeropuerto}] tiempo de espera agotado | Título página: {driver.title}")
        return None
    except Exception as e:
        print(f"[{aeropuerto}] error en Selenium: {type(e).__name__} - {e}")
        return None
    finally:
        if cerrar_al_final:
            driver.quit()

    if not vuelos:
        print(f"[{aeropuerto}] la página cargó pero no se extrajeron vuelos")
        return None

    return vuelos