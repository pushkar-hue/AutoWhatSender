from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, 
    QLabel, QLineEdit, QTextEdit, QFileDialog, QWidget
)
from PyQt5.QtCore import Qt
import sys
import threading  # To keep the UI responsive while sending messages
import csv
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class WhatsAppSenderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WhatsApp Message Sender")
        self.setGeometry(100, 100, 600, 400)
        self.setup_ui()

    def setup_ui(self):
        # Layout
        layout = QVBoxLayout()

        # CSV File Picker
        self.csv_label = QLabel("Select CSV File:")
        layout.addWidget(self.csv_label)

        self.csv_file_path = QLineEdit()
        self.csv_file_path.setPlaceholderText("Click 'Browse' to select a CSV file")
        self.csv_file_path.setReadOnly(True)
        layout.addWidget(self.csv_file_path)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_csv_file)
        layout.addWidget(self.browse_button)

        # Country Code Input
        self.country_code_label = QLabel("Country Code:")
        layout.addWidget(self.country_code_label)

        self.country_code_input = QLineEdit("91")  # Default to India
        self.country_code_input.setPlaceholderText("Enter country code")
        layout.addWidget(self.country_code_input)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        # Send Button
        self.send_button = QPushButton("Send Messages")
        self.send_button.clicked.connect(self.start_sending_messages)
        layout.addWidget(self.send_button)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def browse_csv_file(self):
        # Open file dialog to select a CSV file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.csv_file_path.setText(file_path)

    def start_sending_messages(self):
        # Get inputs
        csv_file = self.csv_file_path.text()
        country_code = self.country_code_input.text().strip()

        if not csv_file:
            self.log_output.append("Please select a CSV file.")
            return

        if not country_code.isdigit():
            self.log_output.append("Invalid country code.")
            return

        # Start a new thread to keep the UI responsive
        threading.Thread(target=self.send_messages, args=(csv_file, country_code), daemon=True).start()

    def send_messages(self, csv_file, country_code):
        try:
            # Read data from CSV
            phone_numbers = []
            messages = []
            with open(csv_file, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                
                # Check if the first row is a header (Optional)
                # If you're certain your CSV always has headers, leave `next(csv_reader)` uncommented.
                # If your CSV doesn't have headers, comment out the next line:
                next(csv_reader)  # Skip header row if it exists

                for line in csv_reader:
                    if len(line) >= 6:
                        name, number, sub1, sub2, sub3, sub4 = line[:6]
                        message = f"""This is a test msg for {name} who got following marks:
                        sub1 = {sub1}
                        sub2 = {sub2}
                        sub3 = {sub3}
                        sub4 = {sub4}"""
                        phone_numbers.append(number.strip())
                        messages.append(message.strip())


            if not phone_numbers or not messages:
                self.log_output.append("No valid data in CSV file.")
                return

            self.log_output.append("Starting to send messages...")
            self._selenium_send_messages(phone_numbers, messages, country_code)
        except Exception as e:
            self.log_output.append(f"Error: {e}")

    def _selenium_send_messages(self, phone_numbers, messages, country_code):
        def setup_driver():
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-gpu")
            service = Service()
            return webdriver.Chrome(service=service, options=chrome_options)

        driver = setup_driver()
        driver.get("https://web.whatsapp.com/")
        self.log_output.append("Please scan the QR code to log in.")
        time.sleep(15)  # Wait for user to scan QR code

        for number, message in zip(phone_numbers, messages):
            try:
                url = f"https://web.whatsapp.com/send?phone={country_code}{number}"
                driver.get(url)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                ).send_keys(message + Keys.ENTER)
                self.log_output.append(f"Message sent to {number}")
                time.sleep(2)
            except Exception as e:
                self.log_output.append(f"Failed to send message to {number}: {e}")
                continue

        self.log_output.append("Completed sending messages.")
        driver.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhatsAppSenderApp()
    window.show()
    sys.exit(app.exec_())
