#READ Readme.txt

##############################
#    IMPORTING LIBRARIES     #
##############################

import sql
from getpass import getpass
from os import system
from time import sleep
from pickle import load
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt

##################################
#     FUNCTION DEFINATIONS       #
##################################

# call to clear screen
def clear_screen():  
    system('cls')
    #execute cmd command cls to clear terminal

# call to freeze screen. can also display text
def wait(text=None):  

    global time_sleep

    #if text is supplied then print it
    if text:
        print(text)
    sleep(time_sleep)

#call to get user input with error trapping
def get_input(description_1,  # menu text to be displayed
              description_2,  # Question to be displayed
              type_int=False,  # True if int is required
              data_range=None, # list of possible answers supplied if int
              screen_clear=True,  # True if screen needs to be cleared before asking question
              yes_no=False):  # True if input will be a yes/no type answer 
    while True: # loop till correct answer
        if screen_clear:
            clear_screen()
        if description_1 is not None: # if description 1 exists then display it
            print(description_1)
        print(description_2, end=':')# description 2 is printed as a prompt

        # if int is required
        if type_int:
            try:
                ch = int(input())
                if data_range is not None:  # if range is given then
                    if ch in data_range: # check if the input is valid
                        break
                    else:
                        wait('Warning:Enter valid data')
            except ValueError:  # if user inputs string
                wait('Warning:Enter a number')
        #if yes/no type answer is required
        elif yes_no:
            ch = input()
            if ch.lower() in ['y', 'yes']:
                return 1
            elif ch.lower() in ['n', 'no']:
                return 0
        else:
            ch = input()
            break

    return ch

# call to get login credential and match them
# called at start.
# returns true or false based on details provided
def login_screen():  

    global login_screen_text

    username = get_input(login_screen_text,'Username:')
    password = getpass('Password:')
    #check if the login details match as in login.dat file
    with open('login.dat', 'rb') as f:
        data = load(f)
        for log in data:
            # allow access if details match
            if log == username and data[log] == password:  
                wait('***Access Granted***')
                return True
        else:
            # Deny access if details don't match
            wait('***Access Denied***')
            return False


# call this function to get a list of roll_no
def get_roll_no_list(heading, append_999=False):  

    global get_roll_no_list_text

    # loop till correct input is provided
    while True:  
        clear_screen()
        print(heading, get_roll_no_list_text, sep='\n')
        input_string = input('Enter here:')
        # Exit condition
        if input_string == '': 
            return
        num = []
        # error may occur during conversion of string to int
        try:  
            # single num
            if ('-' not in input_string) and ('/' not in input_string):  
                num.append(int(input_string))
                break
            # multiple num separated by /
            elif '/' in input_string:  
                for string in input_string.split('/'):
                    num.append(int(string))
                break
            # Range of nums
            elif '-' in input_string:  
                if len(input_string.split('-')) != 2:  # handling bad input
                    wait('Warning:Use single "-"')
                else:
                    # executed if correct input
                    temp = []
                    for string in input_string.split('-'):  # will run twice
                        temp.append(int(string))
                    for value in range(temp[0], temp[1] + 1):
                        num.append(value)
                    break

        except ValueError:
            wait('Warning:Enter valid input')
    #append 999 a pseudo entry representing max marks
    if append_999:
        num.append(999)
    return num

# Display
def menu_1():  

    global menu_1_text
    
    menu_1_choice = get_input(menu_1_text, 'Enter choice', True, (1, 2, 3, 4))
    # runs if specific student is required
    if menu_1_choice == 1:  
        menu_1a()
    # runs if all data is required
    elif menu_1_choice == 2:  
        menu_1b()
    # custom search    
    elif menu_1_choice == 3:
        menu_1c()
    # Exit to menu
    elif menu_1_choice == 4: 
        return


# search by range/specific/multiple roll no
def menu_1a():
    
    global menu_1a_text
    
    number_list = get_roll_no_list(menu_1a_text, True)
    #exit condition
    if number_list == None:
        return
    #get data and display the following number_list as Roll number list
    search(number_list)


# supply list of roll no to display them in a table with subjects
def search(roll_no_list):  

    global search_query

    query = search_query + f'{tuple(roll_no_list)};'
    # use sql function custom_query to result of query
    data = sql.custom_query(query)
    #column headings
    head = ('Title', 'Roll No.', 'English', 'Math', 'Physics', 'Chemistry', 'CS', 'PE')
    clear_screen()
    #print the resultant table using tabulate
    print(tabulate(data, headers=head, tablefmt='fancy_grid'))
    print('999 is a pseudo entry representing "maximum marks"')
    #to pause the screen
    input('Press any key to exit:')


# all student display
def menu_1b():
    
    global menu_1b_text
    global column_names

    #sel(int) is the option selected
    sel = get_input(menu_1b_text, 'Enter Submenu number', True, list(range(1, 9)))
    #represents bool value if names are to be fetched
    get_names = 0
    # if require score of specific subject
    if sel in range(2, 8):  
        get_names = get_input(None, 'Display names?(y/n)', yes_no=True,screen_clear=False)
    #Exit condition
    elif sel == 8:
        return    
    if get_names:
        #if names are required then run this query
        query = f'select a.title ,b.* from student_list a natural join {column_names[sel - 1][0]} b order by roll_no;'
        data = sql.custom_query(query)
        head = list(column_names[sel - 1][1:])
        head.insert(0, ('title',)[0])
    else:
        #if names are not required then runt this query
        data = sql.get_data(table=column_names[sel - 1][0])
        head = column_names[sel - 1][1:]
    #clear screen and print the table using tabulate
    clear_screen()
    print(tabulate(data, headers=head, tablefmt='fancy_grid'))
    print('999 is a pseudo entry representing "maximum marks"')
    input('Press any key to exit:')

# search custom query
def menu_1c():
    #trapping error of: the user may enter incorrect sql syntax
    try:
        # runs till correct query is provided
        while True:  
            query = get_input('Enter you sql query to be executed', '-->', False)
            # commit may be used to make permenant changes to the table
            to_commit = get_input(None, 'Would you like to commit(y/n)', yes_no=True)
            #confirm the actions
            permission = get_input(query, 'Are you sure to execute this query?(y/n)', yes_no=True)
            #if permission is provided execute the query and commit if asked
            if permission:
                data = sql.custom_query(query, bool(to_commit))
                break
        #clear screen and print the table of sql output using tabulate
        clear_screen()
        print(tabulate(data, tablefmt='fancy_grid'))
        input('Press any key to exit:')
    #in case of exception from sql or any other error, display warning and exit
    except Exception:
        wait('Warning:Exception raised exiting')


# insert
def menu_2():
    
    global column_names
    global menu_2_text

    #get the user choice
    menu_2_choice = get_input(menu_2_text, 'Enter Submenu number', True, (1, 2, 3))
    # student entry
    if menu_2_choice == 1:  
        menu_2a()
    # subject entry
    elif menu_2_choice == 2:  
        menu_2b()
    # Exit to menu
    elif menu_2_choice == 3:
        return


# student table insert
def menu_2a():
    
    global column_names

    #get required details from the user using get_input for error trapping
    roll_no = get_input('***INSERT STUDENT ENTRY***', 'Enter Roll Number', True, list(range(1, 999)))
    title = get_input(None, 'Enter title', False, screen_clear=False)
    eng = get_input(None, 'Student has opted for English?(y/n)', screen_clear=False, yes_no=True)
    math = get_input(None, 'Student has opted for Mathematics?(y/n)', screen_clear=False, yes_no=True)
    phy = get_input(None, 'Student has opted for Physics?(y/n)', screen_clear=False, yes_no=True)
    chem = get_input(None, 'Student has opted for chemistry?(y/n)', screen_clear=False, yes_no=True)
    cs = get_input(None, 'Student has opted for Computer Science?(y/n)', screen_clear=False, yes_no=True)
    pe = get_input(None, 'Student has opted for Physical Education?(y/n)', screen_clear=False, yes_no=True)
    data = (roll_no, title, eng, math, phy, chem, cs, pe)
    # get column names from global identifier
    head = column_names[0][1:]
    #clear screen and print the table using tabulate
    clear_screen()
    print(tabulate((data,), headers=head, tablefmt='fancy_grid'))
    #Ask if the entry should be added to the sql database
    enter = get_input(None, 'Do you want to add this entry to database?(y/n)', screen_clear=False, yes_no=True)
    #Entry needs to be added
    if enter == 1:
        # Error will be realised if entry already exists
        try:
            # insert in DB
            sql.insert_data((roll_no, title, eng, math, phy, chem, cs, pe))  
            wait('**Entry added to database**')
        except Exception:
            print('***Roll No. already exists***')
            input('press enter to exit:')
    #don't add the entry and exit
    else:
        wait('**Cancelling Entry**')
        return


# subject tables insert
def menu_2b():
    
    global menu_2b_text
    global column_names

    subject = get_input(menu_2b_text, 'Enter subject number', True, list(range(1, 8)))
    
    # To get marks in correct range for different
    # theory + internal
    #condition is true for english and math
    #they have internal of 20 marks instead of 30
    if subject in [1, 2]:  
        max_theory_marks = 80
        max_internal_marks = 20
    # theory + practicals
    #condition is true for all subjects except math and english
    else:  
        max_theory_marks = 70
        max_internal_marks = 30

    # Other details
    roll_no = get_input(None, 'Enter Roll Number', True, list(range(1, 999)), False)
    s_1_e = get_input(None, 'Enter sem 1 exam marks', True, list(range(0, max_theory_marks + 1)), False)
    s_1_i = get_input(None, 'Enter sem 1 internal marks', True, list(range(0, max_internal_marks + 1)), False)
    s_2_e = get_input(None, 'Enter sem 2 exam marks', True, list(range(0, max_theory_marks + 1)), False)
    s_2_i = get_input(None, 'Enter sem 2 internal marks', True, list(range(0, max_internal_marks + 1)), False)

    #calculating final marks from provided information
    s_1_f = s_1_i + s_1_e  # sem 1 final = sem1 internal + sem1 exam
    s_2_f = s_2_i + s_2_e  # sem 2 final = sem2 internal + sem2 exam
    total = (s_1_f + s_2_f) / 2  # total  = (sem1 final + sem2 final) / 2
    
    #Checking if the student is pass or fail in this subject
    if total > 33:
        is_pass = 1
    else:
        is_pass = 0

    #adding student data in a variable to be used as a row later
    data = [(roll_no,
             s_1_e, s_1_i, s_1_f,
             s_2_e, s_2_i, s_2_f,
             total, is_pass),
            sql.get_data(constraint='roll_no=999', table=column_names[subject][0])[0]]
    # get column names from global identifier
    head = column_names[subject][1:]
    
    #clear screen and print the table using tabulate
    clear_screen()
    print(tabulate(data, headers=head, tablefmt='fancy_grid'))
    print('999 is a pseudo entry representing "maximum marks"')
    #ask if the user wants the above entry to be addded in sql database
    enter = get_input(None, 'Do you want to add this entry to database?(y/n)', screen_clear=False, yes_no=True)
    #add the entry
    if enter == 1:
        #use sql module's insert_data function to add data to database
        sql.insert_data((roll_no,
                         s_1_e, s_1_i, s_1_f,
                         s_2_e, s_2_i, s_2_f,
                         total, is_pass),
                        column_names[subject][0])
        wait('**Entry added to database**')
    #cancel adding of entry and exit
    else:
        wait('**Cancelling Entry**')
        return


# Update
def menu_3():
    
    global menu_3_text
    global column_names

    #get the roll number to be updated from the user
    roll_no = get_input(menu_3_text, 'Enter Roll Number to Update or exit(-1)', True, list(range(-1, 999)))
    # Exit condition
    if roll_no == -1:  
        return

    #get the subject or stundent entry to be updated. it will be an int
    sel = get_input(menu_3a_text, 'Enter Submenu number', True, list(range(1, 9)))
    # Exit condition
    if sel == 8:  
        return

    # to match the indexing in column_names
    subject = sel - 1  
    head = column_names[subject][1:]
    # get existing entry of the roll number
    query = f'select * from {column_names[subject][0]} where {roll_no=};'  
    data = sql.custom_query(query)
    # clear screen and print the exisiting entry of the roll number using tabulate
    clear_screen()
    print('***Current Entry***')
    #save the table string in a variable to be used later
    old_table = tabulate(data, headers=head, tablefmt='fancy_grid')
    print(old_table)

    # it is a nested list with element 0 only hence eliminating it
    data = data[0]
    # if student table is selected
    if sel == 1:
        #print the old entry and ask the new entry for each column
        print('-' * 30)
        title = get_input(f'Old Title:{data[1]}',
                          'Enter New title', False, screen_clear=False)
        print('-' * 30)
        eng = get_input(f'Current choice for English:{bool(data[2])}',
                        'New choice for English?(y/n)', screen_clear=False, yes_no=True)
        print('-' * 30)
        math = get_input(f'Current choice for Mathematics:{bool(data[3])}',
                         'New choice for Mathematics?(y/n)', screen_clear=False, yes_no=True)
        print('-' * 30)
        phy = get_input(f'Current choice for Physics:{bool(data[4])}',
                        'New choice for Physics?(y/n)', screen_clear=False, yes_no=True)
        print('-' * 30)
        chem = get_input(f'Current choice for Chemistry:{bool(data[5])}',
                         'New choice for chemistry?(y/n)', screen_clear=False, yes_no=True)
        print('-' * 30)
        cs = get_input(f'Current choice for Computer Science:{bool(data[6])}',
                       'New choice for Computer Science?(y/n)', screen_clear=False, yes_no=True)
        print('-' * 30)
        pe = get_input(f'Current choice for Physical Education:{bool(data[7])}',
                       'New choice for Physical Education?(y/n)', screen_clear=False, yes_no=True)
        print('-' * 30)

        #add all the new data in a variable as a list to be used as a row in the tabulate function
        new_data = (roll_no, title, eng, math, phy, chem, cs, pe)
        #clear screen and display old table followed by new table, so the user can compare and make a decision
        clear_screen()
        print('***OLD Entry***')
        print(old_table)
        print('***NEW Entry***')
        print(tabulate((new_data,), headers=head, tablefmt='fancy_grid'))
        #Ask if the new entry should be added to sql database
        enter = get_input(None, 'Do you want to update the entry as above?(y/n)', screen_clear=False, yes_no=True)

        #the entry needs to be added
        if enter:
            #long query with appropriate naming of columns and new entries
            query = f'update student_list set '
            query += f'title = "{title}",'
            query += f'eng = {eng},'
            query += f'math = {math},'
            query += f'phy = {phy},'
            query += f'chem = {chem},'
            query += f'cs = {cs},'
            query += f'pe = {pe} '
            query += f'where {roll_no=};'
            sql.custom_query(query,
                             True)  # commit = True
            wait('**Entry updated in database**')
        #the entry does not need to be added and exit
        else:
            wait('***Updating cancelled***')
            return
    # Subject table is selected
    elif sel in range(2, 8):
        #if eng or math is selected then internal marks will be of 20 instead of 30
        if subject in [1, 2]:  
            max_theory_marks = 80
            max_internal_marks = 20
        #for all other subjects internal marks are 30
        else:  
            max_theory_marks = 70
            max_internal_marks = 30
        # get the details from the user
        # old details are provided to cross check or decide and new ones can also be added
        print('-' * 30)
        s_1_e = get_input(f'Old sem 1 exam marks:{data[1]}',
                          'Enter new Sem 1 exam Marks',
                          True, list(range(0, max_theory_marks + 1)), False)
        print('-' * 30)
        s_1_i = get_input(f'Old sem 1 internal marks:{data[2]}',
                          'Enter sem 1 internal marks',
                          True, list(range(0, max_internal_marks + 1)), False)
        print('-' * 30)
        s_2_e = get_input(f'Old Sem 2 exam marks:{data[4]}',
                          'Enter sem 2 exam marks',
                          True, list(range(0, max_theory_marks + 1)), False)
        print('-' * 30)
        s_2_i = get_input(f'Old Sem 2 internal marks:{data[5]}',
                          'Enter sem 2 internal marks',
                          True, list(range(0, max_internal_marks + 1)), False)
        print('-' * 30)
        #calculate final marks from the information provided
        s_1_f = s_1_i + s_1_e  # sem 1 final = sem1 internal + sem1 exam
        s_2_f = s_2_i + s_2_e  # sem 2 final = sem2 internal + sem2 exam
        total = (s_1_f + s_2_f) / 2  # total  = (sem1 final + sem2 final) / 2
        #check if the student is pass or not
        if total > 33:
            is_pass = 1
        else:
            is_pass = 0

        #new data arranged in a list to be used as an entry in the table
        new_data = [(roll_no,
                     s_1_e, s_1_i, s_1_f,  # sem 1
                     s_2_e, s_2_i, s_2_f,  # sem 2
                     total, is_pass),
                    sql.get_data(constraint='roll_no=999', table=column_names[subject][0])[0]]
        #clear screen and display the table using tabulate
        clear_screen()
        print('***OLD Entry***')
        print(old_table)
        print('***NEW Entry***')
        print(tabulate(new_data, headers=head, tablefmt='fancy_grid'))
        print('999 is a pseudo entry representing "maximum marks"')
        #ask if the user wants to enter the data in database
        update = get_input(None, 'Do you want to update the entry as above?(y/n)', screen_clear=False, yes_no=True)
        #if the user asks to add entry to sql
        if update:
            query  = f'update {column_names[subject][0]} set '
            query += f'sem_1_exam = {s_1_e},'
            query += f'sem_1_internal = {s_1_i},'
            query += f'sem_1_final = {s_1_f},'
            query += f'sem_2_exam = {s_2_e},'
            query += f'sem_2_internal = {s_2_i},'
            query += f'sem_2_final = {s_2_f},'
            query += f'total = {total},'
            query += f'pass = {is_pass} '
            query += f'where {roll_no=};'
            sql.custom_query(query,
                             True)
            wait('**Entry updated in database**')
        #if the user does not want to add the entry to sql
        else:
            wait('***Updating cancelled***')


# Remove
def menu_4():
    
    global menu_4_text
    global column_names

    #get the roll number to be removed from the user
    roll_no = get_input(menu_4_text, 'Enter Roll Number to remove or exit(-1)', True, list(range(-1, 999)))
    #Exit condition
    if roll_no == -1:
        return
    #get the name of the student
    name = sql.custom_query(f'select title from {column_names[0][0]} where roll_no = {roll_no};')[0][0]
    #ask if the user is sure about removing the user
    permission = get_input(None, f'Delete record for "{name}" with roll number:{roll_no}?(y/n)', yes_no=True)
    #remove the user
    if permission:
        data = []
        #foreign_key ckecks need to be disabled because the tables in sql are based on foreign key concept
        sql.custom_query('set FOREIGN_KEY_CHECKS=0;', True)
        for table in column_names[::-1]:
            data.append(sql.custom_query(f'delete from {table[0]} where roll_no = {roll_no};', True))
        #foreign_key ckecks need to be turned back on so as to maintain consistancy in data
        sql.custom_query('set FOREIGN_KEY_CHECKS=1;', True)
        print('***Records deleted successfully***')
    #don't remove the user
    else:
        print('***Exiting to menu***')
    input('Press any key to exit:')


# Report card generation
def menu_5():
    
    global menu_5_text
    global column_names

    roll_no = get_input(menu_5_text, 'Enter Roll Number to generate report card', True, list(range(0, 1000)))  # get roll no
    # set important variables for the report card
    school_name = 'Ramsheth Thakur Public School'
    report_heading = 'Report Card'
    # use date time module here to get current date to be printed on report card
    temp = datetime.now()
    date = f'{temp.day}-{temp.month}-{temp.year}'  
    academic_year = '2021-22'
    subject_names = ['English', 'Mathematics', 'Physics', 'Chemistry', 'Computer Science', 'Physical Education']
    name = sql.custom_query(f'select title from student_db.student_list where roll_no = {roll_no}')[0][0]
    columns = 'sem_1_final,sem_2_final,total'
    marks = []
    # data is a tuple with 1st element as table name
    for data in column_names[1:]:  
        temp = sql.custom_query(f'select {columns} from student_db.{data[0]} where roll_no = {roll_no}')
        if not temp:
            marks.extend((('-', '-', '-'),))
        else:
            marks.extend(temp)
    # marks is a nested list like: [(1,2,3),(1,2,3),(1,2,3)...]
    # calculate total marks and if passed
    total_marks = 0
    passed = 'Fail'
    no_of_subjects = 0
    #total marks calculated for subjects opted for
    for subject in marks:
        #subject is opted
        if subject[0] != '-':  
            no_of_subjects += 1
            if subject[2]:
                total_marks += subject[2]
    # normalise the total marks out of 100
    total_marks /= no_of_subjects
    #set variable passed to true if student has passed the school year
    if total_marks >= 33:
        passed = 'Pass'
    # generate report
    # report card format in the form of a nested list
    cells = [(None, school_name, None),
             (None, report_heading, None),
             ('Name of Student\n' + name, None, 'Academic Year\n' + academic_year),
             ('Roll Number: ' + str(roll_no), None, 'Date\n' + date),
             (None, None, None),
             (subject_names[0], 'Term 1', marks[0][0]),
             (None, 'Term 2', marks[0][1]),
             (None, 'Total', marks[0][2]),
             (None, None, None),
             (subject_names[1], 'Term 1', marks[1][0]),
             (None, 'Term 2', marks[1][1]),
             (None, 'Total', marks[1][2]),
             (None, None, None),
             (subject_names[2], 'Term 1', marks[2][0]),
             (None, 'Term 2', marks[2][1]),
             (None, 'Total', marks[2][2]),
             (None, None, None),
             (subject_names[3], 'Term 1', marks[3][0]),
             (None, 'Term 2', marks[3][1]),
             (None, 'Total', marks[3][2]),
             (None, None, None),
             (subject_names[4], 'Term 1', marks[4][0]),
             (None, 'Term 2', marks[4][1]),
             (None, 'Total', marks[4][2]),
             (None, None, None),
             (subject_names[5], 'Term 1', marks[5][0]),
             (None, 'Term 2', marks[5][1]),
             (None, 'Total', marks[5][2]),
             (None, None, None),
             ('Percentage Scored', None, round(total_marks,2)),
             ('Result', None, passed)]
    #print the report card as a table using tabulate
    table = tabulate(cells, numalign='center', tablefmt='fancy_grid')
    #ask if the user wants to save the result to text file
    save = get_input(table, 'Do you want to save this Result?(y/n)', screen_clear=False, yes_no=True)
    #report card needs to be saved
    if save:
        #create new file with the roll_no and date of generation
        file_name = f'{roll_no}_{date}.txt'
        # the file is saved as utf-8 because unicode characters are used in the table
        with open(file_name, 'w+', encoding="utf-8") as f:
            f.write(table)
            print(f'Report saved to file:{file_name}')
    #pause the screen
    input('Press any key to exit')


#compare subjects in mat plot lib # reduce code
def menu_6():
    
    global menu_6_text
    global menu_6_text_2
    global subject_names

    #subject list for axis naming
    assignments = ["sem_1_exam", "sem_1_internal", "sem_1_final", "sem_2_exam", "sem_2_internal", "sem_2_final"]
    alt_assignments = ["sem_1_exam","sem_1_practical","sem_1_final", "sem_2_exam", "sem_2_practical", "sem_2_final"]

    #get input for subject 1
    input_1 = get_input(menu_6_text, "Enter subject 1 of your choice", True, list(range(1, 8)))
    #exit condition
    if input_1 == 7:
        return
    #get input for subject 2
    input_2 = get_input(None, "Enter subject 2 of your choice", True, list(range(0, 8)), False)
    #exit condition
    if input_2 == 7:
        return

    #get input for assignment 
    input_assignment = get_input(None,menu_6_text_2,
                                 True, list(range(1, 8)))
    #exit condition
    if input_assignment == 7:
        return
    #name of assignment chosen is assigned
    assignment = assignments[input_assignment - 1]
    alt_assignment = alt_assignments[input_assignment - 1]

    #name of subject chosen are assigned
    subject_1 = subject_names[input_1 - 1]
    subject_2 = subject_names[input_2 - 1]

    #getting marks from the database for subject 1
    query_1 = 'select '
    if subject_1 not in ("English", "Mathematics"):
        query_1 += f'{alt_assignment} '
    else:
        query_1 += f'{assignment} '
    query_1 += f'from {column_names[input_1][0]};'
    data_x = sql.custom_query(query_1)
    
    #getting marks from the database for subject 2
    query_2 = 'select '
    if subject_2 not in ("English", "Mathematics"):
        query_2 += f'{alt_assignment} '
    else:
        query_2 += f'{assignment} '
    query_2 += f'from {column_names[input_2][0]};'
    data_y = sql.custom_query(query_2)

    #mat plot initial vars
    fig, ax = plt.subplots()
    fig.set_size_inches(7, 5)#plot size

    #add values to x coordinate list
    coord_1 = []
    for crd in data_x:
        try:
            coord_1.append(int(crd[0]))
        except TypeError:
            coord_1.append(0)
    #add values to y coordinate list
    coord_2 = []
    for crd in data_y:
        try:
            coord_2.append(int(crd[0]))
        except TypeError:
            coord_2.append(0)

    #plot data from generated x,y lists
    plt.plot(data_x, data_y, "o")

    #setting label names
    x_axis_name = f'{subject_names[int(input_1) - 1]} Marks'
    y_axis_name = f'{subject_names[int(input_2) - 1]} Marks'
    ax.set_title(f"{x_axis_name} v {y_axis_name}")
    ax.set_xlabel(x_axis_name)
    ax.set_ylabel(y_axis_name)

    #setting variables for the text
    text_color = '#ff6f59'
    text_size = '8'
    max_coord_1 = max(coord_1)
    min_coord_1 = min(coord_1)

    #default variables for the text
    text_pos_x_1 = 0
    text_pos_y_1 = 0
    text_1 = f'Strong {subject_1} , strong {subject_2}'
    text_pos_x_2 = 0
    text_pos_y_2 = 0
    text_2 = f'Weak {subject_1}, weak {subject_2}'

    #Assign the correct text variable values based on subject and assignments chosen for subject 1 and subject 2
    if assignment in ('sem_1_internal', 'sem_2_internal'):
        text_pos_x_1 = max_coord_1 - 6
        text_pos_x_2 = min_coord_1 + 0.5
        text_pos_y_1 = 30.5
        if subject_1 in ('English', 'Mathematics') and subject_2 in ('English', 'Mathematics'):
            text_pos_y_1 = 20.5
        elif subject_1 in ('English', 'Mathematics'):
            text_pos_y_1 = 30.5
        elif subject_2 in ("English", "Mathematics"):
            text_pos_y_1 = 20.5

    elif assignment in ('sem_1_final', 'sem_2_final'):
        text_pos_x_1 = max_coord_1 - 40
        text_pos_y_1 = 101
        text_pos_x_2 = min_coord_1 + 3
        text_pos_y_2 = 0
    elif assignment in ('sem_1_exam', 'sem_2_exam'):
        text_pos_x_1 = max_coord_1 - 30
        text_pos_x_2 = min_coord_1 + 2
        text_pos_y_1 = 71
        if subject_1 in ('English', 'Mathematics') and subject_2 in ('English', 'Mathematics'):
            text_pos_y_1 = 81
        elif subject_1 in ("English", "Mathematics"):
            text_pos_y_1 = 71
        elif subject_2 in ('English', 'Mathematics'):
            text_pos_y_1 = 81
    else:
        text_pos_x_1 = max_coord_1 - 40
        text_pos_y_1 = 101
        text_pos_x_2 = min_coord_1 + 3

    #Create text from the above variables
    ax.text(text_pos_x_1,
            text_pos_y_1,
            text_1,
            color=text_color,
            size=text_size)
    ax.text(text_pos_x_2,
            text_pos_y_2,
            text_2,
            color=text_color,
            size=text_size)

    #draw the graph
    plt.show()
    #close the graph properly on exit
    plt.close()



# function to show the proportion of CS Students
# distribution for optional subjects
def menu_7():
    
    student_list = sql.get_data()

    #initialise counter variables for cs and pe subjects
    cs_count = 0
    pe_count = 0
    #loop as many times as many rows in the stundet_list table
    for i in range(len(student_list)):
        cs_count += student_list[i][6] # add to cs count if student is in cs
        pe_count += student_list[i][7] # add to pe count if student is in pe
    #plot pie chart using matplot lib function plt.pie and appropriate varuiables
    plt.pie([cs_count, pe_count],
            labels=['Students studying CS', 'Students studying PE'],
            colors=['#2ca2a3', '#7c1a1a'],
            wedgeprops={'edgecolor': 'black'})
    #plot the graph
    plt.show()
    #close the graph properly and exit
    plt.close()


# function to compare total marks of single subject
def menu_8():
    
    global menu_8_text
    global column_names
    global subject_names

    # get data of all students 
    # getting values from the database as nested lists
    student_list = sql.get_data()

    #get user input for the subject
    subject_no = get_input(menu_8_text, "Enter subject of your choice to compare", True, list(range(1, 8)))
    #exit condition
    if subject_no == 7:
        return

    #get the student total marks from the selected subject above
    subject = sql.custom_query(f'select roll_no,total from {column_names[subject_no][0]}')

    #matplot init vars
    plt.style.use('dark_background')
    plt.tick_params(labelsize=7)

    #getting the total marks
    x_label = []
    value = []
    #loop as many times as many rows in the stundet_list table
    for i in range(len(student_list)):
        #compare if subject is opted by student
        if student_list[i][subject_no+1] == 1:
            #append the name of the student to the x_label list
            x_label.append(student_list[i][1])
            #append total marks of the studnt in the value list
            value.append(subject[i][1])

    #plot the graph with appropriate values using matplot lib
    plt.barh(x_label, value, height=0.6, label=subject_names[subject_no-1], color='#129aa2')
    plt.title(subject_names[subject_no-1])
    plt.tight_layout()
    plt.legend()
    #draw the graph
    plt.show()
    #close the graph properly and exit
    plt.close()

# function to show student analysis,
# Use type: 'stack' or 'line'
# and roll for the roll number of the student
def menu_9():
    
    global menu_9_text
    global menu_9_text_2
    
    #getting input like roll number and graph to display as integers
    roll_no = get_input(menu_9_text,"Enter Roll number",True,list(range(1,999)))
    graph_type = get_input(menu_9_text_2,"Enter desired type of plot ",True,(1,2))

    #getting student marks for each subject
    student_list = sql.get_data(constraint=f'roll_no in ({roll_no},999)')
    eng = sql.get_data(table='eng',constraint=f'roll_no in ({roll_no},999)')
    math = sql.get_data(table='math',constraint=f'roll_no in ({roll_no},999)')
    phy = sql.get_data(table='phy',constraint=f'roll_no in ({roll_no},999)')
    chem = sql.get_data(table='chem',constraint=f'roll_no in ({roll_no},999)')
    cs = sql.get_data(table='cs',constraint=f'roll_no in ({roll_no},999)')
    pe = sql.get_data(table='pe',constraint=f'roll_no in ({roll_no},999)')
    
    #declaring variables and initial arguments
    plt.style.use('dark_background')
    plt.tick_params(labelsize=8)
    assignment = ['Sem 1 Exam', 'Sem 1 Internal', 'Sem 1 Final', 'Sem 2 Exam', 'Sem 2 Internal', 'Sem 2 Final', 'Total']
    x = [1, 2, 3, 4, 5, 6, 7]
    
    eng_val = []
    math_val = []
    phy_val = []
    chem_val = []
    cs_val = []
    pe_val = []

    # Generating lists
    for i in range(1, 8):#single loop for each assignment
        #sub[0] is student row
        #sub[1] is max marks row
        #normalising all the scores in 0 to 100
        eng_val.append((eng[0][i] / eng[1][i]) * 100)
        math_val.append((math[0][i] / math[1][i]) * 100)
        phy_val.append((phy[0][i] / phy[1][i]) * 100)
        chem_val.append((chem[0][i] / chem[1][i]) * 100)
        if student_list[0][6] == 1:#if cs student
            cs_val.append((cs[0][i] / cs[1][i]) * 100)
        elif student_list[0][7] == 1:#if pe student
            pe_val.append((pe[0][i] / pe[1][i]) * 100)


    # line chart part
    if graph_type == 1:
        if student_list[0][6] == 1:#cs student
            plt.plot(x, cs_val, color='#33c1cf', label='Computer Science', marker='.')
        elif student_list[0][7] == 1:#pe student
            plt.plot(x, pe_val, color='#eb8d2f', label='Physical Education', marker='.')
        plt.plot(x, eng_val, color='#cfcf11', label='English', marker='.')
        plt.plot(x, math_val, color='#cf5555', label='Mathematics', marker='.')
        plt.plot(x, phy_val, color='#cf11cf', label='Physics', marker='.')
        plt.plot(x, chem_val, color='#10cf93', label='Chemistry', marker='.')

    # stack plot part
    elif graph_type == 2:
        if student_list[0][6] == 1:#cs student
            plt.stackplot(x, eng_val, math_val, phy_val, chem_val, cs_val,
                          labels=['English', 'Mathematics', 'Physics', 'Chemistry', 'Computer Science'],
                          colors=['#dede5b', '#a85858', '#a860a8', '#4cb090', '#518c91'])
        elif student_list[0][7] == 1:#pe student
            plt.stackplot(x, eng_val, math_val, phy_val, chem_val, pe_val,
                          labels=['English', 'Mathematics', 'Physics', 'Chemistry', 'Physical Education'],
                          colors=['#dede5b', '#a85858', '#a860a8', '#4cb090', '#a16325'])

    # post processing the plot and figure widgets
    plt.legend()
    plt.title(student_list[0][1])
    plt.xticks(ticks=x, labels=assignment)
    plt.tight_layout()
    plt.show()
    plt.close()
# use plt.close() to close plots between steps


###############################
#       GLOBAL VARIABLES      #
###############################


# menu_n representing menu where n is integer

#login_screen
login_screen_text = ''' ________________________
((---------------------((
 ))       WELCOME       ))
((---------------------(('''

# menu_main
menu_main_text = ''' ___________________________
((------------------------((
 ))      STUDENT DB        ))
((-----------------------=((
 ))    1.Display Entry     ))
((    2.Insert Entry      ((
 ))    3.Update Entry      ))
((    4.Remove Entry      (( 
 ))    5.Generate Report   ))
((    6.Compare Subjects  ((
 ))  7.CS/PE distribution  ))
((    8.Compare Total     ((
 ))    9.Line/Stack Plot   )) 
((         10.Exit        ((
 ))________________________))'''

# menu_1
menu_1_text = ''' __________________________
((-----------------------((
 ))       DISPLAY         ))
((-----------------------((
 )) 1.Selective Roll No.  ))
((     2.All Entries     ((
 ))  3.Custom Search     ))
((     4.Main Menu      ((
 ))______________________))'''


# menu_1a1
menu_1a_text = ''' __________________________
((-----------------------((
 ))  SELECTIVE ROLL NO.   ))
((-----------------------(('''

# get_roll_no_list
get_roll_no_list_text = '''Enter start-end for range of Roll numbers,
Enter multiple Roll numbers by seperator '/',
Enter single Roll number or
press enter to exit'''

# 1st part of search query for searching roll number
# menu_1a2
search_query = f'select \
a.title, \
a.roll_no , \
b.total English, \
c.total Math, \
d.total Physics, \
e.total Chemistry, \
f.total CS, \
g.total PE \
from student_list a \
join eng b \
on a.roll_no = b.roll_no \
join math c \
on a.roll_no = c.roll_no \
join phy d \
on a.roll_no = d.roll_no \
join chem e \
on a.roll_no = e.roll_no \
join cs f \
on a.roll_no = f.roll_no \
join pe g \
on a.roll_no = g.roll_no \
where a.roll_no in '

# menu_1b
menu_1b_text = ''' __________________________
((-----------------------((
 ))  DISPLAY ALL ENTRIES  ))
((-----------------------((
 ))    1.Student List     ))
((    2.English Scores   ((
 )) 3.Mathematics Scores  ))
((   4.Physics Scores    ((
 )) 5.Chemistry Scores    ))
((      6.CS Scores      ((
 ))     7.PE Scores       ))
((      8.Main Menu      ((
 ))_______________________))'''    

# menu_2
menu_2_text = ''' _______________________
((--------------------((
 ))       INSERT       ))
((--------------------((
 ))  1.Student Entry   ))
((   2.Subject marks  ((
 ))    3.Main Menu     ))
((____________________(('''
#Note: student should be entered before subject marks.

# menu_2b
menu_2b_text = ''' _____________________________
((--------------------------((
 ))   INSERT SUBJECT MARKS   ))
((--------------------------((
 ))     1.English Scores     ))
((   2.Mathematics Scores   ((
 ))    3.Physics Scores      ))
((    4.Chemistry Scores    ((
 ))       5.CS Scores        ))
((        6.PE Scores       ((
 ))       7.Main Menu        ))
((__________________________(('''

# menu_3
menu_3_text = ''' ________________________
((---------------------((
 ))       UPDATE        ))
((---------------------(('''

#menu_3a
menu_3a_text = ''' __________________________
((-----------------------((
 ))     SELECT TABLE      ))
((-----------------------((
 ))    1.Student data     ))
((    2.English Scores   ((
 ))     3.Math Scores     ))
((    4.Physics Scores   ((
 ))  5.Chemistry Scores   ))
((       6.CS Scores     ((
 ))      7.PE Scores      ))
((       8.Main Menu     ((
 ))_______________________))'''

# menu_4
menu_4_text = ''' ________________________
((---------------------((
 ))    REMOVE ENTRY     ))
((---------------------(('''

# Nested tuple for column names with first entry(index:0) for table name
# column_name=((table_1,heading1,heading2...),
#             (table_2,heading1,heading2...),
#              ...)
column_names = (  # student list
    ('student_list', 'RollNo.',
     'Title', 'Eng', 'Phy', 'Math', 'Chem', 'CS', 'PE'),
    # English
    ('eng', 'Roll No.',
     'Sem 1 Exam', 'Sem 1 internal', 'Sem 1 final',
     'Sem 1 Exam', 'Sem 2 internal', 'Sem 2 final',
     'Total', 'Pass'),
    # Mathematics
    ('math', 'Roll No.',
     'Sem 1 Exam', 'Sem 1 internal', 'Sem 1 final',
     'Sem 1 Exam', 'Sem 2 internal', 'Sem 2 final',
     'Total', 'Pass'),
    # Physics
    ('phy', 'Roll No.',
     'Sem 1 Exam', 'Sem 1 practical', 'Sem 1 final',
     'Sem 1 Exam', 'Sem 2 practical', 'Sem 2 final',
     'Total', 'Pass'),
    # Chemistry
    ('chem', 'Roll No.',
     'Sem 1 Exam', 'Sem 1 practical', 'Sem 1 final',
     'Sem 1 Exam', 'Sem 2 practical', 'Sem 2 final',
     'Total', 'Pass'),
    # CS
    ('cs', 'Roll No.',
     'Sem 1 Exam', 'Sem 1 practical', 'Sem 1 final',
     'Sem 1 Exam', 'Sem 2 practical', 'Sem 2 final',
     'Total', 'Pass'),
    # PE
    ('pe', 'Roll No.',
     'Sem 1 Exam', 'Sem 1 practical', 'Sem 1 final',
     'Sem 1 Exam', 'Sem 2 practical', 'Sem 2 final',
     'Total', 'Pass'))

#subject names used only for display
subject_names = ["English", "Mathematics","Physics", "Chemistry",
                 "Computer Science", "Physical Education"]

# menu_5
menu_5_text = ''' _________________________
((-------------------------((
 ))  GENERATE REPORT CARD   ))
((-------------------------(('''

# menu_6
menu_6_text = ''' ________________________
((---------------------((
 ))  COMPARE SUBJECTS   ))
((---------------------((
 ))      1.English      ))
((     2.Mathematics   ((
 ))      3.Physics      ))
((     4.Chemistry     ((
 )) 5.Computer Science  ))
(( 6.Physical Education((
 ))    7.Main Menu      ))
((_____________________((
Which two subjects do you want to compare?'''

menu_6_text_2 = ''' ________________________
((---------------------((
 ))  COMPARE SUBJECTS   ))
((---------------------((
 ))    1.Sem 1 Exam     ))
((    2.Sem 1 Int/Prac ((
 ))    3.Sem 1 Final    ))
((     4.Sem 2 Exam    ((
 ))   5.Sem 2 Int/Prac  ))
((     6.Sem 2 Final   ((
 ))     7.Main Menu     ))
((_____________________((
Which Assignment do you want to compare?'''

#menu _8
menu_8_text = ''' _________________________
((----------------------((
 ))   COMPARE STUDENTS   ))
((----------------------((
 ))      1.English       ))
((    2.Mathematics     ((
 ))     3.Physics        ))
((     4.Chemistry      ((
 ))  5.Computer Science  ))
(( 6.Physical Education ((
 ))     7.Main Menu      ))
((______________________(('''
menu_9_text = ''' _________________________
((----------------------((
 ))   MARKS BREAKDOWN    ))
((----------------------(('''
menu_9_text_2 = ''' _________________________
((----------------------((
 ))   MARKS BREAKDOWN    ))
((----------------------((
 ))    1.Line Graph      ))
((     2.Stack Plot     ((
 ))______________________))'''

# sleep time in seconds when freezing screen
time_sleep = 1  

##############################
#           CODE             #
##############################

# loop till user has logged in
while True:  
    clear_screen()
    if login_screen():
        break


# menu loop
while True:
    # loop till correct data is inputted
    while True:
        menu_main_choice = get_input(menu_main_text, 'Enter Your Choice', True,
                                     list(range(1, 11)))
        
        if menu_main_choice != -1:
            break
    if menu_main_choice == 1:
        # display
        menu_1()  
    elif menu_main_choice == 2:
        # insert
        menu_2()  
    elif menu_main_choice == 3:
        # Update
        menu_3()  
    elif menu_main_choice == 4:
        # remove
        menu_4()  
    elif menu_main_choice == 5:
        # Generate report
        menu_5()  
    elif menu_main_choice == 6:
        # compare subjects
        menu_6()  
    elif menu_main_choice == 7:
        # pe/cs distribution 
        menu_7()  
    elif menu_main_choice == 8:
        # single subject compare
        menu_8()  
    elif menu_main_choice == 9:
        # individual student perfomance
        menu_9()
    elif menu_main_choice == 10:
         # exit condition
        for i in range(1, 4):
            clear_screen()
            print('Exiting' + i * '.')
            wait()
        exit()
