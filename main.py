import pandas as pd
import numpy as np
from csv import DictReader
import requests

def url_checker(url: object) -> object:
	try:
		#Get Url
		get = requests.get(url)
		# if the request succeeds
		if get.status_code == 200:
			return(f"{url}: is reachable")
		else:
			return(f"{url}: is Not reachable, status_code: {get.status_code}")

	#Exception
	except requests.exceptions.RequestException as e:
        #print URL with Errs
		print(e)

if __name__ == '__main__':
    with open('csv_Baza_teleadresowa_jst_stan_na_19_05_2021.csv', 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
    df = pd.read_csv('csv_Baza_teleadresowa_jst_stan_na_19_05_2021.csv', encoding = 'unicode_escape', sep=';', lineterminator='\r')
    #for col_name in df.columns:
        #print(col_name)
    for adres in df["adres www jednostki"]:
	    if not str(adres).startswith("http://"):
	        adres = "http://" + adres
	    print(url_checker(adres))


