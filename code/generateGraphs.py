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
import networkx as nx
from matplotlib import pylab
import seaborn as sns

data_path = "../data/"
image_path = "../images/"

def createTweetsTypeChart(df):
    """Given a dataframe df, generate a chart showing the proportion of tweets, retweets and replies"""
    total_replies = df[pd.notna(df['in_reply_to_user_id_str'])] # dataframe with replies only
    retweet_reply = total_replies[pd.notna(total_replies['retweet_user_id_str'])] # dataframe with replies that are also retweet
    non_reply = df[pd.isna(df['in_reply_to_user_id_str'])] # dataframe without replies
    retweet_only = non_reply[pd.notna(non_reply['retweet_user_id_str'])] # dataframe with retweets only
    tweet_only = non_reply[pd.isna(non_reply['retweet_user_id_str'])] # dataframe with tweets only

    x = [len(tweet_only),len(retweet_only),len(retweet_reply),len(total_replies) - len(retweet_reply)]
    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(x)))

    # plot
    fig, ax = plt.subplots()
    ax.pie(x, colors=colors, radius=2, center=(3, 3),labels=["Tweet", "Retweet", "Reply that is Retweet", "Reply"],
        wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=False,
        autopct="%1.1f%%")

    legend = ax.legend(loc='best', bbox_to_anchor=(1, -0.6, 0.5, 0.5), 
                    shadow=True, fontsize='medium', title = "CometLanding Data")


    # Put a nicer background color on the legend.
    legend.get_frame().set_facecolor('C0')

    plt.rcParams["figure.figsize"] = (5,5)

def createDailyTimelinePlot(df):
    # create new dataframe with creation date as index and grouped with the date
    days = df.set_index('created_at').groupby(pd.Grouper(freq='D'))

    # list of days with records of tweets
    day_labels = [str(ts.strftime("%d/%m"))
               for ts in days.count()["id_str"].index.tolist()]
    # list of number of tweets for each recorded date
    day_data = days.count()["id_str"].tolist()

    plt.rcParams["figure.figsize"] = (20, 30)

    plt.title("CometLanding timeline")
    plt.xlabel("Date (dd-MM-2014)")
    plt.ylabel("Number of tweets")

    plt.plot(day_labels, day_data)

def createActiveDayTimelinePlot(df):
    """Given a dataframe df, generate chart showing the timeline of the tweets
    for the day with the most records per hour"""

    date_raw = df[df['created_at'].apply(
    lambda x: True if re.search('^2014-11-12', str(x)) else False)] # get dataframe with tweets on 2014-11-12
    date = date_raw.set_index('created_at').groupby(pd.Grouper(freq='H'))

    date_labels = [str(ts.strftime("%H"))
               for ts in date.count()["id_str"].index.tolist()] # list of hours with records of tweets
    date_data = date.count()["id_str"].tolist() # list of number of tweets for each recorded hour

    plt.rcParams["figure.figsize"] = (5,5)
    
    plt.title("CometLanding timeline 2014/11/12")
    plt.xlabel("Hour")
    plt.ylabel("Tweets")

    plt.stem(date_labels, date_data)

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

def getListOfAllHashTags(file):
	"""Given a json filepath, return a list of hashtags found from the file"""
	# Open JSON file
	with open(file, 'r', encoding="utf8") as json_file:
		json_load = json.load(json_file)

	# List of hashtags found
	hashtagsFull = []
	i = 0
    
	# Gets list of hashtags from JSON file.
	for j in json_load:
		for i in j['hashtags']:
			if(i['text'].lower() != "cometlanding"):
				hashtagsFull.append(i['text'])
	json_file.close()
	return hashtagsFull

def getListOfUniqueHashtags(hashtagsFull):
	"""Given a list of hashtags hashtagsFull, returns a list of unique hashtags found from hashtagsFull"""
	# Gets unique hashtags.
	hashtagsUnique = pd.Series(hashtagsFull)
	hashtagsUnique = hashtagsUnique.unique()

	for index, i in enumerate(hashtagsUnique):
		if(i == "CometLanding"):
			hashtagsUnique[index] = ""
			break

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
    newdf = df[df['Frequency'] > 75]  
    return newdf

def createHashtagChart(file):
    """creates a chart showing the hashtags used and the no. of times used based
    on the given json file"""
    allHashtags = getListOfAllHashTags(file)
    uniqueHashtags = getListOfUniqueHashtags(allHashtags)
    hashtagData = createDataFrameOfHashtagsAndFills(uniqueHashtags, allHashtags)

    hashtagData = pd.DataFrame({'Hashtags':hashtagData['Hashtags'], 'Frequency':hashtagData['Frequency']})
    plt.rcParams.update({'font.size': 8})
    ax = hashtagData.plot.bar(x='Hashtags', y='Frequency', rot=0, figsize=(20,10))

    ax = sns.countplot(x="Hashtags", data=hashtagData)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    plt.tight_layout()

def createWordCloud(allHashtags):
    """Given a list of hashtags allHashtags, generate a corresponding wordcloud"""
    mask = np.array(Image.open(data_path + 'mask.jpg'))
    text = ""
    for x in allHashtags:
        text = text + " " + x.strip()

    # Create and generate a word cloud image:
    wordcloud = WordCloud(width = 12000,
                          height = 9000,
                          #max_words = 200,
                          colormap = 'viridis',
                          mask = mask,
                          collocations=False,
                          background_color = 'white').generate(text)

    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    return wordcloud

def createReplyNetwork(df):
    """creates a network for replies, showing the linkage between the sender and the user being
    replied"""

    replies_network = nx.Graph() # initialize network graph
    seenNodes_replies = set() # set of users involved in replies

    total_replies = df[pd.notna(df['in_reply_to_user_id_str'])] # dataframe with replies only

    for index, row in total_replies.iterrows(): # iterate each reply tweet

        node_1 = row['in_reply_to_screen_name'] # create node for username of replied user

        # add replied user node to network if not already exists and node is not null
        if node_1 not in seenNodes_replies and node_1 is not None:
            replies_network.add_node(node_1)
            seenNodes_replies.add(node_1) # update set of exisitng users in network
            
        node_2 = row['from_user'] # create node for username of the sender

        # add sender node to network if not already exists and node is not null
        if node_2 not in seenNodes_replies and node_2 is not None :
            replies_network.add_node(node_2)
            seenNodes_replies.add(node_2) # update set of exisitng users in network
            
        replies_network.add_edge(node_1,node_2) # add edge between sender and replied user to show linkage
        
        # print(row['in_reply_to_screen_name'], row['from_user'])
    return replies_network

def createRetweetNetwork(df):
    """creates a network for retweets, showing the linkage between tweet sender and the sender
    of the retweeted tweet"""

    retweet_network = nx.Graph() # initialize graph
    seenNodes_retweet = set() # set of users involved in retweets

    non_reply = df[pd.isna(df['in_reply_to_user_id_str'])] # dataframe without replies
    retweet_only = non_reply[non_reply['text'].apply(lambda x: True if re.search("^RT @.*",x) else False)] # dataframe with retweets only

    for index, row in retweet_only.iterrows(): # for each retweet

        node_1 = row["from_user"] # create node for sender

        # add sender node to network if not already exists and node is not null
        if node_1 not in seenNodes_retweet and node_1 is not None:
            retweet_network.add_node(node_1)
            seenNodes_retweet.add(node_1) # update set of exisitng users in network
            
        node_2 = row["text"].split(":")[0][2:] # create node for sender of retweeted tweet
        
        # add retweeted tweet sender node to network if not already exists and node is not null
        if node_2 not in seenNodes_retweet and node_2 is not None:
            retweet_network.add_node(node_2)
            seenNodes_retweet.add(node_2) # update set of exisitng users in network
        
        # add edge between sender and retweeted tweet sender to show linkage
        retweet_network.add_edge(node_1,node_2) 
    return retweet_network

def createMentionNetwork(df):
    """creates a network for mentions, showing the linkage between tweet sender and the other
    mentioned users"""

    mentions_network = nx.Graph() # initialize graph
    seenNodes_mentions = set() # set of users that are senders or mentioned in tweets

    for index, row in df.iterrows(): # for each tweet
        
        node_1 = row["from_user"] # create node for sender

        # add sender to network if not already exists and node is not null
        if node_1 not in seenNodes_mentions and node_1 is not None:
            mentions_network.add_node(node_1)
            seenNodes_mentions.add(node_1) # update set of exisitng users in network
            
        mentions = json.loads(row['entities_str'])['user_mentions'] # get array of user_mentions
        for men in mentions: # for each user mention
            node_2 = men['screen_name'] # get the screen name
            # if screen name is not null
            if node_2 is not None:
                # add mentioned user if not already in network
                if node_2 not in seenNodes_mentions:
                    mentions_network.add_node(node_2)
                    seenNodes_mentions.add(node_2) # update set of exisitng users in network

                # add edge between sender and mentioned user to show linkage
                mentions_network.add_edge(node_1, node_2) 

    return mentions_network

# https://stackoverflow.com/questions/17381006/large-graph-visualization-with-python-and-networkx
def plotNetworkGraph(network):
    """Given a network, plot the corresponding network graph"""
    #initialze Figure
    plt.figure(num=None, figsize=(800,800), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.spring_layout(network)
    nx.draw_networkx_nodes(network,pos)
    nx.draw_networkx_edges(network,pos, edge_color="r")
    nx.draw_networkx_labels(network,pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(-1*xmax, xmax)
    plt.ylim(-1*ymax, ymax)

    return fig
    # pylab.close()
    # del fig

def main(read):
    df = pd.read_csv(read + ".csv",
                 dtype={"id_str": str, "in_reply_to_user_id_str": str, "from_user_id_str": str,
                        "in_reply_to_status_id_str": str, "user_followers_count": "Int64",
                        "user_friends_count": "Int64", "geo_coordinates": str}, 
                        parse_dates=['created_at']
                 )
    createTweetsTypeChart(df)
    plt.savefig(image_path + "tweet_type.png", dpi=300, bbox_inches='tight')
    plt.clf()

    createDailyTimelinePlot(df)
    plt.savefig(image_path + "tweet_timeline_daily.png", dpi=300, bbox_inches='tight')
    plt.clf()

    createActiveDayTimelinePlot(df)
    plt.savefig(image_path + "tweet_timeline_2014_11_12.png", dpi=300, bbox_inches='tight')
    plt.clf()

    createApplicationChart(df)
    plt.savefig(image_path + "top_applications.png", dpi=300, bbox_inches='tight')
    plt.clf()

    createHashtagChart(read + ".json")
    plt.savefig(image_path + "popular_hashtags.png", dpi=300, bbox_inches='tight')
    plt.clf()

    wc = createWordCloud(getListOfAllHashTags(read + ".json"))
    wc.to_file(image_path + 'wordCloud.png')
    plt.clf()

    plotNetworkGraph(createReplyNetwork(df))
    plt.savefig(image_path + "reply_network.pdf")
    plt.clf()

    plotNetworkGraph(createRetweetNetwork(df))
    plt.savefig(image_path + "retweet_network.pdf")
    plt.clf()
    
    plotNetworkGraph(createMentionNetwork(df))
    plt.savefig(image_path + "mentions_network.pdf")
    plt.clf()

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