import sys

import pandas as pd
from main import dtypes, prepare_numbers
from main import regex_dict, load_patterns, remove_duplicates, scrap_emails, scrap_fax, scrap_tel, scrap_address_zip_city, scrap_address_street, scrap_ESP, check_in_page, generate_number_combinations, check_combinations
import requests
from bs4 import BeautifulSoup
import re
from url import get_kontakt_url, check_url
from itertools import islice

terytTypes = {
    'WOJ': 'object', 'POW': 'object', 'GMI': 'object', 'RODZ': 'object', 'NAZWA': 'object', 'NAZWA_DOD': 'object', 'STAN_NA': 'object'
}

new_columns = ['TERYT_WOJ', 'TERYT_POW', 'TERYT_NAZWA_SAMORZAU', 'TERYT_TYP_JST',
			   'COMP_WOJ', 'COMP_POW', 'COMP_NAZWA_SAMORZAU','COMP_TYP_JST',
               'PNA_WOJ', 'PNA_POW', 'PNA_GMI',
               'COMP_PNA_WOJ', 'COMP_PNA_POW', 'COMP_PNA_GMI',
               'SCRAP_URL', 'SCRAP_MAIL', 'SCRAP_TEL', 'SCRAP_FAX', 'SCRAP_POST_CODE', 'SCRAP_STREET', 'SCRAP_ESP',
               'COMP_SCRAP_URL', 'COMP_SCRAP_MAIL', 'COMP_SCRAP_TEL', 'COMP_SCRAP_FAX', 'COMP_SCRAP_POST_CODE', 'COMP_SCRAP_STREET', 'COMP_SCRAP_ESP']
#nowe kolumny do dataframe'ów
typ_JST_dict = {
    "gmina miejsko-wiejska": 'GMW',
    "gmina miejska": 'GM',
    "gmina wiejska": 'GW',
    "województwo": 'W',
    "powiat": 'P',
	"gmina miejska, miasto stołeczne": 'MNP',
	"dzielnica": 'dzielnica'
}

spispnaTypes = {
	'PNA' : 'object', 'MIEJSCOWOŚĆ' : 'object', 'ULICA' : 'object', 'NUMERY' : 'object', 'GMINA' : 'object', 'POWIAT' : 'object', 'WOJEWÓDZTWO' : 'object'
}

if __name__ == "__main__":
	baza_teleadresowa_jst_df = pd.read_csv("csv_Baza_teleadresowa_jst_stan_na_19_05_2021.csv", sep=";",  encoding="windows-1250", dtype=dtypes)
	baza_teleadresowa_jst_df = baza_teleadresowa_jst_df.loc[:,~baza_teleadresowa_jst_df.columns.str.contains('^Unnamed')]

	result_df = baza_teleadresowa_jst_df.reindex(columns=baza_teleadresowa_jst_df.columns.tolist() + new_columns)


	teryt_df = pd.read_csv("data/TERC_Urzedowy_2022-03-14.csv", sep=";",  encoding="utf-8", dtype=terytTypes)

	spispna_df1 = pd.read_csv("data/spispna_miejscowosci.csv", sep=";",  encoding="windows-1250", dtype=spispnaTypes)

	spispna_df2 = pd.read_csv("data/spispna_miejscowosci2.csv", sep=";",  encoding="windows-1250", dtype=spispnaTypes)

	spispna_df = pd.concat([spispna_df1, spispna_df2], ignore_index=True) #aby połączyć oba pliki spisu pna które mają rozdzielone dane

	spispna_df['MIEJSCOWOŚĆ'] = spispna_df['MIEJSCOWOŚĆ'].apply(lambda x: x.split('(')[0].rstrip()) #odrzucenie niepotrzebnej informacji po nawiasie

	load_patterns()
	step = len(result_df)

	if len(sys.argv) == 2:
		step = int(sys.argv[1])
		if step > len(result_df):
			step = len(result_df)
	i=0
	for index, row in islice(result_df.iterrows(), 0, None):
		if i in range(0, len(result_df), step):
			print(f"Przetwarzanie wierszy {i}-{i+step}")
		i += 1
		kod_teryt = row['Kod_TERYT']
		kod_pocztowy = row['Kod pocztowy']
		miasto = row['miejscowość']

		poczta = row['poczta']
		Ulica = row['Ulica']
		Nr_domu = row['Nr domu']
		adres_www = row['adres www jednostki']

		tel_kier = row['telefon kierunkowy']
		tel_reszta = str(row['telefon'])
		tel_reszta2 = str(row['telefon 2'])

		fax_kier = str(row['FAX kierunkowy'])
		fax_reszta = str(row['FAX'])
		esp = row['ESP']

		email = row['ogólny adres poczty elektronicznej gminy/powiatu/województwa']

		# if (adres_www == 'http://www.ugnowemiasto.pl/' or adres_www == 'www.zbuczyn.pl'):
		#    continue

		res_woj = teryt_df.loc[(teryt_df['WOJ'] == kod_teryt[:2]) & (teryt_df['POW'].isna()) & (teryt_df['GMI'].isna())]
		res_pow = teryt_df.loc[(teryt_df['WOJ'] == kod_teryt[:2]) & (teryt_df['POW'] == kod_teryt[2:4]) & (teryt_df['GMI'].isna())]
		res_gmi = teryt_df.loc[(teryt_df['WOJ'] == kod_teryt[:2]) & (teryt_df['POW'] == kod_teryt[2:4]) & (teryt_df['GMI'] == kod_teryt[4:6]) & (teryt_df['RODZ'] == kod_teryt[6])]
		if not res_woj.empty:
			result_df.loc[index, "TERYT_WOJ"] = res_woj['NAZWA'].values[0].lower()
		if not res_pow.empty:
			result_df.loc[index, "TERYT_POW"] = res_pow['NAZWA'].values[0]
		elif not res_woj.empty:
			result_df.loc[index, "TERYT_TYP_JST"] = typ_JST_dict[res_woj['NAZWA_DOD'].values[0]]

		if not res_gmi.empty:
			result_df.loc[index, "TERYT_NAZWA_SAMORZAU"] = res_gmi['NAZWA'].values[0]
			result_df.loc[index, "TERYT_TYP_JST"] = typ_JST_dict[res_gmi['NAZWA_DOD'].values[0]]
		elif not res_pow.empty:
			result_df.loc[index, "TERYT_TYP_JST"] = typ_JST_dict[res_pow['NAZWA_DOD'].values[0]]


		if result_df.loc[index, "TERYT_WOJ"] == result_df.loc[index, "Województwo"]:
			result_df.at[index, 'COMP_WOJ'] = '1'
		else:
			result_df.at[index, 'COMP_WOJ'] = '0'

		if result_df.loc[index, "TERYT_POW"] == result_df.loc[index, "Powiat"]:
			result_df.at[index, 'COMP_POW'] = '1'
		else:
			result_df.at[index, 'COMP_POW'] = '0'

		if result_df.loc[index, "TERYT_NAZWA_SAMORZAU"] == result_df.loc[index, "nazwa_samorządu"]:
			result_df.at[index, 'COMP_NAZWA_SAMORZAU'] = '1'
		else:
			result_df.at[index, 'COMP_NAZWA_SAMORZAU'] = '0'


		if result_df.loc[index, "TERYT_TYP_JST"] == result_df.loc[index, "typ_JST"]:
			result_df.at[index, 'COMP_TYP_JST'] = '1'
		else:
			result_df.at[index, 'COMP_TYP_JST'] = '0'

		res_woj = teryt_df.loc[(teryt_df['WOJ'] == kod_teryt[:2]) & (teryt_df['POW'].isna()) & (teryt_df['GMI'].isna())]
		res_pow = teryt_df.loc[
			(teryt_df['WOJ'] == kod_teryt[:2]) & (teryt_df['POW'] == kod_teryt[2:4]) & (teryt_df['GMI'].isna())]
		res_gmi = teryt_df.loc[(teryt_df['WOJ'] == kod_teryt[:2]) & (teryt_df['POW'] == kod_teryt[2:4]) & (
					teryt_df['GMI'] == kod_teryt[4:6]) & (teryt_df['RODZ'] == kod_teryt[6])]

		#Poczta polska

		pna_row = spispna_df.loc[(spispna_df['PNA'] == kod_pocztowy) & (spispna_df['MIEJSCOWOŚĆ'] == miasto)] #do odszukania odpowiedniego wiersza
		if not pna_row.empty:
			result_df.loc[index, "PNA_WOJ"] = pna_row['WOJEWÓDZTWO'].values[0]
			result_df.loc[index, "PNA_POW"] = pna_row['POWIAT'].values[0]
			result_df.loc[index, "PNA_GMI"] = pna_row['GMINA'].values[0]

		if result_df.loc[index, "PNA_WOJ"] == result_df.loc[index, "Województwo"]:
			result_df.at[index, 'COMP_PNA_WOJ'] = '1'
		else:
			result_df.at[index, 'COMP_PNA_WOJ'] = '0'

		if result_df.loc[index, "PNA_POW"] == result_df.loc[index, "Powiat"]:
			result_df.at[index, 'COMP_PNA_POW'] = '1'
		else:
			result_df.at[index, 'COMP_PNA_POW'] = '0'

		if result_df.loc[index, "PNA_GMI"] == result_df.loc[index, "miejscowość"]:
			result_df.at[index, 'COMP_PNA_GMI'] = '1'
		else:
			result_df.at[index, 'COMP_PNA_GMI'] = '0'


		#SCRAP

		if check_url(adres_www) == False: #jesli strona nie dziala to brak żadnych poprawnych danych
			result_df.at[index, 'SCRAP_URL'] = "blad strony"
			result_df.at[index, 'COMP_SCRAP_URL'] = '0'
			result_df.at[index, 'COMP_SCRAP_MAIL'] = '0'
			result_df.at[index, 'COMP_SCRAP_TEL'] = '0'
			result_df.at[index, 'COMP_SCRAP_FAX'] = '0'
			result_df.at[index, 'COMP_SCRAP_POST_CODE'] = '0'
			result_df.at[index, 'COMP_SCRAP_STREET'] = '0'
			result_df.at[index, 'COMP_SCRAP_ESP'] = '0'
			continue


		urls = get_kontakt_url(adres_www)

		scraped_email = []
		scraped_tel = []
		scraped_fax = []
		scraped_address_zip_city = []
		scraped_address_street = []
		scraped_esp = None


		for url in urls:
			try:
				headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
				response = requests.get(url, headers=headers, verify=False, timeout=10)
				page_body = BeautifulSoup(response.content, "html.parser")
				page_body_str = str(page_body)

				if not result_df.loc[index, "COMP_SCRAP_MAIL"] == "1":
					if (check_in_page(str(email), page_body)) == True:
						scraped_email.append(email)
						result_df.at[index, 'COMP_SCRAP_MAIL'] = '1'
					if not result_df.loc[index, "COMP_SCRAP_MAIL"] == "1":
						scraped_email += scrap_emails(page_body)
						if email in scraped_email:
							scraped_email.clear()
							scraped_email.append(email)
							result_df.at[index, 'COMP_SCRAP_MAIL'] = '1'

				if not result_df.loc[index, "COMP_SCRAP_TEL"] == "1":
					if (check_combinations(generate_number_combinations(tel_kier, tel_reszta), page_body)) == True:
						scraped_tel.append(tel_kier + tel_reszta)
						result_df.at[index, 'COMP_SCRAP_TEL'] = '1'
					if not result_df.loc[index, "COMP_SCRAP_TEL"] == "1":
						scraped_tel += prepare_numbers(scrap_tel(page_body_str))
						if (tel_kier + tel_reszta) in scraped_tel:
							scraped_tel.clear()
							scraped_tel.append(tel_kier + tel_reszta)
							result_df.at[index, 'COMP_SCRAP_TEL'] = '1'

				if not result_df.loc[index, "COMP_SCRAP_FAX"] == "1":
					if (check_combinations(generate_number_combinations(fax_kier, fax_reszta), page_body)) == True:
						scraped_fax.append(fax_kier + fax_reszta)
						result_df.at[index, 'COMP_SCRAP_FAX'] = '1'
					if not result_df.loc[index, "COMP_SCRAP_FAX"] == "1":
						scraped_fax += prepare_numbers(scrap_fax(page_body_str))
						if (fax_kier + fax_reszta) in scraped_fax:
							scraped_fax.clear()
							scraped_fax.append(fax_kier + fax_reszta)
							result_df.at[index, 'COMP_SCRAP_FAX'] = '1'

				if not result_df.loc[index, "COMP_SCRAP_POST_CODE"] == "1":
					if (check_in_page(str(kod_pocztowy), page_body)) == True:
						scraped_address_zip_city.append(kod_pocztowy)
						result_df.at[index, 'COMP_SCRAP_POST_CODE'] = '1'
					if not result_df.loc[index, "COMP_SCRAP_POST_CODE"] == "1":
						scraped_address_zip_city += scrap_address_zip_city(page_body_str)
						if kod_pocztowy in [x[:6] for x in scraped_address_zip_city]:
							scraped_address_zip_city.clear()
							scraped_address_zip_city.append(kod_pocztowy)
							result_df.at[index, 'COMP_SCRAP_POST_CODE'] = '1'

				if str(Ulica).endswith(' '):
					adres_nr = str(Ulica) + str(Nr_domu)
					adres_nr_cut = str(Ulica).split(" ")[-1] + str(Nr_domu)
				else:
					adres_nr = str(Ulica) + " " + str(Nr_domu)
					adres_nr_cut = str(Ulica).split(" ")[-1] + " " + str(Nr_domu)

				if not result_df.loc[index, "COMP_SCRAP_STREET"] == "1":
					if (check_in_page(adres_nr_cut, page_body)) == True:
						scraped_address_street.append(adres_nr)
						result_df.at[index, 'COMP_SCRAP_STREET'] = '1'
					if not result_df.loc[index, "COMP_SCRAP_STREET"] == "1":
						scraped_address_street += scrap_address_street(page_body_str)
						if adres_nr.lower().replace(" ", "") in [adres.lower().replace(" ", "") for adres in scraped_address_street]:
							scraped_address_street.clear()
							scraped_address_street.append(adres_nr)
							result_df.at[index, 'COMP_SCRAP_STREET'] = '1'
					#print(f"Ulica:  {scraped_address_street}")

				if not result_df.loc[index, "COMP_SCRAP_ESP"] == "1":
					if (check_in_page(str(esp), page_body)) == True:
						scraped_esp = esp
						result_df.at[index, 'COMP_SCRAP_ESP'] = '1'
					if not result_df.loc[index, "COMP_SCRAP_ESP"] == "1":
						scraped_esp = scrap_ESP(page_body)
						if str(esp) == scraped_esp:
							result_df.at[index, 'COMP_SCRAP_ESP'] = '1'
						#print(f"Skrytka:  {scraped_esp}")



			except requests.exceptions.RequestException as e:
				print(f"blad strony {url}")


			if result_df.loc[index, "COMP_SCRAP_MAIL"] == "1" and result_df.loc[index, "COMP_SCRAP_TEL"] == "1" \
					and result_df.loc[index, "COMP_SCRAP_FAX"] == "1" and result_df.loc[index, "COMP_SCRAP_POST_CODE"] == "1"\
					and result_df.loc[index, "COMP_SCRAP_STREET"] == "1" and result_df.loc[index, "COMP_SCRAP_ESP"] == "1":
				break #zatrzymujemy program jeśli wszystkie informacje byly sprawdzone i poprawne

		result_df.at[index, 'SCRAP_URL'] = adres_www
		result_df.at[index, 'COMP_SCRAP_URL'] = '1'
		if len(scraped_email) != 0:
			result_df.at[index, 'SCRAP_MAIL'] = scraped_email[0]
		if len(scraped_tel) != 0:
			result_df.at[index, 'SCRAP_TEL'] = ''.join(i for i in scraped_tel[0] if i.isdigit())
		if len(scraped_fax) != 0:
			result_df.at[index, 'SCRAP_FAX'] = ''.join(i for i in scraped_fax[0] if i.isdigit())
		if len(scraped_address_zip_city) != 0:
			result_df.at[index, 'SCRAP_POST_CODE'] = scraped_address_zip_city[0][:6]
		if len(scraped_address_street) != 0:
			result_df.at[index, 'SCRAP_STREET'] = scraped_address_street[0]

		result_df.at[index, 'SCRAP_ESP'] = scraped_esp




		if not result_df.loc[index, "COMP_SCRAP_MAIL"] == "1": #by wszędzie gdzie nie znaleziono poprawnej informacji, zaznaczyć 0
			result_df.at[index, 'COMP_SCRAP_MAIL'] = '0'
		if not result_df.loc[index, "COMP_SCRAP_TEL"] == "1":
			result_df.at[index, 'COMP_SCRAP_TEL'] = '0'
		if not result_df.loc[index, "COMP_SCRAP_FAX"] == "1":
			result_df.at[index, 'COMP_SCRAP_FAX'] = '0'
		if not result_df.loc[index, "COMP_SCRAP_POST_CODE"] == "1":
			result_df.at[index, 'COMP_SCRAP_POST_CODE'] = '0'
		if not result_df.loc[index, "COMP_SCRAP_STREET"] == "1":
			result_df.at[index, 'COMP_SCRAP_STREET'] = '0'
		if not result_df.loc[index, "COMP_SCRAP_ESP"] == "1":
			result_df.at[index, 'COMP_SCRAP_ESP'] = '0'



		if i in range(step, len(result_df), step):
			result_df.to_csv(f"output/out_{i}.csv", index=False, sep=';',
							 columns=baza_teleadresowa_jst_df.columns.tolist() + new_columns, encoding="windows-1250",
							 errors='ignore')
			print(f"Zapisano plik output/out_{i}.csv")



	f = open('output/out.html', 'w', encoding="utf-8")
	a = result_df.to_html()
	f.write(a)
	f.close()

	result_df.to_csv('output/out.csv', index=False, sep=';', columns=baza_teleadresowa_jst_df.columns.tolist() + new_columns, encoding="windows-1250", errors='ignore')




