import subprocess
import sqlite3
import operator
import requests
import time
import re
import json
from requests.auth import HTTPBasicAuth
import requests_unixsocket

def old_line():
    return 0



def add_information(message,extra_info):
    con = sqlite3.connect('alerts.db')
    with con:
         cur = con.cursor()
         query = "INSERT INTO alerts VALUES (null,?,?,?,?,?,?,?,?,?)"
         cur.execute(query,["",1000,message,"","","","",extra_info,""])
         con.commit()
         print("Information logged into alerts")
    return


def check_alerts(command,block_hash):
   #####################################
   #                                   #
   #          TRIGGER LEVELS           #
   #                                   #
   #####################################

    cell_transfer = 5000
    mcell_transfer = 50
    reward_amount = 490
    bridge_amount = 4900
    stake_amount = 10000

   #####################################


    print("CHECKING ALERTS")
    list_items = len(command)
    reward = 0
    #      print(list_items)
    for x in range(list_items):

         #### get date and time in here as we also want to see the exact time
        if "ts_created:" in command[x]:  ## check through every list item to locate transaction created date
            length = len(command[x])
            ts_created = operator.getitem(command[x], slice(length - 26, length - 6))  # if found, copy last 24 letters


        if "IN_EMS:" in command[x]:  ## check through every list item to locate transaction created date
            if "OUT:" in command[x+4]:
                 take1 = command[x+5]
                 search_results = re.finditer(r'\(.*?\)', take1) #find the VALUE of EMISSION
                 for item in search_results:
                       item.group(0)
                 value = item.group(0).rstrip(')').lstrip('(')
                 value2 =int(value) / 1000000000000000000

                 length=len(command[x+6])
                 wallet = operator.getitem(command[x+6], slice(length-104,length)) #get receiving wallet
                 short_wallet = wallet[:10] + "..." + wallet[-15:]

                 if value2 > bridge_amount:
                     print("VALUE:",value2,"into",wallet)

                     con = sqlite3.connect('alerts.db')
                     with con:
                        cur = con.cursor()
                        print("CRE",ts_created)
                        query = "INSERT INTO alerts VALUES (null,?,?,?,?,?,?,?,?,?)"
                        cur.execute(query,[ts_created,0,"was brave enough to bridge ",short_wallet," into CF20.",value2,"CELL","",block_hash])
                        con.commit()
                        print("Alert inserted into database")
                 else:
                     print("nothing major")


        if ("OUT EXT:" in command[x]) and ("OUT EXT:" in command[x+4]) and ("OUT COND:" in command[x+8]):
             ticker = command[x+2]
             if ticker[-5:] == "mCELL":
                 take1 = command[x+3] #find the VALUE of mCELL transfer
                 search_results = re.finditer(r'\(.*?\)', take1) #find the VALUE
                 for item in search_results:
                    item.group(0)
                 value = item.group(0).rstrip(')').lstrip('(')
                 value2 = int(value) / 1000000000000000000
                 if value2 > mcell_transfer:

                     length = len(command[x+1])
                     receiver = operator.getitem(command[x+1], slice(length-104,length)) #get receiving wallet
                     short_wallet = receiver[:10] + "..." + receiver[-15:]
                     length = len(command[x+5])
                     sender = operator.getitem(command[x+5], slice(length-104,length)) #get receiving wallet
                     short_wallet2 = sender[:10] + "..." + sender[-15:]
                     print(short_wallet,"received",value2,"mCELL from",short_wallet2)

                     con = sqlite3.connect('alerts.db')
                     with con:
                           print(short_wallet,"received ",value2,"CELL from",short_wallet2)
                           cur = con.cursor()
                           print("CRE",ts_created)
                           query = "INSERT INTO alerts VALUES (null,?,?,?,?,?,?,?,?,?)"
                           cur.execute(query,[ts_created,20,"sent",short_wallet,short_wallet2,value2,"mCELL","into",block_hash])
                           con.commit()
                           print("Alert inserted into database")




        if ("OUT:" in command[x]) and ("OUT COND:" in command[x+3]) and ("OUT:" in command[x+9]):
             take1 = command[x+1]
             search_results = re.finditer(r'\(.*?\)', take1) #find the VALUE
             for item in search_results:
                item.group(0)
             value = item.group(0).rstrip(')').lstrip('(')
             value2 = int(value) / 1000000000000000000
             if value2 > cell_transfer: #if the amount was higher than our trigger level
                 length = len(command[x+2])
                 receiver = operator.getitem(command[x+2], slice(length-104,length)) #get receiving wallet
                 short_wallet = receiver[:10] + "..." + receiver[-15:]
                 length = len(command[x+11])
                 sender = operator.getitem(command[x+11], slice(length-104,length)) #get sender wallet
                 short_wallet2 = sender[:10] + "..." + sender[-15:]

                 con = sqlite3.connect('alerts.db')
                 with con:
                         print(short_wallet,"received ",value2,"CELL from",short_wallet2)
                         cur = con.cursor()
                         print("CRE",ts_created)
                         query = "INSERT INTO alerts VALUES (null,?,?,?,?,?,?,?,?,?)"
                         cur.execute(query,[ts_created,10,"sent",short_wallet,short_wallet2,value2,"CELL","into",block_hash])
                         con.commit()
                         print("Alert inserted into database")



        if "DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE" in command[x]: ## check through every list item to see if there is delegation transaction
             length = len(command[x])
#             print(command)
             take1 = command[x-1]

             search_results = re.finditer(r'\(.*?\)', take1) #find the VALUE
             for item in search_results:
                item.group(0)
             value = item.group(0).rstrip(')').lstrip('(')
             value2 = int(value) / 1000000000000000000

             length = len(command[x+4])
             pkey = operator.getitem(command[x+3], slice(len(command[x+3])-66,len(command[x+3])))
             print("pkey length",len(pkey))
             node = operator.getitem(command[x+4], slice(length-22,length)) #GET NODE ADDRESS and copy last  24 letters
#             print(command[x+6])



             #Now need to go so much forward until we find OUT EXT:
             scope=20
             for y in range(scope):
               cleared = command[y+x].strip() #remove whitespaces
              # print(cleared)
              # print("command",command[x+y])

               if cleared == "OUT EXT:":
                   print("found it",command[y+x])
                   length = len(command[x+y+1])
                   print("here",command[x+y+1])
                   wallet = operator.getitem(command[x+y+1], slice(length-104,length)) #get delegator wallet
                   short_wallet = wallet[:10] + "..." + wallet[-15:]


             print("")
             print("**************************")
             print("We have token DELEGATION",ts_created)
             print(short_wallet,"delegated",value2,"mCELL for",node,"with pkey hash:",pkey,":::")
             print("**************************")
             print("")
             con = sqlite3.connect('alerts.db')
             with con:
                     cur = con.cursor()
                     print("CRE",ts_created)
                     query = "INSERT INTO alerts VALUES (null,?,?,?,?,?,?,?,?,?)"
                     cur.execute(query,[ts_created,2,"delegated",short_wallet,"for the node",value2,"mCELL",node,block_hash])
                     con.commit()
                     print("Alert inserted into database")



        if "DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_LOCK" in command[x]: # if we have stake transaction
#             break
             length = len(command[x])
             print(command[x])
             take1 = command[x-1] #grab CELL value

             search_results = re.finditer(r'\(.*?\)', take1) #find the VALUE
             for item in search_results:
                item.group(0)
             value = item.group(0).rstrip(')').lstrip('(')
             value2 =int(value) / 1000000000000000000
             print("value2 :",value2)

             length = len(command[x+2])
             time_unlock = operator.getitem(command[x+2], slice(length-21,length)) #if found, copy last 24 letters
#             print(command[x+6])
             time_unlock = time_unlock.strip()

             month = time_unlock[:3]
#             month = str(month_to_number(month))
#             print("month",month)

             year = time_unlock[-4:]
 #            print("year",year)

             day = time_unlock[4:-14]
#             print("day",day)
#             date=parse_date2(time_unlock)

             ending_date = day+'.'+month+'.'+year
             #Now need to go so much forward until we find OUT EXT:
             scope=20
             for y in range(scope):
               cleared = command[y+x].strip() #remove whitespaces
              # print(cleared)
              # print("command",command[x+y])


               if cleared == "OUT EXT:":
                   print("found it",command[y+x])
                   length = len(command[x+y+1])
                   print("here",command[x+y+1])

                   ticker2=command[y+x+2]
                   ticker=ticker2[-5:].strip()

                   ticker_test=command[y+x+6]    #see if next OUT EXT: is actually mKEL
                   ticker_test = ticker_test[-5:].strip()

                   print("ticker test",ticker_test)
                   print("ticker:",ticker)
                   wallet = operator.getitem(command[x+y+1], slice(length-104,length)) #get delegator wallet
                   short_wallet = wallet[:10] + "..." + wallet[-15:]
                   print("value:",value2, type(value2))
                   if ticker == "KEL" or ticker == "mKEL":
                      break
#                   if (ticker == "CELL" or ticker == "mCELL") and ticker_test != "mKEL" and value2 > 500:
                   if ticker == "CELL" and ticker_test != "mKEL" and value2 > stake_amount:

                      print("")
                      print("********** S T A K E ****************")
                      print("We have CELL stake transaction",ts_created)
                      print(short_wallet,"staked",value2,"CELL until ",ending_date)
                      print("*************************************")
                      print("")

                      con = sqlite3.connect('alerts.db')
                      with con:
                        cur = con.cursor()
                        print("CRE",ts_created)
                        query = "INSERT INTO alerts VALUES (null,?,?,?,?,?,?,?,?,?)"
                        cur.execute(query,[ts_created,1,"staked ",short_wallet,"until ",value2,ticker,ending_date,block_hash])
                        con.commit()
                        print("Alert inserted into database")


        if "IN_REWARD" in command[x]:
             reward = 1

        if "Address:" in command[x] and reward == 1:
                  length=len(command[x])
                  wallet = operator.getitem(command[x], slice(length-104,length)) #get receiving wallet

                  length = len(command[x+3])
                  transaction_pkey = operator.getitem(command[x+3], slice(len(command[x+3])-66,len(command[x+3])))
                  con = sqlite3.connect('cellframe.db')
                  with con:
                     cur = con.cursor()
                     cur.execute("""SELECT address FROM node_wallets WHERE pkey=? AND wallet=?""",[transaction_pkey,wallet]) #MATCH wallet with NODE
                     node, = cur.fetchone()
                     node = parse_node_address(node)
#                     print("NODE:",node,"on tassa!")

                     ######## GET REWARD VALUE #######
                     take1 = command[x-1]
                     search_results = re.finditer(r'\(.*?\)', take1) #find the VALUE
                     for item in search_results:
                       item.group(0)
                     value = item.group(0).rstrip(')').lstrip('(')
                     value2 =int(value) / 1000000000000000000
                     print("address:",wallet," got reward of ",value2," CELL")
                     short_wallet = wallet[:10] + "..." + wallet[-15:]

                     reward = 0
                     if value2 > 499:

                         con = sqlite3.connect('alerts.db')
                         with con:
                              cur = con.cursor()
                              print("CRE",ts_created)
                              query = "INSERT INTO alerts VALUES (null,?,?,?,?,?,?,?,?,?)"
                              cur.execute(query,[ts_created,8," received ",short_wallet," whopping",value2,"CELL","in rewards!",block_hash])
                              con.commit()
                              print("Reward alert inserted into database")



#    input("STOP NOW!")
    return












def update_wallet_database():
    print("We are now checking wallet database and updating it")
    con = sqlite3.connect('cellframe.db')
    with con:

        cur = con.cursor()
        query = """ SELECT id FROM wallet_data_organized ORDER BY id DESC"""
        cur.execute(query)
        wallets, = cur.fetchone()  # grab 1 line at the end to see how may wallets we have
        print("We have :", wallets, "to update")

        #        for x in range(1,wallets+1):

        query = """ SELECT current_day FROM flags WHERE id=0"""
        cur.execute(query)
        today, = cur.fetchone()
        print("We are now at day :", today)

        last_update = check_wallet_database_date()

        print("Wallet database was last updated :", last_update)

        #############################################
        #                                           #
        # DO WE NEED TO UPDATE?                     #
        # ARE WE STILL IN THE SAME DAY AS DATABASE? #
        #                                           #
        #############################################

        if last_update == today:
            print("We don't need to update wallet database")
            return
        else:
            print("We need to update wallet_database")

        print("Updating database...")

        dump_wallets()

        for x in range(1, wallets + 1):
            cur = con.cursor()
            query = """ SELECT wallet_address,cell_balance,mcell_balance FROM wallet_data_organized WHERE id=?"""
            cur.execute(query, [x])
            wallet_address, cell_balance, mcell_balance = cur.fetchone()  # Get all data from that wallet
            short_wallet_address = wallet_address[-10:]
            #            short_wallet_address = "N" + short_wallet_address #we add N as sqlite doesn't like table names that begin with number

            if check_if_name_in_all_wallets_list(
                    short_wallet_address) == 0:  # if wallet was not added before, now is time to do that
                # ADD WALLETS name TO DATABASE name list and ACTIVATE wallets own table
                add_wallet(short_wallet_address, today, wallet_address, cell_balance, mcell_balance)

            update_wallet_balance(short_wallet_address, wallet_address, today, cell_balance, mcell_balance)
        update_current_day_to_wallet_database(today)  # update last update date and then we are done
        update_number_of_wallets_today(today)
        return


def update_current_day_to_wallet_database(today):
    con = sqlite3.connect('wallet_database.db')
    with con:
        cur = con.cursor()
        query = """ UPDATE {table} SET last_update_date=? WHERE id=1""".format(table="flags")
        cur.execute(query, [today])
        con.commit()
        print("Wallets database was updated and date has been changed into", today)
        return


def update_wallet_balance(short_wallet_address, wallet_address, today, cell_balance, mcell_balance):
    con = sqlite3.connect('wallet_database.db')
    with con:
        short_wallet_address = "N" + short_wallet_address
        cur = con.cursor()
        query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table=short_wallet_address)
        cur.execute(query)
        lines = cur.fetchone()
        #        print(lines)

        if lines == None:  ##### IF there is no lines yet, we also want to include full wallet address @ id=1
            cur = con.cursor()
            query = """ INSERT INTO {table} VALUES (null,?,?,?,?)""".format(table=short_wallet_address)
            cur.execute(query, [today, wallet_address, cell_balance, mcell_balance])
            con.commit()

        else:  # if this is not the first line, then add everything excluding full wallet address
            cur = con.cursor()
            query = """ INSERT INTO {table} VALUES (null,?,"",?,?)""".format(table=short_wallet_address)
            cur.execute(query, [today, cell_balance, mcell_balance])
            con.commit()

        return


def add_wallet(short_wallet_address, wallet_address, today, cell_balance, mcell_balance):
    con = sqlite3.connect('wallet_database.db')
    with con:
        #        print("checking",short_wallet_address)
        cur = con.cursor()
        query = """ INSERT INTO all_table_names VALUES(null,?)"""
        cur.execute(query, [short_wallet_address])
        con.commit()

        short_wallet_address = "N" + short_wallet_address

        query = """ CREATE TABLE {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, address TEXT, cell_balance REAL, mcell_balance REAL)""".format(
            table=short_wallet_address)
        cur.execute(query)
        con.commit()
        return


def check_if_name_in_all_wallets_list(wallet_table):
    wallet_name = wallet_table
    con = sqlite3.connect('wallet_database.db')
    with con:
        cur = con.cursor()
        query = """SELECT id FROM {table} WHERE wallet_name=?""".format(table="all_table_names")

        cur.execute(query, [wallet_name])
        onko = cur.fetchone()
        #           print("Do we have it?",onko,)
        if onko == None:
            return 0

        return 1


def check_wallet_database_date():
    print("We are now checking wallet database and updating it")
    con = sqlite3.connect('wallet_database.db')
    with con:
        cur = con.cursor()
        query = """ SELECT last_update_date FROM flags WHERE id=1"""
        cur.execute(query)
        last_update, = cur.fetchone()  # grab 1 line at the end to see how may wallets we have
        return last_update


# CHECKS IO NODE HAS ITS NAME IN all_node_names list or not
def check_if_name_in_all_nodes_list(name):
     con=sqlite3.connect('cellframe.db')
     with con:
            cur = con.cursor() # ADD THIS NEW NODE TO NODE NAMES LIST ALSO
            query = """SELECT id FROM {table} WHERE node_name=?""".format(table="all_node_names")

            cur.execute(query,[name])
            onko = cur.fetchone()
            print("no?",onko)
            if onko == None:
               return 0

            return 1





def main_hashing2():
        database = r"cellframe.db"

        # create a database connection
        con = create_connection(database)

        global daily_tx_counter
        daily_tx_counter=0


        input("Ready to launch?...")

        file = open("all_blocks.txt","r")
        ## DO THIS FIRST
        ##  cellframe-node-cli block list -net Backbone -chain main >> all_blocks.txt

        with open(r"all_blocks.txt", 'r') as fp: ##count lines in our file
           for count, line in enumerate(fp):
               pass
               count += 1

        print("Lines",count)



        cur = con.cursor() #lets first see where we left last time and then we can continue from there
        query = """ SELECT hash_line_counter FROM flags WHERE id=0"""
        cur.execute(query)
        old_hash_line, = cur.fetchone()
        print("Old hash line :",old_hash_line)
        old_hash_line = 24886 #24985 #24215                           ##### THIS IS WHERE WE WILL BEGIN OUR SEARCH ####
        lines_to_go = count-old_hash_line
        if lines_to_go < 2:
            return

        print("We have ",lines_to_go,"new hashes")
        input("Should we go or stop?")

        if old_hash_line != 0:
            for y in range(old_hash_line):
              temp = file.readline() #lets read lines until we reach position where last time we ended
        #      print("temp :",temp)

        for x in range(count):
          block_hash = file.readline()
          block_hash = block_hash[1:67]
          print("x = ",x," Count = ",count)
          print("NOW Using:",block_hash[:20],"...",block_hash[-10:])
          print(len(block_hash))
#          input("sto")
          if len(block_hash) != 66: #if our hash is somethign other than hash --> exit
             print("All hashing done in main_hashing2!")
             return 0

          parse_block_hash(block_hash)
          return











def recalculate_all_time_blocks_and_signatures():
      con = sqlite3.connect('cellframe.db')
      cur = con.cursor()
      query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="all_node_names")
      cur.execute(query)
      row_id, = cur.fetchone()
      print("rows to go", row_id)

      for x in range(1, row_id + 1):
         print(x)
         query = """ SELECT node_name FROM all_node_names WHERE id=?""".format()
         cur.execute(query,[x])
         node_name, = cur.fetchone()
         #address=parse_node_address(address)
         print(node_name)

         query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table=node_name)
         cur.execute(query)
         riveja, = cur.fetchone()

         query = """ UPDATE {table} SET all_time_blocks=0, all_time_signatures=0""".format(table=node_name) #RESET EVERY nodes all time blocks / signatures
         cur.execute(query)
         con.commit()



         query = """ SELECT blocks, daily_signatures FROM {table} WHERE id=1""".format(table=node_name)
         cur.execute(query)
         blocks, daily_signatures, = cur.fetchone()


         query = """ UPDATE {table} SET all_time_blocks=?, all_time_signatures=? WHERE id=1""".format(table=node_name)
         cur.execute(query,[blocks,daily_signatures])
         con.commit()



         for i in range(1, riveja):
             query = """ SELECT blocks, all_time_blocks, daily_signatures, all_time_signatures FROM {table} WHERE id=?""".format(table=node_name)
             cur.execute(query,[i])
             blocks, all_time_blocks, daily_signatures, all_time_signatures = cur.fetchone()


             new_all_time_blocks = blocks + all_time_blocks
             new_all_time_signatures = daily_signatures + all_time_signatures

             query = """ UPDATE {table} SET all_time_blocks=?, all_time_signatures=? WHERE id=?""".format(table=node_name)
             cur.execute(query,[new_all_time_blocks,new_all_time_signatures,i+1])
             con.commit()



def zero_all_blocks_and_signatures():
      con = sqlite3.connect('cellframe.db')
      cur = con.cursor()
      query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="all_node_names")
      cur.execute(query)
      row_id, = cur.fetchone()
      print("rows to go", row_id)

      for x in range(1, row_id + 1):
         print(x)
         query = """ SELECT node_name FROM all_node_names WHERE id=?""".format()
         cur.execute(query,[x])
         node_name, = cur.fetchone()
         #address=parse_node_address(address)
         print(node_name)

         query = """SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table=node_name)
         cur.execute(query)
         id, = cur.fetchone()

         query = """UPDATE {table} SET all_time_blocks=0, all_time_signatures=0,blocks=0,daily_signatures=0""".format(table=node_name) #ZERO EVERYTHING
         cur.execute(query)
         con.commit()



def nodes2():
      con = sqlite3.connect('cellframe.db')
      cur = con.cursor()
      query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="all_node_names")
      cur.execute(query)
      row_id, = cur.fetchone()
      print("rows to go", row_id)

      for x in range(1, row_id + 1):
         print(x)
         query = """ SELECT node_name FROM all_node_names WHERE id=?""".format()
         cur.execute(query,[x])
         node_name, = cur.fetchone()
         #address=parse_node_address(address)
         print(node_name)

         query = """ SELECT SUM(blocks) FROM (SELECT blocks FROM {table})""".format(table=node_name)   #""" ORDER BY id DESC LIMIT 7);""".format(table=node_address);
         cur.execute(query)
         vastaus1, = cur.fetchone()

         query = """ SELECT SUM(daily_signatures) FROM (SELECT daily_signatures FROM {table})""".format(table=node_name)   #""" ORDER BY id DESC LIMIT 7);""".format(table=node_address);
         cur.execute(query)
         vastaus2, = cur.fetchone()


         query = """SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table=node_name)
         cur.execute(query)
         id, = cur.fetchone()

         query = """UPDATE {table} SET all_time_blocks=? WHERE id=?""".format(table=node_name)
         cur.execute(query,[vastaus1,id])
         con.commit()

         query = """UPDATE {table} SET all_time_signatures=? WHERE id=?""".format(table=node_name)
         cur.execute(query,[vastaus2, id])
         con.commit()





         #resets everything to ZERO
#         query = """ UPDATE {table} SET blocks=0, all_time_blocks=0, daily_signatures=0, all_time_signatures=0""".format(table=node_name)
#         cur.execute(query)
#         con.commit()

#         query = """ ALTER TABLE {table} ADD COLUMN alias TEXT""".format(table=node_name)
#         cur.execute(query)
#         con.commit()

#         query = """ ALTER TABLE {table} ADD COLUMN tax REAL""".format(table=node_name)
#         cur.execute(query)
#         con.commit()



def remove_wallet_line():   #copies every validator to temporary database (except the one that has left) and then copy them back
     con = sqlite3.connect('wallet_database.db')

     line1 = """CREATE TABLE """
     line2 = """ (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, address TEXT, cell_balance REAL, mcell_balance REAL);"""


#     CREATE TABLE N5zfkp33JQA (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, address TEXT, cell_balance REAL, mcell_balance REAL);


     with con: #create new temp table
        cur = con.cursor()
        query ="SELECT id FROM all_table_names ORDER BY id DESC LIMIT 1"
        cur.execute(query)
        lines_to_go, = cur.fetchone()
        print("lines to go",lines_to_go)

        for i in range(1, lines_to_go+1):

            query = "SELECT wallet_name FROM all_table_names WHERE id=?"
            cur.execute(query,[i])
            wallet, = cur.fetchone()
            wallet1 = "N" + wallet + "_temp"
            wallet2 = "N" + wallet
            print(wallet)

            query = line1 + wallet1 + line2

            cur.execute(query) #create temp wallet table
            con.commit()

            line5 = "INSERT INTO "
            line6 = "(date, address, cell_balance, mcell_balance) SELECT date,address,cell_balance,mcell_balance FROM "
            line7 = " WHERE id=1"
            query = line5 + wallet1 + line6 + wallet2 + line7
            cur.execute(query) #copy from N45ddHOF into N45ddHOF_temp
            con.commit()
            line7 = " WHERE id=2"

            query = line5 + wallet1 + line6 + wallet2 + line7
            cur.execute(query) #copy from N45ddHOF into N45ddHOF_temp
            con.commit()
            line7 = " WHERE id=3"

            query = line5 + wallet1 + line6 + wallet2 + line7
            cur.execute(query) #copy from N45ddHOF into N45ddHOF_temp
            con.commit()





            query = "DROP TABLE " + wallet2 #DESTROY original wallet table
            cur.execute(query)
            con.commit()

            query = line1 + wallet2 + line2 #restore original wallet table structure
            cur.execute(query)
            con.commit()

            query = "INSERT INTO " + wallet2 + " SELECT * FROM " + wallet1
            cur.execute(query)
            con.commit()


            query = "DROP TABLE " + wallet1  #destroy temp table
            cur.execute(query)
            con.commit()


     return










def remove_node(pkey):   #copies every validator to temporary database (except the one that has left) and then copy them back
     con = sqlite3.connect('cellframe.db')

     with con: #create new temp table
        cur = con.cursor()

        sql_create_cellframe_data_table = """CREATE TABLE IF NOT EXISTS cellframe_data (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    address TEXT NOT NULL UNIQUE,
                                    ip TTEXT NOT NULL,
                                    port TEXT NOT NULL,
                                    pinner TEXT,
                                    pkey TEXT,
                                    staked_amount REAL,
                                    weight REAL,
                                    current_day data_type TEXT,
                                    week_counter data_type INTEGER,
                                    last_hash data_type TEXT,
                                    fresh data_type INTEGER,
                                    fire data_type INTEGER,
                                    latitude data_type REAL,
                                    longitude data_type REAL,
                                    node_active_status data_type INTEGER,
                                    country data_type TEXT,
                                    auto_update data_type INTEGER
                                    );"""

        sql_create_cellframe_temp_data_table = """CREATE TABLE IF NOT EXISTS cellframe_temp_data (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    address TEXT NOT NULL UNIQUE,
                                    ip TTEXT NOT NULL,
                                    port TEXT NOT NULL,
                                    pinner TEXT,
                                    pkey TEXT,
                                    staked_amount REAL,
                                    weight REAL,
                                    current_day data_type TEXT,
                                    week_counter data_type INTEGER,
                                    last_hash data_type TEXT,
                                    fresh data_type INTEGER,
                                    fire data_type INTEGER,
                                    latitude data_type REAL,
                                    longitude data_type REAL,
                                    node_active_status data_type INTEGER,
                                    country data_type TEXT,
                                    auto_update data_type INTEGER
                                    );"""

        sql_create_all_node_names = """ CREATE TABLE all_node_names (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        node_name TEXT
                                        );"""



        sql_create_all_node_temp_names = """ CREATE TABLE IF NOT EXISTS all_node_temp_names (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        node_name TEXT
                                        );"""




        cur.execute(sql_create_cellframe_temp_data_table)    #create TEMP tables
        con.commit()
        cur.execute(sql_create_all_node_temp_names)
        con.commit()

        query = """SELECT COUNT (*) FROM cellframe_data""" #how many rows in the nodes list we have
        cur.execute(query)
        lines_to_go_through, = cur.fetchone()
        con.commit()
#        print("gotta copy ",lines_to_go_through, "lines")

        query = """SELECT id, address FROM cellframe_data WHERE pkey=?""" #get the address and id of which we need to delete
        cur.execute(query,[pkey])
        id, address = cur.fetchone()
        con.commit()
        missing_node = parse_node_address(address) #change address format
        print("We need to remove ID",id,"with pkey",pkey,"and with table name",missing_node)
        input("Think before we continue...")

        for i in range(1, lines_to_go_through+1): #copy every row except the one that has gone MISSING
           if i != id:
             print(i)
             query = """INSERT INTO cellframe_temp_data (address,ip,port,pinner,pkey,staked_amount,weight,current_day,week_counter,last_hash,fresh,fire,latitude,longitude,node_active_status,country,auto_update)
                     SELECT address,ip,port,pinner,pkey,staked_amount,weight,current_day,week_counter,last_hash,fresh,fire,latitude,longitude,node_active_status,country,auto_update FROM cellframe_data WHERE id=?"""
             cur.execute(query,[i])
             con.commit()
           else:
             print("we will not copy",id)

        input("STOOOOP, we are about to DELETE")
        query = """DROP TABLE cellframe_data""" #delete original table
        cur.execute(query)
        con.commit()

        cur.execute(sql_create_cellframe_data_table) #create the original table structrure back
        con.commit()

        query = """INSERT INTO cellframe_data SELECT * FROM {table}""".format(table="cellframe_temp_data") #copy back the original table from temp
        cur.execute(query)
        con.commit()

        query = """DROP TABLE cellframe_temp_data""" #and finally delete temporary table
        cur.execute(query)
        con.commit()
        input("all copied and deleted")
        add_information("Deleted from cellframe_data",address)
        ################
        return  #We will return as we don't want to delete everything, right??????
        ################





        query = """SELECT COUNT (*) FROM all_node_names""" #how many rows in the node name list we have
        cur.execute(query)
        lines_to_go_through, = cur.fetchone()
        con.commit()

        query = """SELECT id FROM all_node_names WHERE node_name=?""" #get id of the one we are about to delete
        cur.execute(query,[missing_node])
        id, = cur.fetchone()
        con.commit()

        for i in range(1, lines_to_go_through+1): #copy every row except the one that has gone MISSING
           if i != id:
             print(i)
             query = """INSERT INTO all_node_temp_names (node_name)
                        SELECT node_name FROM all_node_names WHERE id=?"""
             cur.execute(query,[i])
             con.commit()
           else:
             print("we will not copy",id)

        query = """DROP TABLE all_node_names""" #delete original table
        cur.execute(query)
        con.commit()



        cur.execute(sql_create_all_node_names) #create the original table structrure back
        con.commit()

        query = """INSERT INTO all_node_names SELECT * FROM {table}""".format(table="all_node_temp_names") #copy back the original table from temp
        cur.execute(query)
        con.commit()


        query = """DROP TABLE all_node_temp_names""" #and finally delete temporary table
        cur.execute(query)
        con.commit()
        input("all copied and deleted") ########################
     return


def add_node_to_names_list(node):
     con = sqlite3.connect('cellframe.db')

     with con:
        cur = con.cursor()
        query = """ INSERT INTO {table} VALUES (null,?)""".format(table="all_node_names")
        cur.execute(query,[node])
        con.commit()
        print("Node",node,"addded to all_node_names list")
        return









def rearrange_non_validators(id):
     con = sqlite3.connect('cellframe.db')

     with con: #create new temp table
        cur = con.cursor()

        sql_create_temp_validator_nodes_table = """CREATE TABLE IF NOT EXISTS temp_validators(
                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                          node_address TEXT NOT NULL UNIQUE,
                                          ip TEXT NOT NULL,
                                          latitude REAL,
                                          longitude REAL,
                                          country TEXT
                                          );"""



        sql_create_non_validator_nodes_table = """CREATE TABLE IF NOT EXISTS non_validators(
                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                          node_address TEXT NOT NULL UNIQUE,
                                          ip TEXT NOT NULL,
                                          latitude REAL,
                                          longitude REAL,
                                          country TEXT
                                          );"""



        cur.execute(sql_create_temp_validator_nodes_table)
        con.commit()

        query = """SELECT COUNT (*) FROM non_validators""" #how many rows
        cur.execute(query)
        lines_to_go_through, = cur.fetchone()
        con.commit()
        print("gotta copy ",lines_to_go_through, "lines")

        for i in range(1, lines_to_go_through+1): #copy every row except the one that was duplicate
           if i != id:
            print(i)
            query = """INSERT INTO temp_validators (node_address,ip,latitude,longitude,country) SELECT node_address,ip,latitude,longitude,country FROM non_validators WHERE id=?"""
            cur.execute(query,[i])
            con.commit()

        query = """DROP TABLE non_validators""" #delete original table
        cur.execute(query)
        con.commit()

        cur.execute(sql_create_non_validator_nodes_table) #create the original table structrure back
        con.commit()


        query = """INSERT INTO non_validators SELECT * FROM {table}""".format(table="temp_validators") #copy back the original table from temp
        cur.execute(query)
        con.commit()


        query = """DROP TABLE temp_validators""" #and finally delete temporary table
        cur.execute(query)
        con.commit()


     return







def check_missing_node():   #checks if every node in the database are still active validators...if not...DELETE
    con=sqlite3.connect('cellframe.db')

    with con:

       cur = con.cursor()
       query = """ SELECT id FROM {table} ORDER by id DESC LIMIT 1""".format(table="cellframe_data"); #see how many nodes we have in our database
       cur.execute(query)
       amount, = cur.fetchone()

       command = fire_and_split_command("cellframe-node-cli srv_stake list keys -net ", "Backbone", True)    #spits out node keys list
       list_items = len(command)

       for i in range(amount):
             found=0
             id = i+1
             query = """ SELECT address,pkey FROM {table} WHERE id=?""".format(table="cellframe_data");
             cur.execute(query,[id])
             address,pkey = cur.fetchone() #grab address and pkey hash
             correct_address = parse_node_address(address)

             for x in range(list_items):
                 if "Pkey hash:" in command[x]: ## check through every list item to locate nodes Pkey

                     length = len(command[x])
                     pkey2=operator.getitem(command[x], slice(length-66, length)) #if found, copy last 66 letters

                     if pkey2 == pkey: #if correct pkey found, then do nothing and move to the next one
                        found=1
                        break

             if found == 0:
                print("We didn't find:",address)
                print("pKey",pkey)
                remove_node(pkey) #removes node from cellframe_data and all_node_names tables
                break

    return






def create_connection(db_file): #make connection to the database and return con object or none.
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)
    return con


def check_if_validator_table_exists(address):
    con=sqlite3.connect('cellframe.db')
    with con:
        cur = con.cursor()
        query= """SELECT name FROM sqlite_master WHERE type='table' AND name='{}'""".format(address)
        if not cur.execute(query).fetchone():
            return 0
        else:
            return 1




def test_json():
    session = requests_unixsocket.Session()
    r = session.get('http+unix://%2Fopt%2Fcellframe-node%2Fvar%2Frun%2Fnode_cli')
    #print(r.status_code)
    #print(r.text)
    #assert r.status_code == 200
    #print(r)
    input("")
    return
    command = """curl --unix-socket %2Fopt/cellframe-node/var/run/node_cli -X POST http://localhost/connect -d '{"method":"tx_history", "params":["tx_history;-tx;0x47CFAB34F27439E893D61EC70D9EBE0AFCA9757E87C034B4AB9C9F6ECED61CA8;-net;Backbone"], "id":"1"}'"""

    try:
        command_run = subprocess.run(command, check=True, stdout=subprocess.PIPE)
        if split:
            command_run = str(command_run.stdout, encoding="utf-8").splitlines()
        else:
            command_run = str(command_run.stdout, encoding="utf-8")
    except Exception as e:
        print(f"Didn't work, got error: {e}")
        exit(1)
    print(command_run)
    return
#curl --unix-socket /opt/cellframe-node/var/run/node_cli -X POST http://localhost/connect -d '{"method":"tx_history", "params":["tx_history;-all;-net;KelVPN"], "id":"1"}'
#    api_result = session.get('curl --unix-socket %2Fopt%2Fcellframe-node%2Fvar%2Frun%2Fnode_cli -X POST http:%2F%2Flocalhost%2Fconnect -d', params=payload)
#     api_result = requests.get('https://api.ip2location.io/', params=payload)


def check_if_fresh_was_non_validator(): #checks if fresh validator used to be in non validators list and delete it if found



     con = sqlite3.connect('cellframe.db')

     with con:
        cur = con.cursor()
        query = """ SELECT address FROM {table} WHERE fresh=1""".format(table="cellframe_data")
        cur.execute(query)
        con.commit()

        address, = cur.fetchone()

        cur = con.cursor() #try to find node with ID from non validators
        query = """ SELECT id FROM {table} WHERE node_address=?""".format(table="non_validators")
        cur.execute(query,[address])
        con.commit()

        if cur.fetchone() == None: # if no results, this ID is not duplicate
                 print("No duplicates found")
                 return


        cur = con.cursor() #if we got something, then let's get it again as it must be our duplicate
        query = """ SELECT id FROM {table} WHERE node_address=?""".format(table="non_validators")
        cur.execute(query,[address])
        con.commit()


        id, = cur.fetchone()
        print("ID:",id)
        print("is our duplicate")
        input("We found duplicate from row")

        if id != None:

                 rearrange_non_validators(id)

                 print("Deleted duplicate node ",address,"from non_validators table")
        else:
                 print("No duplicate nodes were found")

        return





def check_block_reward():
     kysely = "cellframe-node-cli block reward show -net "
     command = fire_and_split_command(kysely, "Backbone -chain main", True)
     br=command[0]
     block_reward=re.findall("\d+\.\d+",br)
     block_reward=float(block_reward[0])
     print("Block reward updated :",block_reward)

     con = sqlite3.connect('cellframe.db')

     with con:
        cur = con.cursor()
        query = """ UPDATE {table} SET block_reward=? WHERE id=0""".format(table="flags")
        cur.execute(query,[block_reward])
        con.commit()

     return



def create_table(con, create_table_sql): #create database table
    try:
        cur = con.cursor()
        cur.execute(create_table_sql)
    except Error as e:
        print(e)

def check_ip_location(ip): #checks latitude and longitude for the provided ip address and returns them as tuple
     print("Ip address to check :",ip)

     time.sleep(2) #need to wait 2 seconds before new API request
     payload = {'key': 'F0F989964427845B9ABB2C24868F9CDE', 'ip': ip, 'format': 'json'}
     api_result = requests.get('https://api.ip2location.io/', params=payload)
     location_data = api_result.json()

     print(type(location_data))
     print(location_data)
     latitude=location_data["latitude"]
     longitude=location_data["longitude"]
     country=location_data["country_name"]
     print(ip," is located at ",latitude,longitude,"in",country)

     data = latitude, longitude, country
     return data




def combine_tokens_to_wallets(lines): #combines tokens with corresponding wallets within database
    combined_data = {}
    token_pattern = re.compile(r"token_ticker:(\w+), balance:(\d+)")

    for nested_list in lines:
        for line in nested_list:
            if "null" in line:
                continue
            data = line.split()

            wallet_addr = data[3]

            tokens_and_balances = token_pattern.findall(line)

            for token, balance in tokens_and_balances:
                if not "CELL" in token:
                    continue
                balance = float(balance) / 1000000000000000000
                if wallet_addr in combined_data:
                    combined_data[wallet_addr][token] = "{:0.2f}".format(balance)
                else:
                    combined_data[wallet_addr] = {token: "{:0.2f}".format(balance)}

    return combined_data


def calculate_sums():
    con = sqlite3.connect('cellframe.db')
    with con:
        cur = con.cursor()
        query = """ SELECT SUM(mcell_balance) FROM {table}""".format(table="wallet_data_organized")
        cur.execute(query)
        mcell_total, = cur.fetchone()
        #print("mcell : ", mcell_total)

        query = """ SELECT SUM(cell_balance) FROM {table}""".format(table="wallet_data_organized")
        cur.execute(query)
        cell_total, = cur.fetchone()
        #print("cell : ", cell_total)

        query = """ UPDATE {table} SET mcell_total=?""".format(table="balances_total")
        cur.execute(query, [mcell_total])
        con.commit()

        query = """ UPDATE {table} SET cell_total=?""".format(table="balances_total")
        cur.execute(query, [cell_total])
        con.commit()

        return


def null_to_zero():  # fills empty balances with 0
    con = sqlite3.connect('cellframe.db')
    with con:
        cur = con.cursor()
        query = """ UPDATE {table} SET mcell_balance=0 WHERE mcell_balance=''""".format(table="wallet_data_organized")
        cur.execute(query)
        con.commit()
        query = """ UPDATE {table} SET cell_balance=0 WHERE cell_balance=''""".format(table="wallet_data_organized")
        cur.execute(query)
        con.commit()
        return

def move_wallets():  # moves wallets from 1st table to 2nd and puts mcell and cell balances to same line
    con = sqlite3.connect('cellframe.db')
    with con:
        cur = con.cursor()
        query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="wallet_data")
        cur.execute(query)
        lines, = cur.fetchone()  # read how many lines in wallet db is
        print(lines)

        for i in range(lines):

            id = i + 1  # get one wallet data
            query = """ SELECT identifier, token_ticker, balance FROM {table} WHERE id=?""".format(table="wallet_data")
            cur.execute(query, [id])
            wallet_address, ticker, balance = cur.fetchone()
#            print("wallet : ", wallet_address)
#            print("ticker : ", ticker)
#            print("balance :", balance)

            query = """ SELECT EXISTS(SELECT 1 FROM {table} WHERE wallet_address=?)""".format(
                table="wallet_data_organized")
            cur.execute(query, [wallet_address])
            tieto, = cur.fetchone()  # if 0, then there is no such wallet yet....let's create
 #           print("tulos:", tieto, type(tieto))
            #             input("stop")

            if tieto == 0:  # if destination doesn't have this wallet yet

                if ticker == "CELL":
                    query = """ INSERT INTO {table} VALUES (null,?,?,?)""".format(table="wallet_data_organized")
                    data = (wallet_address, balance, "")
                    cur.execute(query, data)
                    con.commit()
                    #                   input("just updated CELL")

                else:
                    query = """ INSERT INTO {table} VALUES (null,?,?,?)""".format(table="wallet_data_organized")
                    data = (wallet_address, "", balance)
                    cur.execute(query, data)
                    con.commit()
            #                  input("just updated mCELL")

            else:  # if destination already had this wallet
                # lets see which token we are about ot update
                if ticker == "mCELL":
                    query = """ UPDATE {table} SET mcell_balance=? WHERE wallet_address=?""".format(
                        table="wallet_data_organized")
                    cur.execute(query, [balance, wallet_address])
                    con.commit()
                #                  input("just updated ANOTHER balance")

                else:
                    query = """ UPDATE {table} SET cell_balance=? WHERE wallet_address=?""".format(
                        table="wallet_data_organized")
                    cur.execute(query, [balance, wallet_address])
                    con.commit()
    #                 input("just updated ANOTHER balance(CELL)")
    print("wallets have been processed...")
    return

def dump_wallets(): #dumps wallets from blockchain into database

    db_path = 'cellframe.db'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""DROP TABLE IF EXISTS wallet_data""") #delete temporary wallet table
    connection.commit()
#    input("deleted table")

    create_table_query = """ CREATE TABLE IF NOT EXISTS wallet_data (
                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                             identifier TEXT,
                             token_ticker TEXT,
                             balance REAL
                            )"""

    cursor.execute(create_table_query) #create new temporary wallet table
    connection.commit()
    connection.close()


    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    get_wallets = "cellframe-node-cli ledger list balance -net Backbone"
    get_wallets = get_wallets.split()
    list_wallets = subprocess.run(get_wallets, check=True, stdout=subprocess.PIPE)
    list_wallets = str(list_wallets.stdout, encoding="utf-8").strip().splitlines()
    data_list = [list_wallets]
    combined_data = combine_tokens_to_wallets(data_list)

    for identifier, token_data in combined_data.items():
        for token, balance in token_data.items():
            insert_query = "INSERT INTO wallet_data (identifier, token_ticker, balance) VALUES (?, ?, ?)"
            cursor.execute(insert_query, (identifier, token, balance))

    connection.commit()
    connection.close()
    move_wallets() #move wallets to another table and combine CELLs and mCELLs to same wallets
    null_to_zero() #insert 0 into every empty line
    calculate_sums() #calculates total sums of tokens and adds them to database
    print("wallets have been totally processed.")
    return


def update_ip_locations():
  input("HERE")
  con=sqlite3.connect('cellframe.db')
  with con:
       cur = con.cursor()
       query = """ SELECT id FROM {table} ORDER by id DESC LIMIT 1""".format(table="cellframe_data"); #see how many nodes we have in our database
       cur.execute(query)
       amount, = cur.fetchone()

       for id in range(1, amount+1): #go through every row

             query = """ SELECT latitude FROM {table} WHERE id=?""".format(table="cellframe_data");
             cur.execute(query,[id])
             latitude,=cur.fetchone()
             print("latitude from db",latitude,type(latitude))
  #           input("stop here")
             if latitude == None or latitude=="" or latitude==0.0:  #update data if there is already something
                   input("time to update then")

                   query = """ SELECT ip from {table} WHERE id=?""".format(table="cellframe_data");
                   cur.execute(query,[id])
                   ip, = cur.fetchone()
                   print("ip we have is :",ip,":")
                   if ip != " 0.0.0.0":
                       input("chekc")
                       latitude, longitude, country = check_ip_location(ip)
                       print("latitude we got ",latitude,"and longitude",longitude)
#                   input("odotas")
                   if ip == " 0.0.0.0":
                       print(" not this one")

                   if latitude != None:
                       query = """ UPDATE {table} SET latitude=? WHERE id=?""".format(table="cellframe_data");
                       cur.execute(query,[latitude,id])
                       con.commit()
                       query = """ UPDATE {table} SET longitude=? WHERE id=?""".format(table="cellframe_data");
                       cur.execute(query,[longitude,id])
                       con.commit()
                       query = """ UPDATE {table} SET country=? WHERE id=?""".format(table="cellframe_data");
                       cur.execute(query,[country,id])
                       con.commit()

 #                      input("updated database for locations data")

                   else:
                       print("no location data from that ip address. IP address must be incorrect")

             else:
               print("ID",id,"already has locations data...move to the next one")



       cur = con.cursor()
       query = """ SELECT id from {table} ORDER by id DESC LIMIT 1""".format(table="non_validators");
       cur.execute(query)
       amount, = cur.fetchone()
#       print("rows to go through in non_validators list:",amount)

       for i in range(1, amount+1): #go through every row in NON_VALIDATORS

             query = """ SELECT latitude FROM {table} WHERE id=?""".format(table="non_validators");
             cur.execute(query,[id])
             latitude,=cur.fetchone()
 #            print("latitude from non_validators db",latitude)
 #            print("latitude we got is :",latitude,"and it's type of :",type(latitude))

             if latitude == None or latitude == "":  #update data
  #                 print("time to update then")

                   query = """ SELECT ip from {table} WHERE id=?""".format(table="non_validators");
                   cur.execute(query,[id])
                   ip, = cur.fetchone()
                   print("ip we have is :",ip,":")
                   if ip != " 0.0.0.0":
                       print("get it")
                       latitude, longitude, country = check_ip_location(ip)
                   if ip == " 0.0.0.0":
                       print("We don't want to check 0.0.0.0")
   #                print("latitude we got ",latitude,"and longitude",longitude)

                   if latitude != None:
                       query = """ UPDATE {table} SET latitude=? WHERE id=?""".format(table="non_validators");
                       cur.execute(query,[latitude,id])
                       con.commit()
                       query = """ UPDATE {table} SET longitude=? WHERE id=?""".format(table="non_validators");
                       cur.execute(query,[longitude,id])
                       con.commit()
                       query = """ UPDATE {table} SET country=? WHERE id=?""".format(table="non_validators");
                       cur.execute(query,[country,id])
                       con.commit()

                   else:
                       print("no location data from that ip address. IP address must be incorrect")
             else:
               print("nope...")


  return






def listToString(s):      #function to convert list item input into text
 str1 = ""
 return (str1.join(s))


def convertTuple(tup):
    str = ''.join(tup)
    return str




def month_to_number(shortMonth): #change written month into number
    return {
       'Jan': 1,
       'Feb': 2,
       'Mar': 3,
       'Apr': 4,
       'May': 5,
       'Jun': 6,
       'Jul': 7,
       'Aug': 8,
       'Sep': 9,
       'Oct': 10,
       'Nov': 11,
       'Dec': 12,
   }[shortMonth]



def parse_node_address(address):   ## removes :: from node address and returns clean version of it
    node_address = address.replace("::","")
    additional = 'N'
    node_address = additional + node_address # Add 'N' in font of node address as Qlite doesn't like tables which name begins with number
#    print("here we got :",node_address)
    return node_address



def update_number_of_wallets_today(date):
    con = sqlite3.connect('cellframe.db')

    with con:
       cur = con.cursor()
       query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="wallet_data_organized")
       cur.execute(query)
       wallet_amount, = cur.fetchone()
       print("There are :", wallet_amount,"wallets today")
#       input("stop here")

       cur = con.cursor()
       query = """ INSERT INTO {table} VALUES (null,?,?)""".format(table="wallet_count")
#       print(query)
#       input("odota")
       cur.execute(query,[date,wallet_amount])
       con.commit()
       print("There are :",wallet_amount,"wallets now")

    return



def get_node_version(tx_hash):           #also get AUTO_UPDATE status
    print("TS HASH:",tx_hash)
    kysely = "cellframe-node-cli srv_stake check -tx "
    kysely = kysely + tx_hash
    kysely = kysely + " -net "

    command = fire_and_split_command(kysely, "Backbone", True)
#    print(command)
    if command == "Network": #if we got errors
       print("")
       print("Error: Command returned : ",command)
       input("We got error while trying to get node version")


    if command[0] == "Requested conditional transaction has no requires conditional output" or command[0] == "No response from node" or command[0] == "Node not found in base" or command[0] == "Can't connect to remote node":
       print("")
       print("error")
       print("")
       return 0,0
    node_version = operator.getitem(command[1], slice(len(command[1])-8,len(command[1])-1)) #get node version from command[1], get last 7 characters
    print(command)
    print("Node version",node_version,"<--")
#    input("stop and see node version")
    auto_update = 0

    tieto = operator.getitem(command[0], slice(0,9))
#    print("tieto=",tieto)

    if tieto == "No respon": #if we got no response from node
       auto_update=0
       return node_version, auto_update

    if tieto == "---------":  #if we got --------- that means we got some data after that line
       automaatti=operator.getitem(command[5], slice(len(command[5])-5,len(command[5])-1))
       print("Auto_update:",automaatti,"<---")
       if automaatti == "true":
            auto_update=1
       else:
            auto_update=0

#    input("Stop")
    return node_version, auto_update







def update_node_versions():
    con=sqlite3.connect('cellframe.db')
    with con:
       cur = con.cursor()
       query = """ SELECT id FROM {table} ORDER by id DESC LIMIT 1""".format(table="cellframe_data"); #see how many nodes we have in our database
       cur.execute(query)
       amount, = cur.fetchone() #how many nodes to go through the whole list?

       for i in range(amount):

             id = i+1
             query = """ SELECT address, auto_update FROM {table} WHERE id=?""".format(table="cellframe_data");
             cur.execute(query,[id])
             address, auto_update, = cur.fetchone()
#             print("Auto updater from database ",auto_update)
             correct_address = parse_node_address(address)
 #            print(correct_address)
             query = """ SELECT tx_hash,node_version FROM {table} WHERE id=1""".format(table=correct_address);
             cur.execute(query)
             tx_hash, node_version, = cur.fetchone()
             print("Auto updater from database ",auto_update,"for node ",correct_address)
             new_version, current_auto_update = get_node_version(tx_hash)
             print("Auto update from blockchain ",current_auto_update)

             if new_version == node_version:   #if new version is the same like old, do nothing
                print("Node version is still the same, do nothing")
             if new_version ==0:
                print("We received 0 for node version, do nothing")
             else:
               # print("not the same")   #otherwise let's see if new version is empty...indicating node inactive...then do nothing
                if new_version != "": #if it's not empty -> update
                   query = """ UPDATE {table} SET node_version=? WHERE id=1""".format(table=correct_address)
                   cur.execute(query, [new_version])
                   con.commit()

                else: #empty
                   print("Node probably offline as it returned :",new_version," for node version...do nothing")

             if auto_update != current_auto_update:
                   query = """ UPDATE {table} SET auto_update=? WHERE id=?""".format(table="cellframe_data")
                   cur.execute(query, [current_auto_update,id])
                   con.commit()
                   print("Auto updater status changed")


       print("Node versions and auto_online status updated")

    return



def mark_first_block_signed_date(data, *args): #not in use atm
         node_address, ts_created, port, pinner, pkey, staked_total, stake_weight = data
         con = sqlite3.connect('cellframe.db')
         cur = con.cursor()
         query = """INSERT INTO {table} VALUES (?,?,?,?,?,?,?,?,?,?,?)""".format(table=node_address);
         tieto=('','','','','','',ts_created,'','','','')
         cur.execute(query, tieto)
         con.commit()
         con.close()

def insert_fresh_node(node_address):   #resets fresh node flags
         con = sqlite3.connect('cellframe.db')
         cur = con.cursor()
         query = """ UPDATE cellframe_data SET fresh=? WHERE address=?""".format(table="cellframe_data")
         cur.execute(query,[1,node_address])
         con.commit()

def insert_fire_node(node_address):   #resets fresh node flags
         con = sqlite3.connect('cellframe.db')
         cur = con.cursor()
         query = """ UPDATE cellframe_data SET fire=? WHERE address=?""".format(table="cellframe_data")
         cur.execute(query,[1,node_address])
         con.commit()



def mark_node_active(node_address):   #marks node as active in cellframe_data
         con = sqlite3.connect('cellframe.db')
         cur = con.cursor()
         query = """ UPDATE cellframe_data SET node_active_status=? WHERE address=?""".format(table="cellframe_data")
         cur.execute(query,[0,node_address])
         con.commit()

def mark_node_inactive(node_address):   #marks node as inactive in cellframe_data
         con = sqlite3.connect('cellframe.db')
         cur = con.cursor()
         query = """ UPDATE cellframe_data SET node_active_status=? WHERE address=?""".format(table="cellframe_data")
         cur.execute(query,[1,node_address])
         con.commit()


def reset_fresh_node():   #resets fresh node flags
         con = sqlite3.connect('cellframe.db')
         cur = con.cursor()
         query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="cellframe_data")
         cur.execute(query)
         result = cur.fetchone()
         row_id2, = result
         row_id = int(row_id2)+1
         for x in range(row_id):
              query = """ UPDATE cellframe_data SET fresh=? WHERE id=?""".format()
              cur.execute(query,[0,x])
              con.commit()

def reset_fire_node():
         con = sqlite3.connect('cellframe.db')
         cur = con.cursor()
         query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table='cellframe_data')
         cur.execute(query)
         result = cur.fetchone()
         row_id2, = result
         row_id = int(row_id2)+1
         for x in range(row_id):
              query = """ UPDATE cellframe_data SET fire=? WHERE id=?""".format()
              cur.execute(query,[0,x])
              con.commit()



def add_last_hash(hash):
         con = sqlite3.connect('cellframe.db') #replace the last hash in database
         with con:
           cur = con.cursor()
           cur.execute((""" INSERT OR IGNORE INTO flags (id, last_hash) VALUES (?,?)"""),[0,hash])
           cur.execute((""" UPDATE flags SET last_hash=? WHERE id=0"""),[hash])
           con.commit()
           return


def increase_hash_line_counter():
    con = sqlite3.connect('cellframe.db')  # replace the last hash in database
    with con:
        cur = con.cursor()
        query = """ SELECT hash_line_counter FROM flags WHERE id=0"""
        cur.execute(query)
        hash_line_counter, = cur.fetchone()
        hash_line_counter += 1

        query = """ UPDATE flags SET hash_line_counter=? WHERE id=0"""
        cur.execute(query,[hash_line_counter])
        con.commit()
        return


def calculate_alltime_rewards(address):
     print("Calculating all time rewards for nodes",address)
#     address = parse_address(address)

     con=sqlite3.connect('cellframe.db')
     with con:
        x=1
        cur = con.cursor()
        query=""" SELECT id FROM {table} ORDER BY ID DESC LIMIT 1""".format(table=address)
        cur.execute(query)
        result, = cur.fetchone() #grab last id so we know how many lines we have to calculate
        print("we need to go through",result,"lines")
        input("ready to go?")

        cur = con.cursor()
        query=""" SELECT all_time_rewards FROM {table} WHERE id=?""".format(table=address)
        cur.execute(query,[x])
        all_time_rewards, = cur.fetchone()

        cur = con.cursor()
        query=""" SELECT daily_rewards FROM {table} WHERE id=?""".format(table=address)
        cur.execute(query,[x])
        daily_rewards, = cur.fetchone()

        print("daily_rewards",daily_rewards)
        print("all_time_rewards",all_time_rewards)
        new_all_time = daily_rewards + all_time_rewards
        print("new all time rewards :",new_all_time)

        cur = con.cursor()
        query=""" UPDATE {table} SET all_time_rewards=? WHERE id=?""".format(table=address)
        cur.execute(query,[new_all_time,x])
        con.commit()
        print("database updated @ id",x)
#        input("confirm?")

        for x in range(2, result):
              print("x",x)
#              input("We found the node")
              cur = con.cursor()
              query=""" SELECT all_time_rewards FROM {table} WHERE id=?""".format(table=address)
              cur.execute(query,[x-1])
              all_time_rewards, = cur.fetchone()

              cur = con.cursor()
              query=""" SELECT daily_rewards FROM {table} WHERE id=?""".format(table=address)
              cur.execute(query,[x])
              daily_rewards, = cur.fetchone()

              print("daily_rewards",daily_rewards)
              print("all_time_rewards",all_time_rewards)
              new_all_time = daily_rewards + all_time_rewards
              print("new all time rewards :",new_all_time)

              cur = con.cursor()
              query=""" UPDATE {table} SET all_time_rewards=? WHERE id=?""".format(table=address)
              cur.execute(query,[new_all_time,x])
              con.commit()
              print("database updated @ id",x)
 #       input("confirm?")



        cur = con.cursor()
        query=""" SELECT all_time_rewards FROM {table} WHERE id=?""".format(table=address)
        cur.execute(query,[result-1])
        all_time_rewards, = cur.fetchone()

        cur = con.cursor()
        query=""" SELECT daily_rewards FROM {table} WHERE id=?""".format(table=address)
        cur.execute(query,[result])
        daily_rewards, = cur.fetchone()

        print("daily_rewards",daily_rewards)
        print("all_time_rewards",all_time_rewards)
        new_all_time = daily_rewards + all_time_rewards
        print("new all time signatures :",new_all_time)

        cur = con.cursor()
        query=""" UPDATE {table} SET all_time_rewards=? WHERE id=?""".format(table=address)
        cur.execute(query,[new_all_time,result])
        con.commit()
        print("database updated @ id",result)
   #     input("confirm?")




def calculate_alltime_signatures(address):
     calculate_alltime_rewards(address)
     print("Calculating all time signatures for node",address)
#     address = parse_address(address)

     con=sqlite3.connect('cellframe.db')
     with con:
        x=1
        cur = con.cursor()
        query=""" SELECT id FROM {table} ORDER BY ID DESC LIMIT 1""".format(table=address)
        cur.execute(query)
        result, = cur.fetchone() #grab last id so we know how many lines we have to calculate
        print("we need to go through",result,"lines")
#        input("ready to go?")

        cur = con.cursor()
        query=""" SELECT all_time_signatures FROM {table} WHERE id=?""".format(table=address)
        cur.execute(query,[x])
        all_time_signatures, = cur.fetchone()

        cur = con.cursor()
        query=""" SELECT daily_signatures FROM {table} WHERE id=?""".format(table=address)
        cur.execute(query,[x])
        daily_signatures, = cur.fetchone()

        print("daily_signatures",daily_signatures)
        print("all_time_signatures",all_time_signatures)
        new_all_time = daily_signatures + all_time_signatures
        print("new all time signatures :",new_all_time)

        cur = con.cursor()
        query=""" UPDATE {table} SET all_time_signatures=? WHERE id=?""".format(table=address)
        cur.execute(query,[new_all_time,x])
        con.commit()
        print("database updated @ id",x)
 #       input("confirm?")
        for x in range(2, result):
              print("x",x)
#              input("We found the node")
              cur = con.cursor()
              query=""" SELECT all_time_signatures FROM {table} WHERE id=?""".format(table=address)
              cur.execute(query,[x-1])
              all_time_signatures, = cur.fetchone()

              cur = con.cursor()
              query=""" SELECT daily_signatures FROM {table} WHERE id=?""".format(table=address)
              cur.execute(query,[x])
              daily_signatures, = cur.fetchone()

              print("daily_signatures",daily_signatures)
              print("all_time_signatures",all_time_signatures)
              new_all_time = daily_signatures + all_time_signatures
              print("new all time signatures :",new_all_time)

              cur = con.cursor()
              query=""" UPDATE {table} SET all_time_signatures=? WHERE id=?""".format(table=address)
              cur.execute(query,[new_all_time,x])
              con.commit()
              print("database updated @ id",x)
  #            input("confirm?")


        cur = con.cursor()
        query=""" SELECT all_time_signatures FROM {table} WHERE id=?""".format(table=address)
        cur.execute(query,[result-1])
        all_time_signatures, = cur.fetchone()

        cur = con.cursor()
        query=""" SELECT daily_signatures FROM {table} WHERE id=?""".format(table=address)
        cur.execute(query,[result])
        daily_signatures, = cur.fetchone()

        print("daily_signatures",daily_signatures)
        print("all_time_signatures",all_time_signatures)
        new_all_time = daily_signatures + all_time_signatures
        print("new all time signatures :",new_all_time)

        cur = con.cursor()
        query=""" UPDATE {table} SET all_time_signatures=? WHERE id=?""".format(table=address)
        cur.execute(query,[new_all_time,result])
        con.commit()
        print("database updated @ id",result)
   #     input("confirm?")







def fire_and_split_command(command, txhash, split=True):  #run our command to dump nodes (c) @hyttmi
    command = command+txhash
    command = command.split()
    try:
        command_run = subprocess.run(command, check=True, stdout=subprocess.PIPE)
        if split:
            command_run = str(command_run.stdout, encoding="utf-8").splitlines()
        else:
            command_run = str(command_run.stdout, encoding="utf-8")
    except Exception as e:
        print(f"Didn't work, got error: {e}")
        exit(1)
    return command_run





def check_online_status(): #stops the program if cellframe-node-cli is OFFLINE

#Didn't work, got error: Command '['cellframe-node-cli', 'net', '-net', 'Backbone', 'get', 'status']' returned non-zero exit status 255.

     kysely = "cellframe-node-cli net -net "
     command = fire_and_split_command(kysely, "Backbone get status", True)

     print(command)
     status = operator.getitem(command[0], slice(0,7)) #if found, copy last 66 letters
     print("status:",status,"<--")

     if status != "Network":
        exit(1) #if we cannot see above line, exit program immediately with code 1

     return



def create_database():

  sql_create_cellframe_data_table = """CREATE TABLE IF NOT EXISTS cellframe_data (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    address TEXT NOT NULL UNIQUE,
                                    ip TTEXT NOT NULL,
                                    port TEXT NOT NULL,
                                    pinner TEXT,
                                    pkey TEXT,
                                    staked_amount REAL,
                                    weight REAL,
                                    current_day data_type TEXT,
                                    week_counter data_type INTEGER,
                                    last_hash data_type TEXT,
                                    fresh data_type INTEGER,
                                    fire data_type INTEGER,
                                    latitude data_type REAL,
                                    longitude data_type REAL,
                                    node_active_status data_type INTEGER,
                                    country data_type TEXT,
                                    auto_update data_type INTEGER
                                    );"""


  sql_create_cellframe_flags_table = """CREATE TABLE IF NOT EXISTS flags (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    last_hash data_type TEXT,
                                    current_day data_type TEXT,
                                    day_counter data_type INTEGER,
                                    month_counter data_type INTEGER,
                                    hash_line_counter data_type INTEGER,
                                    daily_transactions data_type INTEGER,
                                    block_reward data_type REAL
                                    );"""

  sql_create_non_validators = """CREATE TABLE non_validators(
                                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 node_address TEXT NOT NULL UNIQUE,
                                 ip TEXT NOT NULL,
                                 latitude REAL,
                                 longitude REAL,
                                 country TEXT
                                 );"""

  sql_create_wallet_data = """CREATE TABLE wallet_data (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              identifier TEXT,
                              token_ticker TEXT,
                              balance REAL
                              );"""
  sql_create_stakes_table = """CREATE TABLE stakes (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              date_created TEXT,
                              until_date TEXT,
                              wallet TEXT,
                              short_wallet TEXT,
                              value REAL,
                              block_hash TEXT
                              );"""


  sql_create_cellframe_transactions_table = """CREATE TABLE IF NOT EXISTS transactions (
                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                          date data_type TEXT,
                                          daily_transactions data_type INTEGER,
                                          cumulative_transactions data_type INTEGER,
                                          network_weight data_type REAL
                                          );"""

  sql_create_cellframe_wallet_count = """CREATE TABLE wallet_count (
                                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                                         date TEXT,
                                         wallets INTEGER
                                         );"""

  sql_create_cellframe_balances_total = """CREATE TABLE balances_total (
                                           cell_total REAL,
                                           mcell_total REAL
                                           );"""

  sql_create_wallet_data_organized = """CREATE TABLE wallet_data_organized (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        wallet_address TEXT,
                                        cell_balance REAL,
                                        mcell_balance REAL
                                        );"""


  sql_create_delegations = """CREATE TABLE delegations (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              date TEXT,
                              wallet TEXT,
                              short_wallet TEXT,
                              value REAL,
                              node TEXT
                              );"""

  sql_create_node_wallets = """CREATE TABLE node_wallets (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               date TEXT,
                               address TEXT,
                               wallet TEXT,
                               block_hash TEXT,
                               value REAL,
                               pkey TEXT
                               );"""


  sql_create_block_data = """CREATE TABLE block_data (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               date TEXT,
                               datums INTEGER
                               );"""


  sql_create_all_node_names = """ CREATE TABLE all_node_names (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               node_name TEXT
                               );"""


  sql_create_alerts = """ CREATE TABLE alerts (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               date TEXT,
                               type INTEGER,
                               text1 TEXT,
                               wallet1 TEXT,
                               wallet2 TEXT,
                               value REAL,
                               ticker TEXT,
                               text2 TEXT
                               );"""




  database = r"alerts.db"
  con = create_connection(database)

  cur = con.cursor()
#  cur.execute(sql_create_wallet_data_organized)
#  cur.execute(sql_create_cellframe_data_table)
#  cur.execute(sql_create_cellframe_flags_table)
#  cur.execute(sql_create_non_validators)
#  cur.execute(sql_create_wallet_data)
#  cur.execute(sql_create_cellframe_wallet_count)
#  cur.execute(sql_create_stakes_table )
#  cur.execute(sql_create_cellframe_balances_total)
#  cur.execute(sql_create_delegations)
#  cur.execute(sql_create_cellframe_transactions_table)
#  cur.execute(sql_create_node_wallets)
#  cur.execute(sql_create_block_data)
#  cur.execute(sql_create_all_node_names)
  cur.execute(sql_create_alerts)

  con.commit()
  con.close()
  return



def initial_checkup():
#########################################################
#                                                       #
# This function opens previously saved block hash and   #
# compares it with block dump of the same block hash.   #
# If there is difference, we will exit immediately.     #
# If all is ok, we can proceed with the rest of the     #
# program and return 1.                                 #
#                                                       #
#########################################################

    block_hash="0xABF1D49400ABDA167A75CA82B22DABE64E3F17F56D5C82C2A39B26747FF5BFE9"
    command = fire_and_split_command("cellframe-node-cli block -net Backbone -chain main dump ", block_hash, True)    #spits out contents of a block
#    file = open("checkup_file2.txt", "w")
    list_items=len(command)
                                             ######################################################
#    for x in range(list_items):             #                                                    #
#        line_to_write = command[x].strip()  # THESE LINES WERE USED TO CREATE chekcup_file1.txt  #
#        line_to_write = command[x].strip()  #                                                    #
#        line_to_write = command[x] + "\n"   ######################################################
#        file.write(line_to_write)
#    file.close()
#    input("stoP")

    file = open("checkup_file1.txt","r")

    with open(r"checkup_file1.txt", 'r') as fp: ##count lines in our file
           for count, line in enumerate(fp):
               pass
               count += 1

#    print("Lines",count,"list_items",list_items)
    for x in range(count):
      rivi = file.readline()
      rivi = rivi.rstrip()
      command[x] = command[x].rstrip()
#      print(rivi,"<<")
#      print(command[x],"<<")
#      input("")
      if command[x] != rivi:
         print("We have difference in block dump number 1. EXIT")
         file.close()
         exit(1)

    print("Initial testing with block hash 1 ok")
    file.close()

    block_hash2 = "0xE7464DC4DE81B2CCE045904E3E6266777EAE1ED658ABEAF11BBD21622F30F51B"
    command = fire_and_split_command("cellframe-node-cli block -net Backbone -chain main dump ", block_hash2, True)    #spits out contents of a block
#    file = open("checkup_file2.txt", "w")
    list_items=len(command)
    file = open("checkup_file2.txt","r")
    with open(r"checkup_file2.txt", 'r') as fp: ##count lines in our file
           for count, line in enumerate(fp):
               pass
               count += 1
#    print("Lines",count,"list_items",list_items)

    for x in range(count):
      rivi = file.readline()
      rivi = rivi.rstrip()
      command[x] = command[x].rstrip()
#      print(rivi,"<<")
#      print(command[x],"<<")
#      input("")
      if command[x] != rivi:
         print("We have difference in block dump number 2. EXIT")
         file.close()
         exit(1)

    print("Initial testing with block hash 1 ok")
    file.close()
    return(1)


