from playwright.sync_api import sync_playwright
import os, pathlib
from selenium.webdriver.common.by import By


def save_as_pdf(file_path, output_path):
    filePath = os.path.abspath(file_path)
    fileUrl = pathlib.Path(filePath).as_uri()
    
    outputFilePath = os.path.abspath(output_path)
    print(outputFilePath)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(fileUrl)
        page.emulate_media(media="screen")
        page.pdf(path=outputFilePath)
        browser.close()



def safe_driver_get(driver, url="https://www.dec.fazenda.sp.gov.br/DEC/UCServicosDisponiveis/ExibeServicosDisponiveis.aspx"):
    driver.get(url)
    status = driver.execute_script("return window.performance.getEntries()[0].responseStatus")
    if str(status)[0] != "2":
        print("Site is down")
        raise SystemExit
    return driver



def click_panel_in_other_thread(driver):
    driver.find_element(By.ID, "ConteudoPagina_Panel1").click()
