#!/usr/bin/env python

import pandas as pd
import re
import json
import sys
import os.path
from pytz import timezone
import datetime

data_path = "../data/"

def filter_data(df):
    """takes a dataframe df as parameter, filters duplicated or inconsistent data and removes unwanted
    columns inplace"""

    df.drop_duplicates(inplace=True) # remove duplicated data

    # remove if any of the following fields is NaN:
    # id_str(tweet id), from_user_id_str(user id), text, entities_str(hashtags)
    df.dropna(subset=['id_str', 'from_user_id_str', 'text', 'entities_str'], inplace=True)

    # remove tweets without "cometlanding" in the text and the hashtag used
    df.drop(df[~(df['entities_str'].str.contains("cometlanding", case=False))].index, inplace=True)

    # filter tweets whose date is out of supposed range
    start_date = datetime.datetime(2014,11,12)
    start_date = timezone('GMT-0').localize(start_date)
    end_date = datetime.datetime(2014,12,6)
    end_date = timezone('GMT-0').localize(end_date)
    df.drop(df[(pd.to_datetime(df['created_at'], utc=True) < start_date) 
                | (pd.to_datetime(df['created_at'], utc=True) >= end_date)].index, inplace=True)


def refine_id(df):
    """takes a dataframe df as parameter, refines the id_str field with the status_url field inplace"""

    def id_from_row(r):
        """takes a row of dataframe r as parameter, returns the id read from the status_url field,
        or the original id value in id_str field if status_url is NaN or not of correct format"""
        status = r['status_url']
        if pd.notnull(status):
            if re.search("^http://twitter\.com/.+/statuses/[0-9]{18}", status):
                return status[-18:]
            else: 
                return r['id_str']
        else:
            return r['id_str']
    
    df['id_str'] = df.apply(id_from_row, axis=1)
 

def create_application_columns(df):
    # https://pynative.com/python-regex-capturing-groups/
    def regex_cleanup(row):
        target_string = row['source']
        pattern = re.compile(r"<.*>(.*)</.*>")
        for match in pattern.finditer(target_string):
            
            return match.group(1)
    
    df['specific_applications'] = df.apply(regex_cleanup, axis=1)
    df['applications'] = df.apply(regex_cleanup, axis=1)

def refine_application(df):
    
    def application_only(r):
        app = r["applications"]
        if pd.notnull(app):
            if re.search("Twitter",app):
                return app[0:7]
            else: 
                return r["applications"]
        else: 
            return r["applications"]
    
    df['applications'] = df.apply(application_only, axis=1)


def createJson(df, file):
    """takes a dataframe df and filename file as parameter, generate a JSON file with given file for df"""

    json_content = df['entities_str'].to_list()
    json_result = "["

    for j in json_content:
        if isinstance(j, str):
            json_result += j
            if(j != json_content[len(json_content)-1]):
                json_result += ", "
        

    json_result += "]"

    writer = open(file + ".json", 'w')
    writer.write(json_result)
    writer.close()

def usage():
    print("Usage: ./fixdata.py <csv filename>")

def main(read):
    df = pd.read_csv(read,
                 dtype={"id_str": str, "in_reply_to_user_id_str": str, "from_user_id_str": str,
                        "in_reply_to_status_id_str": str, "user_followers_count": "Int64",
                        "user_friends_count": "Int64", "geo_coordinates": str}, 
                        parse_dates=['created_at']
                 )
    df.drop(columns=['time'], inplace=True) # remove time field as duplicated with created_at field
    
    filter_data(df)
    refine_id(df)
    create_application_columns(df)
    refine_application(df)

    fixfile = read[:-4] + "Fixed" # filename prefix of fixed data in csv and json

    createJson(df, fixfile)

    df.to_csv(fixfile + ".csv", index=False)

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        usage()
    elif (not sys.argv[1].endswith(".csv")):
        print("File should be a CSV file: " + sys.argv[1])
        usage()
    elif (not os.path.exists(data_path + sys.argv[1])):
        print("File does not exist: " + data_path + sys.argv[1])
        usage()
    else:
        main(data_path + sys.argv[1])