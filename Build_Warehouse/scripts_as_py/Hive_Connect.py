#!/usr/bin/env python
# coding: utf-8
from pyhive import hive


#establish the connection to a local hive server running on Port 10000
conn = hive.Connection(host="localhost", port=10000, username="cloudera")
cursor = conn.cursor()


#create a schema 'userdb' for this data warehouse
schema_crt = 'CREATE SCHEMA userdb'
res = cursor.execute(schema_crt)


query_string = "CREATE TABLE IF NOT EXISTS userdb.master ( ""institution_url String, ""label_description String, ""title String, ""claim String, ""researcher String, ""editor String, ""category String, ""origin_url String, ""first_citation boolean, ""author String, ""hour String, ""day int, ""month String, ""day_of_the_week String, ""year int, ""platform String, ""label_id int, ""verifier_id int, ""source_id int, ""content_id int, ""time_id int) ""ROW FORMAT DELIMITED ""FIELDS TERMINATED BY ',' ESCAPED BY '~'"

#create a master table that contains all information 
res = cursor.execute(query_string)

#load the data from the cleaned csv
copy_data = "LOAD DATA LOCAL INPATH '/hive_data.csv' INTO TABLE userdb.master"
res = cursor.execute(copy_data)


#control if the table was created 
res = cursor.execute("Select label_id FROM userdb.master")
print(cursor.fetchall())
'''
#control if labels where parsed correctly, especially wrong escapes cause problems in practice
#can be done similar with other columns
for i in range(len(x)):
    if x[i][0] not in range(6):
        print(x[i][0])
        print(i)'''


#Create the fact table
query_string_fact = "CREATE TABLE userdb.fact_news_claim ""AS SELECT content_id, time_id, source_id, verifier_id, label_id FROM userdb.master"
res = cursor.execute(query_string_fact)


#Create the time dimension table
query_string_fact = "CREATE TABLE userdb.dim_time ""AS SELECT time_id, hour, day, day_of_the_week, month, year FROM userdb.master"
res = cursor.execute(query_string_fact)


#Create the content dimension table
query_string_fact = "CREATE TABLE userdb.dim_content ""AS SELECT content_id, claim, title, category FROM userdb.master"
res = cursor.execute(query_string_fact)


#Create the source dimension source
query_string_fact = "CREATE TABLE userdb.dim_source ""AS SELECT source_id, origin_url, author, platform, first_citation FROM userdb.master"
res = cursor.execute(query_string_fact)


#Create the label dimension label using the distinct label to reconstructe the mapping
query_string_fact = "CREATE TABLE userdb.label ""AS SELECT DISTINCT label_id, label_description FROM userdb.master"
res = cursor.execute(query_string_fact)


#Drop the unorganized helper table at the end
res = cursor.execute("Drop table userdb.master")



'''
#test query to control if everything worked
query_string = "SELECT fact_news_claim.source_id, count(*) AS cnt, dim_time.year, dim_time.month "\
"FROM userdb.fact_news_claim "\
"JOIN userdb.dim_time "\
" ON fact_news_claim.time_id = dim_time.time_id "\
"GROUP BY fact_news_claim.source_id, dim_time.month, dim_time.year"

cursor.execute(query_string)
x = cursor.fetchall()'''





