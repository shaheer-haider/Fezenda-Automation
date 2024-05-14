import json
from threading import Thread
from time import sleep
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
import math
from io import StringIO
from selenium.webdriver.support import expected_conditions as EC

from utils import safe_driver_get, save_as_pdf, click_panel_in_other_thread
from constants import *

        
pyautogui.FAILSAFE = False

def process_loja(driver, loja_cnpj):

    driver = safe_driver_get(driver, "https://www.dec.fazenda.sp.gov.br/DEC/UCServicosDisponiveis/ExibeServicosDisponiveis.aspx")

    sleep(0.5)
    
    # open the popup
    ir_para_a_caixa_postal = driver.find_element(By.XPATH, "/html/body/form/table/tbody/tr[6]/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/div/table/tbody/tr/td[2]/div/div[4]/div[2]/div/div/table/tbody/tr[1]/td/div[2]/input")
    ir_para_a_caixa_postal.click()

    sleep(0.2)

    # enter and submit the data in popup
    driver.find_element(By.NAME, "ctl00$ConteudoPagina$tabContainerServicos$tabResponsavel$txtEstabelecimentoCaixaPostalSocio").send_keys(loja_cnpj['CNPJ'])
    driver.find_element(
        By.ID,
        "ConteudoPagina_tabContainerServicos_tabResponsavel_Panel6"
        ).find_element(
            By.ID,
            "ConteudoPagina_tabContainerServicos_tabResponsavel_btnBuscarPorEstabelecimentoSocio"
            ).click()


    driver.find_element(By.LINK_TEXT, "Data de Envio").click()
    driver.find_element(By.LINK_TEXT, "Data de Envio").click()


    driver.find_element(By.ID, "ConteudoPagina_tabContainerCaixaPostal_tabAtivas_ucItensAtivos_ucToolbarPeriodos_btnTodos").click()

    sleep(0.5)

    # get total items and pages
    total_items_el_text = driver.find_element(By.ID, total_items_para_id).get_attribute("innerText")
    total_items = total_items_el_text.split(": ")[-1]
    total_pages = math.ceil(int(total_items) / 7)

    filtered_data = []

    for page in range(0, total_pages - 1):
        # get data from table
        tables = pd.read_html(StringIO(str(driver.find_element(By.ID, table_container_id).get_attribute("innerHTML"))))
        table = tables[0]
        table_data = table.to_dict(orient="records")

        for data in table_data:
            parsed_data = {
                "DataEnvio": data["Data de Envio"],
                "Aviso": data["Identificação"],
                "Type": "",
                "Assunto": data["Assunto"]
            }

            if parsed_data["Assunto"] != text_to_find_on_last_run_null:
                continue
            
            filtered_data.append(data)
            
            try:
                link_text = parsed_data["Aviso"]
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, link_text))
                )
                element.click()
            except:
                sleep(0.5)
                driver.find_element(By.LINK_TEXT, parsed_data["Aviso"]).click()
                    
            # Wait for the popup window to appear
            _ = WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            # Get handles of all the windows
            all_handles = driver.window_handles

            # Switch focus to the popup window
            for handle in all_handles:
                if handle != driver.current_window_handle:
                    driver.switch_to.window(handle)
                    break
            
            
            complemento_sentense = driver.find_element(By.ID, "lblComplemento").get_attribute("innerHTML")
            try:
                entry_type = complemento_sentense.split("- Arquivo ")[1]
            except:
                continue

            parsed_data["Type"] = entry_type
            
            parsed_data["FilePath"] = pdf_storage_path + "+".join([
                f"\\Loja+{loja_cnpj['CNPJ']}",
                f"{str(parsed_data['DataEnvio']).replace('/', '-').replace(' ', '_').replace(':', '-')}",
                f"{parsed_data['Type']}.pdf"
            ])
            
            html_content = driver.page_source

            # Convert HTML to PDF 
            try:
                open("temp.html", "w").write(html_content)
                save_as_pdf("temp.html", parsed_data["FilePath"])
            except Exception as e:
                print(e)
            print(parsed_data)

            driver.switch_to.window(driver.window_handles[0])


        # go to the next page
        pages_href_container = driver.find_element(By.ID, pagination_container_id)
        pagination_urls = pages_href_container.find_elements(By.TAG_NAME, "a")
        print(pagination_urls[-2].get_attribute("innerHTML"))
        pagination_urls[-2].click()
        sleep(0.1)
        status = driver.execute_script("return window.performance.getEntries()[0].responseStatus")
        if str(status)[0] != "2":
            raise NoSuchElementException

    return driver, filtered_data


def run_bot():
    print("Run bot")
    try:

        open("status.txt", "w").write("running")
        driver = webdriver.Chrome()
        driver.get("https://www.dec.fazenda.sp.gov.br/DEC/UCLogin/login.aspx")
        status = driver.execute_script("return window.performance.getEntries()[0].responseStatus")

        if str(status)[0] != "2":
            exit()

        # click certificate button(image)
        Thread(target=click_panel_in_other_thread, args=[driver]).start()
        sleep(1)
        pyautogui.press("enter")

        # if it runs into an error
        if driver.current_url == "https://www.dec.fazenda.sp.gov.br/DEC/Comum/Erro.aspx":
            # click voltar
            driver.find_element(By.NAME, "ctl00$ConteudoPagina$btnVoltar").click()
            
            # youll be redirected to a new page
            # click certificate button(image)            
            Thread(target=click_panel_in_other_thread, args=[driver]).start()
            sleep(1)
            pyautogui.press("enter")
            # Switch back to the main page
            driver.switch_to.default_content()


        dec_loja_cnpj = pd.read_excel(source_excel_file_path).to_dict(orient="records")

        all_data = []
        
        all_cnpjs = list(map(lambda x: x["CNPJ"], dec_loja_cnpj))

        for index, loja_cnpj in list(zip(range(0, len(all_cnpjs)), dec_loja_cnpj)):

            storeFile = open("store.json", "r")
            storeData = json.loads(storeFile.read())

            if(index > all_cnpjs.index(storeData["last_cnpj"])):
                driver, processed_loja = process_loja(driver, loja_cnpj)
                all_data += processed_loja

                storeData["last_cnpj"] = loja_cnpj["CNPJ"]
                
                storeFile = open("store.json", "w")
                storeFile.write(json.dumps(storeData))

    except NoSuchElementException as e:
        open("status.txt", "w").write("stopped")
    except Exception as e:
        open("status.txt", "w").write("stopped due to unknown error. check logs")
        # open("logs.txt", "a").write(e.__str__())
        raise e        
     

if __name__ == "__main__":
    run_bot()