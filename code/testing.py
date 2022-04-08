import pandas as pd
import numpy as np
import sys
import unittest
import time
import datetime

import generateGraphs as gg
import fixdata as fd

def readCSV():
    df = pd.read_csv("../data/CometLandingFixed.csv",
            dtype={"id_str": str, "in_reply_to_user_id_str": str, "from_user_id_str": str,
                    "in_reply_to_status_id_str": str, "user_followers_count": "Int64",
                    "user_friends_count": "Int64", "geo_coordinates": str, "retweet_user_id_str": str}
                 , parse_dates=['created_at']
            )
    return df

class Tests(unittest.TestCase):
    # Test on if filtering of dates is functioning properly.
    def test_one(self):
        df = readCSV()
        start_date = time.mktime(datetime.datetime.strptime(
           '2014/11/12', "%Y/%m/%d").timetuple())
        end_date = time.mktime(datetime.datetime.strptime(
            '2014/12/06', "%Y/%m/%d").timetuple())

        test_date_after_out = time.mktime(
            datetime.datetime.strptime('2014/12/07', "%Y/%m/%d").timetuple())
        test_date_before_out= time.mktime(
            datetime.datetime.strptime('2014/11/11', "%Y/%m/%d").timetuple())

        fd.filter_data(df)
        for date in df['created_at']:
            self.assertEqual(True, (date.timestamp() >= start_date))
            self.assertEqual(True, (date.timestamp() < end_date))

        self.assertEqual(False, (test_date_before_out >= start_date))
        self.assertEqual(True, (test_date_before_out < end_date))

        self.assertEqual(True, (test_date_after_out >= start_date))
        self.assertEqual(False, (test_date_after_out < end_date))

    pass

    # Test on if filtering of duplicates and null records is functioning properly.
    def test_two(self):
        df = readCSV()
        noOfRecordsBefore = len(df)

        fd.filter_data(df)
        noOfRecordsAfter = len(df)
        self.assertEqual(noOfRecordsBefore, noOfRecordsAfter) # Nothing removed

        df.iloc[noOfRecordsBefore - 1] = df.iloc[1]
        #df.iloc[noOfRecordsBefore - 2] = NULL
        noOfRecordsBefore = len(df)
        fd.filter_data(df)
        noOfRecordsAfter = len(df)

        # One duplicate record removed
        self.assertEqual(noOfRecordsBefore - 1, noOfRecordsAfter)

    pass

    # Tests that unique users amount is found.
    def test_three(self):
        df = readCSV()
        df2 = readCSV()
        df.iloc[0] = df.iloc[4]
        df.iloc[1] = df.iloc[4]
        df.iloc[2] = df.iloc[4]
        df.iloc[3] = df.iloc[4]


        fd.filter_data(df)
        uniqueUsers = len(df)
        uniqueUsersTest = len(df2)
        self.assertEqual(uniqueUsers + 4, uniqueUsersTest)
    pass

    # Tests that unique hashtags are found.
    def test_four(self):
        df = readCSV()
        allHashtags = gg.getListOfAllHashTags("../data/CometLandingFixed.json")
        unique = gg.getListOfUniqueHashtags(allHashtags.append('67P'))
        newunique = pd.Series(allHashtags)
        unique2 = newunique.unique()

        self.assertEqual(len(unique) < len(allHashtags), True)
        for i in range(len(unique)):
           self.assertEqual(unique[i], unique2[i])
    pass
    # Tests that top 25 hashtags are the same found in functions.
    def test_five(self):
        df = readCSV()
        allHashtags = gg.getListOfAllHashTags("../data/CometLandingFixed.json")
        unique = gg.getListOfUniqueHashtags(allHashtags)
        newdf = gg.createDataFrameOfHashtagsAndFills(unique, allHashtags)
        newdf2 = newdf.reset_index()
        for i in range(25):
           self.assertEqual(newdf2['Frequency'][i],
                            allHashtags.count(newdf2['Hashtags'][i]))
    pass

    def test_six(self):
        df = readCSV()
        beforeRemovedNan = len(df)

        df['id_str'][0] = np.nan
        recordThatWillReplace = df['id_str'][1]
        self.assertEqual(pd.isna(df['id_str'][0]), True)

        fd.filter_data(df)

        afterRemovedNan = len(df)
        self.assertEqual(beforeRemovedNan - 1, afterRemovedNan)
        self.assertEqual(df['id_str'][1], recordThatWillReplace)
    pass

    def test_seven(self):
        df = readCSV()
        beforeRemovedNan = len(df)

        df['text'][0] = np.nan
        recordThatWillReplace = df['text'][1]
        self.assertEqual(pd.isna(df['text'][0]), True)

        fd.filter_data(df)

        afterRemovedNan = len(df)
        self.assertEqual(beforeRemovedNan - 1, afterRemovedNan)
        self.assertEqual(df['text'][1], recordThatWillReplace)
    pass

    def test_eight(self):
        df = readCSV()
        beforeRemovedNan = len(df)

        df['from_user_id_str'][0] = np.nan
        recordThatWillReplace = df['from_user_id_str'][1]
        self.assertEqual(pd.isna(df['from_user_id_str'][0]), True)

        fd.filter_data(df)

        afterRemovedNan = len(df)
        self.assertEqual(beforeRemovedNan - 1, afterRemovedNan)
        self.assertEqual(df['from_user_id_str'][1], recordThatWillReplace)
    pass

    def test_nine(self):
        df = readCSV()
        beforeRemovedNan = len(df)

        df['entities_str'][0] = np.nan
        recordThatWillReplace = df['entities_str'][1]
        self.assertEqual(pd.isna(df['entities_str'][0]), True)

        fd.filter_data(df)

        afterRemovedNan = len(df)
        self.assertEqual(beforeRemovedNan - 1, afterRemovedNan)
        self.assertEqual(df['entities_str'][1], recordThatWillReplace)
    pass

    def test_ten(self):
        df = readCSV()
        #print(df)
        #print(df['entities_str'][0])
        df['entities_str'][0] = "{'hashtags':[{'text':'Philae','indices':[49,56]},{'text':'google','indices':[139,140]}],'symbols':[],'user_mentions':[{'screen_name':'VersaTechnology','name':'Versa Technology','id':30264992,'id_str':'30264992','indices':[3,19]},{'screen_name':'Philae2014','name':'Philae Lander','id':208442526,'id_str':'208442526','indices':[37,48]}],'urls':[{'url':'http://t.co/6SoGeZTS9N','expanded_url':'http://cnn.it/1qDQu0s','display_url':'cnn.it/1qDQu0s','indices':[139,140]}]}"
        #print(df['entities_str'][0])
        beforeRemoval = len(df)
        fd.filter_data(df)
        afterRemoval = len(df)
        #print(df)
        self.assertEqual(beforeRemoval - 1, afterRemoval)
    pass

def suite():
    loader = unittest.TestLoader()
    testsuite = loader.loadTestsFromTestCase(Tests)
    return testsuite

def test():
    testsuite = suite()
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    result = runner.run(testsuite)

if __name__ == "__main__":
    test()