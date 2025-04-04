import re, bs4, os,  base64, random, string
import numpy as np
import pandas as pd
from jinja2 import Template
from typing import Dict
from openpyxl import Workbook


def generate_password(length=6):
    """Generate a random password with letters, digits, and symbols."""
    chars = ""
    while chars == "" :
        chars = string.ascii_letters + string.digits 

    return ''.join(random.choice(chars) for _ in range(length))


def bs_html(file_path, password, subfolder):
    """Append JavaScript function to prompt for password"""
    with open(file_path, "r") as file:
        html_content = file.read()
    
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    pwd_script = soup.new_tag("script")
    pwd_script.string = """
        function checkPassword() {
        var correctPassword = "%s";
        var auth = false;

        while (!auth) {
            var password = prompt("Please enter the password to view this page:", "");

            if (password == null){
            window.location = "about:blank";
            return false;
            }

            if (password === correctPassword) {
            auth = true;
            return true;
            } else {
            alert("Incorrect Password. Please try again");
            }
        }
        }

        if (!checkPassword()) {
            document.write("Wrong Password"); // Clear page if password is incorrect
        }
    """% password
    
    soup.head.append(pwd_script)

    # Save the modified HTML file
    locked_file_path = os.path.join(subfolder, os.path.basename(file_path))
    with open(locked_file_path, "w") as locked_file:
        locked_file.write(str(soup))
    
    return locked_file_path, password



def process_html_files(directory=".", subfolder='pwd_html_files', log_file="password_log.xlsx"):
    """Find all HTML files, encrypt them, and log passwords in an Excel file."""
    html_files = [f for f in os.listdir(os.path.join(directory, 'html_files')) if f.endswith(".html")]

    wb = Workbook()
    ws = wb.active
    ws.title = "Passwords"
    ws.append(["Filename", "Password"])

    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    for file in html_files:
        password = generate_password()
        locked_file, passcode = bs_html(os.path.join(directory, 'html_files', file), password, subfolder)
        ws.append([file, passcode])
        print(f"Locked {file} -> {locked_file} (Password saved in log) - {password}")

    wb.save(log_file)
    print(f"Password log saved as {log_file}")

# Run the script
process_html_files()
