from urllib.request import Request, urlopen
import zipcodes
from bs4 import BeautifulSoup as soup
import re
from collections import deque
import mysql.connector

cnx = mysql.connector.connect(host='db-mysql-nyc1-rentometer-do-user-7038014-0.db.ondigitalocean.com',
							user='matt-test', password='xyerztz871tiikkp', port='25060', database='rentometer')
cursor = cnx.cursor()

def main():
	zip_map = zipcodes.get_zips()
	urls = create_zipcode_url_strings(zip_map.keys())
	queue = deque(urls)
	page_count = [1]
	while queue:
		zip_code_link = queue.pop()
		zip_code = re.search("zip-(\d{5})/", zip_code_link)
		page = query(zip_code_link)
		property_links = get_property_links(page, queue, page_count)
		if property_links:
			commit_links(property_links, zip_code.group(1))


def commit_links(property_links, zip_code):
	for link in property_links:
		sql = "INSERT INTO property_links(zipcode,link) VALUES ('" + zip_code + "','" + link + "')"
		cursor.execute(sql)
	cnx.commit()

def query(url):
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	webpage = urlopen(req).read()
	
	return webpage


def get_property_links(webpage, queue, count):
	page = soup(webpage, "html.parser")
	hrefs = page.findAll("a")
	property_links = []

	for href in hrefs:
		h = href.get('href')

		next_page = re.search('page', str(h))

		if next_page:
			if int(h[-1:]) > len(count):
				count.append(1)
				queue.append("https://www.rent.com" + h)
			continue

		if h and h.startswith('/') and re.search('(\d+)$', h):
			property_links.append("https://www.rent.com" + h)

	return property_links

def create_zipcode_url_strings(keys):
	ret = []
	for key in keys:
		ret.append("https://www.rent.com/zip-" + key + "/apartments_condos_houses_townhouses")
	return ret

if __name__ == "__main__":
	main()