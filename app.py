import sys
from configparser import ConfigParser
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MONTHS = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
          'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']


def main():

    # get defaults
    config = ConfigParser()
    config.read('default.ini')

    defaults = config['DEFAULT']
    default_username = defaults['Username']
    default_password = defaults['Password']
    default_year = defaults['Year']
    default_month = defaults['Month']

    # ask for credentials
    # Example: 1701120998, grado_1975*
    username = validate_username(input(
                     'Ingrese su cédula de identidad [{}]: '
                     .format(default_username))) or default_username
    password = input('Ingrese su contraseña [{}]: '
                     .format(default_password)) or default_password

    # Ask for initial year and month
    # Example 2019, ENERO
    year = validate_year(input(
                 'Ingrese el año desde el que va a declarar [{}]: '
                 .format(default_year))) or default_year
    month = validate_month(input(
                  'Ingrese el mes desde el que va a declarar [{}]: '
                  .format(default_month))) or default_month

    # save new default values
    config['DEFAULT'] = {
        'Username': username,
        'Password': password,
        'Year': year,
        'Month': month,
    }
    with open('default.ini', 'w') as configfile:
        config.write(configfile)

    # Open web browser
    driver = webdriver.Chrome()
    url = 'https://srienlinea.sri.gob.ec/tuportal-internet/verificaEmail.jspa'
    driver.get(url)

    # go to login
    assert 'Login' in driver.title
    username_input = driver.find_element_by_name('j_username')
    password_input = driver.find_element_by_name('j_password')
    username_input.clear()
    password_input.clear()

    # enter credentials
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    # if user or password are not valid
    try:
        assert 'Usuario o contraseña inválidos.' not in driver.page_source
    except AssertionError:
        print('El usuario y/o contraseña son incorrectos')
        driver.close()
        sys.exit()

    # press start button
    start_button = driver.find_element_by_class_name('ui-icon-closethick')
    start_button.click()
    assert 'Notificaciones' in driver.page_source

    # redirection to web portal
    redirection = 'https://srienlinea.sri.gob.ec/tuportal-internet/'\
        'menusFavoritos.jspa?redireccion=129&idGrupo=127'
    driver.get(redirection)

    # START PROCESS
    start_button = driver.find_element_by_id('j_id414:j_id423')
    assert 'INICIAR PROCESO DE DEVOLUCIÓN' in driver.page_source
    start_button.click()

    # clicking accept button
    wait = WebDriverWait(driver, 10)
    accept_button = wait.until(EC.element_to_be_clickable(
        (By.ID, 'frmConfirmacionCiudadDevolucion:j_id351')))
    accept_button.click()

    # Go to electronic invoices
    facturas_electronicas_link = wait.until(EC.element_to_be_clickable(
        (By.ID, 'j_id325:j_id334')))
    facturas_electronicas_link.click()

    # Calculate number of months
    total_invoices = 0
    current_year = datetime.now().year
    current_month_index = datetime.now().month - 1
    previous_years = current_year - int(year)

    initial_index = MONTHS.index(month)

    if previous_years:
        # months in the first year
        months = MONTHS[initial_index:]
        for month in months:
            # check invoices for all the months
            total_invoices = check_invoices(driver, year, month,
                                            total_invoices)

    # months in the actual year
    months = MONTHS[:current_month_index]
    year = str(current_year)
    for month in months:
        # check invoices for all the months
        total_invoices = check_invoices(driver, year, month, total_invoices)

    assert 1 == 0  # To exit without closing the browser


def check_invoices(driver, year, month, total_invoices):
    """Method to check every invoice given a month and a year"""
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

    # search invoices
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

    # wait for invoices paginator
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

    # wait for first row number element
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

    # if first row number is greater than 1 then we are in another page
    # but the first one
    if first_row_number > 1:
        sleep(1)
        # go to first page
        go_previous_page(driver)

        # wait for the first page
        for i in range(200):
            try:
                wait.until(EC.text_to_be_present_in_element(
                    (By.ID, 'j_id148:tblFacturas:0:j_id165'), '1'))
                break
            except Exception as e:
                print(e)

    # select every invoice in the table
    table_invoices = fill_in_table(driver)
    total_invoices += table_invoices

    # if there is another page then go to next page and select
    # invoices in that page
    i = 1
    while has_next_page(driver):
        go_next_page(driver)
        first_row = i*10 + 1
        id_number = i*10

        # wait until change of cell
        try:
            wait.until(EC.text_to_be_present_in_element(
                (By.ID, 'j_id148:tblFacturas:{}:j_id165'.format(id_number)),
                str(first_row)))
        except TimeoutException:
            pass

        # select invoices
        table_invoices = fill_in_table(driver)
        total_invoices += table_invoices
        i += 1

    # save selected invoices
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

    # wait for detail table to appear
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

    # return total of invoices checked until this moment
    return total_invoices


def fill_in_table(driver):
    table_rows = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas']/tbody/tr")

    for row in table_rows:
        # get iva tax value from invoice
        for i in range(600):
            try:
                cells = row.find_elements_by_tag_name('td')
                iva = cells[4].text
                break
            except Exception:
                pass
        # copy the iva value to next cell
        for i in range(600):
            try:
                iva_input = cells[5].find_element_by_tag_name('input')
                iva_input.clear()
                iva_input.send_keys(iva)
                break
            except Exception:
                pass
        # find the checkbox input
        for i in range(600):
            try:
                checkbox = cells[8].find_element_by_tag_name('input')
                break
            except Exception:
                pass

        # select the invoice if not selected
        sleep(0.2)
        if not checkbox.get_attribute('checked'):
            checkbox.click()
    return len(table_rows)


def has_next_page(driver):
    """Function to know if there is a previous page"""
    paginator_cells = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
        "/tr/td")
    next_button = paginator_cells[-2]
    class_name = next_button.get_attribute('class')
    return 'dsbld' not in class_name


def has_previous_page(driver):
    """Page to know if there is a next page"""
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
    """Function to go to the previous page"""
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
    """Function to go to the next page"""
    paginator_cells = driver.find_elements_by_xpath(
        "//table[@id='j_id148:tblFacturas:paginadorFactura_table']/tbody"
        "/tr/td")
    next_button = paginator_cells[-2]
    next_button.click()


def validate_username(username):
    """Function to validate username"""
    try:
        int(username)
        if len(username) == 10:
            return username
        return False
    except ValueError:
        return False


def validate_year(year):
    """Function to validate the year input"""
    try:
        user_year = int(year)
        current_year = datetime.now().year
        year_limit = current_year - 1
        if user_year >= year_limit and user_year <= current_year:
            return year
        return False
    except ValueError:
        return False


def validate_month(month):
    """Function to validate the month input"""
    month_input = month.upper()
    if month_input in MONTHS:
        return month_input
    return False


if __name__ == '__main__':
    main()
