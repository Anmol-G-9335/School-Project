import mysql.connector as c

user_name = "root"
host_name = "localhost"
password = "password"


# call this function for getting data from DB

def get_data(column_to_display='*',
             table='student_list',
             constraint=None):  # supply custom query but results may not be flexible
    global user_name
    global host_name
    global password
    mycon = c.connect(user=user_name,
                      host=host_name,
                      passwd=password,
                      database="student_db")
    cursor = mycon.cursor()
    if not constraint:
        query = f'select {column_to_display} from student_db.{table} order by roll_no;'
        cursor.execute(query)
        data = cursor.fetchall()
    else:
        query = f'select {column_to_display} from student_db.{table} where {constraint};'
        cursor.execute(query)
        data = cursor.fetchall()
    cursor.close()
    mycon.close()
    return data


def insert_data(nested_tuple_data,
                table='student_list'):
    global user_name
    global host_name
    global password
    mycon = c.connect(user=user_name,
                      host=host_name,
                      passwd=password,
                      database="student_db")
    cursor = mycon.cursor()
    query = f'insert into student_db.{table} values {nested_tuple_data};'
    #    query = 'insert into student_db.{} values {};'.format(table,nested_tuple_data)
    cursor.execute(query)
    mycon.commit()
    data = cursor.fetchall()
    cursor.close()
    mycon.close()
    return data


def custom_query(query, to_commit=False):
    global user_name
    global host_name
    global password
    mycon = c.connect(user=user_name,
                      host=host_name,
                      passwd=password,
                      database="student_db")
    cursor = mycon.cursor()
    cursor.execute(query)
    if to_commit:
        mycon.commit()
    data = cursor.fetchall()
    cursor.close()
    mycon.close()
    return data
