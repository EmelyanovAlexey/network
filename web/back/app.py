from flask import Flask, render_template, url_for, request, redirect
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import csv
import pandas as pd
import numpy as np

# переменные
errorPage = ''
productList = []

# классы


class ProductClass:
    def __init__(self, name, price, description, link):
        self.name = name
        self.price = price
        self.description = description
        self.link = link

    def __repr__(self):
        return f"<name:{self.name} price:{self.price} link:{self.link} description:{self.description}>"

# функции
# просмотр каталога


def get_production_catalog(driver) -> list[ProductClass]:
    print("See Catalog .....")
    productList = []
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
    time.sleep(1.5)
    return productList

# сбор описания


def get_description(driver, productList: list[ProductClass]) -> list[ProductClass]:
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


def save_products(productList):
    print("сохранить")
    with open('back/static/data/products.csv', mode="w", encoding='utf-8') as csvfile:
        file_writer = csv.writer(
            csvfile, delimiter="||", lineterminator="\r")
        file_writer.writerow(['name', 'price', 'description'])
        for product_item in productList:
            file_writer.writerow(
                [product_item.name, product_item.price, product_item.description])


def parser_html(urlCatalog):
    options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')

    driver = webdriver.Chrome(
        executable_path="./driver/chromedriver.exe", options=options)
    driver.maximize_window()

    try:
        driver.get(url=urlCatalog)
        time.sleep(3)
        productList = get_production_catalog(driver)
        get_description(driver, productList)
        save_products(productList)
        print('успешно')

    except Ellipsis as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


# контроллеры
app = Flask(__name__)


@app.route('/')
def index():
    return render_template("./pages/index.html")


@app.route('/error')
def error():
    print(errorPage)
    error = "У меня лапки, моя делать бэк мало, ну или у вас лапки и ссылка не правильная :("
    return render_template("./pages/error.html", error=error)


@app.route('/success')
def success():
    with open('back/static/data/products.csv', mode="r", encoding='utf-8') as csvfile:
        data = list(csv.reader(csvfile, delimiter='\t'))
    
    return render_template("./pages/success.html", productList=data)


@app.route('/form', methods=['POST', 'GET'])
def form():
    if request.method == 'POST':
        try:
            # 'https://www.dns-shop.ru/catalog/17a899cd16404e77/processory/'
            url = request.form['url']
            parser_html(url)
            return redirect('/success')
        except:
            return redirect('/error')
    else:
        return render_template("./pages/form.html")


if __name__ == "__main__":
    app.run(debug=True)
