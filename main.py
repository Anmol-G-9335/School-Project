# install tabulate
# python 3.9.7 working
# python 3.7 not working
import sql
from getpass import getpass
from os import system
from time import sleep
from pickle import load
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt


# function definitions
def clear_screen():  # call to clear screen
    system('cls')


def wait(text=None):  # call to freeze screen
    global time_sleep
    if text:
        print(text)
    sleep(time_sleep)


def get_input(description_1,  # menu text
              description_2,  # Question
              type_int=False,  # input type is int?
              data_range=None,
              screen_clear=True,  # call to get valid input
              yes_no=False):
    while True:
        if screen_clear:
            clear_screen()
        if description_1 is not None:
            print(description_1)
        print(description_2, end=':')
        if type_int:
            try:
                ch = int(input())
                if data_range is not None:  # only validate input if range is given
                    if ch in data_range:
                        break
                    else:
                        wait('Warning:Enter valid data')
            except ValueError:  # if user inputs string
                wait('Warning:Enter a number')
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


def login_screen():  # call to get login credential and match them
    clear_screen()
    print('***Welcome***')
    username = input('Username:')
    password = getpass('Password:')
    with open('login.dat', 'rb') as f:
        data = load(f)
        for log in data:
            if log == username and data[log] == password:
                wait('Access Granted')
                return True
        else:
            wait('Access Denied')
            return False


def get_roll_no_list(heading, append_999=False):  # call this function to get a list of roll_no
    global get_roll_no_list_text
    while True:  # loop till correct input is provided
        clear_screen()
        print(heading, get_roll_no_list_text, sep='\n')
        input_string = input('Enter here:')
        if input_string == '':  # empty input means exit
            return
        num = []
        try:  # error may occur during conversion of string to int
            if ('-' not in input_string) and ('/' not in input_string):  # single num
                num.append(int(input_string))
                break
            elif '/' in input_string:  # multiple num separated by /
                for string in input_string.split('/'):
                    num.append(int(string))
                break
            elif '-' in input_string:  # Range
                if len(input_string.split('-')) != 2:  # handling bad input
                    wait('Warning:Use single "-"')
                else:  # executed if correct input
                    temp = []
                    for string in input_string.split('-'):  # will run twice
                        temp.append(int(string))
                    for value in range(temp[0], temp[1] + 1):
                        num.append(value)
                    break

        except ValueError:
            wait('Warning:Enter valid input')
    if append_999:
        num.append(999)
    return num


def menu_1():  # Display
    global menu_1_text
    menu_1_choice = get_input(menu_1_text, 'Enter choice', True, (1, 2, 3))
    if menu_1_choice == 1:  # runs if specific student is required
        menu_1a()
    elif menu_1_choice == 2:  # runs if all data is required
        menu_1b()
    elif menu_1_choice == 3:
        return


def menu_1a():  # search record
    global menu_1a_text
    menu_1a_choice = get_input(menu_1a_text, 'Enter Choice', True, (1, 2, 3))
    if menu_1a_choice == 1:  # range/specific/multiple
        menu_1a1()
    elif menu_1a_choice == 2:  # custom search
        menu_1a2()
    elif menu_1a_choice == 3:
        return


def menu_1a1():  # search by range/specific/multiple roll no
    global menu_1a1_text
    number_list = get_roll_no_list(menu_1a1_text, True)
    search(number_list)


def search(roll_no_list):  # supply list of roll no to display them in a table with subjects
    global search_query
    query = search_query + f'{tuple(roll_no_list)};'
    data = sql.custom_query(query)
    head = ('Title', 'Roll No.', 'English', 'Math', 'Physics', 'Chemistry', 'CS', 'PE')
    clear_screen()
    print(tabulate(data, headers=head, tablefmt='fancy_grid'))
    print('999 is a pseudo entry representing "maximum marks"')
    input('Press any key to exit:')


def menu_1a2():  # search custom query
    try:
        while True:  # runs till correct data
            query = get_input('Enter you sql query to be executed', '-->', False)
            to_commit = get_input(None, 'Would you like to commit(y/n)', yes_no=True)
            permission = get_input(query, 'Are you sure to execute this query?(y/n)', yes_no=True)
            if permission:
                data = sql.custom_query(query, bool(to_commit))
                break
        clear_screen()
        print(tabulate(data, tablefmt='fancy_grid'))
        input('Press any key to exit:')
    except Exception:
        wait('Warning:Exception raised exiting')


def menu_1b():  # all student display
    global menu_1b_text
    global column_names
    sel = get_input(menu_1b_text, 'Enter Submenu number', True, list(range(1, 9)))
    get_names = 0  # False, don't get name
    if sel in range(2, 8):  # if require score of specific subject
        get_names = get_input(None, 'Display names?(y/n)', yes_no=True)
    elif sel == 8:
        return
    if get_names:
        query = f'select a.title ,b.* from student_list a natural join {column_names[sel - 1][0]} b;'
        data = sql.custom_query(query)
        head = list(column_names[sel - 1][1:])
        head.insert(0, ('title',)[0])
    else:
        data = sql.get_data(table=column_names[sel - 1][0])
        head = column_names[sel - 1][1:]
    clear_screen()
    print(tabulate(data, headers=head, tablefmt='fancy_grid'))
    print('999 is a pseudo entry representing "maximum marks"')
    input('Press any key to exit:')


def menu_2():  # insert
    global column_names
    global menu_2_text
    menu_2_choice = get_input(menu_2_text, 'Enter Submenu number', True, (1, 2, 3))
    if menu_2_choice == 1:  # student entry
        menu_2a()
    elif menu_2_choice == 2:  # subject entry
        menu_2b()
    elif menu_2_choice == 3:  # Exit submenu
        return


def menu_2a():  # student table insert
    global column_names
    roll_no = get_input('***INSERT STUDENT ENTRY***', 'Enter Roll Number', True, list(range(1, 999)))
    title = get_input(None, 'Enter title', False, screen_clear=False)
    eng = get_input(None, 'Student has opted for English?(y/n)', screen_clear=False, yes_no=True)
    math = get_input(None, 'Student has opted for Mathematics?(y/n)', screen_clear=False, yes_no=True)
    phy = get_input(None, 'Student has opted for Physics?(y/n)', screen_clear=False, yes_no=True)
    chem = get_input(None, 'Student has opted for chemistry?(y/n)', screen_clear=False, yes_no=True)
    cs = get_input(None, 'Student has opted for Computer Science?(y/n)', screen_clear=False, yes_no=True)
    pe = get_input(None, 'Student has opted for Physical Education?(y/n)', screen_clear=False, yes_no=True)
    data = (roll_no, title, eng, math, phy, chem, cs, pe)
    head = column_names[0][1:]  # get column names from global identifier
    clear_screen()
    print(tabulate((data,), headers=head, tablefmt='fancy_grid'))
    enter = get_input(None, 'Do you want to add this entry to database?(y/n)', screen_clear=False, yes_no=True)
    if enter == 1:
        try:  # Error will be realised if entry already exists
            sql.insert_data((roll_no, title, eng, math, phy, chem, cs, pe))  # insert in DB
            wait('**Entry added to database**')
        except Exception:
            print('***Roll No. already exists***')
            input('press enter to exit:')
    else:
        return


def menu_2b():  # subject tables insert
    global menu_2b_text
    global column_names
    subject = get_input(menu_2b_text, 'Enter subject number', True, list(range(1, 8)))
    # To get marks in correct range for different subjects
    if subject in [1, 2]:  # theory + internal
        max_theory_marks = 80
        max_internal_marks = 20
    else:  # theory + practicals
        max_theory_marks = 70
        max_internal_marks = 30
    # Other details
    roll_no = get_input(None, 'Enter Roll Number', True, list(range(1, 999)), False)
    s_1_e = get_input(None, 'Enter sem 1 exam marks', True, list(range(0, max_theory_marks + 1)), False)
    s_1_i = get_input(None, 'Enter sem 1 internal marks', True, list(range(0, max_internal_marks + 1)), False)
    s_2_e = get_input(None, 'Enter sem 2 exam marks', True, list(range(0, max_theory_marks + 1)), False)
    s_2_i = get_input(None, 'Enter sem 2 internal marks', True, list(range(0, max_internal_marks + 1)), False)
    s_1_f = s_1_i + s_1_e  # sem 1 final = sem1 internal + sem1 exam
    s_2_f = s_2_i + s_2_e  # sem 2 final = sem2 internal + sem2 exam
    total = (s_1_f + s_2_f) / 2  # total  = (sem1 final + sem2 final) / 2
    if total > 33:
        is_pass = 1
    else:
        is_pass = 0
    data = [(roll_no,
             s_1_e, s_1_i, s_1_f,
             s_2_e, s_2_i, s_2_f,
             total, is_pass),
            sql.get_data(constraint='roll_no=999', table=column_names[subject][0])[0]]  #
    head = column_names[subject][1:]  # get column names from global identifier
    clear_screen()
    print(tabulate(data, headers=head, tablefmt='fancy_grid'))
    print('999 is a pseudo entry representing "maximum marks"')
    enter = get_input(None, 'Do you want to add this entry to database?(y/n)', screen_clear=False, yes_no=True)
    if enter == 1:
        sql.insert_data((roll_no,
                         s_1_e, s_1_i, s_1_f,
                         s_2_e, s_2_i, s_2_f,
                         total, is_pass),
                        column_names[subject][0])  # insert in DB
        wait('**Entry added to database**')
    else:
        return


def menu_3():  # Update
    global menu_3_text
    global column_names
    roll_no = get_input(menu_3_text, '', True, list(range(-1, 999)))
    if roll_no == -1:  # Exit condition
        return
    sel = get_input(menu_3a_text, 'Enter Submenu number', True, list(range(1, 9)))
    if sel == 8:  # Exit condition
        return
    subject = sel - 1  # to match the indexing in column_names
    head = column_names[subject][1:]
    query = f'select * from {column_names[subject][0]} where {roll_no=};'  # get existing entry
    data = sql.custom_query(query)
    clear_screen()
    print('***Current Entry***')
    print(tabulate(data, headers=head, tablefmt='fancy_grid'))
    data = data[0]  # it is a nested list with element 0 only hence eliminating it
    if sel == 1:  # student table
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
        new_data = (roll_no, title, eng, math, phy, chem, cs, pe)
        clear_screen()
        print(tabulate((new_data,), headers=head, tablefmt='fancy_grid'))
        enter = get_input(None, 'Do you want to add this entry to database?(y/n)', screen_clear=False, yes_no=True)
        if enter:
            query = f'update student_list set '
            query += f'title = "{title}",'
            query += f'eng = {eng},'
            query += f'math = {math},'
            query += f'phy = {phy},'
            query += f'chem = {chem},'
            query += f'cs = {cs},'
            query += f'pe = {pe} '
            query += f'where {roll_no=};'
            print(query)
            sql.custom_query(query,
                             True)  # commit = True
            wait('**Entry updated in database**')
        else:
            wait('***Updating cancelled***')
    elif sel in range(2, 8):  # Subject table
        if subject in [1, 2]:  # theory + internal(Eng and Math)
            max_theory_marks = 80
            max_internal_marks = 20
        else:  # theory + practicals(except Eng and Math)
            max_theory_marks = 70
            max_internal_marks = 30
        # Other details
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
        s_1_f = s_1_i + s_1_e  # sem 1 final = sem1 internal + sem1 exam
        s_2_f = s_2_i + s_2_e  # sem 2 final = sem2 internal + sem2 exam
        total = (s_1_f + s_2_f) / 2  # total  = (sem1 final + sem2 final) / 2
        if total > 33:
            is_pass = 1
        else:
            is_pass = 0
        new_data = [(roll_no,
                     s_1_e, s_1_i, s_1_f,  # sem 1
                     s_2_e, s_2_i, s_2_f,  # sem 2
                     total, is_pass),
                    sql.get_data(constraint='roll_no=999', table=column_names[subject][0])[0]]  #
        clear_screen()
        print(tabulate(new_data, headers=head, tablefmt='fancy_grid'))
        print('999 is a pseudo entry representing "maximum marks"')
        update = get_input(None, 'Do you want to add this entry to database?(y/n)', screen_clear=False, yes_no=True)
        if update:
            query = f'update {column_names[subject][0]} set '
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
                             True)  # commit = True
            wait('**Entry updated in database**')
        else:
            wait('***Updating cancelled***')


def menu_4():  # Remove
    global menu_4_text
    global column_names
    roll_no = get_input(menu_4_text, 'Enter Roll Number to remove', True, list(range(-1, 999)))
    if roll_no == -1:
        return
    permission = get_input(None, f'Delete record for Roll No.:{roll_no}?(y/n)', yes_no=True)
    if permission:
        data = []
        sql.custom_query('set FOREIGN_KEY_CHECKS=0;', True)
        for table in column_names[::-1]:
            data.append(sql.custom_query(f'delete from {table[0]} where roll_no = {roll_no};', True))
        sql.custom_query('set FOREIGN_KEY_CHECKS=1;', True)
    print('Records deleted successfully')
    input('Press any key to exit:')


def menu_5():  # Report card generation
    global menu_5_text
    global column_names
    roll_no = get_input(None, menu_5_text, True, list(range(0, 1000)))  # get roll no
    # also possible to generate pseudo report
    # get marks for the student
    school_name = 'Ramsheth Thakur Public School'
    report_heading = 'Report Card'
    temp = datetime.now()
    date = f'{temp.day}-{temp.month}-{temp.year}'  # use date time module here
    academic_year = '2021-22'
    subject_names = ['English', 'Mathematics', 'Physics', 'Chemistry', 'Computer Science', 'Physical Education']
    name = sql.custom_query(f'select title from student_db.student_list where roll_no = {roll_no}')[0][0]
    columns = 'sem_1_final,sem_2_final,total'
    marks = []
    for data in column_names[1:]:  # data is a tuple with 1st element as table name
        temp = sql.custom_query(f'select {columns} from student_db.{data[0]} where roll_no = {roll_no}')
        # print(f'{temp = }')#########################
        if not temp:
            marks.extend((('-', '-', '-'),))
        else:
            marks.extend(temp)
        # print(f'{marks = }')################
    # marks is a nested list like: [(1,2,3),(1,2,3),(1,2,3)...]
    # calculate total marks and if passed
    total_marks = 0
    passed = 'Fail'
    no_of_subjects = 0
    for subject in marks:
        if subject[0] != '-':  # meaning subject is opted
            no_of_subjects += 1
            if subject[2]:
                total_marks += subject[2]
    # print(f'{subject = }\n{total_marks = }\n{no_of_subjects = }')##################
    total_marks /= no_of_subjects  # average
    if total_marks >= 33:
        passed = 'Pass'
    # generate report
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
             ('Percentage Scored', None, total_marks),
             ('Result', None, passed)]
    table = tabulate(cells, numalign='center', tablefmt='fancy_grid')
    save = get_input(table, 'Do you want to save this Result?(y/n)', screen_clear=False, yes_no=True)
    if save:
        file_name = f'{roll_no}_{date}.txt'
        with open(file_name, 'w+', encoding="utf-8") as f:
            f.write(table)
            print(f'Report saved to file:{file_name}')
    input('Press any key to exit')


def menu_6():
    global menu_6_text
    global menu_6_text_2
    subject = ["English", "Mathematics", "Physics", "Chemistry", "Computer Science", "Physical Education"]
    assignments = ["sem_1_exam", "sem_1_internal", "sem_1_final", "sem_2_exam", "sem_2_internal", "sem_2_final"]
    alt_assignments = ["sem_1_practical", "sem_2_practical"]

    input1 = get_input(menu_6_text, "enter subject 1 of your choice", True, list(range(1, 8)))
    if input1 == 8:
        return
    input2 = get_input(None, "enter subject 2 of your choice", True, list(range(0, 8)), False)
    if input2 == 8:
        return

    input_assignment = get_input(menu_6_text_2,
                                 "Enter the corresponding index of the desired assignment:",
                                 True, list(range(1, 8)))
    if input_assignment == 8:
        return
    assignment = assignments[input_assignment - 1]

    sub1 = subject[input1 - 1]
    sub2 = subject[input2 - 1]

    if sub1 not in ("English", "Mathematics"):
        if assignment == "sem_1_internal":
            query1 = f'SELECT {alt_assignments[0]} FROM {column_names[input1][0]};'
            data1 = sql.custom_query(query1)
        elif assignment == "sem_2_internal":
            query1 = f'SELECT {alt_assignments[1]} FROM {column_names[input1][0]};'
            data1 = sql.custom_query(query1)
        else:
            query1 = f'SELECT {assignment} FROM {column_names[input1][0]};'
            data1 = sql.custom_query(query1)
    else:
        query1 = f'SELECT {assignment} FROM {column_names[input1][0]};'
        data1 = sql.custom_query(query1)

    if sub2 not in ("English", "Mathematics"):
        if assignment == "sem_1_internal":
            query2 = f'SELECT {alt_assignments[0]} FROM {column_names[input2][0]};'
            data2 = sql.custom_query(query2)
        elif assignment == "sem_2_internal":
            query2 = f'SELECT {alt_assignments[1]} FROM {column_names[input2][0]};'
            data2 = sql.custom_query(query2)
        else:
            query2 = f'SELECT {assignment} FROM {column_names[input2][0]};'
            data2 = sql.custom_query(query2)
    else:
        query2 = f'SELECT {assignment} FROM {column_names[input2][0]};'
        data2 = sql.custom_query(query2)

    fig, ax = plt.subplots()
    fig.set_size_inches(7, 5)

    coord1 = []
    for crd in data1:
        try:
            coord1.append(int(crd[0]))
        except TypeError:
            coord1.append(0)
            pass

    coord2 = []
    for crd in data2:
        try:
            coord2.append(int(crd[0]))
        except TypeError:
            coord2.append(0)
            pass

    plt.plot(data1, data2, "o")

    ax.set_title(f"{subject[int(input1) - 1]} v {subject[int(input2) - 1]}")
    ax.set_xlabel(f"{subject[int(input1) - 1]} Marks")
    ax.set_ylabel(f"{subject[int(input2) - 1]} Marks")

    if assignment in ("sem_1_internal", "sem_2_internal"):
        if sub1 in ("English", "Mathematics") and sub2 in ("English", "Mathematics"):
            ax.text((max(coord1) - 6), 20.5, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
            ax.text((min(coord1) + 0.5), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
        elif sub1 in ("English", "Mathematics"):
            ax.text((max(coord1) - 6), 30.5, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
            ax.text((min(coord1) + 0.5), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
        elif sub2 in ("English", "Mathematics"):
            ax.text((max(coord1) - 6), 20.5, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
            ax.text((min(coord1) + 0.5), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
        else:
            ax.text((max(coord1) - 6), 30.5, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
            ax.text((min(coord1) + 0.5), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
    elif assignment in ("sem_1_final", "sem_2_final"):
        ax.text((max(coord1) - 40), 101, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                color="#ff6f59", size="8")
        ax.text((min(coord1) + 3), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                color="#ff6f59", size="8")
    elif assignment in ("sem_1_exam", "sem_2_exam"):
        if sub1 in ("English", "Mathematics") and sub2 in ("English", "Mathematics"):
            ax.text((max(coord1) - 30), 81, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
            ax.text((min(coord1) + 2), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
        elif sub1 in ("English", "Mathematics"):
            ax.text((max(coord1) - 30), 71, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
            ax.text((min(coord1) + 2), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
        elif sub2 in ("English", "Mathematics"):
            ax.text((max(coord1) - 30), 81, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
            ax.text((min(coord1) + 2), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
        else:
            ax.text((max(coord1) - 30), 71, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
            ax.text((min(coord1) + 2), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                    color="#ff6f59", size="8")
    else:
        ax.text((max(coord1) - 40), 101, f"Strong {subject[int(input1) - 1]} , strong {subject[int(input2) - 1]}",
                color="#ff6f59", size="8")
        ax.text((min(coord1) + 3), 0, f"Weak {subject[int(input1) - 1]}, weak {subject[int(input2) - 1]}",
                color="#ff6f59", size="8")

    plt.style.use('dark_background')
    plt.show()


def menu_7():
    student_list = sql.get_data(table='student_list')

    # function to show the proportion of CS Students
    cs_count = 0
    pe_count = 0
    for i in range(49):
        cs_count += student_list[i][6]
        pe_count += student_list[i][7]
    plt.pie([cs_count, pe_count], labels=['Students studying CS', 'Students studying PE'],
            colors=['#2ca2a3', '#7c1a1a'],
            wedgeprops={'edgecolor': 'black'})
    plt.show()


# function to compare total marks of every subject
def menu_8():
    # getting values from the database as nested lists
    student_list = sql.get_data(table='student_list')
    eng = sql.get_data(table='eng')
    math = sql.get_data(table='math')
    phy = sql.get_data(table='phy')
    chem = sql.get_data(table='chem')
    cs = sql.get_data(table='cs')
    pe = sql.get_data(table='pe')

    global menu_8_text
    subj = get_input(menu_8_text, "Enter subject of your choice", True, list(range(1, 8)))
    if subj == 8:
        return

    # subject dictionary
    sub_dict = {1: ['Eng', eng], 2: ['Mathematics', math], 3: ['Physics', phy], 4: ['Chemistry', chem],
                5: ['Computer Science', cs], 6: ['Physical Education', pe]}

    plt.style.use('dark_background')
    plt.tick_params(labelsize=7)
    x_label = []
    value = []
    for i in range(49):
        if student_list[i][subj] == 1:
            x_label.append(student_list[i][1])
            value.append(sub_dict[subj][1][i][7])

    plt.barh(x_label, value, height=0.6, label=sub_dict[subj][0], color='#129aa2')
    plt.title(sub_dict[subj][0])
    plt.tight_layout()
    plt.legend()
    plt.show()


# function to show student analysis,
# Use type: 'stack' or 'line'
# and roll for the roll number of the student
def menu_9():
    student_list = sql.get_data(table='student_list')
    eng = sql.get_data(table='eng')
    math = sql.get_data(table='math')
    phy = sql.get_data(table='phy')
    chem = sql.get_data(table='chem')
    cs = sql.get_data(table='cs')
    pe = sql.get_data(table='pe')

    global menu_9_text
    global menu_9_text_2
    print(menu_9_text)
    roll = int(input("Enter desired roll no. "))
    print(menu_9_text_2)
    typ = int(input("Enter desired type of plot "))

    # declaring variables and initial arguments
    roll -= 1
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
    for i in range(1, 8):
        temp = eng
        eng_val.append((temp[roll][i] / temp[len(temp) - 1][i]) * 100)
        temp = math
        math_val.append((temp[roll][i] / temp[len(temp) - 1][i]) * 100)
        temp = phy
        phy_val.append((temp[roll][i] / temp[len(temp) - 1][i]) * 100)
        temp = chem
        chem_val.append((temp[roll][i] / temp[len(temp) - 1][i]) * 100)
        if student_list[roll][6] == 1:
            temp = cs
            cs_val.append((temp[roll][i] / temp[len(temp) - 1][i]) * 100)
        elif student_list[roll][7] == 1:
            temp = pe
            pe_val.append((temp[roll][i] / temp[len(temp) - 1][i]) * 100)

    # line chart part
    if typ == 1:
        if student_list[roll][6] == 1:
            plt.plot(x, cs_val, color='#33c1cf', label='Computer Science', marker='.')
        elif student_list[roll][7] == 1:
            plt.plot(x, pe_val, color='#eb8d2f', label='Physical Education', marker='.')
        plt.plot(x, eng_val, color='#cfcf11', label='English', marker='.')
        plt.plot(x, math_val, color='#cf5555', label='Mathematics', marker='.')
        plt.plot(x, phy_val, color='#cf11cf', label='Physics', marker='.')
        plt.plot(x, chem_val, color='#10cf93', label='Chemistry', marker='.')

    # stack plot part
    elif typ == 2:
        if student_list[roll][6] == 1:
            plt.stackplot(x, eng_val, math_val, phy_val, chem_val, cs_val,
                          labels=['English', 'Mathematics', 'Physics', 'Chemistry', 'Computer Science'],
                          colors=['#dede5b', '#a85858', '#a860a8', '#4cb090', '#518c91'])
        elif student_list[roll][7] == 1:
            plt.stackplot(x, eng_val, math_val, phy_val, chem_val, pe_val,
                          labels=['English', 'Mathematics', 'Physics', 'Chemistry', 'Physical Education'],
                          colors=['#dede5b', '#a85858', '#a860a8', '#4cb090', '#a16325'])

    # post processing the plot and figure widgets
    plt.legend()
    plt.title(student_list[roll][1])
    plt.xticks(ticks=x, labels=assignment)
    plt.tight_layout()
    plt.show()


# use plt.close() to close plots between steps
# menu_main
'''***Student DB***
1.Display Data
2.Insert Data
3.Update Data
4.Remove Data
5.Results/Performance
6.Compare Subjects
7.Show CS
8.Compare Total
9.Line/Stack Plot
10.Exit'''
menu_main_text = ''' ___________________
((------------------((
 ))  STUDENT DB      ))
((------------------((
 )) 1.Display Entry  ))
(( 2.Insert Entry   ((
 )) 3.Update Entry   ))
(( 4.Remove Entry   (( 
 )) 5.Generate Report))
(( 6.Compare Subject((
 )) 7.Show CS        ))
(( 8.Compare Total  ((
 )) 9.Line/Stack Plot)) 
(( 10.Exit          ((
 ))__________________))'''  # Generate result(individual and class statistics)
# display or search

# menu_1
menu_1_text = '''***DISPLAY***
1.Specific/Range of Roll number
2.All roll number
3.Exit submenu'''

# menu_1a
menu_1a_text = '''***Search record***
1.Search by Roll Number (specific/range/multiple)
2.Custom search
3.exit'''

# menu_1a1
menu_1a1_text = '***Search by Roll No.***'

# get_roll_no_list
get_roll_no_list_text = '''1.For range use'-' to separate two numbers
2.For multiple numbers separate each number by '/'
3.Or enter a single number
4.Press enter to exit'''

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
menu_1b_text = '''***Display***
1.Student List 
2.English Scores
3.Mathematics Scores
4.Physics Scores
5.Chemistry Scores
6.Computer Science Scores
7.Physical Education Scores
8.Exit Submenu'''

# menu_2
menu_2_text = '''***INSERT***
1.Student Entry
2.Subject marks
3.exit submenu
Note: student should be entered before subject marks.'''

# menu_2b
menu_2b_text = '''***INSERT SUBJECT MARKS
1.English Scores
2.Mathematics Scores
3.Physics Scores
4.Chemistry Scores
5.Computer Science Scores
6.Physical Education Scores
7.Exit'''

# menu_3
menu_3_text = '''***Update***
Enter Number to update or -1 to exit'''
menu_3a_text = '''***Table select***
1.Student data
2.English Scores
3.Math Scores
4.Physics Scores
5.Chemistry Scores
6.Computer Science Scores
7.Physical education Scores
8.Exit'''

# menu_4
menu_4_text = '''***Remove Entry***
-1 to exit'''

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
# menu_5
menu_5_text = 'Enter Roll Number to generate report card for'

# menu_6
menu_6_text = '''Which two subjects do you want to compare?
1.English
2.Mathematics
3.Physics
4.Chemistry
5.Computer Science
6.Physical Education
7.Exit submenu'''

menu_6_text_2 = '''Assignments:
1.sem_1_exam
2.sem_1_internal/practical
3.sem_1_final
4.sem_2_exam
5.sem_2_internal/practical
6.sem_2_final
7.Exit submenu'''

menu_8_text = '''Which subject's totals do you want to compare?
1.English
2.Mathematics
3.Physics
4.Chemistry
5.Computer Science
6.Physical Education
7.Exit submenu'''

menu_9_text = '''Choose a roll number'''
menu_9_text_2 = '''Choose type of plot:
1. Line Graph
2. Stack Plot'''

###

time_sleep = 1  # sec

# Code
while True:  # login loop
    clear_screen()
    if login_screen():
        break

while True:  # menu loop
    while True:  # loop till correct data is inputted
        clear_screen()
        menu_main_choice = get_input(menu_main_text, 'What to do?', True,
                                     list(range(1, 11)))  # menu_n representing menu where n is integer
        if menu_main_choice != -1:
            break
    if menu_main_choice == 1:
        menu_1()  # display
    elif menu_main_choice == 2:
        menu_2()  # insert
    elif menu_main_choice == 3:
        menu_3()  # Update
    elif menu_main_choice == 4:
        menu_4()  # remove
    elif menu_main_choice == 5:
        menu_5()
    elif menu_main_choice == 6:
        menu_6()
    elif menu_main_choice == 7:
        menu_7()
    elif menu_main_choice == 8:
        menu_8()
    elif menu_main_choice == 9:
        menu_9()
    elif menu_main_choice == 10:  # exit
        for i in range(1, 4):
            clear_screen()
            print('Exiting' + i * '.')
            wait()
        exit()
