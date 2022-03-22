import pandas as pd
import json
import sys
import os.path

default_path = "../data/"

def filter_data(df):
    """takes a dataframe df as parameter, filters duplicated or inconsistent data and removes unwanted
    columns inplace"""

    df.drop(columns=['time'], inplace=True) # remove time field as duplicated with created_at field

    df.drop_duplicates(inplace=True) # remove duplicated data
    # df.dropna(axis = 0, how = 'all') # drop row if all fields are NaN

    # remove if any of the following fields is NaN:
    # id_str(tweet id), from_user_id_str(user id), text, entities_str(hashtags)
    df.dropna(subset=['id_str', 'from_user_id_str', 'text', 'entities_str'], inplace=True)

    # remove tweets without the hashtag "cometlanding" of any case
    df.drop(df[~(df['entities_str'].str.contains("cometlanding", case=False))].index, inplace=True)


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
    df = pd.read_csv(default_path + read,
                 dtype={"id_str": str, "in_reply_to_user_id_str": str, "from_user_id_str": str,
                        "in_reply_to_status_id_str": str, "user_followers_count": "Int64",
                        "user_friends_count": "Int64", "geo_coordinates": str}, 
                        parse_dates=['created_at']
                 )

    filter_data(df)
    refine_id(df)

    fixfile = read[:-4] + "Fixed" # filename prefix of fixed data in csv and json

    createJson(df, fixfile)

    df.to_csv(fixfile + ".csv", index=False)

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        usage()
    elif (~(sys.argv[1].endswith(".csv"))):
        print("File should be a CSV file!")
        usage()
    elif (~(os.path.exists(default_path + sys.argv[1]))):
        print("File does not exist: " + default_path + sys.argv[1])
        usage()
    else:
        main(default_path + sys.argv[1])