"""
WOW DB Project
World of Warcraft 3.3.5a Item List

Author: thuliast
Creation Date: 18-12-2019
"""

VERSION = "0.5a"
import sqlite3
import sys
from prettytable import from_db_cursor
from prettytable import PrettyTable

print("------------------------------------------")
print("|                                        |")
print("|                                        |")
print("|           World of Warcraft            |")
print("|               Item List                |")
print("|                                        |")
print("|              Version:",VERSION,"             |")
print("|                                        |")
print("------------------------------------------\n")



class encyclopedia(object):
    #Setup db connection
    def on_load(self):
        self.db_name = "wowdb.sqlite3"
        try:
            self.con = sqlite3.connect(self.db_name, timeout = 20)
            self.cur = self.con.cursor()
        except sqlite3.Error as error:
            print("Connection Error. " + error)

            
    def db_search(self,item_to_search):
        self.item_to_search = item_to_search
        self.cur = self.con.cursor()
        self.cur.execute("SELECT entry, name, itemlevel, requiredlevel \
FROM item_list WHERE name LIKE ? ORDER BY entry",('%{}%'.format(self.item_to_search),))        
        self.tb = from_db_cursor(self.cur)
        print(self.tb.get_string(title="List of Items found"))
        
        print("-" * 80)
        self.choice = input("Another search(y) or quit(n)? :")
        self.choice = self.choice.lower()
        if self.choice == "n":
            print("Have a nice day")
            self.on_exit()
        elif self.choice == "y":
            main()
        else :
            print("Unrecognized choice. Quit to Main")
            main()
    

    def on_exit(self):    
        self.cur.close()
        self.con.close()
        sys.exit()


def main():
    e = encyclopedia()
    e.on_load()
    choice = "y"
    while choice == "y":
        item = input("Type the item(s) you want to search: ")
        if item != "":
            e.db_search(item)
        print("\n")
        
        
if __name__=="__main__":
    main()
