from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from calendar import monthrange
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

input = open('DateCriteria.txt', 'r')
input_seperated = input.read().split(';')

def input(i):
	return input_seperated[i][input_seperated[i].index('=') + 1 : input_seperated[i].index('|')].strip()

permit_homepage = input(0)
current_scheduled_day = None
earliest_day = datetime.strptime(input(1), "%m-%d-%Y").date()
next_available_dates_arr = []
next_available_dates_string = ''
next_available_dates_date = None
within_date_range = False
check_frequency = float(input(2))

#Method for finding the difference in months between two date objects.
def monthdelta(d1, d2):
    
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta

#Waits for an html element to exist before attempting to use it.
def wait_for(path, by_xpath = False, by_id = False, js_exe = False):

	if((not by_xpath and not by_id and not js_exe) or (by_xpath and by_id and js_exe)):
		raise ValueError('Either by_xpath, by_id, or js_exe must be True.')

	not_exist = True
	if(by_xpath):
		while not_exist:
			try:
				driver.execute_script("arguments[0].click();", driver.find_element_by_xpath(path))
				not_exist = False
				return driver.find_element_by_xpath(path)
			except:
				time.sleep(0.25)
	elif(by_id):
		while not_exist:
			try:
				driver.find_element_by_id(path)
				not_exist = False
				return driver.find_element_by_id(path)
			except:
				time.sleep(0.25)
	elif(js_exe):
		while not_exist:
			try:
				driver.execute_script(path)
				not_exist = False
				return driver.execute_script(path)
			except:
				time.sleep(0.25)

#Main method
def main(attempt, permit_homepage, current_scheduled_day, earliest_day, next_available_dates_arr, next_available_dates_string, next_available_dates_date, within_date_range):
	#Permit Homepage
	driver.get(permit_homepage)
	time.sleep(3)
	#Clicks on 'Inspections & Appointments'
	wait_for('//*[@id="ctl00_PlaceHolderMain_dvContent"]/div[2]/ul/li[1]/ul/li[5]/a', by_xpath = True)
	not_exist = True
	while not_exist:
		try:
			driver.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming"]/tbody/tr[6]/td/table/tbody/tr/td[4]/a').click()
			not_exist = False
		except NoSuchElementException:
			break
	#Finds all intake dates
	not_exist = True
	upcoming_inspection_dates = ''
	while not_exist:
		try:
			soup = BeautifulSoup(driver.page_source, 'html.parser')
			upcoming_inspection_dates = [datetime.strptime(item.text.split(': ')[1], '%m/%d/%Y').date() for item in soup.find('table', {'id' : 'ctl00_PlaceHolderMain_InspectionList_gvListUpcoming'}).findAll('span', text = re.compile('Date:'))]
			not_exist = False
		except AttributeError:
			raise Exception('Cannot Load Inspections and Appointments Tab')
	#Retrieves the max inspection day.
	current_scheduled_day = max(upcoming_inspection_dates)
	current_scheduled_day_action_num = upcoming_inspection_dates.index(current_scheduled_day) + 2
	#Clikcs on action button
	wait_for('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming_ctl0' + str(current_scheduled_day_action_num) + '_paActionMenu_lblActions"]', by_xpath = True)
	#Clicks on subaction: reschedule
	wait_for('//*[@id="ctl00_PlaceHolderMain_InspectionList_gvListUpcoming_ctl0' + str(current_scheduled_day_action_num) + '_paActionMenu_MenuItemContainer"]/div[2]/a', by_xpath = True)
	#Switches driver to iframe that pops up
	driver.switch_to.frame(wait_for('ACADialogFrame', by_id = True))
	#Retreives the next avaible dates as a string
	while len(next_available_dates_string) < 1:
		try:
			soup = BeautifulSoup(driver.page_source, 'html.parser')
			intake_dates = soup.find('span', {'id' : 'intake-dates'})
			next_available_dates_string = intake_dates.getText()
		except:
			time.sleep(0.5)
	#Next avaible date in different object types
	next_available_dates_arr = next_available_dates_string.split(' ')[:-1]
	all_dates = [datetime.strptime(item, "%m/%d/%Y").date() for item in next_available_dates_arr]
	next_available_dates_date = None
	for date in all_dates:
		#Makes the next available date whichever date is within date range
		if (date - earliest_day).days > 0:
			next_available_dates_date = date
			break
	#Difference between the next scheduled date and current scheduled date
	month_delta = current_scheduled_day.month - next_available_dates_date.month
	#Checks if the next available date is within the input time peramiters.
	if((next_available_dates_date - earliest_day).days > 0 and (current_scheduled_day - next_available_dates_date).days > 0):
		within_date_range = True
		print('Within Date Range:', within_date_range)
		#Clicks to the correct month group
		time.sleep(3)
		print('Month Delta:', month_delta)
		for i in range(month_delta):
			element = driver.find_element_by_xpath('//*[@id="ctl00_phPopup_calendar_AccelaLinkButton1"]/span')
			driver.execute_script("arguments[0].click();", element)
			time.sleep(4)
		#Locates day on calendar and clicks it
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		tag = soup.findAll('a', text = re.compile(str(next_available_dates_date.day)))[0]
		js = tag['href']
		js_next_date_link_int = int(js.split("'")[3].strip())
		print(js_next_date_link_int)
		#//*[@id="ctl00_phPopup_calendar_EventItem132218460000000000"]
		#Confirms selection
		wait_for("javascript:__doPostBack('ctl00$phPopup$calendar$calendar1','" + str(js_next_date_link_int) + "');var p = new ProcessLoading();p.showLoading(false);", js_exe = True)
		time.sleep(6)
		#Presses continue
		element = driver.find_element_by_xpath('//*[@id="ctl00_phPopup_calendar_divDayEventItems"]/div/span/label')
		driver.execute_script("arguments[0].click()", element)
		time.sleep(6)
		#Presses continue
		wait_for('//*[@id="ctl00_phPopup_lnkContinue"]/span', by_xpath = True)
		time.sleep(6)
		#Presses Submit
		wait_for('//*[@id="ctl00_phPopup_lnkContinue"]/span', by_xpath = True)
		time.sleep(6)
		wait_for('//*[@id="ctl00_phPopup_lnkFinish"]/span', by_xpath = True)
	else:
		print('The Next Available Date is Outside Your Time Range.')
		print('Current Scheduled Day:', current_scheduled_day)
		print('Your Earliest Allowable Day:', earliest_day)
		print('Earliest Next Available Day:', next_available_dates_date)
	df = pd.DataFrame({'PermitURL' : permit_homepage, 
		'CurrentTime' : datetime.now().strftime("%m/%d/%Y %H:%M:%S"), 
		'WithinRange' : within_date_range, 
		'CurrentScheduledDay' : current_scheduled_day,
		'EarliestAllowableDay' : earliest_day,
		'1stAvailableDay' : all_dates[0],
		'2ndAvailableDay' : all_dates[1],
		'3rdAvailableDay' : all_dates[2],
		'4thAvailableDay' : all_dates[3]}, index = [attempt])
	df = df.reindex(columns = ['PermitURL', 'CurrentTime', 'WithinRange', 'CurrentScheduledDay', 'EarliestAllowableDay', '1stAvailableDay', '2ndAvailableDay', '3rdAvailableDay', '4thAvailableDay'])
	try:
		df.to_csv('SeattlePermitScheduler.csv', mode = 'a', header = False)
	except PermissionError:
		print('Please Close the CSV File.')
if __name__ == '__main__':
	not_completed = True
	while not_completed:
		try:
			#Open autonomous Chrome browser
			options = webdriver.ChromeOptions()
			options.add_argument('--ignore-certificate-errors')
			options.add_argument('--test-type')
			options.add_argument('--start-maximized')
			driver = webdriver.Chrome(options = options)
			driver.implicitly_wait(20)
			attempt = 0
			while not within_date_range:

				attempt += 1
				print('-----------------------------------------')
				print('Attempt Number:', attempt)

				main(attempt, permit_homepage, current_scheduled_day, earliest_day, next_available_dates_arr, next_available_dates_string, next_available_dates_date, within_date_range)

				print('Next Attempt At:', datetime.now() + timedelta(minutes = check_frequency))
				print('Sleeping For ' + str(check_frequency) + ' minutes...')
				time.sleep(check_frequency * 60)
			not_completed = False
		except Exception as e:
			driver.close()
			print(e)