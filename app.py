from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def main():
    driver = webdriver.Chrome()
    url = 'https://srienlinea.sri.gob.ec/tuportal-internet/verificaEmail.jspa'
    driver.get(url)
    assert "Login" in driver.title
    username = driver.find_element_by_name("j_username")
    password = driver.find_element_by_name("j_password")
    username.clear()
    password.clear()

    username.send_keys("1721353611")
    password.send_keys("pycon")
    password.send_keys(Keys.RETURN)

    assert "Bienvenido" in driver.page_source
    driver.close()


if __name__ == '__main__':
    main()
