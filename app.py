from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException


MONTHS = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
          'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']


def main():
    driver = webdriver.Chrome()
    url = 'https://srienlinea.sri.gob.ec/tuportal-internet/verificaEmail.jspa'
    driver.get(url)
    assert 'Login' in driver.title
    username = driver.find_element_by_name('j_username')
    password = driver.find_element_by_name('j_password')
    username.clear()
    password.clear()

    username.send_keys("1701120998")
    password.send_keys("grado_1975*")
    password.send_keys(Keys.RETURN)

    start_button = driver.find_element_by_class_name('ui-icon-closethick')
    start_button.click()
    assert 'Notificaciones' in driver.page_source

    redirection = 'https://srienlinea.sri.gob.ec/tuportal-internet/'\
        'menusFavoritos.jspa?redireccion=129&idGrupo=127'
    driver.get(redirection)

    start_button = driver.find_element_by_id('j_id414:j_id423')
    assert 'INICIAR PROCESO DE DEVOLUCIÓN' in driver.page_source
    start_button.click()

    wait = WebDriverWait(driver, 10)
    accept_button = wait.until(EC.element_to_be_clickable(
        (By.ID, 'frmConfirmacionCiudadDevolucion:j_id351')))
    accept_button.click()

    facturas_electronicas_link = wait.until(EC.element_to_be_clickable(
        (By.ID, 'j_id325:j_id334')))
    facturas_electronicas_link.click()

    year = '2019'
    month = 'ENERO'
    total_invoices = 0

    current_year = datetime.now().year
    current_month_index = datetime.now().month - 1
    previous_years = current_year - int(year)

    initial_index = MONTHS.index(month)

    if previous_years:
        # months in the first year
        months = MONTHS[initial_index:]
        for month in months:
            total_invoices = check_invoices(driver, year, month,
                                            total_invoices)

    # months in the actual year
    months = MONTHS[:current_month_index]
    year = str(current_year)
    for month in months:
        total_invoices = check_invoices(driver, year, month, total_invoices)

    # driver.close()
    assert 1 == 0  # To exit without closing the driver


def check_invoices(driver, year, month, total_invoices):
    wait = WebDriverWait(driver, 10)

    # year selection
    for i in range(200):
        try:
            driver.find_element_by_xpath(
                "//select[@name='j_id148:cmbAnio']/option[text()='{}']"
                .format(year)).click()
            break
        except NoSuchElementException:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                    "//select[@name='j_id148:cmbAnio']/option[text()='{}']"
                    .format(year)))).click()
            break
        except Exception:
            pass

    # Period selection
    for i in range(200):
        try:
            driver.find_element_by_xpath(
                "//select[@name='j_id148:cmbPeriodo']/option[text()='{}']"
                .format(month)).click()
            break
        except NoSuchElementException:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                    "//select[@name='j_id148:cmbPeriodo']/option[text()='{}']"
                    .format(month)))).click()
            break
        except Exception:
            pass

    for i in range(200):
        try:
            driver.find_element_by_id(
                'j_id148:btnBuscarComprobantesElectronicos').click()
            break
        except NoSuchElementException:
            wait.until(EC.element_to_be_clickable(
                (By.ID,
                    'j_id148:btnBuscarComprobantesElectronicos')))\
                    .click()
            break
        except Exception:
            pass

    for i in range(200):
        try:
            driver.find_element_by_id(
                'j_id148:tblFacturas:paginadorFactura_table')
            break
        except NoSuchElementException:
            wait.until(EC.presence_of_element_located(
                (By.ID,
                    'j_id148:tblFacturas:paginadorFactura_table')))
            break
        except Exception:
            pass

    for i in range(200):
        try:
            first_row = driver.find_element_by_xpath(
                "//table[@id='j_id148:tblFacturas']/tbody/tr/td")
            break
        except NoSuchElementException:
            first_row = wait.until(EC.presence_of_element_located(
                (By.XPATH,
                    "//table[@id='j_id148:tblFacturas']/tbody/tr/td")))
            break
        except Exception:
            pass

    first_row_number = int(first_row.text)

    if first_row_number > 1:
        sleep(1)
        go_previous_page(driver)
        for i in range(200):
            try:
                wait.until(EC.text_to_be_present_in_element(
                    (By.ID, 'j_id148:tblFacturas:0:j_id165'), '1'))
                break
            except Exception as e:
                print(e)

    table_invoices = fill_in_table(driver)
    total_invoices += table_invoices
    i = 1
    while has_next_page(driver):
        go_next_page(driver)
        # wait until change of cell
        first_row = i*10 + 1
        id_number = i*10
        try:
            wait.until(EC.text_to_be_present_in_element(
                (By.ID, 'j_id148:tblFacturas:{}:j_id165'.format(id_number)),
                str(first_row)))
        except TimeoutException:
            pass
        table_invoices = fill_in_table(driver)
        total_invoices += table_invoices
        i += 1

    for i in range(200):
        try:
            driver.find_element_by_id(
                'j_id148:btnGuardarFacturasSeleccionadas').click()
            break
        except NoSuchElementException:
            wait.until(EC.element_to_be_clickable(
                (By.ID,
                    'j_id148:btnGuardarFacturasSeleccionadas')))\
                .click()
            break
        except Exception:
            pass

    for i in range(200):
        try:
            driver.find_element_by_id(
                'j_id148:tablaDetalleArchivo')
            summary_cells = driver.find_elements_by_css_selector(
                '.reporte .rich-table-row td')
            semitotal_invoices = int(summary_cells[-3].text)
            if semitotal_invoices == total_invoices:
                break

        except NoSuchElementException:
            wait.until(EC.presence_of_element_located(
                (By.ID,
                    'j_id148:tablaDetalleArchivo')))
        except Exception:
            pass

    return total_invoices


def fill_in_table(driver):
    table_rows = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas']/tbody/tr")

    for row in table_rows:
        for i in range(600):
            try:
                cells = row.find_elements_by_tag_name('td')
                iva = cells[4].text
                break
            except Exception:
                pass

        for i in range(600):
            try:
                iva_input = cells[5].find_element_by_tag_name('input')
                iva_input.clear()
                iva_input.send_keys(iva)
                break
            except Exception:
                pass

        for i in range(600):
            try:
                checkbox = cells[8].find_element_by_tag_name('input')
                break
            except Exception:
                pass

        sleep(0.2)
        if not checkbox.get_attribute('checked'):
            checkbox.click()
    return len(table_rows)


def has_next_page(driver):
    paginator_cells = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
        "/tr/td")
    next_button = paginator_cells[-2]
    class_name = next_button.get_attribute('class')
    return 'dsbld' not in class_name


def has_previous_page(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located(
        (By.XPATH,
            "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
            "/tr/td")))
    paginator_cells = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
        "/tr/td")
    previous_button = paginator_cells[1]
    class_name = previous_button.get_attribute('class')
    return 'dsbld' not in class_name


def go_previous_page(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located(
        (By.XPATH,
            "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
            "/tr/td")))
    paginator_cells = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
        "/tr/td")
    previous_button = paginator_cells[1]
    previous_button.click()


def go_next_page(driver):
    paginator_cells = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
        "/tr/td")
    next_button = paginator_cells[-2]
    next_button.click()


if __name__ == '__main__':
    main()
