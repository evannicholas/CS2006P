
import pandas as pd
import json

df = pd.read_csv("../data/CometLanding.csv",
                 dtype={"id_str": str, "in_reply_to_user_id_str": str, "from_user_id_str": str,
                        "in_reply_to_status_id_str": str, "user_followers_count": "Int64",
                        "user_friends_count": "Int64", "geo_coordinates": str}, 
                        parse_dates=['created_at']
                 )

df = df.drop(columns=['time'])

df = df.drop_duplicates() # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html
df = df.dropna(axis = 0, how = 'all')


# print(df.loc[0, 'created_at'])
json_content = df['entities_str'].to_list()
json_result = "["

for j in json_content:
    if isinstance(j, str):
        json_result += j
        if(j != json_content[len(json_content)-1]):
            json_result += ", "
       

json_result += "]"

writer = open('../data/CometLandingFixed.json', 'w')
writer.write(json_result)
writer.close()

df.to_csv('../data/CometLandingFixed.csv', index=False)
