import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings()


def check_url(adres_www): #do sprawdzenia dzialania strony www
	if not adres_www.startswith("http"):
		url = "http://" + adres_www
	else:
		url = adres_www

	try:
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
		response = requests.get(url, headers=headers, verify=False, timeout=10)

		if response.status_code == 200:
			return True
		else:
			return False
	except requests.exceptions.RequestException as e:
		try:
			url = e.request.url
			headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
			response = requests.get(url, headers=headers, verify=False, timeout=10)
			if response.status_code == 200:
				print("przekierowanie: ", url)
				return True, url
			else:
				return False
		except Exception as e:
			return False


def get_kontakt_url(adres_www): #do wydobycia adresu url strony kontaktowej oraz adresu url strony bip
	urls = []
	kontakt_url = None
	bip_url = None
	if not adres_www.startswith("http"):
		url = "http://" + adres_www
		#print(str(i) + " " + url)
	else:
		url = adres_www
	try:
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
		response = requests.get(url, headers=headers, verify=False, timeout=10)
		soup = BeautifulSoup(response.content, "html.parser")

		if soup.select_one("a[href*=bip]") is not None:
			a = soup.select_one("a[href*=bip]")
			href = a.get('href')
			if href is not None:
				if href.startswith("http"):
					bip_url = href
					urls.append(bip_url)
				else:
					bip_url = url + href
					urls.append(bip_url)
		elif soup.select_one("a[href*=biuletyn]") is not None:
			a = soup.select_one("a[href*=biuletyn]")
			href = a.get('href')
			if href is not None:
				if href.startswith("http"):
					bip_url = href
					urls.append(bip_url)
				else:
					bip_url = url + href
					urls.append(bip_url)

		if soup.find("a", string=re.compile("[kK]ontakt")):
			a = soup.find("a", string=re.compile("[kK]ontakt"))
			href = a.get('href')
			if href is not None:
				if href.startswith("http"):
					kontakt_url = href
				elif href.startswith("/pl") and url.endswith("pl/"):
					kontakt_url = url[:-3] + href
				elif not href.startswith("/") and not url.endswith("/"):
					kontakt_url = url + "/" + href
				else:
					kontakt_url = url + href
				urls.append(kontakt_url)

	except requests.exceptions.RequestException as e:
		try:
			url = e.request.url
			headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
			response = requests.get(url, headers=headers, verify=False, timeout=10)
			soup = BeautifulSoup(response.content, "html.parser")


			if soup.select_one("a[href*=bip]") is not None:
				a = soup.select_one("a[href*=bip]")
				href = a.get('href')
				if href is not None:
					if href.startswith("http"):
						bip_url = href
						urls.append(bip_url)
					else:
						bip_url = url + href
						urls.append(bip_url)
			elif soup.select_one("a[href*=biuletyn]") is not None:
				a = soup.select_one("a[href*=biuletyn]")
				href = a.get('href')
				if href is not None:
					if href.startswith("http"):
						bip_url = href
						urls.append(bip_url)
					else:
						bip_url = url + href
						urls.append(bip_url)

			if soup.find("a", string=re.compile("[kK]ontakt")):
				a = soup.find("a", string=re.compile("[kK]ontakt"))
				href = a.get('href')
				if href is not None:
					if href.startswith("http"):
						kontakt_url = href
					elif href.startswith("/pl") and url.endswith("pl/"):
						kontakt_url = url[:-3] + href
					else:
						kontakt_url = url + href
					urls.append(kontakt_url)
		except requests.exceptions.RequestException as e:
			print("blad")
		except:
			print("blad")
	except:
		print("blad")

	urls.append(url)

	return urls