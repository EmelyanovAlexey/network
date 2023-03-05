import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import csv

# ОПИСАНИЕ
# Парсер сайт DNS, прогрмма совершает аторизацию и 
# после совершает проход по каталогу процессоров и собирает информацию о продуктах. 
# В конце сохраняет иформацию в products.csv

class ProductClass:
    def __init__(self, name, price, description, link):
        self.name = name
        self.price = price
        self.description = description
        self.link = link

    def __repr__(self):
        return f"<name:{self.name} price:{self.price} link:{self.link} description:{self.description}>"

# Авторизация
def commandAuth(driver) -> bool:
    print("Authorization ......")
    try:
        driver.find_element(By.CLASS_NAME, "user-page__login-btn").click()
        time.sleep(1)
        driver.find_element(
            By.CLASS_NAME, "block-other-login-methods__password-button").click()
        time.sleep(0.5)
        inputLogin = driver.find_element(
            By.CLASS_NAME, "form-entry-with-password__input")
        inputLogin.find_element(
            By.CLASS_NAME, "base-ui-input-row__input").send_keys("89513923452")
        inputPassword = driver.find_element(
            By.CLASS_NAME, "form-entry-with-password__password")
        inputPassword.find_element(
            By.CLASS_NAME, "base-ui-input-row__input").send_keys("Ae97980525")
        time.sleep(1)
        driver.find_element(By.CLASS_NAME, "base-main-button").click()
        print('Authorization successfully')
        return True
    except Ellipsis as _ex:
        print(_ex)
        return False

# просмотр каталога
def commandSeeCatalog(driver) -> list[ProductClass]:
    print("See Catalog .....")
    # search amount page
    link_last_page = driver.find_element(
        By.CLASS_NAME, "pagination-widget__page-link_last").get_attribute('href')
    link_last_page_arr = link_last_page.split("?p=")

    # list products
    productList = []

    if (len(link_last_page_arr) > 1):
        for index_page in range(int(link_last_page_arr[1])):
            products = driver.find_elements(By.CLASS_NAME, "catalog-product")

            for product in products:
                time.sleep(0.1)
                productScroll = product.find_element(
                    By.CLASS_NAME, "catalog-product__name")
                ActionChains(driver)\
                    .scroll_to_element(productScroll)\
                    .perform()
                link = product.find_element(
                    By.CLASS_NAME, "catalog-product__name").get_attribute('href')
                price = product.find_element(
                    By.CLASS_NAME, "product-buy__price").text
                name = product.find_element(
                    By.CLASS_NAME, "catalog-product__name span").text
                productList.append(ProductClass(name, price, "", link))
                print(name + " " + price + " " + link + " \n")

            driver.find_element(
                By.CLASS_NAME, "pagination-widget__page-link_next").click()
            time.sleep(1.5)
        print('Catalog successfully')
        return productList

# сбор описания
def commandSeeProducts(driver, productList: list[ProductClass]) -> list[ProductClass]:
    print("Get Description .....")
    for product in productList:
        description = ""
        driver.get(url=product.link)
        time.sleep(1.5)
        
        teg_text_description = driver.find_element(
            By.CLASS_NAME, "product-card-description-text p")
        
        description = teg_text_description.text
   
        description = teg_text_description.text
        product.description = description
    return productList

# сохраняем полученные данные
def saveProducts(productList):
    print("сохранить")
    # reader_object = csv.reader(file, delimiter = ",")
    with open('products.csv', mode="w", encoding='utf-8') as csvfile:
        file_writer = csv.writer(
            csvfile, delimiter=",", lineterminator="\r")
        file_writer.writerow(['name', 'price', 'description'])

        for product_item in productList:
            file_writer.writerow(
                [product_item.name, product_item.price, product_item.description])


# основная функция бор информации (авторизация + продукт)
def get_source_html(urlAuth, urlCatalog):
    options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')

    driver = webdriver.Chrome(
        executable_path="./driver/chromedriver.exe", options=options)
    driver.maximize_window()

    try:
        driver.get(url=urlAuth)
        if (commandAuth(driver)):
            driver.get(url=urlCatalog)
            time.sleep(3)
            productList = commandSeeCatalog(driver)
            commandSeeProducts(driver, productList)
            saveProducts(productList)

    except Ellipsis as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


def main():
    get_source_html(urlAuth="https://www.dns-shop.ru/profile/menu/",
                    urlCatalog="https://www.dns-shop.ru/catalog/17a899cd16404e77/processory/")


# Main
if __name__ == "__main__":
    main()
