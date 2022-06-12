import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from url import get_kontakt_url

regex_dict = {
    "tel": ['tel.txt'],
    "address_zip_code": ['kod_miasto.txt'],
    "address": ['adres.txt'],
    "fax": ['fax.txt'] #pliki zawierające wyrażenia regularne
}

def load_patterns(): #aby załadować wyrażenia regularne z plików
    global regex_dict
    for key in regex_dict:
        tmp = []
        tmp.append(regex_dict[key][0])
        tmp.append([])
        data_file = open(f"regex_patterns/{regex_dict[key][0]}", "r", encoding="utf-8")
        for pattern in data_file.read().split('\n'):
            tmp[1].append([pattern, ".*" + pattern + ".*"])
        regex_dict.update({key: tmp})
        data_file.close()

def remove_duplicates(list): #aby nie powtarzały się elementy w listach
    res = []
    [res.append(x) for x in list if x not in res]
    return res

def scrap_emails(soup): #do znalezienia emaili
        email = soup(text=re.compile(r'[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*'))

        _emailtokens = str(email).replace("\\t", "").replace("\\n", "").split(' ')

        email_list = []

        if len(_emailtokens):
            email_list.append([match.group(0) for token in _emailtokens for match in
                    [re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(token.strip()))] if match])

        email_list = np.squeeze(email_list, axis=0) #aby jednowymiarowa tabela

        return remove_duplicates(email_list)

def scrap_fax(soup_text): #do znalezienia faxow
    try:
        fax_list = []
        for pattern in regex_dict.get("fax")[1]:
            num_only = re.compile(pattern[0]).search(soup_text)
            if num_only:
                fax_list.append(num_only.group().strip())
        return remove_duplicates(fax_list)
    except:
        return []

def scrap_tel(soup_text): #do znalezienia numerow telefonow
    try:
        tel_list = []
        for pattern in regex_dict.get("tel")[1]:
            num_only = re.compile(pattern[0]).search(soup_text)
            if num_only:
                tel_list.append(num_only.group().strip())
        return remove_duplicates(tel_list)
    except:
        return []

def scrap_address_zip_city(soup_text): #do znalezienia kodow pocztowych
    try:
        address_zip_city_list = []
        for pattern in regex_dict.get("address_zip_code")[1]:
            zip = re.compile(pattern[0]).search(soup_text)
            if zip:
                address_zip_city_list.append(zip.group().strip())
        return remove_duplicates(address_zip_city_list)
    except:
        return []

def scrap_address_street(soup_text): #do znalezienia adresów
    try:
        address_list = []
        for pattern in regex_dict.get("address")[1]:
            street = re.compile(pattern[0]).search(soup_text)
            if street:
                address_list.append(street.group().strip())
        return remove_duplicates(address_list)
    except:
        return []

def scrap_ESP(soup): #do znalezienia skrytek ESP
        esp_pattern = '\/\w*\/[sS]krytka[ESP]*'
        esp = re.search(esp_pattern, soup.text)
        if esp is not None:
            return esp.group(0)

def check_in_page(text, soup): #do odszukania tekstu na stronie
    try:
        return bool(soup.find(text=re.compile(text)))
    except:
        return False

def generate_number_combinations(tel_kier, tel_reszta): #wygenerowanie różnych kombinacji numerów
    combinations = []
    combinations.append(tel_kier+tel_reszta)
    combinations.append("0" + tel_kier + tel_reszta)
    combinations.append(tel_kier + " " + tel_reszta)
    combinations.append(tel_kier + "-" + tel_reszta)
    combinations.append(tel_kier + tel_reszta[0]+"-"+tel_reszta[1:4]+"-"+tel_reszta[4:7])
    combinations.append(tel_kier + tel_reszta[0] + " " + tel_reszta[1:4] + " " + tel_reszta[4:7])
    combinations.append(tel_kier + " " + tel_reszta[0:2] + " " + tel_reszta[2:4] + " " + tel_reszta[4:7])
    combinations.append(tel_kier + " " + tel_reszta[0:2] + "-" + tel_reszta[2:4] + "-" + tel_reszta[4:7])
    combinations.append(tel_kier + " " + tel_reszta[0:3] + "-" + tel_reszta[3:5] + "-" + tel_reszta[5:7])
    combinations.append(tel_kier + " " + tel_reszta[0:3] + " " + tel_reszta[3:5] + " " + tel_reszta[5:7])
    combinations.append(tel_kier + "-" + tel_reszta[0:3] + "-" + tel_reszta[3:5] + "-" + tel_reszta[5:7])
    combinations.append(tel_kier + " " + tel_reszta[0:2] + "-" + tel_reszta[2:4] + "-" + tel_reszta[5:7])
    combinations.append(tel_kier + " " + tel_reszta[0:4] + " " + tel_reszta[4:7])
    combinations.append(tel_kier + " " + tel_reszta[0:4] + "-" + tel_reszta[4:7])
    combinations.append(tel_kier + " " + tel_reszta[0:4] + " - " + tel_reszta[4:7])
    combinations.append("\(+48 "+ tel_kier + "\) " + tel_reszta[0:2] + " " + tel_reszta[2:4] + " " + tel_reszta[4:7]) #wywala?
    combinations.append("\(+48 "+ tel_kier + "\) " + tel_reszta[0:3] + "-" + tel_reszta[3:5] + " " + tel_reszta[5:7]) #wywala?
    combinations.append("\(+48 "+ tel_kier + "\) " + tel_reszta) #wywala?

    combinations.append(tel_kier+"\)" + " " + tel_reszta[0:2] + " " + tel_reszta[2:4] + " " + tel_reszta[4:7])
    combinations.append(tel_kier+"\)" + " " + tel_reszta[0:3] + " " + tel_reszta[3:5] + " " + tel_reszta[5:7])
    combinations.append(tel_kier+"\)" + " " + tel_reszta[0:2] + " " + tel_reszta[2:5] + " " + tel_reszta[5:7])
    combinations.append(tel_kier+"\)" + " " + tel_reszta[0:3] + "-" + tel_reszta[3:5] + "-" + tel_reszta[5:7])

    combinations.append(tel_kier+"\)" + " " + tel_reszta[0:4] + "-" + tel_reszta[4:7])
    combinations.append(tel_kier+"\)" + " " + tel_reszta[0:4] + " " + tel_reszta[4:7])

    combinations.append(tel_kier+"\)" + " " + tel_reszta)

    combinations.append(tel_kier+"\)" + " " + tel_reszta[0:1] + "-" + tel_reszta[1:4] + " " + tel_reszta[4:7])

    combinations.append(tel_kier +"\)" + tel_reszta)
    combinations.append(tel_kier + "/ " + tel_reszta[0:3] + " " + tel_reszta[3:5] + " " + tel_reszta[5:7])
    combinations.append(tel_kier + "/ " + tel_reszta[0:3] + "-" + tel_reszta[3:5] + "-" + tel_reszta[5:7])
    combinations.append(tel_kier + "/ " + tel_reszta[0:3] + "- " + tel_reszta[3:5] + "- " + tel_reszta[5:7])

    combinations.append(tel_kier + " " + tel_reszta[0:2] + "-" + tel_reszta[2:4] + "-" + tel_reszta[4:7])



    return combinations

def check_combinations(combinations, soup):
    try:
        for c in combinations:
            if bool(soup.find(text=re.compile(c))) == True:
                return True #przerwanie aby nie sprawdzać reszty kombinacji
    except requests.exceptions.RequestException as e:
        return False
    except:
        return False

def prepare_numbers(scraped_numbers): #do przygotowania numerow telefonow i faxow do postaci samych cyfr
    numbers = []
    for number in scraped_numbers:
        temp_number = re.findall("\d+", number)
        temp_number = ''.join(temp_number)
        temp_number = temp_number[len(temp_number) - 9:]
        numbers.append(temp_number)
    return numbers

dtypes = {
    'Kod_TERYT': 'object', 'nazwa_samorządu': 'object', 'Województwo': 'object', 'Powiat': 'object', 'typ_JST': 'object',
    'nazwa_urzędu_JST': 'object', 'miejscowość': 'object', 'Kod pocztowy': 'object', 'poczta': 'object','Ulica': 'object',
    'Nr domu': 'object', 'telefon kierunkowy': 'object', 'telefon': 'object', 'telefon 2': 'object', 'wewnętrzny': 'object',
    'FAX kierunkowy': 'object', 'FAX': 'object', 'FAX wewnętrzny': 'object',
    'ogólny adres poczty elektronicznej gminy/powiatu/województwa': 'object', 'adres www jednostki': 'object',
    'ESP': 'object'
}
