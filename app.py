import sys
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, \
    TimeoutException, NoSuchElementException

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
    check_invoices(driver, year, month)
    month = 'FEBRERO'
    check_invoices(driver, year, month)

    # driver.close()
    assert 1 == 0


def check_invoices(driver, year, month):
    wait = WebDriverWait(driver, 10)

    # year selection
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//select[@name='j_id148:cmbAnio']/option[text()='{}']".format(year)
    ))).click()

    # Period selection
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
            "//select[@name='j_id148:cmbPeriodo']/option[text()='{}']"
            .format(month)))).click()

    wait.until(EC.element_to_be_clickable(
        (By.ID,
            'j_id148:btnBuscarComprobantesElectronicos')))\
        .click()

    wait.until(EC.presence_of_element_located(
        (By.ID,
            'j_id148:tblFacturas:paginadorFactura_table')))

    first_number = driver.find_element_by_xpath(
        "//table[@id='j_id148:tblFacturas']/tbody/tr/td")
    first_number = int(first_number.text)

    if first_number > 1:
        go_previous_page(driver)
        try:
            wait.until(EC.text_to_be_present_in_element(
                (By.ID, 'j_id148:tblFacturas:0:j_id165'), '1'))
        except TimeoutException:
            print('timeout')

    total_iva = 0

    table_iva = fill_in_table(driver)
    total_iva += table_iva

    i = 1
    while has_next_page(driver):
        go_next_page(driver)
        # wait until change of cell
        first_number = i*10 + 1
        id_number = i*10
        wait.until(EC.text_to_be_present_in_element(
            (By.ID, 'j_id148:tblFacturas:{}:j_id165'.format(id_number)),
            str(first_number)))

        table_iva = fill_in_table(driver)
        total_iva += table_iva
        i += 1

    driver.find_element_by_id(
        'j_id148:btnGuardarFacturasSeleccionadas').click()

    # try:
    #     wait.until(EC.presence_of_element_located(
    #         (By.ID, 'j_id148:tablaDetalleArchivo')))
    # except StaleElementReferenceException as e:
    #     print(e)

    wait.until(EC.presence_of_element_located(
        (By.ID, 'j_id148:tablaDetalleArchivo')))
    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.reporte .rich-table-row td')))
    except TimeoutException:
        print('timeout')

    summary_cells = driver.find_elements_by_css_selector(
            '.reporte .rich-table-row td')
    total_iva_cell = float(summary_cells[-2].text)  # debe ser igual al total iva

    while total_iva_cell != total_iva:
        summary_cells = driver.find_elements_by_css_selector(
            '.reporte .rich-table-row td')
        total_iva_cell = summary_cells[-2].text  # debe ser igual al total iva


def fill_in_table(driver):
    table_rows = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas']/tbody/tr")
    table_iva = 0

    for row in table_rows:
        cells = row.find_elements_by_tag_name('td')
        iva = cells[4].text
        table_iva += float(iva)
        iva_input = cells[5].find_element_by_tag_name('input')
        iva_input.send_keys(iva)
        checkbox = cells[8].find_element_by_tag_name('input')
        checkbox.click()
    return table_iva


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
