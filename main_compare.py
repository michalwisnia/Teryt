import pandas as pd
from main import dtypes


terytTypes = {
    'WOJ': 'object', 'POW': 'object', 'GMI': 'object', 'RODZ': 'object', 'NAZWA': 'object', 'NAZWA_DOD': 'object', 'STAN_NA': 'object'
}

new_columns = ['TERYT_WOJ', 'TERYT_POW', 'TERYT_NAZWA_SAMORZAU', 'TERYT_TYP_JST',
			   'COMP_WOJ', 'COMP_POW', 'COMP_NAZWA_SAMORZAU','COMP_TYP_JST',
               'PNA_WOJ', 'PNA_POW', 'PNA_GMI',
               'COMP_PNA_WOJ', 'COMP_PNA_POW', 'COMP_PNA_GMI']

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

	# print(result_df)

	teryt_df = pd.read_csv("data/TERC_Urzedowy_2022-03-14.csv", sep=";",  encoding="utf-8", dtype=terytTypes)

	spispna_df1 = pd.read_csv("data/spispna_miejscowosci.csv", sep=";",  encoding="windows-1250", dtype=spispnaTypes)

	spispna_df2 = pd.read_csv("data/spispna_miejscowosci2.csv", sep=";",  encoding="windows-1250", dtype=spispnaTypes)

	spispna_df = pd.concat([spispna_df1, spispna_df2], ignore_index=True)

	for index, row in result_df.iterrows():
		kod_teryt = row['Kod_TERYT']
		kod_pocztowy = row['Kod pocztowy']
		# print(kod_teryt)
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

		pna_row = spispna_df.loc[(spispna_df['PNA'] == kod_pocztowy)]

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

	f = open('out.html', 'w')
	a = result_df.to_html()
	f.write(a)
	f.close()

	result_df.to_csv('out.csv')




