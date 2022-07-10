import datetime
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from variable import menu, importLoc, holidayWeb, exportLoc
from config import pastUrl, pastQueryString, currentUrl, currentQueryString, futureUrl, futureQueryString, headers
import calendar
# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
@dataclass
class Holiday:
    name: str
    date: datetime   
    
    
    def __str__ (self):
        return f"{self.name} ({self.date:%Y-%m-%d})"
# -------------------------------------------
# The HolidayList class acts as a wrapper and container
# For the list of holidays
# Each method has pseudo-code instructions
# --------------------------------------------
@dataclass
class HolidayList:
    innerHolidays: list
   
    
    def findHoliday(self,holidayName, date):
        # Find Holiday in innerHolidays
        for i in self.innerHolidays:
            # Return Holiday
            if holidayName == i.name and date == i.date: return i
        return False

    
    def addHoliday(self, holidayObj):
        # Make sure holidayObj is an Holiday Object by checking the type
        if type(holidayObj) is not Holiday: 
            print("\nError:\nThe object you tried to add is not a holiday.")
            return False
        # Use innerHolidays.append(holidayObj) to add holiday
        else:
            holidayInList = self.findHoliday(holidayObj.name,holidayObj.date)
            if holidayInList == False:
                self.innerHolidays.append(holidayObj)
                # print to the user that you added a holiday
                print(f"\nSuccess:\n{holidayObj.name} ({holidayObj.date:%Y-%m-%d}) has been added to the holiday list.")
                return True
            else:
                print(f"\nError:\n{holidayObj.name} ({holidayObj.date:%Y-%m-%d}) is already in the holiday list.")
                return False


    def removeHoliday(self,holidayName, date):
        holidayFound = self.findHoliday(holidayName, date)
        # Find Holiday in innerHolidays by searching the name and date combination.
        if holidayFound != False:
            for i in self.innerHolidays:
                if holidayName == i.name and date == i.date:
                    # inform user you deleted the holiday
                    print(f"\nSuccess:\n{holidayName} ({date:%Y-%m-%d}) has been removed from the holiday list.")
                    # remove the Holiday from innerHolidays
                    self.innerHolidays.remove(i)
                    return True
        else:
            print(f"\nError:\n{holidayName} ({date:%Y-%m-%d}) not found.")
            return False


    def read_json(self,filelocation):
        # Read in things from json file location
        with open(filelocation,"r") as holidayJSON:
            data = json.load(holidayJSON)
            for i in data["holidays"]:
                date = datetime.datetime.strptime(i["date"],"%Y-%m-%d")
                # Since addHoliday would have print out message, which is not preferrable,
                # use findHoliday to prevent duplicate and append non-duplicated holiday into the list directly
                if self.findHoliday(i["name"],date) != False:
                    newHoliday = Holiday(i["name"],date)
                    self.innerHolidays.append(newHoliday)
                

    def save_to_json(self,filelocation):
        # Write out json file to selected file.
        with open(filelocation,"w") as holidayJSON:
            tempHolidayList = []
            for i in self.innerHolidays:
                holiday = {"name":i.name, "date":i.date.strftime("%Y-%m-%d")}
                tempHolidayList.append(holiday)
            json.dump(tempHolidayList,holidayJSON)

        
    def scrapeHolidays(self):
        # Scrape Holidays from https://www.timeanddate.com/holidays/us/
        # Remember, 2 previous years, current year, and 2  years into the future. 
        # You can scrape multiple years by adding year to the timeanddate URL. For example https://www.timeanddate.com/holidays/us/2022
        for i in range(2020,2025):
            html = getHTML(f"{holidayWeb}{i}?hol=33554809")
            soup = BeautifulSoup(html,"html.parser") 
            table = soup.find("table", attrs={"id":"holidays-table"})
            body = table.find("tbody")
            for row in body.find_all("tr", class_ = "showrow"):
                date = row.find("th").text
                dateYear = f"{i} {date}"
                holidate = datetime.datetime.strptime(dateYear, "%Y %b %d")
                name = row.find_all("td")[1].text
                # Check to see if name and date of holiday is in innerHolidays array
                # Add non-duplicates to innerHolidays
                holidayFound = self.findHoliday(name, holidate)
                if holidayFound == False:
                    newHoliday = Holiday(name, holidate)
                    self.innerHolidays.append(newHoliday)
    

    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        return len(self.innerHolidays)

    
    def filter_holidays_by_week(self,year, week_number):
        # Use a Lambda function to filter by week number and save this as holidays, use the filter on innerHolidays
        # Week number is part of the the Datetime object
        # Cast filter results as list
        holiInWeek = list(filter(lambda x: x.date.isocalendar()[0] == year and x.date.isocalendar()[1] == week_number, self.innerHolidays))
        # return your holidays
        return holiInWeek


    def displayHolidaysInWeek(self,holidayList):
        # Use your filter_holidays_by_week to get list of holidays within a week as a parameter
        # holiList is supposed to be a list that contains the year and week number as int
        holiInWeek = self.filter_holidays_by_week(holidayList[0], holidayList[1])
        # Output formated holidays in the week. 
        # * Remember to use the holiday __str__ method.
        for i in holiInWeek:
            print(i)


    def getWeather(self, weekInYear):
        print()
        dayList = []
        # Ensure the dateList is added properly.
        dateList = [1,2,3,4,5,6,0]
        for i in dateList:
            dayList.append(datetime.datetime.strptime(f"{weekInYear[0]}-{weekInYear[1]}-{i}","%Y-%W-%w"))
        # Adjust the diff between %w days in week and isocalendar days in week
        todayInWeek = datetime.datetime.now().isocalendar()[2]-1
        # Query API for weather in that week range
        if todayInWeek < 5: dayAndWeather = dayNotInWeekend(todayInWeek, dayList)
        # Wince Weather API can only track back 5 days, When today is Weekend, only pushes back four days
        else: dayAndWeather = dayInWeekend(todayInWeek, dayList)
        holiInWeek = self.filter_holidays_by_week(weekInYear[0], weekInYear[1])
        for i in holiInWeek:
            for j in range(len(dayAndWeather)):
                if i.date == dayAndWeather[j]["date"]:
                    print(f"{i} - {dayAndWeather[j]['weather']}")


    def viewCurrentWeek(self):
        # Use the Datetime Module to look up current week and year
        current = datetime.datetime.now()
        currentYear = current.isocalendar()[0]
        currentWeekNumber = current.isocalendar()[1]
        weekInYear = [currentYear, currentWeekNumber]
        # Ask user if they want to get the weather
        option = checkYesOrNo("\nWould you like to see this week's weather? [y/n]: ")
        print("\nThese are the holidays for this week:")
        # If yes, use your getWeather function and display results
        if option: self.getWeather(weekInYear)
        # Use your displayHolidaysInWeek function to display the holidays in the week
        else: self.displayHolidaysInWeek(weekInYear)
        
# Used for displaying main menu.
def lineSeparator(str):
    print(f"\n{str}\n{'='*len(str)}")


def getHTML(url):
    response = requests.get(url)
    return response.text

# Used to determine whether the user input is correct for choose menu options
def detMenuInput(option):
    if option.isnumeric() == False:
        print("\nEnter a number to choose option.")
        return 0
    elif int(option) not in range(1,6):
        print("\nInvalid choice. Please try again.")
        return 0
    else: return int(option)

# Used to convert user input into date properly.
def inputIsDate(isDate, holiDate):
    try:
        holiDateTime = datetime.datetime.strptime(holiDate,"%Y-%m-%d")
        isDate = True
        return holiDateTime
    except:
        print("\nError:\nInvalid date. Please try again.")
        return isDate

# Check user input is yes or no
def checkYesOrNo(string):
    while True:
        option = input(string).lower()
        if option != "y" and option != "n": print("\nInvalid input. Please try again.")
        else: break
    if option == "y": return True
    else: return False


def getYear(string):
    if string.isnumeric() == False:
        print("\nPlease put in a number between 2000 to 2030 for year.")
        return False
    elif int(string) not in range(2000,2031):
        print("\nThe year you entered is out the range of range for the list.")
        return False
    else: return int(string)


def getWeekNumber(year, string):
    if string == "" and year == datetime.datetime.now().year:
        return 100
    elif string.isnumeric() == False:
        print("\nPlease put a number between 1 to 52 for week number.")
        return False
    elif int(string) not in range(1,53):
        print("\nInvalid week number. Please try again.")
    else: return int(string)


def getAPI(url, headers, params):
    response = requests.request("GET",url, headers=headers, params= params)
    return response.json()

def dayNotInWeekend(todayInWeek, dayList):
    dayAndWeather = []
    try:
        if todayInWeek > 0:
            for i in range(todayInWeek):
                dayUNIX = calendar.timegm(dayList[i].utctimetuple())
                pastQueryString.update({"dt":f"{dayUNIX}"})
                pastAPI = getAPI(pastUrl, headers, pastQueryString)
                weather = pastAPI["current"]["weather"][0]["description"].title()
                dayAndWeather.append({"date":dayList[i], "weather":weather})
        currentAPI = getAPI(currentUrl, headers, currentQueryString)
        weather = currentAPI["weather"][0]["description"].title()
        dayAndWeather.append({"date":dayList[todayInWeek], "weather":weather})
        futureQueryString.update({"cnt":f"{6-todayInWeek}"})
        futureAPI = getAPI(futureUrl, headers, futureQueryString)
        for i in range(6-todayInWeek):
            weather = futureAPI["list"][i]["weather"][0]["description"].title()
            dayAndWeather.append({"date":dayList[todayInWeek+i+1], "weather":weather})
    except:
        print("\nSomething wrong happened.")
        dayAndWeather.append({"date":"nothing", "weather":"nothing"})
    return dayAndWeather


def dayInWeekend(todayInWeek,dayList):
    dayAndWeather = []
    try:
        for i in range(todayInWeek-4,todayInWeek):
            dayUNIX = calendar.timegm(dayList[i].utctimetuple())
            pastQueryString.update({"dt":f"{dayUNIX}"})
            pastAPI = getAPI(pastUrl, headers, pastQueryString)
            weather = pastAPI["current"]["weather"][0]["description"].title()
            dayAndWeather.append({"date":dayList[i], "weather":weather})
        currentAPI = getAPI(currentUrl, headers, currentQueryString)
        weather = currentAPI["weather"][0]["description"].title()
        dayAndWeather.append({"date":dayList[todayInWeek], "weather":weather})
        if todayInWeek == 5:
            futureQueryString.update({"cnt":"1"})
            futureAPI = getAPI(futureUrl, headers, futureQueryString)
            weather = futureAPI["list"][0]["weather"][0]["description"].title()
            dayAndWeather.append({"date":dayList[6], "weather":weather})
    except:
        print("\nSomething wrong happened.")
        dayAndWeather.append({"date":"nothing", "weather":"nothing"})
    return dayAndWeather


def addAHoliday(holiList):
    lineSeparator("Add a Holiday")
    holiName = input("Holiday: ")
    holiDate = input("Date: ")
    isDate = inputIsDate(False, holiDate)
    while isDate == False:
        trueDate = input(f"\nDate for {holiName}: ")
        isDate = inputIsDate(isDate, trueDate)
    holiday = Holiday(holiName,isDate)
    holidayAdded = holiList.addHoliday(holiday)
    return holidayAdded


def removeAHoliday(holiList):
    lineSeparator("Remove a Holiday")
    holidayRemoved = False
    while holidayRemoved == False:
        holiName = input("Holiday Name: ")
        holiDate = input("Holiday Date: ")
        isDate = inputIsDate(False, holiDate)
        while isDate == False:
            trueDate = input(f"\nDate for {holiName}: ")
            isDate = inputIsDate(isDate, trueDate)
        holidayRemoved = holiList.removeHoliday(holiName, isDate)
    return holidayRemoved


def saveHolidayList(changeMade, holiList):
    lineSeparator("Saving Holiday List")
    if changeMade:
        while True:
            option = checkYesOrNo("\nAre you sure you want to save your changes? [y/n]: ")
            if option:
                holiList.save_to_json(exportLoc)
                print("\nSuccess:\nYour changes have been saved.")
                break
            else: 
                print("\nCanceled:\nHoliday list file save canceled.")
                break   
    else:
        print("\nAll changes have been saved. You will be redirected to the main menu.")
            

def viewHolidays(holiList):
    lineSeparator("View Holidays")
    #only accept year from 2000 to 2030
    validYear = getYear(input("Which Year?: "))
    while validYear == False:
        validYear = getYear(input("\nWhich Year?: "))
    #Only display current week option for the current year
    if validYear == datetime.datetime.now().isocalendar()[0]:
        validWeekNumber = getWeekNumber(validYear, input("Which week? #[1-52, Leave blank for the current week]: "))
    else:
        validWeekNumber = getWeekNumber(validYear, input("Which week? #[1-52]: "))
    while validWeekNumber == False:
        if validYear == datetime.datetime.now().isocalendar()[0]:
            validWeekNumber = getWeekNumber(validYear, input("\nWhich week? #[1-52, Leave blank for the current week]: "))
        else:
            validWeekNumber = getWeekNumber(validYear, input("\nWhich week? #[1-52]: "))
    if validWeekNumber == 100:
        holiList.viewCurrentWeek()
    else:
        print(f"\nThese are the holidays for {validYear} week #{validWeekNumber}:")
        holiList.displayHolidaysInWeek([validYear,validWeekNumber])


def listExit(changeMade):
    lineSeparator("Exit")
    if changeMade: option = checkYesOrNo("\nAre you sure you want to exit?\nYour changes will be lost.\n[y/n] ")
    else: option = checkYesOrNo("\nAre you sure you want to exit? [y/n] ")
    return option


def main():
    # Large Pseudo Code steps
    # -------------------------------------
    # 1. Initialize HolidayList Object
    holidayList = HolidayList([])
    # 2. Load JSON file via HolidayList read_json function
    holidayList.read_json(importLoc)
    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    holidayList.scrapeHolidays()
    lineSeparator("Holiday Management")
    print(f"There are {holidayList.numHolidays()} holidays stored in the system.")
    # Since the initially scrapped data is not store yet, the change is made by default.
    changeMade = True
    # 4. Create while loop for user to keep adding or working with the Calender 
    while True:
        # 5. Display User Menu (Print the menu)
        lineSeparator("Holiday Menu")
        choice = detMenuInput(input(menu))
        # 6. Take user input for their action based on Menu and check the user input for errors
        # 7. Run appropriate method from the HolidayList object depending on what the user input is
        # 8. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 
        if choice == 0: continue
        elif choice == 1:     
            changeMade = addAHoliday(holidayList)
            continue
        elif choice == 2:   
            changeMade = removeAHoliday(holidayList)
            continue
        elif choice == 3:
            saveHolidayList(changeMade, holidayList)
            changeMade = False
            continue
        elif choice == 4:
            viewHolidays(holidayList)
            continue
        elif choice == 5:
            wantExit = listExit(changeMade)
            if wantExit:
                print("\nGoodbye!")
                break
            else:
                print("\nSince you do not want to exit, you will be redirected to the main menu.")
                continue


if __name__ == "__main__":
    main()
# Additional Hints:
# ---------------------------------------------
# You may need additional helper functions both in and out of the classes, add functions as you need to.
#
# No one function should be more then 50 lines of code, if you need more then 50 lines of code
# excluding comments, break the function into multiple functions.
#
# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.
