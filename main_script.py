from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import csv

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Configure and return the Chrome WebDriver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-gpu")
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_element(driver, xpath, timeout=30):
    """Wait for an element to be present and return it."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

def send_messages(phone_numbers, messages, country_code="91"):
    """
    Send messages to multiple WhatsApp numbers.
    
    Args:
        phone_numbers (list): List of phone numbers without country code
        messages (list): List of messages to send
        country_code (str): Country code without + symbol, defaults to "91"
    """
    driver = setup_driver()
    driver.get("https://web.whatsapp.com/")
    
    logger.info("Please scan the QR code to log in.")
    # Wait for user to scan QR code and load WhatsApp
    time.sleep(15)
    
    try:
        for phone_number, message in zip(phone_numbers, messages):
            # Clean and format phone number
            cleaned_number = ''.join(filter(str.isdigit, str(phone_number)))
            formatted_number = f"{country_code}{cleaned_number}"
            chat_url = f"https://web.whatsapp.com/send?phone={formatted_number}"
            
            try:
                driver.get(chat_url)
                logger.info(f"Attempting to send message to {formatted_number}")
                
                # Wait for chat to load and check if number exists
                message_box_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
                input_box = wait_for_element(driver, message_box_xpath)
                
                try:
                    # Clear previous text if any
                    input_box.clear()
                    
                    # Type and send message
                    input_box.send_keys(message)
                    time.sleep(1)  # Small delay before sending
                    input_box.send_keys(Keys.ENTER)
                    
                    logger.info(f"Message sent successfully to {formatted_number}")
                    time.sleep(2)  # Delay between messages
                    
                except Exception as msg_error:
                    logger.error(f"Failed to send message to {formatted_number}. Error: {msg_error}")
                    continue
                
            except Exception as number_error:
                logger.error(f"Failed to connect with {formatted_number}. Error: {number_error}")
                continue
            
            logger.info(f"Completed sending message to {formatted_number}")
            time.sleep(3)  # Delay before next number
            
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    
    finally:
        logger.info("Closing WebDriver")
        driver.quit()

# Example Usage
if __name__ == "__main__":
    try:
        messages = []
        phone_numbers = []
        
        # Open CSV file with proper encoding
        with open("Book1.csv", "r", encoding='utf-8') as file:
            csvFile = csv.reader(file)
            next(csvFile)  # Skip header row only once
            
            for lines in csvFile:
                if len(lines) >= 6:  # Make sure we have all required columns
                    name = lines[0].strip()
                    number = lines[1].strip()
                    sub1 = lines[2].strip()
                    sub2 = lines[3].strip()
                    sub3 = lines[4].strip()
                    sub4 = lines[5].strip()
                    
                    # Create a single continuous message for each person
                     # Using triple quotes for multi-line strings
                    message = f"""This is a test msg for {name} who got following marks
                    sub1 = {sub1}
                    sub2 = {sub2}
                    sub3 = {sub3}
                    sub4 = {sub4}"""
                    messages.append(message)
                    phone_numbers.append(number)
        
        if messages and phone_numbers:
            send_messages(
                phone_numbers=phone_numbers,
                messages=messages,
                country_code="91"  # India country code
            )
        else:
            logger.error("No data found in CSV file")
            
    except FileNotFoundError:
        logger.error("CSV file 'Book1.csv' not found")
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")