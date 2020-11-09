"""
WOW DB Project
World of Warcraft 3.3.5a Item List

Author: thuliast
Creation Date: 18-12-2019
"""

VERSION = "0.4"
import sqlite3
import sys

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

    def print_header(self):
        #A small function to print line separator
        print("-" * 80)
        print("%5s | %50s | %5s | %5s" % ("ID.","Description","Item Lvl","Req.Lvl"))
        print("-" * 80)
        
        
    def db_search(self,item_to_search):
        counter = 0
        self.item_to_search = item_to_search
        self.cur.execute("SELECT entry, name, itemlevel, requiredlevel \
FROM item_list WHERE name LIKE ? ORDER BY entry",('%{}%'.format(self.item_to_search),))        
        result = self.cur.fetchall()
        self.print_header()
        
        if result is None:
            print("No record(s) match your request.")
            main()
        else:
            for element in result:
                print("%5s | %50s | %8s | %5s" % (element[0],element[1],element[2],element[3]))
                counter += 1

        print("-" * 80)
        print("Number of elements found: " ,str(counter))

    
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
        choice = input("Another search(y) or quit(n)? :")
        choice = choice.lower()
    if choice == "n":
        print("Have a nice day")
        e.on_exit()


if __name__=="__main__":
    main()
