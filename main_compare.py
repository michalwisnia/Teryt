import numpy as np
import pandas as pd
from main import dtypes
import requests
from bs4 import BeautifulSoup
import re
from url import get_kontakt_url


if __name__ == "__main__":
	baza_teleadresowa_jst_df = pd.read_csv("csv_Baza_teleadresowa_jst_stan_na_19_05_2021.csv", sep=";",  encoding="windows-1250", dtype=dtypes)
	baza_teleadresowa_jst_df = baza_teleadresowa_jst_df.loc[:,~baza_teleadresowa_jst_df.columns.str.contains('^Unnamed')]



