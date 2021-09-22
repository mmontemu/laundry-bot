#This is a bot that will create a dataset of laundry machine openings
#imports

#scheduling libraries
import schedule
import time
#google sheets libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#scraping library
import requests
#library used for getting time
from datetime import datetime #why




#If you are using this for some reason, update these two variables with the url to the washing machine tracker and your # of machines
#You also need to update the name of your credentials file for your service account and to set sheetName to the name of your spreadsheet
#Also you can change the frequency that the bot checks the washers and dryers -- in minutes between checks
url = "url of washing machine tracker"
numberOfMachines = 8
laundryKeyFile = 'Name of Json Key File'
sheetName = "Laundry Data"
checkFrequency = 15

#use this https://www.youtube.com/watch?v=cnPlKLEGR7E& if you are stupid like me and documentation hurts your head






#stolen code from stack overflow - sets up spreadsheet
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(laundryKeyFile, scope)
client = gspread.authorize(creds)
sheet = client.open(sheetName)
sh = sheet.get_worksheet(0)

#sets up days of the week for later use
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
typeList = []
startIndx = 0
#sets up dryer and washer statuses -- true is washer and false is dryer
content = requests.get(url).text
for i in range(numberOfMachines) :
    num = int(content.find("class=\"type\"", startIndx, len(content)))
    if content[num + 13] == "W" : #jank
        typeList.append(True)
    else :
        typeList.append(False)







#freeMachines is the amount of machines that are open at that time
#content is the entire html page
#the num and startIndx variables are probably stupid but they work
def laundryScraper() :
    content = requests.get(url).text
    startIndx = 0
    freeMachines = 0
    freeWashers = 0
    freeDryers = 0
    for i in range(numberOfMachines) :
        num = int(content.find("class=\"status\"", startIndx, len(content)))

        #if data is jank then I can exclude more cases, but for now I am only excluding the "In Use" state, leaving the others
        if content[num + 15] != "I" :
            freeMachines += 1
            if typeList[i] :
                freeWashers += 1
            else :
                freeDryers += 1
        startIndx = num + 1
    print(freeMachines)
    minu = str(datetime.today().minute)
    if len(str(datetime.today().minute)) == 1 :
        minu = "0" + minu
    #inserts into the spreadsheet [timestamp, day of week, hour/minutes, machines availible] 
    sh.insert_row([datetime.today().timestamp(), weekdays[datetime.today().weekday()], str(datetime.today().hour) + ":" + minu, freeWashers, freeDryers, freeMachines], 2)
    

schedule.every(checkFrequency).seconds.do(laundryScraper)
while True:
    schedule.run_pending()
    time.sleep(1)
