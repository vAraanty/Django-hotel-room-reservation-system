from msedge.selenium_tools import Edge, EdgeOptions
from time import sleep
import datetime


options = EdgeOptions()
options.use_chromium = True
# options.add_extension(f'{path().absolute()}\\steamdb.crx')
options.add_argument("--log-level=3")
options.add_argument("--silent")


def wait_for_clickable(driver, selector):
    while True:
        results = driver.find_elements_by_css_selector(selector)
        try:
            results[0].click()
        except:
            sleep(0.2)
        else:
            break


def main():
    driver = Edge(executable_path=r'D:\geckodriver\msedgedriver.exe', options=options)
    counter = 0
    date = datetime.date(2021, 6, 27)
    
    driver.get("http://127.0.0.1:8000/book/")
    
    driver.execute_script('window.open("")')
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://randus.org/uk")

    wait_for_clickable(driver, '[class="btn btn-primary loadUser"]')
    sleep(5)
    while True:
        if counter == 3:
            counter = 0
            date += datetime.timedelta(days=3)
        full_name = driver.find_element_by_css_selector('[class="h4 card-title mb-2"]').get_attribute('textContent')
        phone_number = driver.find_element_by_css_selector('body > section.section.section-lg.pt-0.pb-5 > div > div > div:nth-child(1) > div > div.card-body > div > div.row.text-left > div > ul > li:nth-child(3) > div > div > div').get_attribute('textContent')
        login = driver.find_element_by_css_selector('body > section.section.section-lg.pt-0.pb-5 > div > div > div:nth-child(1) > div > div.card-body > div > div.row.text-left > div > ul > li:nth-child(5) > div > div > div').get_attribute('textContent')
        email = login + '@amazingmail.xyz'
        
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element_by_css_selector('[name="name"]').send_keys(full_name.split(' ')[1])
        driver.find_element_by_css_selector('[name="surname"]').send_keys(full_name.split(' ')[0])
        driver.find_element_by_css_selector('[name="email"]').send_keys(email)
        driver.find_element_by_css_selector('[name="phone_number"]').send_keys(phone_number)
        driver.execute_script(f'document.querySelector("#id_arrival_date").value = "{str(date)}";')
        driver.execute_script(f'document.querySelector("#id_departure_date").value = "{str(date + datetime.timedelta(days=3))}";')
        driver.execute_script(f'document.querySelector("#id_room").value = {counter + 1};')
        sleep(0.5)
        driver.find_element_by_css_selector('[type="submit"]').click()
        sleep(1)
        
        driver.switch_to.window(driver.window_handles[1])
        driver.find_element_by_css_selector('body > section.section.section-lg.pt-0.pb-5 > div > div > div:nth-child(1) > div > div.card-body > div > div.card-footer > div > div:nth-child(1) > button').click()
        while True:
            new_phone = driver.find_element_by_css_selector('body > section.section.section-lg.pt-0.pb-5 > div > div > div:nth-child(1) > div > div.card-body > div > div.row.text-left > div > ul > li:nth-child(3) > div > div > div').get_attribute('textContent')    
            if new_phone == phone_number:
                sleep(1)
            else:
                break
        
        counter += 1
    



if __name__ == '__main__':
    main()
