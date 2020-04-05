import os
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import datetime as dt
from collections import defaultdict, OrderedDict, Counter
import numpy as np
import emoji
from tabulate import tabulate
from nltk.sentiment import SentimentAnalyzer

class sqlObj:
    def __init__(self):
        db = "/Users/"+os.getlogin()+"/Library/Messages/chat.db"
        con = sqlite3.connect(db)
        self.curs = con.cursor()
        self.columns = {
            "date":'datetime(message.date/1000000000 + strftime("%s", \
                    "2001-01-01"), "unixepoch", "localtime") as date_utc',
            "text":'text',
            "is_from_me":'is_from_me',
            "handle_id":'handle_id',
            "ROWID": 'ROWID',
            "id": 'id'
        }

    def query(self,date=None,text=None,is_from_me=None,handle_id=None,
                ROWID=None,id_=None,table="message",condition=None):
        assert table in ["message","handle"], "Invalid table, must be either \
                                                'message' or 'handle'"
        if table == "message":
            assert any([date,text,is_from_me,handle_id]), "No columns \
                                                            selected from \
                                                            'message' table"
        else:
            assert any([ROWID,id_]), "No columns selected from 'handle' table"
        
        cols = ','.join([x for x, y in zip(self.columns.values(),
                                            [date,text,is_from_me,
                                             handle_id, ROWID, id_]) if y])

        if condition:
            query = 'select ' + cols + ' from ' + table + ' where ' + condition
        else:
            query = 'select ' + cols + ' from ' + table

        self.curs.execute(query)
        return self.curs.fetchall()
    
    def getHandleIds(self,number=None):
        if number:
            handle_rows = self.query(ROWID=True, table="handle",
                                    condition='id="'+number+'"')
        else:
            handle_rows = self.query(ROWID=True, table="handle")

        ids = [str(val[0]) for val in handle_rows]
        assert len(ids) > 0, "Number: {} not in database".format(number)
        return ids

    def getEmojis(self,s):
        if not s:
            return []
        return [c for c in s if c in emoji.UNICODE_EMOJI]

    def keywordFreq(self,keywords,number=None):
        assert len(keywords) > 0, "No keywords entered"

        if number:
            assert type(number) == str, "Number must be a string"
            handle_rows = self.query(ROWID=True,table="handle",
                                        condition='id='+number)
            ids = [str(val[0]) for val in handle_rows]
            assert len(ids) > 0, "Number: {} not in database".format(number)
        else:
            handle_rows = self.query(ROWID=True,table="handle")
            ids = [str(val[0]) for val in handle_rows]
            assert len(ids) > 0, "No numbers in database"
        
        rows = self.query(date=True, text=True,
                          condition='handle_id in ('+','.join(ids)+')')

        main = dict.fromkeys(keywords)
        for keyword in keywords:
            res = defaultdict(int)
            for row in rows:
                if row[1] and keyword in row[1].lower():
                    d = [int(v) for v in row[0].split(' ')[0].split('-')]
                    date = dt.date(*d)
                    res[dates.date2num(date)] += 1
            main[keyword] = res

        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(dates.DateFormatter("%Y-%m-%d"))

        plt.title("Word Frequency")
        plt.xlabel("Date")
        plt.ylabel("Frequency")
        plt.xticks(rotation=45, ha="right")
        for keyword in keywords:
            plt.plot(main[keyword].keys(),main[keyword].values(),label=keyword)
        plt.legend()
        fig.tight_layout()
        plt.savefig("results/keyword_freq")
        plt.show()
    
    def kMostCommon(self,k=10):
        ids = dict(self.query(ROWID=True,id_=True,table="handle"))
        rows = self.query(handle_id=True)

        res = dict.fromkeys(list(set(ids.values())),0)
        for row in rows:
            if row[0] in ids:
                res[ids[row[0]]] += 1

        sorted_d = OrderedDict(sorted(res.items(), key=lambda kv: kv[1],
                                        reverse=True))

        fig, ax = plt.subplots()
        plt.title("Contact Frequency")
        plt.xlabel("Contact")
        plt.ylabel("# of Messages")
        plt.bar(list(sorted_d.keys())[:k], list(sorted_d.values())[:k])
        plt.xticks(rotation=45,ha="right")
        fig.tight_layout()
        plt.savefig("results/contact_freq")
        plt.show()

    def compareMessageNums(self,number):
        ids = self.getHandleIds(number)

        rows = self.query(date=True,text=True,is_from_me=True,
                            condition='handle_id in ('+','.join(ids)+')')

        new_rows = []
        for row in rows:
            d = [int(v) for v in row[0].split(' ')[0].split('-')]
            date = dt.date(*d)
            new_rows.append([date,row[0],row[2]])
        rows = sorted(new_rows)
        res = {"Me": OrderedDict(), number: OrderedDict()}
        me_count = 0
        them_count = 0
        for row in rows:
            if row[2]:
                me_count += 1
                res["Me"][dates.date2num(row[0])] = me_count
            else:
                them_count += 1
                res[number][dates.date2num(row[0])] = them_count

        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(dates.DateFormatter("%Y-%m-%d"))

        plt.title("Number of Messages over Time")
        plt.xlabel("Date")
        plt.ylabel("# of Messages")
        plt.plot(res["Me"].keys(),res["Me"].values(),label="Me")
        plt.plot(res[number].keys(),res[number].values(),label=number)
        plt.legend()
        fig.tight_layout()
        plt.savefig("results/message_num")
        plt.show()

    def compareMessageLengths(self,number):
        ids = self.getHandleIds(number)

        rows = self.query(date=True,text=True,is_from_me=True,
                            condition='handle_id in ('+','.join(ids)+')')

        new_rows = []
        for row in rows:
            d = [int(v) for v in row[0].split(' ')[0].split('-')]
            date = dt.date(*d)
            new_rows.append([date, row[0], row[2]])
        rows = sorted(new_rows)
        res = {"Me": OrderedDict(), number: OrderedDict()}
        me_count = 0
        them_count = 0
        for row in rows:
            if row[2]:
                me_count += len(row[1])
                res["Me"][dates.date2num(row[0])] = me_count
            else:
                them_count += len(row[1])
                res[number][dates.date2num(row[0])] = them_count

        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(dates.DateFormatter("%Y-%m-%d"))

        plt.title("Cumulative Length of Messages over Time")
        plt.xlabel("Date")
        plt.ylabel("Cumulative Length of Messages")
        plt.plot(res["Me"].keys(), res["Me"].values(), label="Me")
        plt.plot(res[number].keys(), res[number].values(), label=number)
        plt.legend()
        fig.tight_layout()
        plt.savefig("results/message_len")
        plt.show()

    def mostCommonEmojis(self,number):
        ids = self.getHandleIds(number)

        rows = self.query(text=True,is_from_me=True,
                            condition='handle_id in ('+','.join(ids)+')')

        res = {"Me":Counter(),number:Counter()}
        for row in rows:
            if row[1]:
                res["Me"] += Counter(self.getEmojis(row[0]))
            else:
                res[number] += Counter(self.getEmojis(row[0]))
        
        res["Me"] = dict(sorted(res["Me"].items(),key=lambda kv: kv[1],
                                reverse=True))
        res[number] = dict(sorted(res[number].items(),key=lambda kv: kv[1],
                                    reverse=True))
        
        print("\nMy emoji usage:")
        print(tabulate([[emj, count] for emj, count in list(
            res["Me"].items())[:10]],headers=["Emoji","Count"]))
        print("\n"+number+" emoji usage:")
        print(tabulate([[emj, count] for emj, count in list(
            res[number].items())[:10]], headers=["Emoji","Count"]))
        print("\n")

    def sentimentAnalysis(self,number):
        ids = self.getHandleIds(number)

        rows = self.query(date=True,text=True,is_from_me=True,
                        condition='handle_id in ('+','.join(ids)+')')

        sent_analyzer = SentimentAnalyzer()

        res = {"Me":{},number:{}}

        plt.title("Sentiment Analysis")
        plt.ylabel("Sentiment")
        plt.xlabel("Date")
        plt.legend()
        plt.savefig("results/sentiment")
        plt.show()

    def timeOfDay(self,number):
        return


if __name__ == "__main__":
    s = sqlObj()
    res = s.query(date=True,text=True,condition='handle_id in (430)')
    # s.keywordFreq(["hey"])
    # s.kMostCommon(k=10)
    # s.compareMessageNums("+12345678901")
    # s.compareMessageLengths("+12345678901")
    #res = s.getAllMessages()
    
    

