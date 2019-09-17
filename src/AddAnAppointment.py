from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--test-type')

driver1 = webdriver.Chrome(options = options)
driver1.implicitly_wait(20)
driver1.set_window_size(781,830)
driver1.set_window_position(-10,0)

driver2 = webdriver.Chrome(options = options)
driver2.implicitly_wait(20)
driver2.set_window_size(781,830)
driver2.set_window_position(760,0)

input = open('DateCriteria.txt', 'r')
input_seperated = input.read().split(';')

def input(i):
	return input_seperated[i][input_seperated[i].index('=') + 1 : input_seperated[i].index('|')].strip()

permit_homepage = input(0)
current_scheduled_day = None
earliest_day = datetime.strptime(input(1), "%m-%d-%Y").date()

#Waits for an html element to exist before attempting to use it.
def wait_for(path, by_xpath = False, by_id = False, js_exe = False):

	if((not by_xpath and not by_id and not js_exe) or (by_xpath and by_id and js_exe)):
		raise ValueError('Either by_xpath, by_id, or js_exe must be True.')

	not_exist = True
	if(by_xpath):
		while not_exist:
			try:
				driver1.execute_script("arguments[0].click();", driver.find_element_by_xpath(path))
				driver2.execute_script("arguments[0].click();", driver.find_element_by_xpath(path))
				not_exist = False
				return driver.find_element_by_xpath(path)
			except:
				time.sleep(0.25)
	elif(by_id):
		while not_exist:
			try:
				driver1.find_element_by_id(path)
				driver2.find_element_by_id(path)
				not_exist = False
				return driver.find_element_by_id(path)
			except:
				time.sleep(0.25)
	elif(js_exe):
		while not_exist:
			try:
				driver1.execute_script(path)
				driver2.execute_script(path)
				not_exist = False
				return driver.execute_script(path)
			except:
				time.sleep(0.25)

driver1.get(permit_homepage)
driver2.get(permit_homepage)

driver1.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_dvContent"]/div[2]/ul/li[1]/ul/li[5]/a').click()
driver2.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_dvContent"]/div[2]/ul/li[1]/ul/li[5]/a').click()

max_page_num = 1

try:

	max_page_num = max([int(num) for num in driver1.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming"]/tbody/tr[6]/td/table/tbody/tr').text.split(' ')[2:-2]])
	max_page_num = max([int(num) for num in driver2.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming"]/tbody/tr[6]/td/table/tbody/tr').text.split(' ')[2:-2]])

except NoSuchElementException:

	print('Inspections & Appointments Pages:', max_page_num)

for i in range(max_page_num - 1):

	try: 
			
		driver1.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming"]/tbody/tr[6]/td/table/tbody/tr/td[4]/a').click()
		driver2.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming"]/tbody/tr[6]/td/table/tbody/tr/td[4]/a').click()
		time.sleep(1)

	except (NoSuchElementException, WebDriverException):

		break	

#Finds all intake dates
not_exist = True
upcoming_inspection_dates = ''
while not_exist:

	try:

		soup = BeautifulSoup(driver1.page_source, 'html.parser')

		upcoming_inspection_dates = [datetime.strptime(item.text.split(': ')[1], '%m/%d/%Y').date() for item in soup.find('table', {'id' : 'ctl00_PlaceHolderMain_InspectionList_gvListUpcoming'}).findAll('span', text = re.compile('Date:'))]
			
		not_exist = False

	except AttributeError:

		print('Sleeping...')
		time.sleep(0.25)

#Retrieves the max inspection day.
current_scheduled_day = max(upcoming_inspection_dates)

current_scheduled_day_action_num = upcoming_inspection_dates.index(current_scheduled_day) + 2

time.sleep(2)

#Clikcs on action button
driver1.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming_ctl0' + str(current_scheduled_day_action_num) + '_paActionMenu_lblActions"]').click()
driver2.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming_ctl0' + str(current_scheduled_day_action_num) + '_paActionMenu_lblActions"]').click()

print('Actions Pressed')

#Clicks on subaction: reschedule
driver1.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming_ctl0' + str(current_scheduled_day_action_num) + '_paActionMenu_MenuItemContainer"]/div[2]/a').click()
driver2.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming_ctl0' + str(current_scheduled_day_action_num) + '_paActionMenu_MenuItemContainer"]/div[2]/a').click()

#Switches driver to iframe that pops up
driver1.switch_to.frame(driver1.find_element_by_id('ACADialogFrame'))
driver2.switch_to.frame(driver2.find_element_by_id('ACADialogFrame'))

next_available_dates_string = ''

time.sleep(2)

#Retreives the next avaible dates as a string
while len(next_available_dates_string) < 1:

	try:

		soup = BeautifulSoup(driver1.page_source, 'html.parser')
		intake_dates = soup.find('span', {'id' : 'intake-dates'})
		next_available_dates_string = intake_dates.getText()

	except AttributeError:

		time.sleep(0.5)

#Next avaible date in different object types
next_available_dates_arr = next_available_dates_string.split(' ')[:-1]

all_dates = [datetime.strptime(item, "%m/%d/%Y").date() for item in next_available_dates_arr]

next_available_dates_date = []
for i in range(len(all_dates)):

	#Makes the next available date whichever date is within date range
	if (all_dates[i] - current_scheduled_day).days > 0:

		next_available_dates_date = [all_dates[i],all_dates[i+1]]
		break

print(next_available_dates_date)

#Locates day on calendar and clicks it
soup = BeautifulSoup(driver1.page_source, 'html.parser')
tag = soup.findAll('a', text = re.compile(str(next_available_dates_date[0].day)))[0]
js_1 = tag['href']
js_next_date_link_int_1 = int(js_1.split("'")[3].strip())

#Locates day on calendar and clicks it
soup = BeautifulSoup(driver2.page_source, 'html.parser')
tag = soup.findAll('a', text = re.compile(str(next_available_dates_date[1].day)))[0]
js_2 = tag['href']
js_next_date_link_int_2 = int(js_2.split("'")[3].strip())

driver1.execute_script(("javascript:__doPostBack('ctl00$phPopup$calendar$calendar1','" + str(js_next_date_link_int_1) + "');var p = new ProcessLoading();p.showLoading(false);"))
driver2.execute_script(("javascript:__doPostBack('ctl00$phPopup$calendar$calendar1','" + str(js_next_date_link_int_2) + "');var p = new ProcessLoading();p.showLoading(false);"))

time.sleep(6)

#Presses continue
element = driver1.find_element_by_xpath('//*[@id="ctl00_phPopup_calendar_divDayEventItems"]/div/span/label')
driver1.execute_script("arguments[0].click()", element)
element = driver2.find_element_by_xpath('//*[@id="ctl00_phPopup_calendar_divDayEventItems"]/div/span/label')
driver2.execute_script("arguments[0].click()", element)

time.sleep(4)

#Presses continue
driver1.find_element_by_xpath('//*[@id="ctl00_phPopup_lnkContinue"]/span').click()
driver2.find_element_by_xpath('//*[@id="ctl00_phPopup_lnkContinue"]/span').click()

time.sleep(4)

#Presses Submit
driver1.find_element_by_xpath('//*[@id="ctl00_phPopup_lnkContinue"]/span').click()
driver2.find_element_by_xpath('//*[@id="ctl00_phPopup_lnkContinue"]/span').click()

time.sleep(4)

driver1.find_element_by_xpath('//*[@id="ctl00_phPopup_lnkFinish"]/span').click()
driver2.find_element_by_xpath('//*[@id="ctl00_phPopup_lnkFinish"]/span').click()

driver1.close()
driver2.close()