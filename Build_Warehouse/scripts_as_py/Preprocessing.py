#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


#Load the data as CSV 
df = pd.read_csv('politifact_phase1_raw_2018_7_3.csv')


#get them number of missing values
number_of_missing_values = len(np.where(pd.isnull(df))[0])
data_size = len(df)
perc = number_of_missing_values/data_size
print('The percentage of rows missing values is: %f' % (perc))


#If Percentage is low enough (< 0.01) drop the values 
df = df.dropna()


#The data by politicfacts also contains a small amount of data without an indication of the truth of the claim but on how an opionion has changed
#this data is diregarded here
df = df[df.fact_tag_phase1 != 'Full Flop']
df = df[df.fact_tag_phase1 != 'Half Flip']
df = df[df.fact_tag_phase1 != 'No Flip']


#Extract the author
df['author'] = df['article_claim_citation_phase1'].str.extract(r'((?<=— ).+?(?=\son))')


#Extract time correctly
df['hour'] = df['article_published_date_phase1'].str.extract(r'((?<=at\s).+)')
df['day'] = df['article_published_date_phase1'].str.extract(r'((?<=\s)[0-9]+(?=[a-z]+))')
df['month'] = df['article_published_date_phase1'].str.extract(r'((?<=,\s).*?(?=\s[0-9]+.+,))')
df['day_of_the_week'] = df['article_published_date_phase1'].str.extract(r'(.+(?=,.*, ))')
df['year'] = df['article_published_date_phase1'].str.extract(r'((?<=,\s)\d+(?=\sat))')


#these columns were processed and will not be needed in the 
df = df.drop(columns=['article_published_date_phase1', 'article_claim_citation_phase1'])


#This regex is the result of hours of trying, it is not perfect as sometimes www. is included, sometimes not
#however this solution finds the same identifier for every link and the platform is always completely contained and is therefore preferred
df['platform'] = df['original_url_phase1'].str.extract(r'((?<=\/\/)[^\/]+(?=\.))')


#to represent the hierarchy of the data a key will induced on the labels here already
#create a key for the entries
idx = range(0,len(df))
print('The following labels exist:')
print(df['fact_tag_phase1'].unique())


#if the previous output gave 6 labels the transformation was correct and a key for every label will be introduced
d = {
    'Pants on Fire!': 0,
    'False': 1,
    'Mostly False': 2,
    'Half-True' : 3,
    'Mostly True' : 4,
    'True' : 5
}
df['label'] = df['fact_tag_phase1'].map(d)


#because Hive can not parse text in quotatation marks there needs to be preprocessing
#furthermore, there are problems with "," values, they are escaped by '~' in this project
#therefore this section does replacements to ensure the data is parsed correctly by hive

df['article_title_phase1'] = df['article_title_phase1'].str.replace(',','~,')
df['article_claim_phase1'] = df['article_claim_phase1'].str.replace(',','~,')
df['article_categories_phase1'] = df['article_categories_phase1'].str.replace(',','~,')
df['article_researched_by_phase1'] = df['article_researched_by_phase1'].str.replace(',','~,')
df['article_edited_by_phase1'] = df['article_edited_by_phase1'].str.replace(',','~,')
df['original_url_phase1'] = df['original_url_phase1'].str.replace('~','(clean-tild)')
df['original_url_phase1'] = df['original_url_phase1'].str.replace(',','~,')
df['author'] = df['author'].str.replace(',','~,')


df['original_url_phase1'] = df['original_url_phase1'].str.replace('\r\n','')
df['article_claim_phase1'] = df['article_claim_phase1'].str.replace('\r\n','')
df['article_claim_phase1'] = df['article_claim_phase1'].str.replace('-','')

df['article_title_phase1'] = df['article_title_phase1'].str.replace('"','')
df['article_claim_phase1'] = df['article_claim_phase1'].str.replace('"','')
df['platform'] = df['platform'].str.replace(',','')


#some changes to make sure that the data will be interpeted correctly by hive
df['eval_key'] = idx
df['source_key'] = idx

#df['measure_claim_length']  = df['article_claim_phase1'].str.len()
df.page_is_first_citation_phase1 = df.page_is_first_citation_phase1.apply(str)
df['page_is_first_citation_phase1'] = df['page_is_first_citation_phase1'].str.upper() 

df['content_key'] = idx
df['date_key'] = idx

#save the file as csv
df.to_csv('hive_data.csv', index = False, header=False)

