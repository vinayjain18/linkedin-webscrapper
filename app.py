import streamlit as st
import pandas as pd
import os
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

bio = {
    'Name': [],
    'Address': [],
    'Position': [],
    'Company_name': [],
    'Year': [],
    'Company_location': [],
    'College_name_1': [],
    'Degree_name_1': [],
    'Passing_year_1':[],
    'College_name_2': [],
    'Degree_name_2': [],
    'Passing_year_2':[],
}

def education(section):
    f = section.find_elements(By.TAG_NAME, 'li')
    #print(e[0].text)
    for inde, a in enumerate(f):
        if inde > 1:
            break
        else:
            try:
                posi = a.find_elements(By.CLASS_NAME, 'visually-hidden')
                bio[f'College_name_{inde+1}'].append(posi[0].text)
                bio[f'Degree_name_{inde+1}'].append(posi[1].text)
                bio[f'Passing_year_{inde+1}'].append(posi[2].text)
            except Exception as e:
                pass

def experience(section):
    f = section.find_element(By.TAG_NAME, 'li')
    posi = f.find_elements(By.CLASS_NAME, 'visually-hidden')
    try:
        bio['Position'].append(posi[0].text)
        bio['Company_name'].append(posi[1].text)
        bio['Year'].append(posi[2].text)
        bio['Company_location'].append(posi[3].text)
    except Exception as e:
        pass

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(executable_path=os.path.abspath("chromedriver")), options=chrome_options)  

image = Image.open('linkedin.png')
st.set_page_config(page_title="LinkedIn WebScrapper", page_icon=image)
st.title("Welcome to LinkedIn WebScrapper")
st.write(" ")

username = st.text_input("Enter the Email id or Phone Number:", placeholder="Email or Phone")
password = st.text_input("Enter the password:", type="password", placeholder="Password")

st.error("Note: The Username and Password you entered will not be saved and it will only be used for this session only.\
    For more transparency, you can also see the code on my GitHub repo. And if you have 2 factor authentication turned on,\
        please turn it off till the scrapping process gets over.")

st.write(" ")
csv_file = st.file_uploader(
    "Upload CSV file:", 
    type='csv', 
    help='Upload the CSV file with LinkedIn profile URLs in the first column with **"URLs"** as the column name.'
    )
st.write('Upload the CSV file with LinkedIn profile URLs in the first column with **"URLs"** as the column name.')
st.write(" ")

submit = st.button("Submit")

@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def starting_chrome():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)
    return driver


if submit and csv_file is not None:
    if username=="" or password=="":
        st.error("Please Enter Username/Password")
    else:
        try:
            #driver = starting_chrome()
            driver.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")

            Email = driver.find_element(By.XPATH, '//*[@id="username"]')
            Email.send_keys(username)

            passwd = driver.find_element(By.XPATH, '//*[@id="password"]')
            passwd.send_keys(password)

            login = driver.find_element(By.XPATH, '//*[@id="organic-div"]/form/div[3]/button')
            login.click()

            df = pd.read_csv(csv_file)

            for url in df.loc[:, 'URLs']:
                driver.get(url)
                name = driver.find_element(By.CLASS_NAME, 'text-heading-xlarge')
                bio['Name'].append(name.text)

                # To get the current address
                location = driver.find_element(By.CSS_SELECTOR, 'span.text-body-small.inline.t-black--light.break-words')
                bio['Address'].append(location.text)

                sections = driver.find_elements(By.CLASS_NAME, 'artdeco-card.ember-view.relative.break-words.pb3.mt2 ')

                for section in sections:
                    div = section.find_element(By.CLASS_NAME, 'pvs-header__container')
                    if div.text.split('\n')[0] == 'Experience':
                        experience(section)

                    if div.text.split('\n')[0] == 'Education':
                        education(section)
                    
                for item in list(bio.keys()):
                    if len(bio['Name']) > len(bio[item]):
                        bio[item].append("Not Available")
                
            driver.close()

            st.success("Scrapping completed successfully.")

            df = pd.DataFrame.from_dict(bio, orient='index')
            df = df.transpose()
            st.dataframe(df)
            st.write("")
            csv = convert_df(df)
            st.download_button(
                label="Download the CSV file",
                data=csv,
                file_name="linkedin_data.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error("Something went wrong! Please check the username and password are correct and you have turned off\
                the 2 factor authentication for now.")
