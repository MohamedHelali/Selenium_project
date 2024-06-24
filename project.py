from selenium import webdriver

# The keys Class provide keys in the keyboard
# The By class is used to locate element within the document
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

#BeautifulSoup 
from bs4 import BeautifulSoup

#CSV library for creating the csv file
import csv

# unicodedata library is used to remove (normalize) accents
import unicodedata

"""
        
        Extract all the links to each pc from the product listing pages **
        Extract the technical data for each pc as well as its price and availability ** 
        Store the newly aquired data in a .csv or .excel file ** 
        
"""


PATH =r"C:\Users\Mohamed\Desktop\courses\python_projects\chromedriver.exe"


# Checks if the next page button exists on the web page
def check_next_page(driver):

    soup = BeautifulSoup(driver.page_source,"html.parser")
    hrs=soup.find("ul",{"class":"items pages-items"})
    next_page = hrs.find("li",{"class":"item pages-item-next"})
    if next_page:
        return True
    return False

# allows us the navigate through the products catalogue
def click_next_page(driver):
    next = driver.find_element(By.XPATH,"//a[@class='action  next']")
    next.click()

def remove_accent(name):

    nfkd_form = unicodedata.normalize('NFKD',name)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def format_int(prix):
    numeric_string = u"".join(c for c in prix if c.isdigit())
    return int(numeric_string)

def get_products(driver):

    soup = BeautifulSoup(driver.page_source,"html.parser")
    a_tags = soup.find_all("a",{"class":"product-item-link"},href=True)
    return [a["href"] for a in a_tags]

def get_product_details(driver,link):

    spec_dict={}
    driver.get(link)
    #ref = driver.find_element(By.CLASS_NAME,"value").text
    #price = driver.find_element(By.CLASS_NAME,"price").text
    #print(ref)
    #print(price)
    technical_spec = driver.find_element(By.ID,"tab-label-additional-title")
    technical_spec.click()
    soup = BeautifulSoup(driver.page_source,"html.parser")
    #Locating the spec table
    spec_table = soup.find("table",{"id":"product-attribute-specs-table"})
    #Extracting lines of the table
    lines = spec_table.tbody.find_all('tr')
    for line in lines:
        key = remove_accent(line.find("th").text.strip())
        val = remove_accent(line.find("td").text.strip())
        spec_dict[key] = val
    
    #Extracting the product price
    prix = format_int(soup.find("span",{"class":"price"}).text.strip())
    spec_dict["Prix_DT"] = prix
    return spec_dict  

# determine the output file header based on the various product specs
def file_Header(products):
    filednames=[]
    for product in products:
        for field in list(product.keys()):
            if field not in filednames:
                filednames.append(field)
    return filednames

def productsToFile(products,fieldnames):
    
    with open("products.csv","w") as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)


def main():
    home_page = ""
    products = []
    # Getting
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(PATH,options=options)


    #get the webpage that we want to scrap
    driver.get("https://www.mytek.tn/")
    try:
        menu_bar = driver.find_element(By.ID,"rw-menutop")
        buttons = menu_bar.find_elements(By.CLASS_NAME,"custom-menus")
        for button in buttons:
            if button.text == "Gaming":
                button.click()
                home_page = driver.current_url
                break
    
        # Check the number of product pages in the site
        #print(check_next_page(driver)) 
        
        while True:
            # currently using only one product to test functionality
            pc_links = get_products(driver)
            for pc_link in pc_links:
                products.append(get_product_details(driver,pc_link))
                #break 
            
            #return the catalogue page
            driver.get(home_page)
            # Testing moving through the cataloque pages  
            if check_next_page(driver):
                click_next_page(driver)
                home_page = driver.current_url
            else:
                break
        #identify the header for the output file 
        fieldnames = file_Header(products)

        productsToFile(products,fieldnames)

        driver.quit()

    except NoSuchElementException:
        pass
    except StaleElementReferenceException:
        pass 

    #driver.close() # closes the current tab
    #driver.quit() # closes the web browser

if __name__ == "__main__":
    main()
