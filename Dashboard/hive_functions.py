""" hive_functions.py
    Author:         Carl Winkler
    Date:           03. December 2021
    Description:    A collection of hive queries run with pyhive to receive data for the dashboard
"""

import pandas as pd

#####################################################
#Helpers
#####################################################
def column(matrix, i):
    return [row[i] for row in matrix]

#####################################################
#Hive Queries for the dashboard
#####################################################

#this function retreives overall number of entries by label
def entries_by_labels(cursor):
    query = 'SELECT label_id, count(*) FROM userdb.fact_news_claim GROUP BY label_id'
    cursor.execute(query)
    return cursor.fetchall()

#get the length of an entry
def getlength(cursor, id=42):
    query = 'SELECT claim FROM userdb.dim_content WHERE content_id =' + str(id)
    cursor.execute(query)
    x = cursor.fetchall()
    return len(x[0][0])

#perform a hive-query defined by the user
def run_query(cursor, query='SELECT * FROM userdb.label'):
    cursor.execute(query)
    return cursor.fetchall()

#return the 10 most popular authors with their respective number of entries
def get_10_pop_auth(cursor):
    query_string = "SELECT dim_source.author, count(*) AS cnt "\
    "FROM userdb.dim_source "\
    "GROUP BY dim_source.author "\
    "order by cnt desc"
    cursor.execute(query_string)
    output = cursor.fetchall()

    return output[:10]

#return a pandas dataframe of temporal data describing the number of claims by author in a month
#join several tables of the star schema and generate a suited dataframe
def get_time_series(cursor):
    query_string = "SELECT dim_source.author, count(*) AS cnt, dim_time.year, dim_time.month "\
    "FROM userdb.fact_news_claim "\
    "INNER JOIN userdb.dim_time "\
    " ON fact_news_claim.time_id = dim_time.time_id "\
    "INNER JOIN userdb.dim_source "\
    " ON dim_source.source_id = fact_news_claim.source_id "\
    "INNER JOIN ("\
    "SELECT dim_source.author, count(*) AS cnt1 "\
    "FROM userdb.dim_source "\
    "GROUP BY dim_source.author "\
    "order by cnt1 desc limit 10"\
    ") t1 "\
    " ON dim_source.author = t1.author "\
    "GROUP BY dim_source.author, dim_time.month, dim_time.year"

    cursor.execute(query_string)
    x = cursor.fetchall()

    #to represent the time as machine intepretable the month are mapped to numbers
    df = pd.DataFrame(x, columns = ['stock', 'value', 'year' ,'month'])
    d = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April' : 4,
        'May' : 5,
        'June' : 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October' : 10,
        'November' : 11,
        'December' : 12
    }
    df['month'] = df['month'].map(d)
    df['day'] = 1
    df.index = pd.to_datetime(df[['year', 'month', 'day']])
    df = df.sort_index()
    return df