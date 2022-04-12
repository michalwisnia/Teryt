import urllib

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def scrap_emails(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")

    email = soup(text=re.compile(r'[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*'))

    _emailtokens = str(email).replace("\\t", "").replace("\\n", "").split(' ')

    if len(_emailtokens):
        print([match.group(0) for token in _emailtokens for match in
               [re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(token.strip()))] if match])
    '''mailtos = soup.select('a[href^=mailto]')
    emails = []
    for i in mailtos:
        #if i.string != None:
            #emails.append(i.string.encode('utf-8').strip())
        href = i['href']
        try:
            str1, str2 = href.split(':')
        except ValueError:
            break
        emails.append(str2)
    
    return emails
    '''
#def scrapfax(link):

#def find
dtypes = {
    'Kod_TERYT': 'object', 'nazwa_samorządu': 'object', 'Województwo': 'object', 'Powiat': 'object', 'typ_JST': 'object',
    'nazwa_urzędu_JST': 'object', 'miejscowość': 'object', 'Kod pocztowy': 'object', 'poczta': 'object','Ulica': 'object',
    'Nr domu': 'object', 'telefon kierunkowy': 'object', 'telefon': 'object', 'telefon 2': 'object', 'wewnętrzny': 'object',
    'FAX kierunkowy': 'object', 'FAX': 'object', 'FAX wewnętrzny': 'object',
    'ogólny adres poczty elektronicznej gminy/powiatu/województwa': 'object', 'adres www jednostki': 'object',
    'ESP': 'object'
}

baza_teleadresowa_jst_df = pd.read_csv("csv_Baza_teleadresowa_jst_stan_na_19_05_2021.csv", sep=";", encoding="windows-1250", dtype=dtypes)
baza_teleadresowa_jst_df = baza_teleadresowa_jst_df.loc[:, ~baza_teleadresowa_jst_df.columns.str.contains('^Unnamed')]


i = 0
for adres_www in baza_teleadresowa_jst_df['adres www jednostki']:

    fax = baza_teleadresowa_jst_df['FAX kierunkowy'][i]

    kontakt_url = None
    if not adres_www.startswith("http"):
        url = "http://" + adres_www
        print(str(i) + " " + url)
        try:
            response = requests.get(url)
            # print(response.status_code)
            soup = BeautifulSoup(response.content, "html.parser")

            if soup.select_one("a[href*=bip]") is not None:
                a = soup.select_one("a[href*=bip]")
                href = a.get('href')
                # print(href)
                if href.startswith("http"):
                    kontakt_url = href
                    print(kontakt_url)
                else:
                    kontakt_url = url + href
                    print(kontakt_url)
            elif soup.select_one("a[href*=biuletyn]") is not None:
                a = soup.select_one("a[href*=biuletyn]")
                href = a.get('href')
                # print(href)
                if href.startswith("http"):
                    kontakt_url = href
                    print(kontakt_url)
                else:
                    kontakt_url = url + href
                    print(kontakt_url)
            else:
                print("test1")

            if kontakt_url is not None:
                kontakt_url_response = requests.get(kontakt_url)
                print(kontakt_url_response.status_code)
        except requests.exceptions.RequestException as e:
            try:
                new_url = e.request.url
                print(new_url)
                response = requests.get(new_url, verify=False)
                # print(response.status_code)
                soup = BeautifulSoup(response.content, "html.parser")
                if soup.select_one("a[href*=bip]") is not None:
                    a = soup.select_one("a[href*=bip]")
                    href = a.get('href')
                    # print(href)
                    if href.startswith("http"):
                        kontakt_url = href
                        print(kontakt_url)
                    else:
                        kontakt_url = new_url + href
                        print(kontakt_url)
                    kontakt_url_response = requests.get(kontakt_url)
                    print(kontakt_url_response.status_code)
            except requests.exceptions.RequestException as e:
                print("blad")
                # continue

    else:
        url = adres_www
        print(str(i) + " " + url)
        try:
            response = requests.get(url)
            # print(response.status_code)
            soup = BeautifulSoup(response.content, "html.parser")

            if soup.select_one("a[href*=bip]") is not None:
                a = soup.select_one("a[href*=bip]")
                href = a.get('href')
                # print(href)
                if href.startswith("http"):
                    kontakt_url = href
                    print(kontakt_url)
                else:
                    if href.startswith("/pl") and url.endswith("pl/"):
                        kontakt_url = url[:-3] + href
                    else:
                        kontakt_url = url + href
                    print(kontakt_url)
            else:
                print("test2")

            if kontakt_url is not None:
                kontakt_response = requests.get(kontakt_url)
                print(kontakt_response.status_code)
        except requests.exceptions.RequestException as e:
            print("blad")
            continue

    print(scrap_emails(kontakt_url))

    i+=1

    print()