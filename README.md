# Zheding's Holiday Manager

**Prerequisite**

Python is installed (a version higher than 3.8 is highly recommended)

**File Explained**

Holiday_List.json: JSON file generated from "Save Holiday List" feature in the Holiday Manager

holidays.json Initial JSON to import some holidays to start with 

variable.py: Some variables stored in the separate file to make the main python file more readable

Holiday_Manager.png: Flowchart for Holiday Manager

Holiday_Manager.py: Main program of the assessment

**Instructions**

1. Ask the owner for the "config.py" in order for the program to run properly

2. Download "config.py", "holidays.json", "variable.py", and "Holiday_Manager.py" and put them in the same folder

3. Open python IDE of your choice and set the directory to the folder in step 2

4. Run "Holiday_Manager.py" to run the program.

**Important Features**

1. All user input of dates should be in format of %Y-%m-%d (ex. 2020-01-01), Otherwise the program will print an error message and let user input the date again.

2. The View Holidays function only support view holidays in week1 through week 52 in 2000 to 2030. Try to avoid adding a holiday out side the range because you can not
see the holiday in the python directly. (You can still see the holiday by saving the file to "Holiday_list.json" and view it from there).

3. Since the Open Weather Map API only supports Historical Weather Data for the last 5 days, user will not be able to see the whole list of weather if user run the
program in Weekends.

