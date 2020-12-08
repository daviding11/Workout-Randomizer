from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup 
import datetime
from datetime import date as dt
from datetime import datetime 
import re
import psycopg2

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

main_url = "https://www.bodybuilding.com/exercises/finder"

# grab list of urls for each exercise

driver.get(main_url)
xpath_num = 18

#while True:
#temp solution 3125
while xpath_num <= 993:

	#check if button still exist
	c = driver.page_source
	page_soup = soup(c,"html.parser")
	containers = page_soup.findAll("button", {"class":"bb-flat-btn bb-flat-btn--size-lg js-ex-loadMore ExLoadMore-btn"})
	#print(len(containers))
	'''
	if len(containers) == 0:
		break
	else:
	'''
	
	SCROLL_PAUSE_TIME = 1


	# Get scroll height
	last_height = driver.execute_script("return document.body.scrollHeight")

	while True:
		# Scroll down to bottom
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

		# Wait to load page
		time.sleep(SCROLL_PAUSE_TIME)

		# Calculate new scroll height and compare with last scroll height
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			   break
		last_height = new_height

	#click on button
	time.sleep(2.5)

	xpath = "//*[@id='js-ex-category-body']/div[2]/div[" + str(xpath_num) + "]/button"
	print(xpath)
	driver.find_element_by_xpath(xpath).click()
	xpath_num = xpath_num + 15

#grabbing all exercise URLs
c = driver.page_source
page_soup = soup(c,"html.parser")
containers = page_soup.findAll("div", {"class":"ExResult-row flexo-container flexo-between"})
url_list = []
array_length = len(containers)

## open up excel file

#filename = "Exercises.csv"
#f = open(filename,"w")
#headers = "NAME, RATING, E_TYPE, MUSCLE, EQUIPMENT, LEVEL, DESCRIPTION, BENEFIT_LIST \n"
#f.write(headers)

for i in range(array_length):
	contain = containers[i]
	exerciselink = contain.a["href"]
	link = "https://www.bodybuilding.com" + exerciselink
	url_list.append(link)

#remove bad urls

bad_urls = []

#open up connection
#Establish the Connection
conn = psycopg2.connect(database="xxx", user='postgres', password='xxx', host='localhost', port= '5434')

#Setting auto commit false
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()


#grab all the information from each exercise url
for i in range(len(url_list)):
	driver.get(url_list[i])

	c = driver.page_source
	page_soup = soup(c,"html.parser")

	if page_soup.find("div",{"class":"outage"}) is None:

		#get rating, exercise nme and description
		rating = page_soup.find("div",{"class":"ExRating-badge"}).text
		rating = "".join(rating.split())
		rating = str(rating)
		name = " ".join(re.findall("[a-zA-Z]+", page_soup.find("h1",{"class":"ExHeading ExHeading--h2 ExDetail-h2"}).text))

		if page_soup.find("div",{"class":"ExDetail-shortDescription grid-10"}) is None:
			description = ""
		else:
			description = " ".join(re.findall("[a-zA-Z]+", page_soup.find("div",{"class":"ExDetail-shortDescription grid-10"}).text))


		#confirming if exericse has the basic inforating
		if page_soup.find("div",{"class":"grid-3 grid-12-s grid-8-m"}) is None:
			e_type = ""
			muscle = ""
			equip = ""
			level = ""
		else:
			#grabbing basic attribute for exercise
			results = page_soup.find("div",{"class":"grid-3 grid-12-s grid-8-m"})
			results_2 = results.findAll("li")

			##needs adjust to deal if one of the fours does not appear
			for i in range(len(results_2)):
				text = " ".join(re.findall("[a-zA-Z:]+", results_2[i].text))
				text = text.split(":")
				category = text[0]
				item = text[-1][1:]

				if category == "Type":
					e_type = item
				elif category =="Main Muscle Worked":
					muscle = item
				elif category == "Equipment":
					equip = item
				elif category == "Level":
					level = item

		#e_type = " ".join(re.findall("[a-zA-Z]+", results_2[0].text.replace(',','')))
		#muscle = " ".join(re.findall("[a-zA-Z]+", results_2[1].text.replace(',','')))
		#equip = " ".join(re.findall("[a-zA-Z]+", results_2[2].text.replace(',','')))
		#level = " ".join(re.findall("[a-zA-Z]+", results_3[3].text)).split(" ")[1]

		#grab the benefits
		if page_soup.find("div",{"class":"ExDetail-benefits grid-8"}) is None:
			benefits = ""
		else:
			benefits = page_soup.find("div",{"class":"ExDetail-benefits grid-8"})
			benefits = benefits.findAll("li")

		benefit_list = []

		for i in range(len(benefits)):
			benefit_list.append(benefits[i].text)

		benefit_list = '|'.join(benefit_list)

	else:
		name = ""
		rating = ""
		e_type = ""
		muscle = ""
		equip = ""
		level = ""
		description = "" 
		benefit_list = ""

	#print(name + "," + rating + "," + e_type + "," + muscle + "," + equip + "," + level + "," + description + "," + benefit_list + "\n")
	#print(name + "," + e_type + "," + muscle + "," + equip + "," + level + "," + description + "," + benefit_list + "\n")
	#f.write(name + "," + rating + "," + e_type + "," + muscle + "," + equip + "," + level + "," + description + "," + benefit_list + "\n")

	#insert values into database
	SQL = 'INSERT INTO public."WORKOUT" ("NAME","LEVEL","MUSCLE_GROUP","EXERCISE_TYPE","EQUIPMENT","DESCRIPTION","BENEFIT_LIST","RATING") VALUES(%s,%s,%s,%s,%s,%s,%s,%s);'

	name = '{' + name + '}'
	level = '{' + level + '}'
	muscle = '{' + muscle + '}'
	e_type = '{' + e_type + '}'
	equip = '{' + equip + '}'
	description = '{' + description + '}'
	benefit_list = '{' + benefit_list + '}'
	rating = '{' + rating + '}'

	data = (name,level,muscle,e_type,equip,description,benefit_list,rating)
	cursor.execute(SQL,data)
	conn.commit()


	time.sleep(1)


# Closing the connection
conn.close()

print("done DIU LAY")
