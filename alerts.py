
#import requests_unixsocket
from functions import *
import subprocess
import sqlite3
import operator
import requests
import time
import re
import json
from requests.auth import HTTPBasicAuth


def old_line():
    return 26240




def find_block_date(command):  # check inside signed block to find out which pkey was the 1st signer and at what date
    list_items = len(command)
    #      print(list_items)
    for x in range(list_items):

        if "ts_created:" in command[x]:  ## check through every list item to locate transaction created date
            length = len(command[x])
            ts_created = operator.getitem(command[x], slice(length - 26, length - 6))  # if found, copy last 24 letters
            print(command[x])
            ts_created = parse_date(ts_created)
#            check_day_counter(ts_created) #see if day has changed
            return(ts_created)




def alerts(command,block_hash):
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







    input("STOP NOW!")
    return








def check_delegations(block_hash): #check inside signed block to find out which pkey was the 1st signer and at what date
#      block_hash="0xABF1D49400ABDA167A75CA82B22DABE64E3F17F56D5C82C2A39B26747FF5BFE9" # delegation
#      block_hash="0xB9A3A4EAF853783F59C8FB91514737E596CF7E5589024E6FD82A13E2E9BDB15D" # stake
      print("Block hash :",block_hash,"******************")
#      block_hash="0xE8634A18749969D065F3D4F7A5BB9B40E1221F821BE6B5A5E16B65F8FABCB20B"
#      block_hash="0x1742C30031E2B4475FF3459CFFC0DC4E84898AC9F1E60F63333C1082CB0D6E57" # emission
#      block_hash="0xF7E7ABB22012EDAC79337D1C391E4908883ECB71C38639AB42D0D04C754DF897" # rewards
      block_hash="0x6F06A1B334B3A8500E2321A244D8CD69C9E8AE142D1663B48C192F9E70EC4651" #normal mCELL transaction
#      block_hash="0xB7468D3CD79AD8B5D22488C2AB0836B47077114060076D23A98CFBC096256863" #normal CELL transaction
      reward=0
      
      command = fire_and_split_command("cellframe-node-cli block -net Backbone -chain main dump ", block_hash, True)    #spits out contents of a block


      # Checks if block date is different and if yes, it will  go to update all week counts
      # and initializes new day for every node
      # Finally comes back here so we can continue checking rewards and signatures etc.
      ts_created = find_block_date(command)

#      alerts(command)
   
      print("parsed date", ts_created)
      list_items=len(command)
      alerts(command,ts_created)
      input("************************************************ stop")

      for x in range(list_items):
        if "_datums:"  in command[x]:
             length = len(command[x])
             datums = operator.getitem(command[x], slice(length-2,length))
             datums.strip()
             datums = int(datums)
             print("datums! :",datums)

             con = sqlite3.connect('cellframe.db')
             with con:
                     cur = con.cursor()

                     query = """ SELECT id FROM block_data ORDER BY id DESC LIMIT 1"""
                     cur.execute(query)
                     rivi, = cur.fetchone()

                     query = """ SELECT date FROM block_data WHERE id=?""" #check the date
                     cur.execute(query,[rivi])
                     old_date, = cur.fetchone()

                     if old_date == ts_created: #still same day
                            query = """ SELECT datums FROM block_data WHERE id=?""" #read old
                            cur.execute(query,[rivi])
                            old_datums, = cur.fetchone()
                            new_datums = old_datums + datums #sum it up

                            query = """UPDATE block_data SET datums=? WHERE id=?""" #and update
                            cur.execute(query,[new_datums,rivi])
                            con.commit() 


                     else:
                            query = """INSERT INTO block_data VALUES(null,?,?)""" #and update
                            cur.execute(query,[ts_created,datums])
                            con.commit()

 

        if "_IN_REWARD" in command[x]:
             print("We have reward")
             reward = 1


        if "_Address:" in command[x] and reward == 1:
                  length=len(command[x])
                  wallet = operator.getitem(command[x], slice(length-104,length)) #get receiving wallet

                  length = len(command[x+3])
                  transaction_pkey = operator.getitem(command[x+3], slice(len(command[x+3])-66,len(command[x+3])))
                  print("pkey",transaction_pkey)
                  print("address",wallet)
            #      input("stop")
                  con = sqlite3.connect('cellframe.db')
                  with con:
                     cur = con.cursor()
                     cur.execute("""SELECT address FROM node_wallets WHERE pkey=? AND wallet=?""",[transaction_pkey,wallet]) #MATCH wallet with NODE
                     node, = cur.fetchone()
                     node = parse_node_address(node)
                     print("NODE:",node,"on tassa!")
#                     input("oota")


                     ######## GET REWARD VALUE #######
                     take1 = command[x-1]
                     search_results = re.finditer(r'\(.*?\)', take1) #find the VALUE
                     for item in search_results:
                       item.group(0)
                     value = item.group(0).rstrip(')').lstrip('(')
                     value2 =int(value) / 1000000000000000000
                     print("address:",wallet," got reward of ",value2," CELL")
                     reward = 0

                     print("ts_created:",ts_created)
#                     print("today:",today,":")
             #        input("STOP write down rewards")
                     cur = con.cursor()
                     query = """SELECT daily_rewards FROM {table} WHERE date=?""".format(table=node)
                     cur.execute(query,[ts_created])
                     daily_rewards, = cur.fetchone()
                     print("daily rewards from database:",daily_rewards)
#                     input("mites meni?")
                     daily_rewards = daily_rewards + value2
                     onko=check_if_validator_table_exists(node)
                     print(onko)
                     if onko == 1:
                           query = """ UPDATE {table} SET daily_rewards=? WHERE date=?""".format(table=node)
                           cur.execute(query,[daily_rewards,ts_created])
                           con.commit()
      #                   input("mites meni?")


                  # STILL NEED TO MAKE CREATE TABLE FUNCTION
                  # PUT REWARDS INTO DATABASE IN HERE
                  #


        if "_DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE" in command[x]: ## check through every list item to see if there is delegation transaction
             length = len(command[x])
             print(command)
             take1 = command[x-1]
             print("*********************************************************************************")
             print("We have node stake transaction :",block_hash)
             print("*********************************************************************************")
#             input("get ready to take it")

             search_results = re.finditer(r'\(.*?\)', take1) #find the VALUE
             for item in search_results:
                item.group(0)
             value=item.group(0).rstrip(')').lstrip('(')
             value2 =int(value) / 1000000000000000000

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

#             input("FINAL STOP")
             con = sqlite3.connect('cellframe.db')
             with con:
                 cur = con.cursor()
                 query = "INSERT INTO delegations VALUES (null,?,?,?,?,?)"
                 cur.execute(query,[ts_created,wallet,short_wallet,value2,node])
                 con.commit()
                 print("Delegation inserted into database")




                 cur = con.cursor()
                 cur.execute("""SELECT pkey FROM node_wallets WHERE wallet=?""",[wallet])
                 tieto = cur.fetchone()
                 print("tieto",tieto)
                 print("pkey",pkey,":")
                 if tieto == None:
   #                 cur = con.cursor()
   #                 cur.execute("""SELECT pkey FROM node_wallets WHERE wallet=?""",[wallet])
   #                 tieto, = cur.fetchone()
   #                 print("tiet:",tieto,":")
   #                 if tieto != pkey:
                     cur = con.cursor()
                     query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?,?)""".format(table="node_wallets")
                     cur.execute(query,[ts_created,node,wallet,block_hash,value2,pkey])
                     con.commit()
                     input("Node wallet added into the database")

                 if tieto != None:
                       cur = con.cursor()
                       cur.execute("""SELECT address,pkey FROM node_wallets WHERE wallet=?""",[wallet])
                       osoite,tieto, = cur.fetchone()
                       print("TÄSÄ tiet",tieto,":",osoite,":",node,":")
                       input("no?")
                       if tieto != pkey and osoite != node:
                          input("no mitä vittua?")
                          cur = con.cursor()
                          query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?,?)""".format(table="node_wallets")
                          cur.execute(query,[ts_created,node,wallet,block_hash,value2,pkey])
                          con.commit()
                          input("Node added again in the database")

                       else:
                          print("pkey",tieto[0],":")
                          input("**** Same pkey already in the database ****")



        if "_DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_LOCK" in command[x]: # if we have stake transaction
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
                   if (ticker == "CELL" or ticker == "mCELL") and ticker_test != "mKEL" and value2 > 500:

                      print("")
                      print("********** S T A K E ****************")
                      print("We have CELL stake transaction",ts_created)
                      print(short_wallet,"staked",value2,"CELL until ",ending_date)
                      print("*************************************")
                      print("")

                      con = sqlite3.connect('cellframe.db')
                      with con:
                         cur = con.cursor()
                         query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?,?)""".format(table="stakes")
                         cur.execute(query,[ts_created,ending_date,wallet,short_wallet,value2,block_hash])
                         con.commit()
                         input("database updated")
                         break



        # GET EVERYONE WHO SIGNED THIS BLOCK AND DISTRIBUTE THEM TO DATABASE
        varmistus = command[x]
        varmistus = varmistus[-8:19] #need this as one blcok type had signatures instead of Signatures

        if "_signatures:" in command[x] and varmistus == "count": #SEE how many signers there was
#             print("varmistus",varmistus[-8:19])
 #            print(":",command[x],":")
 #            print(":",command[x+1],":")
             length = len(command[x])
             signatures = operator.getitem(command[x], slice(length-2,length))
             signatures.strip()
             print("signatures",signatures)
#             print("commandX",command[x])
             signatures = int(signatures)
             print("We have ",signatures,"signatures:",)
#             signatures +=1
             skip_line=1 
             rows=0

             for rows in range(signatures):

                     length = len(command[x+rows+skip_line]) #get every signers pkey hash
                     pkey_hash = operator.getitem(command[x+rows+skip_line], slice(length-67, length-1)) #...and copy the last 65 letter
                     print(rows,"pkey_hash:",pkey_hash,":...Go add_block_sign(pkey_hash,ts_created")
                     skip_line += 1
                     if rows == 0:
                          add_block_sign(pkey_hash,ts_created,1) #add 1st block signature to pkey_hash owner node
                     else:
                          add_block_sign(pkey_hash, ts_created,0)  #add the rest of the signatures to pkey_hash owner node
#             input("stop")


#      input("stop")
      return ts_created







#def parse_date(date): #change date format from 21 DEC 23 ---> 21.12.2023
#    print("original date",date)
#    length=len(date)
#    year = operator.getitem(date, slice(length-2,length))
#    year = "20"+year
#    print("year",year)

#    month = date[3:6]
#    print("month",month)
#    month=month_to_number(month)

#    day = date[:2]
#    final_date = day+'.'+str(month)+'.'+year
#    print("day:",day)
#    print("Final_date",final_date)
#    input("STOP")
#    return final_date



def parse_date(date):   #change date format from Nov 17 2023 ---> 17.11.2023
    length=len(date)
#    print("date is ",date)
    year = operator.getitem(date, slice(length-13,length-9))
#    print("year",year)
    month = date[3:6]
#    print("month",month)
    month=month_to_number(month)

    day = date[:2]
#    print("day",day)
    final_date = day+'.'+str(month)+'.'+year
#    print("final date:",final_date)
#    input("stop")
    
    return final_date





def parse_date2(date):   #change date format from Nov 17 2023 ---> 17.11.2023
    length=len(date)
#    print("date is ",date)
    year = operator.getitem(date, slice(length-13,length-9))
 #   print("year",year)
    month = date[3:6]
  #  print("month",month)
#    month=month_to_number(month)

    day = date[:2]
#    print("day",day)
    final_date = day+'.'+month+'.'+year
#    final_date = year+'.'+str(month)+'.'+day
 #   print("final date:",final_date)
  #  input("stop")
    return final_date


#    length=len(date)   #change date format from Nov 17 2023 ---> 17.11.2023
#    year = operator.getitem(date, slice(length-4,length))
#    month = date[4:7]
#    month=month_to_number(month)
#    day = date[8:10]
#    final_date = day+'.'+str(month)+'.'+year
#    return final_date






#########################################################
#                                                       #
#                  THIS IS THE MAIN                     #
#                                                       #
#########################################################
def main_hashing():
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

########## REMOVE THIS LATER
        old_hash_line = old_line()

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
          print("x = ",x," Total hash lines = ",count)
 ##         block_hash="0x281748C14060FFFC89D03ED2B1EDBBA2E06E2E87DB3A918E599EBD2BA45607FA"
          print("Now using:",block_hash," with length of:",len(block_hash))
          input("stop and confirm the block hash")
          if len(block_hash) != 66: #if our hash is somethign other than hash --> exit
             print("All hashing done!")
             return 0

          ts_created = check_delegations(block_hash)
          print("we came back from check_delegations")
  #        increase_daily_transactions()
          input("stop")
#          add_last_hash(block_hash)
 #         increase_hash_line_counter()
          input("SAFE TO QUIT")


        file.close()
        return 1




#create_database()


#rearrange_non_validators(27)
#check_online_status() #see if we are good to go
#check_missing_node()
main_hashing()

#update_non_validators_list()
#update_ip_locations()
#update_node_active_statuses_and_data()
#check_block_reward()
#check_if_fresh_was_non_validator()
#update_node_versions() #versions and AUTO_UPDATE status
#update_wallet_database()




