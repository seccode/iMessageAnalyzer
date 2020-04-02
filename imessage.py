import os
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import datetime as dt
from collections import defaultdict, OrderedDict
import numpy as np

class sqlObj:
    def __init__(self):
        db = "/Users/"+os.getlogin()+"/Library/Messages/chat.db"
        con = sqlite3.connect(db)
        self.curs = con.cursor()

    def keywordFreq(self,keywords,number=None):
        assert len(keywords) > 0, "No keywords entered"

        if number:
            assert type(number) == str, "Number must be a string"
            _ = self.curs.execute('select ROWID from handle where id="'+number+'"')
            ids = tuple([val[0] for val in self.curs.fetchall()])
            assert len(ids) > 0, "Number: {} not in database".format(number)
        else:
            _ = self.curs.execute('select ROWID from handle')
            ids = tuple([val[0] for val in self.curs.fetchall()])
            assert len(ids) > 0, "No numbers in database"
        
        main = dict.fromkeys(keywords)
        for keyword in keywords:
            res = defaultdict(int)
            self.curs.execute(
                'select datetime(message.date/1000000000 + strftime("%s", \
                "2001-01-01") ,"unixepoch","localtime") as date_utc, \
                text from message where handle_id in '+str(ids))

            rows = self.curs.fetchall()
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
        plt.savefig("keyword_freq")
        plt.show()
    
    def kMostCommon(self,k=10):
        _ = self.curs.execute('select ROWID, id from handle')
        ids = dict(self.curs.fetchall())
        self.curs.execute(
            'select handle_id from message')
        rows = self.curs.fetchall()
        res = dict.fromkeys(list(set(ids.values())),0)
        for row in rows:
            if row[0] in ids:
                res[ids[row[0]]] += 1

        sorted_d = OrderedDict(sorted(res.items(), key=lambda kv: kv[1],reverse=True))

        fig, ax = plt.subplots()
        plt.title("Contact Frequency")
        plt.xlabel("Contact")
        plt.ylabel("# of Messages")
        plt.bar(list(sorted_d.keys())[:k], list(sorted_d.values())[:k])
        plt.xticks(rotation=45,ha="right")
        fig.tight_layout()
        plt.savefig("contact_freq")
        plt.show()

    def compareMessageNums(self,number):
        _ = self.curs.execute('select ROWID from handle where id="'+number+'"')
        ids = tuple([val[0] for val in self.curs.fetchall()])
        assert len(ids) > 0, "Number: {} not in database".format(number)

        _ = self.curs.execute(
            'select datetime(message.date/1000000000 + strftime("%s", \
                "2001-01-01") ,"unixepoch","localtime") as date_utc, \
                text, is_from_me from message where handle_id in '+str(ids))
        rows = self.curs.fetchall()
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
        plt.savefig("message_num")
        plt.show()

    def compareMessageLengths(self,number):
        _ = self.curs.execute('select ROWID from handle where id="'+number+'"')
        ids = tuple([val[0] for val in self.curs.fetchall()])
        assert len(ids) > 0, "Number: {} not in database".format(number)

        _ = self.curs.execute(
            'select datetime(message.date/1000000000 + strftime("%s", \
                "2001-01-01") ,"unixepoch","localtime") as date_utc, \
                text, is_from_me from message where handle_id in '+str(ids))
        rows = self.curs.fetchall()
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
        plt.savefig("message_len")
        plt.show()

    def getAllMessages(self):
        self.curs.execute(
            'select datetime(message.date/1000000000 + strftime("%s", \
            "2001-01-01") ,"unixepoch","localtime") as date_utc, \
            text from message')
        rows = self.curs.fetchall()
        ret = {}
        for row in rows:
            ret[row[0]] = row[1]
        return ret

if __name__ == "__main__":
    s = sqlObj()
    # s.keywordFreq(["hey"])
    s.kMostCommon(k=10)
    # s.compareMessageNums("+12345678901")
    # s.compareMessageLengths("+12345678901")
    #res = s.getAllMessages()
    
    

