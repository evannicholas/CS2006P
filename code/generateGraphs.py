#!/usr/bin/env python

import pandas as pd
import sys
import os.path
import math
import json
import re
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import datetime as dt

data_path = "../data/"
image_path = "../images/"

def createTweetsTypeChart(df):
    """Given a dataframe df, generate a chart showing the proportion of tweets, retweets and replies"""
    total_replies = df[pd.notna(df['in_reply_to_user_id_str'])] # dataframe with replies only
    non_reply = df[pd.isna(df['in_reply_to_user_id_str'])] # dataframe without replies
    retweet_only = non_reply[non_reply['text'].apply(lambda x: True if re.search("^RT @.*",x) else False)] # dataframe with retweets only
    tweet_only = non_reply[non_reply['text'].apply(lambda x: False if re.search("^RT @.*",x) else True)] # dataframe with tweets only

    x = [len(tweet_only),len(retweet_only),len(total_replies)]
    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(x)))

    # plot
    fig, ax = plt.subplots()
    ax.pie(x, colors=colors, radius=2, center=(3, 3),labels=["Tweet", "Retweet", "Replies"],
        wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=False,
        autopct="%1.1f%%")

    legend = ax.legend(loc='best', bbox_to_anchor=(1, -0.6, 0.5, 0.5), 
                    shadow=True, fontsize='medium', title = "CometLanding Data")


    # Put a nicer background color on the legend.
    legend.get_frame().set_facecolor('C0')

    plt.savefig(image_path + "tweet_type.png", dpi=300, bbox_inches='tight')

def createActiveDayTimelinePlot(df):
    """Given a dataframe df, generate chart showing the timeline of the tweets
    for the day with the most records per hour"""

    # chart for day with most records 2014-11-12 per hour
    date_raw = df[df['created_at'].apply(
    lambda x: True if re.search('^2014-11-12', str(x)) else False)] # get dataframe with tweets on 2014-11-12
    date = date_raw.set_index('created_at').groupby(pd.Grouper(freq='H'))

    date_labels = [str(ts.strftime("%H"))
               for ts in date.count()["id_str"].index.tolist()] # list of hours with records of tweets
    date_data = date.count()["id_str"].tolist() # list of number of tweets for each recorded hour
    
    plt.title("CometLanding timeline 2014/11/12")
    plt.xlabel("Hour")
    plt.ylabel("Tweets")

    plt.stem(date_labels, date_data)
    plt.savefig(image_path + "tweet_timeline_2014_11_12.png", dpi=300, bbox_inches='tight')

def createApplicationChart(df):
    """Given a dataframe df, generate chart showing the number of tweets for
    each type of application used, where the top 6 most used ones will be 
    shown distinctively and the rest will be classified as others."""

    # count number of tweets for each app
    app_raw = df.groupby(["applications"]).agg(["count"])["id_str"]
    # sort the apps in descending order by their counter
    app_sorted = app_raw.sort_values(by="count",ascending=False)

    # get the counters for the top 6 most used apps
    top6_app = app_sorted.head(6)["count"]
    # get the total of counters for the rest of the apps
    others_count_app = app_sorted.sum() - app_sorted.head(6).sum()
    others_dict_app = {"Others": others_count_app[0]}
    others_app = pd.Series(data=others_dict_app)
    top7_app = pd.concat([top6_app, others_app])

    label = top7_app.keys().tolist() # app name as labels for chart
    data = top7_app.values.tolist() # number of tweets corr. to each app

    plt.rcdefaults()
    fig, ax = plt.subplots()

    y_pos = label
    ax.barh(y_pos, data, align='center')
    ax.set_yticks(y_pos, labels=label)
    ax.invert_yaxis()  
    ax.set_xlabel('Usage')
    ax.set_title('Top 7 applications')

    total = df["applications"].size # total number of tweets

    # Calculate the usage percentage for each app
    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        x, y = p.get_xy() 
        ax.annotate(percentage, (x, y + p.get_height() * 1.02), ha='right')

    plt.savefig(image_path + "top_applications.png", dpi=300, bbox_inches='tight')

def getListOfAllHashTags(file):
	"""Given a json filepath, return a list of hashtags found from the file"""
	# Open JSON file
	with open(file, 'r', encoding="utf8") as json_file:
		json_load = json.load(json_file)

	# List of hashtags found
	hashtagsFull = []

	# Gets list of hashtags from JSON file.
	for j in json_load:
		for i in j['hashtags']:
			hashtagsFull.append(i['text'])
	json_file.close()
	return hashtagsFull

def getListOfUniqueHashtags(hashtagsFull):
	"""Given a list of hashtags hashtagsFull, returns a list of unique hashtags found from hashtagsFull"""
	# Gets unique hashtags.
	hashtagsUnique = pd.Series(hashtagsFull)
	hashtagsUnique = hashtagsUnique.unique()
	return hashtagsUnique

def createDataFrameOfHashtagsAndFills(hashtagsUnique, hashtagsFull):
    """Given a list of unique hashtags and original list of hashtags with duplicates, 
    create a corresponding dataframe"""
	# Creates dataframe
    data = {'Hashtags': hashtagsUnique, 'Frequency': [0] * len(hashtagsUnique)}  
    df = pd.DataFrame(data)  

    # Finds frequency of each hashtag found.
    for i in hashtagsFull:
        for index, j in enumerate(df['Hashtags']):
            if(i == j):
                df['Frequency'][index] += 1

    # Sort values to descending.
    df = df.sort_values(['Frequency'], ascending=False)
    return df
	
def printData(hashtagDataFrame):	
	"""Given a dataframe of hashtags, print the dataframe"""
	print(hashtagDataFrame)

# Example usage 
#allHashtags = getListOfAllHashTags()
#uniqueHashtags = getListOfUniqueHashtags(allHashtags)
#hashtagData = createDataFrameOfHashtagsAndFills(uniqueHashtags, allHashtags)
#printData(hashtagData)


def createWordCloud(allHashtags):
    """Given a list of hashtags allHashtags, generate a corresponding wordcloud"""
    mask = np.array(Image.open('../moon.jpg'))
    text = " ".join(x.split()[0] for x in allHashtags)
    # Create and generate a word cloud image:
    wordcloud = WordCloud(width = 12000,
                          height = 9000,
                          #max_words = 200,
                          colormap = 'Purples',
                          mask = mask,
                          background_color = 'white').generate(text)

    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    wordcloud.to_file(image_path + 'wordCloud.png')


def main(read):
    df = pd.read_csv(read + ".csv",
                 dtype={"id_str": str, "in_reply_to_user_id_str": str, "from_user_id_str": str,
                        "in_reply_to_status_id_str": str, "user_followers_count": "Int64",
                        "user_friends_count": "Int64", "geo_coordinates": str}, 
                        parse_dates=['created_at']
                 )
    createTweetsTypeChart(df)
    plt.clf()
    createActiveDayTimelinePlot(df)
    plt.clf()
    createApplicationChart(df)
    plt.clf()
    createWordCloud(getListOfAllHashTags(read + ".json"))

def usage():
    print("Usage: ./generateGraphs <file prefix>")

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        usage()
    elif (not os.path.exists(data_path + sys.argv[1] + ".csv")):
        print("File does not exist: " + data_path + sys.argv[1] + ".csv")
        usage()
    elif (not os.path.exists(data_path + sys.argv[1] + ".json")):
        print("File does not exist: " + data_path + sys.argv[1] + ".json")
        usage()
    else:
        main(data_path + sys.argv[1])
        # print(default_path + sys.argv[1])