import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/GIA_courses_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/GIA_courses.csv'

course_data = {'Level_Code': '', 'University': 'Governance Institute of Australia', 'City': '', 'Country': '',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': 'yes', 'Part_Time': 'yes', 'Prerequisite_1': '',
               'Prerequisite_2': '', 'Prerequisite_3': '', 'Prerequisite_1_grade': '', 'Prerequisite_2_grade': '',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': 'A', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': 'no', 'Face_to_Face': '',
               'Blended': 'no', 'Remarks': ''}

possible_cities = {'canberra': 'Canberra', 'bruce': 'Bruce', 'mumbai': 'Mumbai', 'melbourne': 'Melbourne',
                   'brisbane': 'Brisbane', 'sydney': 'Sydney', 'queensland': 'Queensland', 'perth': 'Perth',
                   'shanghai': 'Shanghai', 'bhutan': 'Bhutan', 'online': 'Online', 'hangzhou': 'Hangzhou',
                   'hanoi': 'Hanoi', 'bundoora': 'Bundoora', 'brunswick': 'Brunswick', 'bendigo': 'Victoria'}

possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    remarks_list = []
    actual_cities = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # COURSE TITLE
    title_container = soup.find('div', class_='w-event-detail-box')
    if title_container:
        title = title_container.find('h2')
        if title:
            course_data['Course'] = title.get_text()
            print('COURSE TITLE: ', course_data['Course'])

            # DECIDE THE LEVEL CODE
            for i in level_key:
                for j in level_key[i]:
                    if j in course_data['Course']:
                        course_data['Level_Code'] = i
            print('COURSE LEVEL CODE: ', course_data['Level_Code'])

            # DECIDE THE FACULTY
            for i in faculty_key:
                for j in faculty_key[i]:
                    if j.lower() in course_data['Course'].lower():
                        course_data['Faculty'] = i
            print('COURSE FACULTY: ', course_data['Faculty'])

            # COURSE LANGUAGE
            for language in possible_languages:
                if language in course_data['Course']:
                    course_data['Course_Lang'] = language
                else:
                    course_data['Course_Lang'] = 'English'
            print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # DESCRIPTION
    body_div = soup.find('div', class_='w-rte')
    if body_div:
        desc_list = []
        desc_p_list = body_div.find_all('p')
        if desc_p_list:
            for p in desc_p_list:
                desc_list.append(p.get_text().strip())
            desc_list = ' '.join(desc_list)
            course_data['Description'] = desc_list
            print('COURSE DESCRIPTION: ', desc_list)
        # DURATION
        duration_title = body_div.find('h2', text=re.compile(r'How long will it take me to complete postgraduate study\?',
                                                             re.IGNORECASE))
        if duration_title:
            dura_ul = duration_title.find_next_sibling('ul')
            if dura_ul:
                dura_li = dura_ul.find('li')
                if dura_li:
                    duration_text = dura_li.get_text().lower().strip()
                    converted_duration = dura.convert_duration(duration_text)
                    if duration_text is not None:
                        duration_l = list(converted_duration)
                        if duration_l[0] == 1 and 'Years' in duration_l[1]:
                            duration_l[1] = 'Year'
                        if duration_l[0] == 1 and 'Months' in duration_l[1]:
                            duration_l[1] = 'Month'
                        course_data['Duration'] = duration_l[0]
                        course_data['Duration_Time'] = duration_l[1]
                        print('COURSE DURATION: ', str(duration_l[0]) + ' / ' + duration_l[1])
    duration_tag = soup.find('h3', text=re.compile('CPD Hours', re.IGNORECASE))
    if duration_tag:
        duration_p = duration_tag.find_next_sibling('p')
        if duration_p:
            duration_text = duration_p.get_text().strip()
            if duration_text == '1':
                course_data['Duration'] = duration_text
                course_data['Duration_Time'] = 'Hour'
            else:
                course_data['Duration'] = duration_text
                course_data['Duration_Time'] = 'Hours'
            print('COURSE DURATION: ', str(course_data['Duration'] + ' / ' + course_data['Duration_Time']))

    # FEES
    fees = soup.find('h3', text=re.compile(r'Cost \(Inc GST\)', re.IGNORECASE))
    course_data['Local_Fees'] = ''
    if fees:
        local_list = []
        fee = fees.find_next('p')
        if fee:
            fee_list_temp = fee.get_text().split("$")
            if fee_list_temp:
                del fee_list_temp[0]
                fee_list = fee_list_temp
                for f in fee_list:
                    local_list.append(f)
                local_list = ' / '.join(local_list)
                course_data['Local_Fees'] = local_list
                course_data['Int_Fees'] = local_list
                print('LOCAL FEES: ', course_data['Local_Fees'])
                print('INTERNATIONAL FEES: ', course_data['Int_Fees'])
    # DELIVERY
    delivery_tag = soup.find('h3', text=re.compile('Details', re.IGNORECASE))
    if delivery_tag:
        temp_list = []
        delivery_list = delivery_tag.find_next_siblings('p')
        if delivery_list:
            for p in delivery_list:
                temp_list.append(p.get_text().lower().strip())
            temp_list = ' '.join(temp_list)
            if 'online' in temp_list or 'virtual' in temp_list:
                course_data['Online'] = 'yes'
                actual_cities.append('online')
            elif 'kpmg' in temp_list:
                course_data['Offline'] = 'yes'
                course_data['Face_to_Face'] = 'yes'
            elif 'institute' in temp_list:
                course_data['Offline'] = 'yes'
                course_data['Face_to_Face'] = 'yes'
            else:
                course_data['Offline'] = 'no'
                course_data['Online'] = 'no'
                course_data['Face_to_Face'] = 'no'
                actual_cities.append('sydney')
            if 'perth' in temp_list:
                actual_cities.append('perth')
            if 'sydney' in temp_list:
                actual_cities.append('sydney')
    else:
        course_data['Online'] = 'yes'
        course_data['Offline'] = 'yes'
        course_data['Face_to_Face'] = 'yes'
        actual_cities.append('online')
        actual_cities.append('sydney')
    print('DELIVERY: ', ' online: ' + course_data['Online'] + ' offline: ' + course_data['Offline'])
    print('CITY: ', actual_cities)

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities

    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance',
                          'Face_to_Face', 'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('GIA_courses_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)





