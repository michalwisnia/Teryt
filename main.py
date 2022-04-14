import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from url import get_kontakt_url

regex_dict = {
    "tel": ['tel.txt'],
    "address_zip_code": ['kod_miasto.txt'],
    "address": ['adres.txt']
}


def load_patterns():
    global regex_dict
    for key in regex_dict:
        tmp = []
        tmp.append(regex_dict[key][0])
        tmp.append([])
        data_file = open(f"regex_patterns/{regex_dict[key][0]}", "r")
        for pattern in data_file.read().split('\n'):
            tmp[1].append([pattern, ".*" + pattern + ".*"])
        regex_dict.update({key: tmp})
        data_file.close()

def remove_duplicates(list):
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

def scrap_tel(soup):
    tel_list = []
    for pattern in regex_dict.get("tel")[1]:
        regex_strip = re.compile(pattern[0])
        regex_search = re.compile(pattern[1])
        result = soup.body.findAll(text=regex_search)
        for x in result:
            num_only = regex_strip.search(x)
            tel_list.append(num_only.group())
    return remove_duplicates(tel_list)

def scrap_address_zip_city(soup):
    address_zip_city_list = []
    for pattern in regex_dict.get("address_zip_code")[1]:
        regex_strip = re.compile(pattern[0])
        regex_search = re.compile(pattern[1])
        result = soup.body.findAll(text=regex_search)
        for x in result:
            zip = regex_strip.search(x)
            address_zip_city_list.append(zip.group())
    return remove_duplicates(address_zip_city_list)

def scrap_address_street(soup):
    address_list = []
    for pattern in regex_dict.get("address")[1]:
        regex_strip = re.compile(pattern[0])
        regex_search = re.compile(pattern[1])
        result = soup.body.findAll(text=regex_search)
        for x in result:
            street = regex_strip.search(x)
            address_list.append(street.group())
    return remove_duplicates(address_list)

def scrap_ESP(soup):
        esp_pattern = '\/\w*\/[sS]krytka[ESP]*'
        esp = re.search(esp_pattern, soup.text)
        if esp is not None:
            return esp.group(0)

def check_in_page(text, soup): #do odszukania tekstu na stronie
    return bool(soup.find(text=re.compile(text)))

#def check_all_in_page

dtypes = {
    'Kod_TERYT': 'object', 'nazwa_samorządu': 'object', 'Województwo': 'object', 'Powiat': 'object', 'typ_JST': 'object',
    'nazwa_urzędu_JST': 'object', 'miejscowość': 'object', 'Kod pocztowy': 'object', 'poczta': 'object','Ulica': 'object',
    'Nr domu': 'object', 'telefon kierunkowy': 'object', 'telefon': 'object', 'telefon 2': 'object', 'wewnętrzny': 'object',
    'FAX kierunkowy': 'object', 'FAX': 'object', 'FAX wewnętrzny': 'object',
    'ogólny adres poczty elektronicznej gminy/powiatu/województwa': 'object', 'adres www jednostki': 'object',
    'ESP': 'object'
}


if __name__ == "__main__":

    baza_teleadresowa_jst_df = pd.read_csv("csv_Baza_teleadresowa_jst_stan_na_19_05_2021.csv", sep=";", encoding="windows-1250", dtype=dtypes)
    baza_teleadresowa_jst_df = baza_teleadresowa_jst_df.loc[:, ~baza_teleadresowa_jst_df.columns.str.contains('^Unnamed')]

    load_patterns()

    i = 0
    for index, row in baza_teleadresowa_jst_df.iterrows():
        print(i)
        kod_teryt = row['Kod_TERYT']
        kod_pocztowy = row['Kod pocztowy']
        poczta = row['poczta']
        Ulica = row['Ulica']
        Nr_domu = row['Nr domu']
        adres_www = row['adres www jednostki']

        tel_kier = row['telefon kierunkowy']
        tel_reszta = row['telefon']
        tel_reszta2 = row['telefon 2']

        fax_kier = row['FAX kierunkowy']
        fax_reszta = row['FAX']
        kontakt_url = get_kontakt_url(adres_www)

        email = row['ogólny adres poczty elektronicznej gminy/powiatu/województwa']

        load_patterns()
        try:
            response = requests.get(kontakt_url)
            page_body = BeautifulSoup(response.content, "html.parser")


            print(email)
            print("zawarty email = ", check_in_page(str(email), page_body))
            print('--------SCRAP-------')
            print(f"Email:  {scrap_emails(page_body)}")
            print(f"Telefony:  {scrap_tel(page_body)}")
            print(f"Kod pocztowy, miasto:  {scrap_address_zip_city(page_body)}")
            print(f"Ulica:  {scrap_address_street(page_body)}")
            print(f"Skrytka:  {scrap_ESP(page_body)}")
        except requests.exceptions.RequestException as e:
            print("blad strony")




        i += 1

        print()
