import requests
from bs4 import BeautifulSoup
import re

def get_kontakt_url(adres_www):
	kontakt_url = None
	if not adres_www.startswith("http"):
		url = "http://" + adres_www
		#print(str(i) + " " + url)
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
		#print(str(i) + " " + url)
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
			#continue

	return kontakt_url