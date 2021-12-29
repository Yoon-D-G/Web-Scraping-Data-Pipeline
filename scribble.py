import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import re


# # # request = requests.get('https://archivecat.lancashire.gov.uk/calmview/advanced.aspx?src=CalmView.Catalog')
# # # soup = BeautifulSoup(request.content, 'html.parser')
# # driver = webdriver.Firefox()
# # driver.get('https://archivecat.lancashire.gov.uk/calmview/advanced.aspx?src=CalmView.Catalog')
# # search_bar = driver.find_element_by_id("ctl00_main_DSCoverySearch1_ctl00_SearchText_AltRefNo_default")
# # search_bar.clear()
# # search_bar.send_keys("wcw")
# # search_bar.send_keys(Keys.RETURN)

# # # with open('scribble', 'w') as file:
# # #     file.write(str(soup))

# print('ewen')

# self.dataframe = pd.DataFrame(columns=[
#     'Document Reference',
#     'Title', 
#     "Testator's name",
#     'Occupation/status',
#     'Place',
#     'Contents'
# ])

# def append_data_to_dataframe(self, doc_ref, title, name, occupation, place, contents):
#     self.dataframe.append({
#         'Document Reference': doc_ref,
#         'Title': title, 
#         "Testator's name": name,
#         'Occupation/status': occupation,
#         'Place': place,
#         'Contents': contents
#     }, ignore_index=True) 

# data_list = [['Document reference', 'WCW/Supra/C554A/1'], ['Title', 'Archdeaconry of Chester Probate Records'], [["Testator's name: William Abbot"], ['Occupation/status: timber merchant'], ('Contents: will, codicil, wrapper', ['Place: Liverpool'])], ['Date', '04 Jul 1795'], ['Level', 'Item'], ['Access', 'This material is available to view at Lancashire Archives. See our website or contact us for more details.'], ['Access status', 'Open']]

# print(data_list[0][1] + '\n' + 
# data_list[1][1] + '\n' +
# data_list[2][0][0].split(':')[1].strip() + '\n' + 
# # data_list[2][1][0].split(':')[1].strip() + '\n' +
# # data_list[2][2][0].split(':')[1].strip() + '\n' + 
# # data_list[2][2][1][0].split(':')[1].strip() + '\n' +
# # data_list[3][1])

# # # doc_ref, title, name, occupation, place, date, contents

# # data = [['Document reference', 'WCW/Supra/C554A/1'], ['Title', 'Archdeaconry of Chester Probate Records'], [["Testator's name: William Abbot"], ['Occupation/status: timber merchant'], ('Contents: will, codicil, wrapper', ['Place: Liverpool'])], ['Date', '04 Jul 1795'], ['Level', 'Item'], ['Access', 'This material is available to view at Lancashire Archives. See our website or contact us for more details.'], ['Access status', 'Open']]

# # for d in data:
# #     for i in d:
# #         for j in i:
# #             for k in j:
# #                 if len(k) > 1:
# #                     print(k)

# # def recurse(data):
# #     for d in recurse(data):
# #         print(d)
# # recurse(data)


# # def flatten(data):
# #     for x in data:
# #         if (isinstance(x, list) or isinstance(x, tuple)) and not isinstance(x, str):
# #             yield from flatten(x)
# #         else:
# #             yield x

# # flat_list = [i for i in flatten(data)]
# # print(flat_list)

# # data = ['Document reference', 'WCW/Supra/C554A/1', 'Title', 'Archdeaconry of Chester Probate Records', "Testator's name: William Abbot", 'Occupation/status: timber merchant', 'Contents: will, codicil, wrapper', 'Place: Liverpool', 'Date', '04 Jul 1795', 'Level', 'Item', 'Access', 'This material is available to view at Lancashire Archives. See our website or contact us for more details.', 'Access status', 'Open']

# # # if 'Document reference' in data:
# # #     print(data[data.index('Document reference') + 1]) 

# # # for i in data:
# # #     if 'Occupation' in i:
# # #         print(i.split(':')[1].strip())

# # print([1, 2, 3].split())

# def request_html(url):
#     request = requests.get(url)
#     content = request.content
#     soup = BeautifulSoup(content, 'html.parser')
#     print(soup)

# request_html('https://archivecat.lancashire.gov.uk/calmview/Overview.aspx?src=CalmView.Catalog&r=((AltRefNo%3d%27wcw%27))')

def year_finder(data):
    year_finder = re.compile('\d\d\d\d')
    year = re.findall(year_finder, data)
    return year

data = "20 Dec 1824 (1st grant), 8 Nov 1856 (2nd grant)"

for year in year_finder(data):
    data = data.replace(year, '')
    print(data)
day_finder = re.compile('(\d\d|\d)(\s|[a-zA-Z])')
days = re.findall(day_finder, data)
if days:
    print([day[0] for day in days])
else:
    print(None)

[('20', ' '), ('24', ' '), ('1', 's'), ('8', ' '), ('56', ' '), ('2', 'n')]

[('0', ' '), ('4', ' '), ('1', 's'), ('8', ' '), ('6', ' '), ('2', 'n')]

