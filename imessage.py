import os
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import datetime as dt
from collections import defaultdict, OrderedDict

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
            assert len(ids) > 0, "Number not in database"
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
        assert len(ids) > 0, "Number not in database"

        _ = self.curs.execute(
            'select text, is_from_me from message where handle_id in '+str(ids))
        rows = self.curs.fetchall()
        tot = len(rows)
        count = 0
        for row in rows:
            if row[1]:
                count += 1

        fig, ax = plt.subplots()
        plt.title("Number of Messages Comparison")
        plt.xlabel("Number")
        plt.ylabel("# of Messages")
        plt.bar(.25,count,.5,label="Me")
        plt.bar(.75,tot - count,.5,label=number)
        plt.legend()
        fig.tight_layout()
        plt.tick_params(
            axis='x',
            which='both',
            bottom=False,
            top=False,
            labelbottom=False)
        plt.savefig("message_num")
        plt.show()

    def compareMessageLengths(self,number):
        _ = self.curs.execute('select ROWID from handle where id="'+number+'"')
        ids = tuple([val[0] for val in self.curs.fetchall()])
        assert len(ids) > 0, "Number not in database"

        _ = self.curs.execute(
            'select text, is_from_me from message where handle_id in '+str(ids))
        rows = self.curs.fetchall()
        me = 0
        them = 0
        for row in rows:
            if not row[0]:
                continue
            if row[1]:
                me += len(row[0])
            else:
                them += len(row[0])

        fig, ax = plt.subplots()
        plt.title("Length of Messages Comparison")
        plt.xlabel("Number")
        plt.ylabel("Total Messages Length")
        plt.bar(.25, me, .5, label="Me")
        plt.bar(.75, them, .5, label=number)
        plt.legend()
        fig.tight_layout()
        plt.tick_params(
            axis='x',
            which='both',
            bottom=False,
            top=False,
            labelbottom=False)
        plt.savefig("message_len")
        plt.show()
        return

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
    s.kMostCommon(k=10)
    #res = s.getAllMessages()
    
    

