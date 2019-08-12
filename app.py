from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


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

    # Year selection
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
            "//select[@name='j_id148:cmbAnio']/option[text()='2019']")))\
        .click()

    # Period selection
    wait.until(EC.element_to_be_clickable(
        (By.XPATH,
            "//select[@name='j_id148:cmbPeriodo']/option[text()='JULIO']")))\
        .click()
    wait.until(EC.element_to_be_clickable(
        (By.ID,
            'j_id148:btnBuscarComprobantesElectronicos')))\
        .click()

    table = wait.until(EC.presence_of_element_located(
        (By.ID,
            'j_id148:tblFacturas')))
    if table:
        fill_table(driver)

    while has_next_page(driver):
        go_next_page(driver)
        sleep(1)
        table = wait.until(EC.presence_of_element_located(
            (By.ID,
             'j_id148:tblFacturas')))
        if table:
            fill_table(driver)

    sleep(5)
    driver.close()


def fill_table(driver):
    table_rows = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas']/tbody/tr")

    for row in table_rows:
        cells = row.find_elements_by_tag_name('td')
        iva = cells[4].text
        iva_input = cells[5].find_element_by_tag_name('input')
        iva_input.send_keys(iva)
        checkbox = cells[8].find_element_by_tag_name('input')
        checkbox.click()


def has_next_page(driver):
    paginator_cells = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
        "/tr/td")
    next_button = paginator_cells[-2]
    class_name = next_button.get_attribute('class')
    return 'dsbld' not in class_name


def go_next_page(driver):
    paginator_cells = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
        "/tr/td")
    next_button = paginator_cells[-2]
    next_button.click()


if __name__ == '__main__':
    main()
