import os
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import datetime as dt
from collections import defaultdict

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
        plt.xticks(rotation=45)
        for i, keyword in enumerate(keywords):
            plt.plot(main[keyword].keys(),main[keyword].values(),label=keyword)
        plt.legend()
        fig.tight_layout()
        plt.savefig("result")
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
    #res = s.getAllMessages()
    
    

