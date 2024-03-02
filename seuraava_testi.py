
from functions import *
import subprocess
import sqlite3
import operator
import requests
import time
import re
import json
from requests.auth import HTTPBasicAuth
import requests_unixsocket
from datetime import datetime

def old_line():
    return 0




def find_block_date(command):  # check inside signed block to find out which pkey was the 1st signer and at what date
    list_items = len(command)
    #      print(list_items)
    for x in range(list_items):

        if "ts_created:" in command[x]:  ## check through every list item to locate transaction created date
            length = len(command[x])
            ts_created = operator.getitem(command[x], slice(length - 26, length - 6))  # if found, copy last 24 letters
            print(command[x])
            ts_created = parse_date(ts_created)
            check_day_counter(ts_created) #see if day has changed
            return(ts_created)





def increase_daily_transactions():  # increases daily transactions by 1
    con = sqlite3.connect('cellframe.db')
    cur = con.cursor()
    with con:
        tabletoedit = "flags"
        query = """ SELECT id, daily_transactions FROM transactions ORDER BY id DESC LIMIT 1"""
        cur.execute(query)
        id, daily_transactions, = cur.fetchone()
        daily_transactions += 1

        query = """ UPDATE transactions SET daily_transactions=? WHERE ID=?"""
        cur.execute(query, [daily_transactions, id])
        con.commit()
        return


def check_day_counter(block_date):
    day_counter = 0
    print("We came to check_day_counter")
    con = sqlite3.connect('cellframe.db')
    cur = con.cursor()
    with con:

        tabletoedit = "flags"
        cur.execute(""" SELECT current_day FROM flags WHERE id=0""")
        result, = cur.fetchone()

        print("RESULT FROM CURRENT DAY:", result)
        input("Stop")
        if result == None:  # if there was nothing in the current day column, we will initialize these flags
            print("***** ERROR IN DAY COUNTER *******")
            return

        if result != block_date:  # ts_created: ### IF WE WENT TO ANOTHER DAY!!!!

            print("######################################")
            print("#                                    #")
            print("#          NEW DAY HAS COME          #")
            print("#                                    #")
            print("######################################")

            cur.execute(""" SELECT day_counter FROM flags WHERE id=0""")
            day_counter, = cur.fetchone()

            day_counter += 1

            cur.execute((""" UPDATE flags SET day_counter=? WHERE id=0"""), [day_counter])
            cur.execute((""" UPDATE flags SET current_day=? WHERE id=0"""), [block_date])

            con.commit()
            #######################################
            #                                     #
            # Time to check weekly counter status #
            #                                     #
            #######################################
            #           input("odota...")
            query = """ SELECT id FROM cellframe_data ORDER BY id DESC""".format()
            cur.execute(query)  # go through every validator to add up their weekly blocks
            line, = cur.fetchone()

            for x in range(1, line+1):  # UPDATE EVERY VALIDATORS WEEKLY COUNT
                query = """ SELECT address FROM cellframe_data WHERE id=?""".format()
                cur.execute(query, [line])
                address, = cur.fetchone()
                node_address = parse_node_address(address)

                #                    count 7 days blocks together here
                query = """ SELECT SUM(blocks)
                                 FROM (SELECT blocks FROM
                                 {table} ORDER BY id
                                 DESC LIMIT 7);""".format(table=node_address);

                cur.execute(query)
                vastaus, = cur.fetchone()

                query = """ UPDATE {table} SET week_count=? WHERE id=1""".format(table=node_address)
                cur.execute(query, [str(vastaus)])
                con.commit()

                query = """ SELECT SUM(blocks)
                             FROM (SELECT blocks FROM
                             {table} ORDER BY id
                              DESC LIMIT 30);""".format(table=node_address);

                cur.execute(query)
                vastaus3, = cur.fetchone()
                query = """ UPDATE {table} SET month_count=? WHERE id=1""".format(table=node_address);
                cur.execute(query, [str(vastaus3)])
                con.commit()

            # if day has changed, then we need to add all daily_transactions, cumulative transactions & update network weight
            cur = con.cursor()
            query = """ SELECT daily_transactions, cumulative_transactions, network_weight FROM transactions ORDER BY id DESC LIMIT 1"""
            cur.execute(query)
            daily_transactions, cumulative_transactions, network_weight = cur.fetchone()
            print(daily_transactions, cumulative_transactions, network_weight)
            cur = con.cursor()

            ######## ADD new date line to transactions with initial daily transaction 1
            query = """INSERT INTO {table} VALUES (NULL,?,?,?,?)""".format(table="transactions")

            cumulative_transactions = cumulative_transactions + daily_transactions

            cur.execute(query, [block_date, 1, cumulative_transactions, network_weight])
            con.commit()
            daily_tx_counter = 1
            ##### DO THE SAME FOR REWARDS

            initialize_new_day(block_date)
            return

        print("Still in the same day, do NOTHING with the day counter...")
        return


def initialize_new_day(date):
        print("We came to initialize new day")
        con = sqlite3.connect('cellframe.db')
        with con:
            cur = con.cursor()
            query = """ SELECT id FROM all_node_names ORDER BY id DESC""".format()  ##GET THE BIGGEST ROW ID (and see how many validators there is)
            cur.execute(query)
            rivi, = cur.fetchone()

            print("We have ", rivi," validators to go through")
            for x in range(1, rivi+1):  # GO THROUGH EVERY VALIDATOR
                query = """ SELECT node_name FROM all_node_names WHERE id=?""".format()  ##GET THE next validator
                cur.execute(query, [x])
                node_address, = cur.fetchone()

                query = """ SELECT blocks,all_time_blocks,stake_value,weight,daily_signatures,all_time_signatures,daily_rewards,all_time_rewards FROM {table} ORDER BY id DESC LIMIT 1""".format(table=node_address)
                # GET all time blocks, stake value and weight form validator table
                cur.execute(query)
                result = cur.fetchone()  # grab 1 line
                blocks, all_time_blocks, stake_value, weight, daily_signatures, all_time_signatures, daily_rewards, all_time_rewards = result
                all_time_blocks = all_time_blocks + blocks
                all_time_signatures = daily_signatures + all_time_signatures
                all_time_rewards = daily_rewards + all_time_rewards

                query = """INSERT INTO {table} (date,blocks,all_time_blocks,stake_value,weight,daily_signatures,all_time_signatures,daily_rewards,all_time_rewards) VALUES(?,?,?,?,?,?,?,?,?)""".format(table=node_address)
                cur.execute(query, [date, 0, all_time_blocks, stake_value, weight, 0, all_time_signatures, 0, all_time_rewards])
                con.commit()
                print("Just initialized new day for node : ", node_address, "row_id : ", x)  # we just copied old info to new line
#                input("wait")
        print("making sure this gets done")
        dump_wallets()
        return

#                update_node_active_statuses_and_data() #then get the latest stake value, weight and active status and update to each node


def check_delegations(block_hash): #check inside signed block to find out which pkey was the 1st signer and at what date
      print("Block hash :",block_hash,"******************")

#      block_hash="0xE8634A18749969D065F3D4F7A5BB9B40E1221F821BE6B5A5E16B65F8FABCB20B"
      reward=0
      command = fire_and_split_command("cellframe-node-cli block -net Backbone -chain main dump ", block_hash, True)    #spits out contents of a block


      # Checks if block date is different and if yes, it will  go to update all week counts
      # and initializes new day for every node
      # Finally comes back here so we can continue checking rewards and signatures etc.
      ts_created = find_block_date(command)


#      print("parsed date", ts_created)
      list_items=len(command)
#      input("stop")

      for x in range(list_items):
        if "datums:"  in command[x]:
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

 

        if "IN_REWARD" in command[x]:
             print("We have reward")
             reward = 1


        if "Address:" in command[x] and reward == 1:
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
                     node = cur.fetchone()

                     if node == None:  #if addres not found with pkey and wallet, then try with only pkey
                        cur = con.cursor()
                        cur.execute("""SELECT address FROM node_wallets WHERE pkey=?""",[transaction_pkey]) #MATCH pkey with NODE
                        node, = cur.fetchone()
                        node = parse_node_address(node)

                        cur.execute("""SELECT id,wallet FROM node_wallets WHERE pkey=?""",[transaction_pkey]) #MATCH pkey with NODE
                        iidd, wallet2, = cur.fetchone()
                        print(wallet2)
                        print(node)

                        if wallet != wallet2:
                            query = """UPDATE node_wallets SET wallet=? WHERE id=? and pkey=?"""
                            cur.execute(query,[wallet,iidd,transaction_pkey])
                            con.commit()
                            print("Node wallets updated")

                        input("stoP")

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


        if "DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE" in command[x]: ## check through every list item to see if there is delegation transaction
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
                       print("Here is the old information ",tieto,":",osoite,":",node,":")
                       input("So?")
                       if tieto != pkey and osoite != node:
                          input("Same wallet, different pkey and node address?")
                          cur = con.cursor()
                          query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?,?)""".format(table="node_wallets")
                          cur.execute(query,[ts_created,node,wallet,block_hash,value2,pkey])
                          con.commit()
                          input("Node added again in the database. Someone delegated into new node from same wallet.")

                       else:
                          print("pkey",tieto,":") #was tieto[0]
                          input("**** Same pkey already in the database ****")
                          break



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

        if "signatures:" in command[x] and varmistus == "count": #SEE how many signers there was
#             print("varmistus",varmistus[-8:19])
 #            print(":",command[x],":")
 #            print(":",command[x+1],":")
             length = len(command[x])
             signatures = operator.getitem(command[x], slice(length-2,length))
             signatures.strip()
 #            print("signatures",signatures)
#             print("commandX",command[x])
             signatures = int(signatures)
  #           print("We have ",signatures,"signatures:",)
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
      check_alerts(command,block_hash) #put some interesting data into alerts database
      return ts_created




def add_block_sign(pkey,ts_created,signer_number):

     if signer_number == 1:
         print("Add block sign (1ST SIGNER)")
     else:
         print("Adding the REST OF THE SIGNERS...")

     con = sqlite3.connect('cellframe.db')
     with con:

        cur = con.cursor()
        cur.execute(""" SELECT * FROM cellframe_data WHERE pkey=?""",[pkey])
        result = cur.fetchone() #grab 1 line from where we found the correct pkey hash. Then we can get the node address and other details
        print("result in ad_block_sign():",result)

        if result: # NODE IN DATABASE
              print("We found the node from database")
              cur = con.cursor()
              cur.execute(""" SELECT address FROM cellframe_data WHERE pkey=?""",[pkey])
              address, = cur.fetchone() #grab 1 line from where we found the correct pkey hash. Then we can get the node address and other details
              address = parse_node_address(address)
              print("Which node has that pkey?:",address,"<--")


              if (check_if_validator_table_exists(address)) == 0: #it should already be here if we came here
                 print("NO such node",address," was found")
                 return
              #ts_created=parse_date(ts_created)
 
#              print("date:",ts_created,":")

              #check if node table has this line....if not return and if yes, continue
              cur = con.cursor()
              query = """ SELECT daily_signatures FROM {table} WHERE date=?""".format(table=address)
              cur.execute(query,[ts_created])
              daily_signatures = cur.fetchone() #get the last row# form node table
              print("daily_signatures:",daily_signatures,"from database")
             # input("katos")
              if daily_signatures == None:
                 print("NONE...LETs CHECK WITH DIFFERENT DATE FORMAT") #not there but we can still check with different day format...9.11.2023 / 09.11.2023
                 pituus = len(ts_created)
#                 query = """ SELECT date FROM {table} WHERE id=51""".format(table=address)
#                 cur.execute(query)
#                 day = cur.fetchone() #get the last row# form node table
                 date2 = ts_created[-(pituus-1):] #REMOVE 1st zero
                 date2 = " "+date2 #add one whitespace in front of the date
                 print("ts_cr:",ts_created,"this is what we try to find")
                 print("date2:",date2,":")
                 print("ts_created length",len(ts_created))
                 print("date2 length",len(date2))
                 ts_created=date2
                 query = """ SELECT daily_signatures FROM {table} WHERE date=?""".format(table=address)
                 cur.execute(query,[date2])
                 daily_signatures = cur.fetchone() #get the last row# form node table
                 print("signatures",daily_signatures)
                 if daily_signatures == None:

                     print("ts_cr:",ts_created,":")
 #                    input("STILL NONE...I give up") #STIL NOT THERE...give up
                     return

                 if ts_created == date2:
                    print("dates are matching after conversion")
                    ts_created = date2
                    print("changed the date format for ts_created")

              if signer_number == 0: #this was normal signature
                  query = """ SELECT daily_signatures FROM {table} WHERE date=?""".format(table=address)
                  cur.execute(query, [ts_created])
                  daily_signatures = cur.fetchone()  # get the last row# form node table

                  if daily_signatures == None:
                      daily_signatures = 0

                  daily_signatures = daily_signatures[0]
                  daily_signatures += 1
                  print("new daily_signatures:", daily_signatures)
                  query = """ UPDATE {table} SET daily_signatures=? WHERE date=?""".format(
                      table=address)  # add one signature for today
                  cur.execute(query, [daily_signatures, ts_created])
                  con.commit()
                  print("added normal signature...")
                  return

              else: # this was 1st block signature
                      cur = con.cursor()
                      query = """ SELECT blocks,daily_signatures FROM {table} WHERE date=?""".format(table=address)
                      cur.execute(query,[ts_created])
                      blocks, daily_signatures, = cur.fetchone()
                      if blocks == None:
                         blocks = 0
                      if daily_signatures == None:
                         daily_signatures = 0

                      blocks += 1
                      daily_signatures += 1

                      print("new new blocks:", blocks)
                      cur = con.cursor()
                      query = """ UPDATE {table} SET blocks=?, daily_signatures=? WHERE date=?""".format(table=address) #add one signature for today
                      cur.execute(query,[blocks, daily_signatures, ts_created])
                      con.commit()
                      print("added 1st block signature...")



              print("UPDATED SIGNATURES for ",address)
              return

        if result == None:
              print("****************************************************************")
              print("Not in the database, let's see if it's active validator anyhow...")
              print("****************************************************************")

              command = fire_and_split_command("cellframe-node-cli srv_stake list keys -net ", "Backbone", True)    #spits out node keys list
              list_items=len(command)


              for x in range(list_items):
                 if "Pkey hash:" in command[x]: ## check through every list item to locate nodes Pkey
                     #print("Command : ",command[x])
                     length = len(command[x])
                     pkey2=operator.getitem(command[x], slice(length-66, length)) #if found, copy last 66 letters
                     print("add_sign() Pkey",pkey2)
                     if pkey2 == pkey: #if correct pkey found, then get the rest of the nodes info
                        print("WE ARE AT ADD_SIGNATURE ******************** This node is currently active. We will proceed to take it's info")
                        print("LOYTYS")

                        stake_value = float(operator.getitem(command[x+1], slice(14,len(command[x+1]))))
                        print("Stake_value:",stake_value,"<--")

                        node_weight = float(operator.getitem(command[x+2], slice(16, len(command[x+2])-1)))
                        print("Node weight:",node_weight,"<--")

                        node_address = operator.getitem(command[x+4], slice(12, len(command[x+4])))
                        print("Node address:",node_address,"<--")

                        active_status = operator.getitem(command[x+7], slice(9, len(command[x+7])))
                        print("Node active:",active_status,"<--")
#                        input("Stop")

                        tx_hash = operator.getitem(command[x+3], slice(10, len(command[x+3])))
                        print("TS HASH", tx_hash)

                        command2 = fire_and_split_command("cellframe-node-cli node dump -net Backbone -chain ", "main", True)    #spits out rest of node info
                        if command[0] == "No records":
#                            print("Command run for node dump returned :", command2)
                            return
                        list_items2=len(command2)
                        for x in range(list_items2):
                                 comparison = str(command2[x])
                                 comparison = comparison[:22]

                                 if node_address == comparison:     #when found the correct node
                                     node_information = command2[x]
                                     length3 = len(command2[x])
                                     node_information = node_information[26:length3-67]
                                     ip_address = ''.join(node_information.split())     #remove white spaces from front and back
                                     node_information = command2[x]
                                     length3 = len(command2[x])
                                     port = node_information[43:length-24]
                                     port = ''.join(port.split())  #remove white spaces from front and back
                                     node_information = command2[x]
                                     length3 = len(command2[x])
                                     pinner = node_information[51:length]
                                     pinner = ''.join(pinner.split())          #remove white spaces from front and back
                                     con = sqlite3.connect('cellframe.db')
                                     with con:
                                       #################################################################
                                       #                                                               #
                                       # We have active node info and will add it's info into database #
                                       #                                                               #
                                       #################################################################

                                        cur = con.cursor()
                                        query = """INSERT INTO {table} VALUES(null,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(table="cellframe_data")
                                        tieto = (node_address,ip_address,port,pinner,pkey,stake_value,node_weight,'','','',1,0,0,0,1,'',0) #new node begins with fresh flag
                                        input("Put node to database...@ add signatures")
                                        cur.execute(query, tieto)
                                        con.commit()
                                        correctaddress = parse_node_address(node_address) #remove :: from node address and add N in front as sqlite doesn't like tables that begins with number
                                        reset_fresh_node()
                                        insert_fresh_node(node_address)
                                        print("check if validator table is threre",check_if_validator_table_exists(correctaddress))
                                       ##############################################
                                       #                                            #
                                       #   Now we will also create nodes own table  #
                                       #                                            #
                                       ##############################################


                                        if check_if_validator_table_exists(correctaddress) == 1: #check if this was returning validator who's table we still have in our database

                                             print("We have the old table still in the database. Let's update some stuff into it (@ add signature)")
                                            
                                             query = """ UPDATE {table} SET tx_hash=? WHERE id=1""".format(table=correctaddress)
                                             cur.execute(query,[tx_hash])
                                             con.commit()

                                             query = """ SELECT id,date FROM {table} ORDER BY id DESC LIMIT 1""".format(table=correctaddress)
                                             cur.execute(query)
                                             id, old_date = cur.fetchone() #get the last line
                                             con.commit()

                                             if old_date != ts_created:
                                                    print("new day @ ADD_SIGNATURE")
                                                    query = """ SELECT blocks,all_time_blocks,daily_signatures,all_time_signatures FROM {table} WHERE id=?""".format(table=correctaddress) #get old data
                                                    cur.execute(query,[id])
                                                    con.commit()
                                                    blocks, all_time_blocks,daily_signatures,all_time_signatures = cur.fetchone()

                                                    if daily_signatures == None:
                                                       daily_signatures = 0
                                                    if all_time_signatures == None:
                                                       all_time_signatures = 0

                                                    print(blocks,"  ",all_time_blocks)
                                                    blocks = 0 #first block of the day

                                                    daily_signatures = 1
                                                    all_time_signatures += 1

######################### CHECK THIS LATER
 #                                                   query = """ SELECT week_count,month_count FROM {table} WHERE id=1""".format(table=correctaddress) #get old data
#                                                    cur.execute(query)
  #                                                  con.commit()
   #                                                 weekly,monthly, = cur.fetchone()
    #                                                weekly += 1
     #                                               monthly += 1

#                                                    query = """ UPDATE {table} SET week_count=?, month_count=? WHERE id=1""".format(table=correctaddress) #update stuff
 #                                                   cur.execute(query,[weekly,monthly])
 #                                                   con.commit()

                                                    query = """INSERT INTO {table} VALUES(null,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(table=correctaddress)

                                                    tieto=(ts_created,blocks,all_time_blocks,'',stake_value,node_weight,'','','','',daily_signatures,all_time_signatures,'','')
                                                    cur.execute(query, tieto)
                                                    con.commit()

                                                    return

                                             else: #still the same day


                                                    query = """ SELECT blocks,all_time_blocks,daily_signatures,all_time_signatures FROM {table} WHERE id=?""".format(table=correctaddress)
                                                    cur.execute(query,[id])
                                                    con.commit()
                                                    blocks, all_time_blocks, daily_signatures, all_time_signatures = cur.fetchone()
                                                    #print(blocks,"  ",all_time_blocks)
                                                    if signer_number == 1:
                                                        blocks += 1
                                                        daily_signatures += 1
                                                    else:
                                                        daily_signatures += 1

                                                    query = """ UPDATE {table} SET daily_signatures=?, all_time_signatures=? ,stake_value=?, weight=? WHERE id=?""".format(table=correctaddress)
                                                    cur.execute(query,[daily_signatures,all_time_signatures,stake_value,node_weight,id])
                                                    con.commit()

                                                    query = """ UPDATE {table} SET tx_hash=? WHERE id=1""".format(table=correctaddress)
                                                    cur.execute(query,[tx_hash])
                                                    con.commit()

                                                    #query = """ SELECT week_count,month_count FROM {table} WHERE id=1""".format(table=correctaddress) #get old data
                                                    #cur.execute(query)
                                                    #con.commit()
                                                    #weekly,monthly, = cur.fetchone()
                                                    #weekly += 1
                                                    #monthly += 1
                                                    #input("I dont think we come here")
                                                    #query = """ UPDATE {table} SET week_count=?, month_count=? WHERE id=1""".format(table=correctaddress) #update stuff
                                                    #cur.execute(query,[weekly,monthly])
                                                    #con.commit()
#                                                    data_list=[] #list(result) #convert tuple into list
#                                                    data_list.append(correctaddress) #replace our correct address in the list
#                                                    data_list.append(ts_created) #add the date to the list
#                                                    node_status=1
#                                                    data_list.append(node_status)
#                                                    result = tuple(data_list) #convert list back to tuple
                                                    return


                                        # TOTALLY  NEW  NODE
                                        else: #no, this is totally new
                                             print("Not found from database. TOTALLY NEW ... Initialize totally new table for this validator")

                                        input("stop....WE ARE ABOUT TO CREATE NODE PAGE ******************")
                                        query = """ CREATE TABLE IF NOT EXISTS {table} (
                                                 ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                 date data_type TEXT,
                                                 blocks data_type INTEGER,
                                                 all_time_blocks INTEGER,
                                                 first_block data_type TEXT,
                                                 stake_value data_type REAL,
                                                 weight data_type REAL,
                                                 week_count data_type INTEGER,
                                                 month_count data_type INTEGER,
                                                 tx_hash data_type TEXT,
                                                 node_version data_type TEXT,
                                                 daily_signatures data_type INTEGER,
                                                 all_time_signatures INTEGER,
                                                 daily_rewards REAL,
                                                 all_time_rewards REAL)""".format(table=correctaddress)
                                        cur.execute(query)
                                        cur = con.cursor()
                                        node_version, auto_update = get_node_version(tx_hash)
                                        print("Adding new node into database @ add_block_sign()")
                                        query = """INSERT INTO {table} VALUES(null,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(table=correctaddress)
                                        print("ts_created",ts_created,type(ts_created))
                                        print("stake_value",stake_value,type(stake_value))
                                        print("node_weight",node_weight,type(node_weight))
                                        print("tx_hash",tx_hash,type(tx_hash))
                                        print("node_version",node_version,type(node_version))
                                        input("All ok? Especially ts_created?")

                                        if signer_number == 1:     # 1st signer
                                            blocks = 1
                                            signatures = 1
                                        else:
                                            signatures = 1        # normal signer
                                            blocks = 0

                                        tieto=(ts_created,blocks,0,ts_created,stake_value,node_weight,0,0,tx_hash,node_version,signatures,0,0,0) #new node begins with 1 signature 0 rewards
                                        cur.execute(query,tieto)
                                        con.commit()
                                        input("Node added in add_sign() onko ok?...next we will see if we have it's name in all_node_name_list")
                                        if check_if_name_in_all_nodes_list(correctaddress) == 0: #if node not in list
                                             add_node_to_names_list(correctaddress)

#                                             cur = con.cursor() # ADD THIS NEW NODE TO NODE NAMES LIST ALSO
#                                             query = """INSERT INTO {table} VALUES (null,?)""".format(table="all_node_names")
#                                             cur.execute(query,[correctaddress])
#                                             con.commit()
                                             print("This node also added into all_node_names list")
                                             input("care to check?")
                                        else:
                                             print("This node already had it's name in all nodes list")
                                             input("Care to check?")
                                        return


                     else:
                        print("...add_sign()")

        print("Not in database and not active validator")
        ####################################################################################
        #                                                                                  #
        # We can sometimes come here if validator has signed blocks but then went offline  #
        # and we still need to distribute their rewards even though table removed from     #
        # active validators list.                                                          #
        #                                                                                  #
        ####################################################################################
        con = sqlite3.connect('cellframe.db')
        with con:

           cur = con.cursor()
           cur.execute(""" SELECT address FROM node_wallets WHERE pkey=?""",[pkey])
           result = cur.fetchone() #grab 1 line from where we found the correct pkey hash. Then we can get the node address and other details
           if result == None:
              print("OUT OF LUCK")
              return

           else:

              cur = con.cursor()
              cur.execute(""" SELECT address FROM node_wallets WHERE pkey=?""",[pkey])
              address, = cur.fetchone() #grab 1 line from where we found the correct pkey hash. Then we can get the node address and other details
              address = parse_node_address(address)

              if check_if_validator_table_exists(address) == 1: #check if this was node still has it's table but has disappeared from list_keys and cellframe_data
                  print("We found the correct table ",address)
                  print("HERE SPRINKLE THOSE SIGNATURES")

                  #check if node table has this line....if not return and if yes, continue
                  query = """ SELECT daily_signatures FROM {table} WHERE date=?""".format(table=address)
                  cur.execute(query,[ts_created])
                  daily_signatures = cur.fetchone() #get the last row# form node table
                  print("daily_signatures:",daily_signatures,"from database")
                 # input("katos")
                  if daily_signatures == None:
                     print("NONE...LETs CHECK WITH DIFFERENT DATE FORMAT") #not there but we can still check with different day format...9.11.2023 / 09.11.2023
                     pituus = len(ts_created)
#                 query = """ SELECT date FROM {table} WHERE id=51""".format(table=address)
#                 cur.execute(query)
#                 day = cur.fetchone() #get the last row# form node table
                     date2 = ts_created[-(pituus-1):] #REMOVE 1st zero
                     date2 = " "+date2 #add one whitespace in front of the date
                     print("ts_cr:",ts_created,"this is what we try to find")
                     print("date2:",date2,":")
                     print("ts_created length",len(ts_created))
                     print("date2 length",len(date2))
                     ts_created=date2
                     query = """ SELECT daily_signatures FROM {table} WHERE date=?""".format(table=address)
                     cur.execute(query,[date2])
                     daily_signatures = cur.fetchone() #get the last row# form node table
                     print("signatures",daily_signatures)
                     if daily_signatures == None:

                         print("ts_cr:",ts_created,":")
 #                    input("STILL NONE...I give up") #STIL NOT THERE...give up
                         return

                     if ts_created == date2:
                        print("dates are matching after conversion")
                        ts_created = date2
                        print("changed the date format for ts_created")

                  if signer_number == 0: #this was normal signature
                      query = """ SELECT daily_signatures FROM {table} WHERE date=?""".format(table=address)
                      cur.execute(query, [ts_created])
                      daily_signatures = cur.fetchone()  # get the last row# form node table

                      if daily_signatures == None:
                          daily_signatures = 0

                      daily_signatures = daily_signatures[0]
                      daily_signatures += 1
                      print("new daily_signatures:", daily_signatures)
                      query = """ UPDATE {table} SET daily_signatures=? WHERE date=?""".format(
                          table=address)  # add one signature for today
                      cur.execute(query, [daily_signatures, ts_created])
                      con.commit()
                      print("added normal signature...")
#                      con.close()
                      return
                  else: # this was 1st block signature
                          query = """ SELECT blocks,daily_signatures FROM {table} WHERE date=?""".format(table=address)
                          cur.execute(query,[ts_created])
                          blocks, daily_signatures, = cur.fetchone()
                          if blocks == None:
                             blocks = 0
                          if daily_signatures == None:
                             daily_signatures = 0

                          blocks += 1
                          daily_signatures += 1

                          print("new new blocks:", blocks)
                          query = """ UPDATE {table} SET blocks=?, daily_signatures=? WHERE date=?""".format(table=address) #add one signature for today
                          cur.execute(query,[blocks, daily_signatures, ts_created])
                          con.commit()
                          print("added 1st block signature...")

                  print("UPDATED SIGNATURES for ",address)
#                  con.close()
                  return

              else:
                  print("No, this one is a TOTAL mystery signer : ",pkey)
#                  con.close()


     return














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




def get_node_version2(tx_hash):           #also get AUTO_UPDATE status (MAYBE CAN DELETE)
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





def update_node_active_statuses_and_data():

    con=sqlite3.connect('cellframe.db')
    with con:
       cur = con.cursor()
       query = """ SELECT id FROM {table} ORDER by id DESC LIMIT 1""".format(table="cellframe_data") #see how many nodes we have in our database
       cur.execute(query)
       amount, = cur.fetchone()

       command = fire_and_split_command("cellframe-node-cli srv_stake list keys -net ", "Backbone", True)    #spits out node keys list
       list_items = len(command)
       print("This is from Update node active statuses and data")
  #     print("List items :",command)
  #     input("Stop here and look what you see before we continue")
       for i in range(amount):

             id = i+1
             query = """ SELECT address,pkey FROM {table} WHERE id=?""".format(table="cellframe_data")
             cur.execute(query,[id])
             address,pkey = cur.fetchone() #grab address and pkey hash

             correct_address = parse_node_address(address)

             for x in range(list_items):
                 if "Pkey hash:" in command[x]: ## check through every list item to locate nodes Pkey

                     length = len(command[x])
                     pkey2=operator.getitem(command[x], slice(length-66, length)) #if found, copy last 66 letters
 
                     if pkey2 == pkey: #if correct pkey found, then get the rest of the nodes info
#                        print(command)
                        stake_value = float(operator.getitem(command[x+1], slice(14,len(command[x+1]))))
                        node_weight = float(operator.getitem(command[x+2], slice(16, len(command[x+2])-1)))
                        tx_hash = operator.getitem(command[x+3], slice(10, len(command[x+3])))
                        node_address = operator.getitem(command[x+4], slice(12, len(command[x+4])))
                        active_status = operator.getitem(command[x+7], slice(9, len(command[x+7])))
                        print("pkey:",pkey)
                        print("stake_value",stake_value)
                        print("node_weight",node_weight)
                        print("tx_hash",tx_hash)
                        print("node_address:",node_address)
                        print("active_status:",active_status)
 #                       input("katos")
                        if active_status != "true":
                              status = 1
                              print("This node is NOT active")
                        else:
                              status = 0 #node is active
                              print("This node is active")

                        correct_address = parse_node_address(node_address) #get correct node address
                        query = """ UPDATE {table} SET staked_amount=?, weight=?, node_active_status=? WHERE address=?""".format(table="cellframe_data")
                        cur.execute(query,[stake_value,node_weight,status,node_address])
                        con.commit()

                        correct_address = parse_node_address(node_address) #update tx_hash also
                        query = """ UPDATE {table} SET tx_hash=? WHERE id=1""".format(table=correct_address)
                        cur.execute(query,[tx_hash])
                        con.commit()



                        query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table=correct_address)
                        cur.execute(query)
                        dd, = cur.fetchone() #get the last row# form node table

                        query = """ UPDATE {table} SET stake_value=?, weight=? WHERE id=?""".format(table=correct_address)
                        cur.execute(query,[stake_value,node_weight,dd])
                        con.commit()



       network_weight = command[list_items-2]
       network_weight = network_weight[14:].rsplit()
       print("Network weight :", network_weight[0])
       input("**************** CHECK THIS *************************")

       con = sqlite3.connect('cellframe.db')
       with con:
                 cur = con.cursor()
                 query = """SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="transactions")
                 cur.execute(query)
                 last_line, = cur.fetchone()

                 query = """UPDATE {table} SET network_weight=? WHERE id=?""".format(table="transactions")
                 cur.execute(query, [network_weight[0],last_line])
                 con.commit()

       print("Updated node statuses and  weight + stake value...+ Network total weight")
       return




def update_non_validators_list():

      command = fire_and_split_command("cellframe-node-cli node dump -net Backbone -chain ", "main", True) #get the node dump to see all nodes

      lista = len(command)
      con = sqlite3.connect('cellframe.db')
      cur = con.cursor()
      with con:

          for x in range(3,lista-2): #start from 3rd line and finish 2 lines before end

             if command[0] == "No records":
                print("Command run for node dump returned :", command)
#                input("stop here")
                return 0
 #            print(command[x])
             first_line = command[x]
             node_address=first_line[:22]
             ip = first_line[25:41]
             ip.lstrip()
             print("Node ip:",ip,end="")
#             print(len(ip))
             print("  **  Node address :",node_address, end="")

             #check if node is in validators list already
             query = """ SELECT EXISTS(SELECT 1 FROM cellframe_data WHERE address=?)""".format(table="cellframe_data")
             cur.execute(query,[node_address])
             tieto, = cur.fetchone()    # returns 0 if node is not validator and 1 if it is validator

             if tieto == 0:
                 print("  **  Node was not on cellframe validators list")
             else:
                 print("  **  is active validator")

             if tieto != 1: ## not in validator list, how about non_validators list?

                  query = """ SELECT EXISTS(SELECT 1 FROM non_validators WHERE node_address=?)""".format()
                  cur.execute(query,[node_address])
                  tieto2, = cur.fetchone()
                  
                  if tieto2 != 1: ## also not in non_validators list...let's proceed to update database
                      print("****************************************************************************************************")
                      print("* Didn't find this node from cellframe_data nor non_validators list. Proceed to database it's info  *")
                      print("****************************************************************************************************")
                      query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?)""".format(table='non_validators')
                      cur.execute(query,[node_address,ip,'','',''])
                      con.commit()

                      #let's throw this info into alerts
#                      con = sqlite3.connect('alerts.db')
 #                     with con:
  #                         cur = con.cursor()
   #                        query = "INSERT INTO alerts VALUES (null,?,?,?,?,?,?,?,?,?)"
    #                       cur.execute(query,["",40,"appeared into the non-validators list","","Node","","",node_address,""])
     #                      con.commit()
      #                     print("Alert inserted into database (node added into non-validators list)")
#



                      input("Updated database")





     #        else:
                  #nothing


      return







############################################## we come here from add_signature_for_node
def steal_node_info(nodeaddress):
              nodeaddress,ts_done = nodeaddress
              print("Stealing node information from cli (steal_node_info) We will do LIST KEYS")
              command = fire_and_split_command("cellframe-node-cli srv_stake list keys -net ","Backbone", True)
              list_items=len(command)
#              print("List items :",command)
              real_node_address = nodeaddress[1:17]
              real_node_address = real_node_address[:4] + '::' + real_node_address[4:16]
              real_node_address = real_node_address[:10] + '::' + real_node_address[10:14]         #convert node address back to original form with all those ::'s
              real_node_address = real_node_address[:18] + '::' + nodeaddress[13:17]
              real_node_address.lstrip()
              print("We converted node address back to original form which is:",real_node_address,"<--")

              for x in range(list_items):
                 if "Node addr:" in command[x]: ## check through every list item to locate nodes node address
                     print("Command : ",command[x])
                     length = len(command[x])
                     node_address=operator.getitem(command[x], slice(length-22, length)) #if found, copy last 22 letters


                     print("Node address =",node_address,":")

                     if real_node_address == node_address: #if correct node address has been found, get the rest of node info

                        print("This is our correct address")
                        stake_value = float(operator.getitem(command[x-3], slice(14,len(command[x-3]))))
                        node_weight = float(operator.getitem(command[x-2], slice(16, len(command[x-2])-1)))
                        node_address = operator.getitem(command[x+4], slice(12, len(command[x+4])))
#                        active_status = operator.getitem(command[x+5], slice(9, len(command[x+5])))

                        #print("This node is currently active. We will proceed to take it's info")
                  #      print("LOYTYS")
#                        input("Press Enter to continue...")
 #                       stake_value = str(command[x-3])  #grab the nodes stake value
 #                       stake_value = float(stake_value[14:])
                        print("Stake value = ",stake_value)
  #                      node_weight = str(command[x-2])
   #                     node_weight = node_weight[17:]
    #                    node_weight = node_weight[0:-1] #remove the last % form weight
     #                   node_weight = float(node_weight)         #convert to REAL
                        print("Node weight:",node_weight)
      #                  node_address = str(command[x+4])
#                        data = node_address,stake_value,node_weight
                        data = stake_value, node_weight
                        return data
                 else:
                   print(command[x])
                   if "Active:" in command[x]:
                        print(command[x])
                        length2 = len(command[x])

                        node_active_status = operator.getitem(command[x], slice(length2-5,length2))
                        print("Node active status from steal node info:",node_active_status)
                        if node_active_status == "true":
                            #mark node as active
                            mark_node_active(real_node_address)
                        else:
                            mark_node_inactive(real_node_address)
                            #mark node as inactive




def re_read_signatures(block_hash): #check inside signed block to find out which pkey was the 1st signer and at what date

      command = fire_and_split_command("cellframe-node-cli block -net Backbone -chain main dump ", block_hash, True)    #spits out contents of a block
      list_items=len(command)

      for x in range(list_items): #read every item in the block


        if "ts_created:" in command[x]:  ## check through every list item to locate transaction created date
            length = len(command[x])
            ts_created = operator.getitem(command[x], slice(length - 26, length - 6))  # if found, copy last 24 letters
            print(command[x])
            ts_created = parse_date(ts_created)
#            print("ts_created",ts_created)
#            input("")
#            break #we only want the 1st one

        varmistus = command[x]
        varmistus = varmistus[-8:19] #need this as one blcok type had signatures instead of Signatures

        if "signatures:" in command[x] and varmistus == "count": #SEE how many signers there was
             length = len(command[x])
             signatures = operator.getitem(command[x], slice(length-2,length))
             signatures.strip()
             signatures = int(signatures)
             skip_line=1
             rows=0
 #            print("we have",signatures," signatures")
 #            input("")
             for rows in range(signatures):

                     length = len(command[x+rows+skip_line]) #get every signers pkey hash
                     pkey_hash = operator.getitem(command[x+rows+skip_line], slice(length-67, length-1)) #...and copy the last 65 letter
#                     print(rows,"pkey_hash:",pkey_hash,":...Go add_block_sign(pkey_hash,ts_created")
                     skip_line += 1
                     if rows == 0:
                          print("Block date",ts_created)
                          add_block_sign(pkey_hash,ts_created,1) #add 1st block signature to pkey_hash owner node
                     else:

                          add_block_sign(pkey_hash, ts_created,0)  #add the rest of the signatures to pkey_hash owner node

      return






def go_through_every_block():
        database = r"cellframe.db"

        # create a database connection
        con = create_connection(database)

#        global daily_tx_counter
#        daily_tx_counter=0

        input("Ready to speed run though every block?...")
        file = open("all_blocks.txt","r")

        with open(r"all_blocks.txt", 'r') as fp: ##count lines in our file
           for count, line in enumerate(fp):
               pass
               count += 1

        print("Blocks to read",count)


        old_hash_line = old_line()
        lines_to_go = count-old_hash_line
        if lines_to_go < 2:
            return

        print("But we are going to read ",lines_to_go,"blocks")
        input("Launch?")

        if old_hash_line != 0:
            for y in range(old_hash_line):
              temp = file.readline() #lets read lines until we reach position where last time we ended

        for x in range(count):
          block_hash = file.readline()
          block_hash = block_hash[1:67]

          result = re.match("^[A-Za-z0-9]{66}$", block_hash) #check if we have real hash
          if result == None:
              print("All hashing done!")
              file.close()
              return 0

          print("Current blockx = ",x," / ",count)
          print("Now using:",block_hash," with length of:",len(block_hash))
          if len(block_hash) != 66: #if our hash is somethign other than hash --> exit
             print("All hashing done!")
             return 0

          re_read_signatures(block_hash)
        input("safe to quit")
        file.close()
        return 1



def show_our_blocks():
#
# Calculates all time blocks (1st signatures)
# Verify with  cellframe-node-cli block list -net Backbone -chain main -cert <certificate name>
#
      con = sqlite3.connect('cellframe.db')
      cur = con.cursor()

      query = """ SELECT SUM(blocks) FROM (SELECT blocks FROM {table})""".format(table="N5C72D63B6AE5618E")
      cur.execute(query)
      vastaus1, = cur.fetchone()
      print("Timos blocks counted",vastaus1)

      query = """ SELECT SUM(blocks) FROM (SELECT blocks FROM {table})""".format(table="N223ED4C1A3AC1172")
      cur.execute(query)
      vastaus1, = cur.fetchone()
      print("Mikas blocks counted",vastaus1)
      return










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
  #      old_hash_line = old_line()

        lines_to_go = count-old_hash_line
        if lines_to_go < 2:
            return

        print("We have ",lines_to_go,"new hashes")
        input("Should we go or stop?")

        if old_hash_line != 0:
            for y in range(old_hash_line):
              temp = file.readline() #lets read lines until we reach position where last time we ended


        for x in range(count):
          block_hash = file.readline()
          block_hash = block_hash[1:67]

          result = re.match("^[A-Za-z0-9]{66}$", block_hash) #check if we have real hash
          if result == None:
              print("All hashing done!")
              file.close()
              return 0

          print("x = ",x," Total hash lines = ",count)
          print("Now using:",block_hash," with length of:",len(block_hash))
          input("stop and confirm the block hash")
          if len(block_hash) != 66: #if our hash is somethign other than hash --> exit
             print("All hashing done!")
             return 0

          ts_created = check_delegations(block_hash)
          increase_daily_transactions()
          add_last_hash(block_hash)
          increase_hash_line_counter()
          input("SAFE TO QUIT")


        file.close()
        return 1
    
def fetch_all_tx():
    cmd_output = fire_and_split_command("cellframe-node-cli ledger tx -all -net Backbone", False)
    matches = re.findall(r'transaction: (?:\(emit\)\s)?hash (.*?)\n.*?TS Created: (.*?)\n', cmd_output, re.DOTALL)
    txs_by_date = {}
    for match in matches:
        hash_value = match[0].strip()
        timestamp = datetime.strptime(match[1].strip(),'%a %b %d %H:%M:%S %Y')
        date_key = timestamp.strftime('%-d.%-m.%Y')
        if date_key in txs_by_date:
            txs_by_date[date_key].append(hash_value)
        else:
            txs_by_date[date_key] = [hash_value]
    return txs_by_date

def insert_tx_to_db():
    conn = sqlite3.connect('databases/cellframe.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS txs
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      date TEXT,
                      amount INTEGER)''')

    x = fetch_all_tx()
    
    for date, hashes in x.items():
        hash_count = len(hashes)
        cursor.execute("INSERT INTO txs (date, amount) VALUES (?, ?)", (date, hash_count))
        
    conn.commit()
    conn.close()


##### TO RESET BLOCKS / SIGNATURES ####
#old_line()                          # get starting point from the top this file
#zero_all_blocks_and_signatures()    # zeroes blocks and signatures for every possible node
#go_through_every_block()            # reads through every block to get signatures
show_our_blocks()                   # calculate our blocks from database for confirmation
#######################################
input("stop")



#test_json()
initial_checkup()
check_online_status() #see if we are good to go
check_missing_node()
main_hashing()
update_non_validators_list()
update_ip_locations()
update_node_active_statuses_and_data()
check_block_reward()
check_if_fresh_was_non_validator()
update_node_versions() #versions and AUTO_UPDATE status
update_wallet_database()




