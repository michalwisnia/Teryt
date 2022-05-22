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
    "fax": ['fax.txt']
}

def load_patterns():
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

def scrap_fax(soup_text):
    try:
        fax_list = []
        for pattern in regex_dict.get("fax")[1]:
            num_only = re.compile(pattern[0]).search(soup_text)
            if num_only:
                fax_list.append(num_only.group().strip())
        return remove_duplicates(fax_list)
    except:
        return []

def scrap_tel(soup_text):
    try:
        tel_list = []
        for pattern in regex_dict.get("tel")[1]:
            num_only = re.compile(pattern[0]).search(soup_text)
            if num_only:
                tel_list.append(num_only.group().strip())
        return remove_duplicates(tel_list)
    except:
        return []

def scrap_address_zip_city(soup_text):
    try:
        address_zip_city_list = []
        for pattern in regex_dict.get("address_zip_code")[1]:
            zip = re.compile(pattern[0]).search(soup_text)
            if zip:
                address_zip_city_list.append(zip.group().strip())
        return remove_duplicates(address_zip_city_list)
    except:
        return []

def scrap_address_street(soup_text):
    try:
        address_list = []
        for pattern in regex_dict.get("address")[1]:
            street = re.compile(pattern[0]).search(soup_text)
            if street:
                address_list.append(street.group().strip())
        return remove_duplicates(address_list)
    except:
        return []

def scrap_ESP(soup):
        esp_pattern = '\/\w*\/[sS]krytka[ESP]*'
        esp = re.search(esp_pattern, soup.text)
        if esp is not None:
            return esp.group(0)

def check_in_page(text, soup): #do odszukania tekstu na stronie
    try:
        return bool(soup.find(text=re.compile(text)))
    except:
        return False

def generate_number_combinations(tel_kier, tel_reszta):
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
    #print(combinations)
    try:
        for c in combinations:
            if bool(soup.find(text=re.compile(c))) == True:
                #print("found ",c)
                return True
    except requests.exceptions.RequestException as e:
        #print("blad strony")
        #print("not found")
        return False
    except:
        return False

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
        esp = row['ESP']

        email = row['ogólny adres poczty elektronicznej gminy/powiatu/województwa']
        
        #row['adres www jednostki'] += url_checker(adres_www)
        # jeśli adres strony nie działa, puste komórki + break

        urls = get_kontakt_url(adres_www)
        print(urls)

        scraped_email = []
        scraped_tel = []
        scraped_fax = []
        scraped_address_zip_city = []
        scraped_address_street = []
        scraped_esp = None


        #print(scrap_address(kontakt_url))
        #print(scrap_ESP(kontakt_url))
        load_patterns()
        for url in urls:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
                response = requests.get(url, headers=headers, verify=False, timeout=10)
                page_body = BeautifulSoup(response.content, "html.parser")

                print(email)
                print("zawarty email = ", check_in_page(str(email), page_body))
                print('--------SCRAP-------')
                print(url)
                if len(scraped_email) == 0:
                    scraped_email = scrap_emails(page_body)
                    print(f"Email:  {scraped_email}")
                if len(scraped_tel) == 0:
                    scraped_tel = scrap_tel(page_body)
                    print(f"Telefony:  {scraped_tel}")
                if len(scraped_fax) == 0:
                    scraped_fax = scrap_fax(page_body)
                    print(f"Fax:  {scraped_fax}")
                if len(scraped_address_zip_city) == 0:
                    scraped_address_zip_city = scrap_address_zip_city(page_body)
                    print(f"Kod pocztowy, miasto:  {scraped_address_zip_city}")
                if len(scraped_address_street) == 0:
                    scraped_address_street = scrap_address_street(page_body)
                    print(f"Ulica:  {scraped_address_street}")
                if scraped_esp is None:
                    scraped_esp = scrap_ESP(page_body)
                    print(f"Skrytka:  {scraped_esp}")

                # if (check_in_page(str(email), page_body)) == False:
                #     row['ogólny adres poczty elektronicznej gminy/powiatu/województwa'] += scrap_emails(page_body)
                #
                # # print(tel_kier+" "+tel_reszta)
                # if (check_combinations(generate_number_combinations(tel_kier, tel_reszta), page_body)) == False:
                #     print(scrap_tel(page_body))
                #     row['telefon kierunkowy'] = scrap_tel(page_body)[0][0:1]
                #     row['telefon'] = scrap_tel(page_body)[0][1:]
                #     # replace the number with a new one
                #
                # if (check_combinations(generate_number_combinations(tel_kier, tel_reszta), page_body)) == False:
                #     print(scrap_fax(page_body))
                #     row['FAX kierunkowy'] = scrap_fax(page_body)[0][0:1]
                #     row['FAX'] = scrap_fax(page_body)[0][1:]
                #
                # if (check_in_page(str(esp), page_body)) == False:
                #     row['ESP'] = scrap_ESP(page_body)
                #
                #
                # print(f"Kod pocztowy, miasto:  {scrap_address_zip_city(page_body)}")
                # print(f"Ulica:  {scrap_address_street(page_body)}")


            except requests.exceptions.RequestException as e:
                print("blad strony")

            if len(scraped_email) != 0 and len(scraped_tel) != 0 and len(scraped_fax) != 0 and len(scraped_address_zip_city) != 0 and len(scraped_address_street) !=0 and scraped_esp is not None:
                break

        i += 1


    baza_teleadresowa_jst_df.to_csv('baza_nowa.csv')