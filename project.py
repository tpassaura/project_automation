from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
import time
import sqlite3
from db import crete_data_base
import re
from termcolor import colored, cprint


def main():
    # Define drive 
    crete_data_base()
    global driver
    global actions 

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    actions = ActionChains(driver)
    try:
        new_invoice()
        insert_info()
        
    except:
        sys.exit(Exception)
    driver.close()

# Function to log in on the webpage
def login():
        # find elements of the page
        username = driver.find_element(By.ID, "id_username")
        password = driver.find_element(By.ID, "id_password")
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        
        # Insert login information
        username.send_keys("") #PRIVATE INFORMATION
        password.send_keys('') #PRIVATE INFORMATION
        # Click on the login button
        login_button.click()

# Function to start new invoice entering 
def new_invoice():

    # Get current url
    current_url = driver.current_url
   
    # Check if current page is the invoice loucher page
    if current_url != (""): #PRIVATE INFORMATION
        driver.get("") #PRIVATE INFORMATION
        # Check if website requested login 
        current_url = driver.current_url
        if current_url == "": #PRIVATE INFORMATION
            login()  
        # Click on add new incoice button
        driver.find_element(By.ID, "changelist-btn-add").click()

# Function to check if the invoice was saved correctly 
def check_saved(numero):
    # Get current url 
    current_url = driver.current_url    
    # Define base url for invoice saveds
    base_url = "" #PRIVATE INFORMATION
    pattern = re.escape(base_url) + r'\d+/'
    # check if the current url matchs the url desired 
    match = re.search(pattern, current_url)
    # If saved print that was successful 
    if match:
        cprint(f"Lançada com sucesso: {numero}", "green")
        new_invoice()
    # If not saved print that was a error and enter next invoice
    else:
        cprint(f"Erro ao lançar: {numero}", "red")
        new_invoice()

# Function to insert invoice information on the system 
def insert_info():
    # Conect to data base 
    conexao = sqlite3.connect('dados_notas.db')
    cursor = conexao.execute("SELECT numero FROM notas")
    # Creat list of invoice to insert
    notas = cursor.fetchall()

    # Define invoice informations
    for nota in notas:
        numero = nota[0].strip()
        sede = conexao.execute("SELECT sede FROM notas WHERE numero = ?", nota).fetchone()[0].strip()
        fornecedor = conexao.execute("SELECT fornecedor FROM notas WHERE numero = ?", nota).fetchone()[0].strip()
        emissao = conexao.execute("SELECT emissao FROM notas WHERE numero = ?", nota).fetchone()[0].strip()
        especie = conexao.execute("SELECT especie FROM notas WHERE numero = ?", nota).fetchone()[0].strip()
        
        # Insert the incoive information on the system 
        insert_invoice_info(sede, fornecedor, emissao, numero, especie)

        # Get invoice list of products
        products = conexao.execute("SELECT id FROM products WHERE numero = ?", nota).fetchall()

        # Define the product information to insert on the system
        for index, products in enumerate(products):
            produto = conexao.execute("SELECT produto FROM products WHERE id = ?", products).fetchone()[0].strip()
            valor = conexao.execute("SELECT valor FROM products WHERE id = ?", products).fetchone()[0].strip()
            contrato = conexao.execute("SELECT contrato FROM products WHERE id = ?", products).fetchone()[0].strip()
            cc = conexao.execute("SELECT cc FROM products WHERE id = ?", products).fetchone()[0].strip()
            movimento = conexao.execute("SELECT movimento FROM products WHERE id = ?", products).fetchone()[0].strip()

            # Insert prooduct information on the system
            insert_product_info(index, produto, valor, contrato, cc, movimento)
        # Save invoice and check if was saved successfuly 
        driver.find_element(By.ID, "changeform-save").click()  
        check_saved(numero)

# Function to insert invoice information on the system
def insert_invoice_info(sede, fornecedor, emissao, numero, especie):
    # Insert sede information
    if sede != "": #PRIVATE INFORMATION
        # Find the remove sede button and click
        driver.find_element(By.ID, "id_sede-deck").find_element(By.CLASS_NAME, "remove").click()
        # Write sede
        insert_input("id_sede-autocomplete", sede)

    #insert supplier information
    insert_input("id_fornecedor-autocomplete", fornecedor)

    #insert issue information
    driver.find_element(By.ID, "id_data_emissao").clear()
    driver.find_element(By.ID, "id_data_emissao").send_keys(emissao, Keys.ESCAPE)

    #insert invoice number information
    insert_input("id_numero", numero)

    # Insert invoice series information
    insert_input("id_subserie", "0")

    # insert invoice type information
    Select(driver.find_element(By.ID, "id_serie")).select_by_value(especie)

    # Expand "fechamento" tab
    driver.find_element(By.XPATH, '//*[@id="content"]/form/div[1]/div[2]/div/fieldset[6]/legend/a/div/i').click()

    # Insert invoice project information
    insert_input("id_contrato-autocomplete", "OPERAÇÕES APOIO")

    # Check "conferido" button
    driver.find_element(By.ID, "id_conferido").click()

# Function to insert invoice products
def insert_product_info(index, produto, valor, contrato, cc, movimento):
        # Add new product if its not the frist of the invoice
        if index != 0:
            driver.find_element(By.XPATH, "//a[contains(text(), 'Adicionar Produto')]").click()
        # Insert product name
        insert_input(f"id_produtonfentrada_set-{index}-produto-autocomplete", produto)
        # Insert product stock
        insert_input( f"id_produtonfentrada_set-{index}-local-autocomplete", "SERVICOS")
        # Insert product amount 
        insert_input( f"id_produtonfentrada_set-{index}-qtde_compra", "1")
        # Insert product price
        insert_input( f"id_produtonfentrada_set-{index}-valor_unitario", valor)
        # Insert product order number
        insert_input( f"id_produtonfentrada_set-{index}-order", index+1)
        
        # Expand product informations tab
        driver.find_element(By.XPATH, '//*[@id="panel-produtonfentrada_set"]/div/div[1]/div[2]/div/fieldset[2]/legend/a/div/i').click()
        # Insert product project
        insert_input( f"id_produtonfentrada_set-{index}-contrato-autocomplete", contrato)
        # Insert product cost center
        insert_input( f"id_produtonfentrada_set-{index}-centro_custo-autocomplete", cc)
        # insert product buy entry type
        insert_input( f"id_produtonfentrada_set-{index}-tipo_movimento-autocomplete", movimento)

# Function to insert a information on a HTML tag of the system
def insert_input(tag, info):
     
    # Find HTML tag
    input_field = driver.find_element(By.ID, tag)
    # Insert information on tag field
    input_field.send_keys(info)
    # Check if system find the informaiton 
    if "autocomplete" in tag:
        # Wait the system to find the information
        wait_visible()
        # Click on the fild and press "TAB" to confirm
        input_field.click()
        time.sleep(1)
        pyautogui.press('tab')

# Fucntion to wait the system to return that the input was found 
def wait_visible():
    wait = WebDriverWait(driver, 10)  # Maximum wait time of 10 seconds
    # Wait and find the element list  
    wait.until(EC.presence_of_element_located((By.CLASS_NAME ,"autocomplete-light-widget")))

# Run the program 
if __name__ == "__main__":
    main()