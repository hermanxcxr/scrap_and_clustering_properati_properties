from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys

import time
import pandas as pd
import re

WEBSITE = "https://www.properati.com.co/"
PAGES_LIMIT = 21

def features(driver,delay,feature):
    e_gen_size_counter = driver.find_elements_by_xpath('//div[starts-with(@class,"StyledTypologyBlock")]/div[starts-with(@class,"StyledTypologyItem")]')
        
    for counter,e_element in enumerate(e_gen_size_counter, start=1):
        e_area_text = e_element.find_element_by_xpath('//div[starts-with(@class,"StyledTypologyBlock")]/div[starts-with(@class,"StyledTypologyItem")][{}]/div[2]/span[2]'.format(counter))
        area_text = e_area_text.text
        if area_text == feature:
            e_gen_size = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[starts-with(@class,"StyledTypologyBlock")]/div[starts-with(@class,"StyledTypologyItem")][{}]/div[2]/span[1]'.format(counter))))
            break
    size = e_gen_size.text
    v_size = float(re.search('\d+',size).group(0))

    return size,v_size

def property_scan(driver,delay,properties,count,link):
    driver.get(link)
    
    driver.execute_script("window.scrollBy(0,200)")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0,400)")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0,500)")
    time.sleep(1)
    
    try:
        e_gen_name = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//h1[starts-with(@class,"StyledTitle")]')))
        p_name = e_gen_name.text
        v_name = re.search('[A-Z][a-z]+',p_name).group(0)
    except:
        p_name = None
        v_name = None

    try:
        e_gen_price = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//span[starts-with(@class,"StyledPrice")]')))
        price = e_gen_price.text
        v_price = price.replace("$","").replace(" ","").replace(".","")
        v_price = float(v_price)
    except:
        price = None
        v_price = None

    try:
        size, v_size = features(driver,delay,"Totales")
    except:
        size = None
        v_size = None
    
    try:    
        rooms, v_rooms = features(driver,delay,"Habitaciones")
    except:
        try:    
            rooms, v_rooms = features(driver,delay,"Ambientes")
        except:
            rooms = None
            v_rooms = None

    try:    
        baths, v_baths = features(driver,delay,"Baños")
    except:
        try:    
            baths, v_baths = features(driver,delay,"Baño")
        except:
            baths = None
            v_baths = None

    try:
        see_more_button = driver.find_element_by_xpath('//div[starts-with(@class,"StyledButtonViewMore")]/button')
        see_more_button.click()
    except:
        pass

    try:
        e_gen_description = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[starts-with(@class,"StyledCollapsible")]/div[@class="child-wrapper"]/div')))
    except:
        #driver.execute_script("window.scrollBy(0,-600)")
        #e_gen_description = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[starts-with(@class,"StyledCollapsible")]/div[@class="child-wrapper"]/div')))
        pass
    
    try:
        description = e_gen_description.get_attribute("outerHTML")
    except:
        description = None

    try:        
        g_coord = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[@class="gm-style"]/div/div/a')))
    except: 
        '''
        try:
            driver.execute_script("window.scrollBy(0,-800)")
            g_coord = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[@class="gm-style"]/div/div/a')))
            print('-800')
            try:
                driver.execute_script("window.scrollBy(0,1000)")
                g_coord = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[@class="gm-style"]/div/div/a')))
                print('1000')
            except:
                g_coord = None
        except:
            g_coord = None
        '''
        g_coord = None
    
    try:
        maps_url = str(g_coord.get_attribute("href"))
        coordinates = re.findall('-?\d?\d.[0-9]{1,6}',maps_url)        
        v_coordinate_x = float(coordinates[0])
        v_coordinate_y = float(coordinates[1])
    except:
        coordinates = None
        v_coordinate_x = None
        v_coordinate_y = None
    print(coordinates)
    
    #['url','coordinates','v_coordinates','type','v_type','price','v_price','size','v_size','description']
    properties.loc[count] = [link,coordinates,v_coordinate_x,v_coordinate_y,p_name,v_name,price,v_price,size,v_size,v_rooms,v_baths,description]
    
    return properties

def links(driver):
    temp_property_links = []
    time.sleep(2)
    property_link_elements = driver.find_elements_by_xpath('//div[starts-with(@class,"StyledCard")]/a[@target="_blank"]')
    #property_link_elements = WebDriverWait(driver,5).until(EC.presence_of_all_elements_located((By.XPATH,'//select[@id="property-type"]')))

    driver.execute_script("window.scrollBy(0,200)")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0,400)")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0,500)")
    time.sleep(1)

    for count,link in enumerate(property_link_elements):
        if count%2 != 0: 
            link = link.get_attribute('href')
            temp_property_links.append(link)
    
    return temp_property_links

def run(city):
    
    #Ejecución en primer plano
    options = webdriver.ChromeOptions() #Instanciar driver
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
    '''
    #Ejecución en segundo plano
    #window_size = "1920,1080"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size={}".format(window_size))
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
    '''
    delay = 5
    driver.get(WEBSITE)
    
    #Búsqueda
    property_type = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//select[@id="property-type"]')))
    property_type.click()
    property_type_option = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//select[@id="property-type"]/option[2]')))
    property_type_option.click()
    text_case = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//input[@id="search-places"]')))
    text_case.clear()
    text_case.send_keys(city)
    time.sleep(1.25)
    first_option = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[@class="text-suggestion text-selected"]/span')))
    first_option.click()
    search_button = driver.find_element_by_xpath('//button[@class="btn btn-primary btn-large"]')
    search_button.click()

    #Obtención de las url de propiedades
    property_links = []
    num_pages = 0
    button = True
  
    while(button == True and num_pages < PAGES_LIMIT):    
        try:
            temp_property_links = links(driver)
            property_links += temp_property_links
            num_pages += 1
            try:
                next_button = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[@class="pager"]/a[contains(@class,"pager-next") and contains(@class,"disabled")]')))
                time.sleep(5)
                print("primer try")
                button = False                
            except:
                next_button = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH,'//div[@class="pager"]/a[contains(@class,"pager-next")]')))
                next_button.click()                                
        except:
            driver.refresh()

    print(len(property_links))
    '''
    with open('links.txt','w',encoding='utf-8') as f:
        f.write(str(property_links))
    f.close()
    '''
    properties = pd.DataFrame(
            columns=[
                'url','coordinates','v_coordinate_x','v_coordinate_y','type','v_type','price','v_price','size','v_size','v_rooms','v_baths','description'
                ])
    for count,link in enumerate(property_links):
        properties = property_scan(driver,delay,properties,count,link)

    properties.to_excel('outputs/propiedades.xlsx')
  
if __name__ == '__main__' :
    city = str(input("Ciudad de búsqueda: "))
    run(city)