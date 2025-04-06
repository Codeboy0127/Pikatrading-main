from playwright.sync_api import sync_playwright
import time
import os




def fill_form():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless= True)  # Set headless=True for production
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to the website
        page.goto('https://thailandpost-oa.com/')

        try:
            # Wait for the form to be visible
            page.wait_for_selector('form', timeout=10000)
            
            # Fill in the form fields
            # Note: Replace these selectors and values with the actual ones from the website
            # These are example selectors - you'll need to update them based on the actual form
            page.fill('[name="tid"]', 'raud_boss@hotmail.com')
            page.fill('[name="tpasswd"]', 'themafia')
            page.click('button[type="submit"]')
            print('after submit line')

            page.wait_for_selector('form', timeout=10000)
            page.fill('input[placeholder="ชื่อ นามสกุล"]', 'John Doe Nal Trump')
            page.fill('textarea[placeholder="ที่อยู่จัดส่ง"]', '591/7 แยก17 แขวง คลองเจ้าคุณสิงห์ เขต วังทองหลาง กรุงเทพมหานคร 10310')
            page.fill('input[placeholder="เบอร์โทรศัพท์ติดต่อ"]', '0235363327')
            time.sleep(2)
            page.click('.btn-reciever-confirm')
            print('after submit form')
            time.sleep(2)
            page.click('input[type="radio"][value="10x10"]')
            page.click('.swal2-confirm')
            print('after select paper type')
            page.locator('h2#swal2-title:text("สร้างใบจ่าหน้าสำเร็จ")').wait_for()

           
            
            with page.expect_download() as download_info:
                page.get_by_text("ดาวน์โหลด").click()
            # Wait for the download event
            download = download_info.value

            # Get the URL of the downloaded PDF
            pdf_url = download.url
            #print(f"PDF URL: {pdf_url}")

            # Get the originating page URL
            #originating_page_url = download.page.url
            #print(f"Originating Page URL: {originating_page_url}")
                    
            #page.get_by_text("ดาวน์โหลด").click() 
            
            # Start waiting for the download
            
            print("Form filled successfully!")
            return pdf_url
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        finally:
            # Close the browser
            browser.close()

url = fill_form() 
print(f"Generated URL: {url}") 

