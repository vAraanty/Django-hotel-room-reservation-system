from msedge.selenium_tools import Edge, EdgeOptions
from time import sleep


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
    
    driver.get("http://127.0.0.1:8000/accounts/signup/")
    
    driver.execute_script('window.open("")')
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://randus.org/uk")

    wait_for_clickable(driver, '[class="btn btn-primary loadUser"]')
    sleep(5)
    while True:
        full_name = driver.find_element_by_css_selector('[class="h4 card-title mb-2"]').get_attribute('textContent')
        phone_number = driver.find_element_by_css_selector('body > section.section.section-lg.pt-0.pb-5 > div > div > div:nth-child(1) > div > div.card-body > div > div.row.text-left > div > ul > li:nth-child(3) > div > div > div').get_attribute('textContent')
        login = driver.find_element_by_css_selector('body > section.section.section-lg.pt-0.pb-5 > div > div > div:nth-child(1) > div > div.card-body > div > div.row.text-left > div > ul > li:nth-child(5) > div > div > div').get_attribute('textContent')
        email = login + '@amazingmail.xyz'
        
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element_by_css_selector('[name="name"]').send_keys(full_name.split(' ')[1])
        driver.find_element_by_css_selector('[name="surname"]').send_keys(full_name.split(' ')[0])
        driver.find_element_by_css_selector('[name="login"]').send_keys(login)
        driver.find_element_by_css_selector('[name="email"]').send_keys(email)
        driver.find_element_by_css_selector('[name="phone_number"]').send_keys(phone_number)
        driver.find_element_by_css_selector('[name="password1"]').send_keys('12345678')
        driver.find_element_by_css_selector('[name="password2"]').send_keys('12345678')
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
    
    



if __name__ == '__main__':
    main()
