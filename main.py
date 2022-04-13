import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from url import get_kontakt_url

regex_dict = {
    "tel": ['tel.txt'],
    "address_zip_code": ['kod_miasto.txt']
}

#address_regex = ['ul\.', 'UL\.', 'ul:']
#address_regex = [".*" + address + ".*" for address in address_regex]

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

# def load_patterns():
#     global tel_regex, address_zip_code_regex
#     global regex_dict
#     data_file = open(f"regex_patterns/tel.txt", "r")
#     for tel in data_file.read().split('\n'):
#         tel_regex.append([tel, ".*" + tel + ".*"])
#     data_file.close()
#
#     data_file = open(f"regex_patterns/kod_miasto.txt", "r")
#     for kod_miasto in data_file.read().split('\n'):
#         address_zip_code_regex.append([kod_miasto, ".*" + kod_miasto + ".*"])
#     data_file.close()


def remove_duplicates(list):
    res = []
    [res.append(x) for x in list if x not in res]
    return res

def scrap_emails(link): #do znalezienia emaili
    try:

        response = requests.get(link)

        soup = BeautifulSoup(response.content, "html.parser")

        email = soup(text=re.compile(r'[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*'))

        _emailtokens = str(email).replace("\\t", "").replace("\\n", "").split(' ')

        email_list = []

        if len(_emailtokens):
            email_list.append([match.group(0) for token in _emailtokens for match in
                    [re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(token.strip()))] if match])

        email_list = np.squeeze(email_list, axis=0) #aby jednowymiarowa tabela

        return remove_duplicates(email_list)
    except requests.exceptions.RequestException as e:
        print("blad strony")

def scrap_tel(link):
    try:
        tel_list = []
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        for pattern in regex_dict.get("tel")[1]:
            regex_strip = re.compile(pattern[0])
            regex_search = re.compile(pattern[1])
            result = soup.body.findAll(text=regex_search)
            for x in result:
                num_only = regex_strip.search(x)
                tel_list.append(num_only.group())

        return remove_duplicates(tel_list)
    except requests.exceptions.RequestException as e:
        print("blad strony")

def scrap_address(link):
    try:
        address_list = []
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        for pattern in regex_dict.get("address_zip_code")[1]:
            regex_strip = re.compile(pattern[0])
            regex_search = re.compile(pattern[1])
            result = soup.body.findAll(text=regex_search)
            for x in result:
                num_only = regex_strip.search(x)
                address_list.append(num_only.group())
        return remove_duplicates(address_list)
    except requests.exceptions.RequestException as e:
        print("blad strony")



def check_in_page(text, link): #do odszukania tekstu na stronie
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        return bool(soup.find(text=re.compile(text)))
    except requests.exceptions.RequestException as e:
        print("blad strony")

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

        print(email)
        print("zawarty email = ", check_in_page(str(email), kontakt_url))

        load_patterns()
        # print(scrap_emails(kontakt_url))
        print(scrap_tel(kontakt_url))
        print(scrap_address(kontakt_url))




        i += 1

        print()
