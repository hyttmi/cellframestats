import subprocess
import sqlite3
import operator
import requests
import time
import re
import os.path

#cellframe-node-cli dag event dump -event 0x528D14831C03C2FC8CB859BBD9C208273A5004940B80FC110175B770352B5BAB -net Backbone -chain zerochain -FROM THREM
def has_day_changed(event_date):
         day_counter=0

         con = sqlite3.connect('zerochain.db')
         with con:
           cur = con.cursor()
           query = """ SELECT current_day FROM flags ORDER BY id DESC"""
           cur.execute(query)
           result, = cur.fetchone()
           con.commit()

           if result == event_date or result=="1.1.1900":       #let's see if this is the same day or there is no records in flags table just yet
                     print("**** Still the same day! *****")
                     return 0
           else:
                     print(" ********************************* NEW DAY HAS COME **********************************")
                     print(" *                                                                                   *")
                     print(" *                                                                                   *")
                     print(" *                                                                                   *")
                     print(" *************************************************************************************")
                     #INITIALIZE NEW DAY FOR FLAGS

                     cur = con.cursor()
                     query = """ SELECT cumulative_cell_emission FROM {table} ORDER BY id DESC LIMIT 1""".format(table="flags")
                     cur.execute(query)
                     cumu, = cur.fetchone()
                     query = """ SELECT day_counter,month_counter FROM {table} WHERE id=1""".format(table="flags")
                     cur.execute(query)
                     day_counter, month_counter, = cur.fetchone()

                     day_counter = int(day_counter)
                     day_counter += 1
                     month_counter = int(month_counter)

                     if day_counter == 30:
                          month_counter += 1
                          day_counter=0

                     print("cumu day change",cumu)
                     query = """INSERT INTO {table} VALUES(null,null,?,null,null,null,?,?)""".format(table="flags")
                     cur.execute(query,[event_date,1,cumu])
                     con.commit()
                     query = """UPDATE {table} SET day_counter=? WHERE id=1""".format(table="flags")
                     cur.execute(query,[day_counter])
                     con.commit()
                     query = """UPDATE {table} SET month_counter=? WHERE id=1""".format(table="flags")
                     cur.execute(query,[month_counter])
                     con.commit()



                     print("Just initialized new day to flags")
 #                    input("wait")

                     return 1




def parse_block_hash(event_hash): #check inside event and get data

#   if event_hash=="0x8AB559F9D2B99E08F684CA131DD77354EBC1A7E2225182F581706CC7D8BFAB2C": #strange event. Nobody can open it
#     return None,event_hash


 #  event_hash="0x2065730DD4D5B07B66B8722B7BF672346FEB14803EA0B71875FEA7108131384E"

   event_hash = event_hash + " -net Backbone -chain zerochain -FROM THREM"
   round_number = 0

   command = fire_and_split_command("cellframe-node-cli dag event dump -event ", event_hash, True)    #spits out contents of a block
   list_items=len(command)

   con = sqlite3.connect('zerochain.db')
   with con:
        cur = con.cursor()

        for x in range(list_items):

          if "ts_created:" in command[x]: ## check through every list item to locate transaction created date
             length = len(command[x])
             ts_created = operator.getitem(command[x], slice(length-26, length-6)) #if found, copy last 24 letters

             take1 = command[x-3]
             round_id = take1[12:]
             print("TS_Created",ts_created)
             print("round id",round_id)



  #           print("checking validity of event", command[list_items-2])
 #            print(command[list_items-2])
  #           input("stoooop")
             if command[list_items-2] == "  Skip incorrect or illformed DATUM":  #we have broken block, do nothing and return
                input("Broken block")
                return False, event_hash



             ##################################
             # CHECK IF STILL IN THE SAME DAY #
             ##################################
             real_date = parse_date(ts_created)
             knowledge = has_day_changed(real_date) # see if we are still in the same day
             input("check date")
             if knowledge == 1: #new day
                     print("Zeroed daily events")
                     daily_events=1
             else:              #same day
                     print("Added 1 to daily events")
                     cur = con.cursor()
                     query = """ SELECT id,daily_events FROM {table} ORDER BY id DESC LIMIT 1""".format(table="flags")
                     cur.execute(query)
                     row, daily_events, = cur.fetchone()
                     daily_events += 1
                     query = """UPDATE {table} SET daily_events=? WHERE id=?""".format(table="flags")
                     cur.execute(query,[daily_events,row])
                     con.commit()





             print("TS CREATED:",real_date)

          if "type_id:="  in command[x]: ## See what event we are dealing with 


                length = len(command[x])
                type=command[x]
                type_id=type[12:] #get event type
                print("TYPE HERE:",type_id)

            



                if type_id == "DATUM_DECREE":
                      print("************ !!!! WE HAVE SOMETHING NEW !!! *****************")
 
                      take1=event_hash[:66]
                      event_hash=take1

                      take1=command[x-3]
                      hash_inside=take1[10:]

                      take1=command[x+3]
                      print("take1",take1)
                      signatures=take1[18:]
                      sign=int(signatures)

                      print("event hash :",event_hash)
                      print("hash_inside :",hash_inside)
                      print("round id :",round_id)
                      print("signatures :",sign)

                      cur = con.cursor()

                      query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(table="zerochain_hashes")
                      data = (event_hash,round_id,ts_created,hash_inside,type_id,"","",0,"",sign,"","","","","","","","",0,"")
                      cur.execute(query, data)
                      con.commit()





                if type_id == "DATUM_TOKEN_DECL":
                      print("******************************* We have token declaration! *********************************")
                      take1=event_hash[:66]
                      event_hash=take1
 
                      take1=command[x+4]
                      signatures=take1[18:]
                      sign=int(signatures)

                      print("Sgnatures:",sign) #sign = 3 in our case
                      y=sign+6 #depending on how many signatures there are, we need to jump forward to get our wanted data

                      take1=command[x+y]
                      hash=take1[6:]
                      take1=command[x+y+1]
                      ticker=take1[8:]

                      take1=command[x+y+2]
                      size=int(take1[6:])

                      take1=command[x+y+3]
                      version=int(take1[9:])

                      take1=command[x+y+4]
                      type=take1[6:]

                      take1=command[x+y+5]
                      subtype=take1[9:]

                      take1=command[x+y+6]
                      decimals=int(take1[10:])

                      take1=command[x+y+7]
#                      print("TAKE1:",take1)
                      testi=take1[:10]
 #                     print("TEST THIS HERE:",testi)

                      if testi=="sign_total":
#                           print("JEEE")
                           take1=command[x+y+9]
                           total_supply=take1[14:]
                           flags=0
                      else:
                           take1=command[x+y+8]
                           total_supply=take1[14:]
                           take1=command[x+y+9]
                           flags=take1[7:]

                      print("Event hash", event_hash)
                      print("Declaration hash:",hash)
                      print("Ticker",ticker)
                      print("Size:",size)
                      print("Version:",version)
                      print("Type:",type)
                      print("Subtype:",subtype)
                      print("Decimals:",decimals)
                      print("Total supply:",total_supply)
                      print("Flags:",flags)
#                      input("wait")
                      query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(table="zerochain_hashes")
                      data = (event_hash,round_id,ts_created,"",type_id,hash,"",0,"",signatures,ticker,size,version,type,subtype,decimals,total_supply,flags,0,0)
                      cur.execute(query, data)
                      con.commit()
                      query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="flags")
                      cur.execute(query)
                      line_number, = cur.fetchone()
#                      line_number=int(line_number)
                      print("line",line_number)
                      query = """ UPDATE {table} SET current_day=? WHERE id=?""".format(table="flags")
                      cur.execute(query, [real_date,line_number])
                      con.commit()
#                      event_hash=""
#                      hash=""
#                      round_id=0
#                      type_id=0
#                      type=0
#                      hash=""
#                      signatures=0
#                      ticker=""
#                      size=0
#                      subtype=""
#                      decimals=0
#                      total_supply=""
#                      flags=0


                elif type_id == "DATUM_TOKEN_EMISSION":
                      print("---- We have token emission! ----")
                      take1=event_hash[:66]
                      event_hash=take1

                      take1=command[x-3]
                      hash_inside=take1[10:]


                      print("ROUND ID",round_id)

                      take1=command[x+3]
                      print("take1",take1)
                      signatures=take1[18:]
                      sign=int(signatures)
   #                   print("Signatures : ",sign)
  #                    input("stop")

#                      print(sign) #sign = 3 in our case
#                      y=sign+5 #depending on how many signatures there are, we need to jump forward to get our wanted data
                      testi=command[x+4]
                      testi=testi[6:10]
                      testi.strip()

                      testi2=command[x+5]
                      testi2=testi2[6:10]
                      testi2.strip()
 
                     
                      testi3=command[x+6]
                      testi3=testi3[6:10]
                      testi3.strip()


                      testi4=command[x+7]
                      testi4=testi4[6:10]
                      testi4.strip()


                      testi5=command[x+8]
                      testi5=testi5[6:10]
                      testi5.strip()


                      testi6=command[x+9]
                      testi6=testi6[6:10]
                      testi6.strip()


                      if (sign == 3 and testi == "type" and testi2 == "type" and testi3 == "type" and testi4 != "type"): #says we have 3 signatures and we have 3 signatures
                        y=sign+4
                        print("Says we have 3 signatures and we have 3",testi," ",testi2," ",testi3," ",testi4," ",testi5," ",testi6)

                      if (sign == 3 and testi == "type" and testi2 == "type" and testi3 == "type" and testi4 == "type"): #says we have 3 signatures and we have 4 signatures
                        y=sign+5
                        print("Says we have 3 signatures but actually we have 4",testi," ",testi2," ",testi3," ",testi4," ",testi5," ",testi6)

                      if (sign == 4 and testi == "type" and testi2 == "type" and testi3 == "type" and testi4 == "type"): #says we have 4 signatures and we have 4 signatures
                        y=sign+4
                        print("Says we have 4 signatures and we do have 4",testi," ",testi2," ",testi3," ",testi4," ",testi5," ",testi6)


                      if (sign == 4 and testi == "type" and testi2 == "type" and testi3 == "type" and testi4 != "type"): #says we have 4 signatures and we have 3 signatures
                        y=sign+3
                        print("Saying we have 4 signatures but actually there is only 3",testi," ",testi2," ",testi3," ",testi4," ",testi5," ",testi6)

                      if (sign == 5 and testi == "type" and testi2 == "type" and testi3 == "type" and testi4 == "type" and testi5 != "type"): #says we have 5 signatures and we have 4 signatures
                        y=sign+3
                        print("Says we have 5 signatures but there is only 4",testi," ",testi2," ",testi3," ",testi4," ",testi5," ",testi6)

                      if (sign == 5 and testi == "type" and testi2 == "type" and testi3 == "type" and testi4 == "type" and testi5 == "type"): #says we have 5 signatures and we have 5 signatures
                        y=sign+4
                        print("Says there is 5 signatures and that is true",testi," ",testi2," ",testi3," ",testi4," ",testi5," ",testi6)

                      if (sign == 6 and testi == "type" and testi2 == "type" and testi3 == "type" and testi4 == "type" and testi5 == "type" and testi6 != "type"): #says we have 6 signatures and we have 5 signatures
                        y=sign+3
                        print("Says we got 6 signatures but we only have 5",testi," ",testi2," ",testi3," ",testi4," ",testi5," ",testi6)

                      if (sign == 6 and testi == "type" and testi2 == "type" and testi3 == "type" and testi4 == "type" and testi5 == "type" and testi6 == "type"): #says we have 6 signatures and we have 6 signatures
                        y=sign+4
                        print("Says we have 6 signatures and that is the case",testi," ",testi2," ",testi3," ",testi4," ",testi5," ",testi6)







#                      if testi == "type" and sign==4:    #if there are only 3 signatures even though it says 4. We need to alter future locations from here
 #                       y=sign+4
  #                      print("Let's see if we're in correct location",command[x+7])
#                      if testi == "type" and signatures==3:
                      take1=command[x+y]
                      emission_hash=take1[15:]
                      print("Emisssion hash:",emission_hash)
                      take1=command[x+y+1]
                      print("TAKE1:",take1) #ota value

                      search_results = re.finditer(r'\(.*?\)', take1) 
                      for item in search_results: 
                         item.group(0)
                      value=item.group(0).rstrip(')').lstrip('(')
                      value2 =int(value) / 1000000000000000000

                      location=take1.find(')')
   #                   print("location:",location)
                      ticker=take1[location+2:location+6]
                      if ticker=="KEL,":
                          ticker = "KEL"
                      print("TAKE:",ticker) 
                      input("no mita ny?")
                      print("Event hash:",event_hash)
                      print("Hash inside:",hash_inside)
                      print("Signatures:",sign)
                      print("Emission hash:",emission_hash)
                      print("Value",value2)
                      take1=command[x+y+2]
                      to_address=take1[11:]
                      if (ticker == "CELL" and value2 > 5000000):
                         print("Event hash:",event_hash)
                         input("value too big",value2)

 #                     print("To address:",to_address)
                      take1=command[x+y+3]
                      signs_count=take1[13:]
#                      input("stoppa haar")
                      #signs_count=int(signs_count)
  #                    print("Signs_count:",signs_count)
                      take1=command[x+y+4]
                      tsd_total_size=take1[18:]
 #                     input("ny seis")

                      #making exeptions for 1.1.2023 hash 0x07D46FA8FB7D156E62C24178CA49F3DF2F0CA3189986087CC66299B192D10F9F
                      #                 and 14.1.2023     0x6E0B3D19CE6B9B0EC5C34EDF16FBB286AFEEB4E1CAED6E24085BDCF11CE30D60
                      #                      2.2.20230    0x7BFBF8BA287673E973205F888729B50020E2EA8827B41159F3D7C4995680E78D
                      if tsd_total_size=="10800071622524105541" or tsd_total_size=="14153675786783313242" or tsd_total_size=="14407712627444676375":
                            tsd_total_size=0
                            value2=0
                      else:
                            tsd_total_size=int(tsd_total_size)

                      cur = con.cursor()

                      query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(table="zerochain_hashes")
                      data = (event_hash,round_id,ts_created,hash_inside,type_id,"",emission_hash,value2,to_address,sign,ticker,"","","","","","","",0,tsd_total_size)
                      cur.execute(query, data)
                      con.commit()

                      if ticker == "CELL":
                           query = """ SELECT cumulative_cell_emission FROM {table} ORDER BY id DESC LIMIT 1""".format(table="flags")
                           cur.execute(query)
                           cumu, = cur.fetchone()
#                           print("Cumulative CELL emission :",cumu)

#                           cumulative_cell_emission= cumu + value2
#                           cumulative_cell_emisison = float(cumulative_cell_emission)
  #                         print("new cumulative:",cumulative_cell_emission)

                           query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="flags")
                           cur.execute(query)
                           rivi, = cur.fetchone()





                           query = """ SELECT id FROM {table} ORDER BY id DESC LIMIT 1""".format(table="zerochain_hashes")
                           cur.execute(query)
                           last_id, = cur.fetchone()

                           print("****** Rivi nro :",last_id)
                           tarkastusrivi = last_id - 1
                           print("****** Tarkastusrivi :",tarkastusrivi)
                           query = """ SELECT emission_hash FROM {table} WHERE id=?""".format(table="zerochain_hashes")
                           cur.execute(query,[tarkastusrivi])
                           previous_hash, = cur.fetchone()

                           if emission_hash != previous_hash: #if we don't have double emission, add into cumulative CELL

                              cumulative_cell_emission= cumu + value2
                              cumulative_cell_emisison = float(cumulative_cell_emission)

                              cur = con.cursor()
                              query = """ UPDATE flags SET cumulative_cell_emission=? WHERE id=?"""
                              cur.execute(query, [cumulative_cell_emission,rivi])
                              con.commit()

                           else:
                              print("")
                              print("")
                              print("#!#!#!#!   Emission hash =",emission_hash)
                              print("#!#!#!#!   Previous hash =",previous_hash)
                              print("")
                              print("")
                              input("now we stop here")



         #                  cur = con.cursor()
         #                  query = """ UPDATE flags SET cumulative_cell_emission=? WHERE id=?"""
         #                  cur.execute(query, [cumulative_cell_emission,rivi])
         #                  con.commit()
#                      input("katos ny")


 #                     event_hash=""
 #                     hash=""
 #                     round_id=0
 #                     ts_created=""
 #                     hash_inside=""
 #                     type_id=0
 #                     emission_hash=""
 #                     to_addr=""
 #                     sign=0
 #                     tsd_total_size=0


                else:
                      print("")
                      print("something else : ",type_id)
                      print("")
   print("EVENT HASH PERKELE:",event_hash)
#   con.close()
   return True, event_hash





def create_connection(db_file): #make connection to the database and return con object or none.
    con = None
    try:
       con = sqlite3.connect(db_file)
       return con
    except:
       print("not working")
       exit()

    return con




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


def parse_date(date):   #change date format from Nov 17 2023 ---> 17.11.2023
    length=len(date)
 #   print("date is ",date)
    year = operator.getitem(date, slice(length-13,length-9))
#    print("year",year) 
    month = date[3:6]
#    print("month",month)
    month=month_to_number(month)

    day = date[:2]
#    print("day",day)
    final_date = day+'.'+str(month)+'.'+year
    print("final date:",final_date)
#    input("stop")
    return final_date


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
        exit()
    return command_run


def create_table(con, create_table_sql): #create database table
    try:
        cur = con.cursor()
        cur.execute(create_table_sql)
        con.commit()
    except:
        print("error")



def initialize_database():
     con = create_connection(database)
     with con:
        cur = con.cursor()
        query = """ INSERT INTO {table} VALUES (null,?,?,?,?,?,?,?)""".format(table="flags")
        cur.execute(query,["INITIAL VALUES 0zOIJFOSDIFUOHNOLI3245jhf9dsfk2345lkj","1.1.1900",0,0,0,0,0])
        con.commit()
     return




database = r"zerochain.db"



sql_create_zerochain_hashes_data_table = """CREATE TABLE IF NOT EXISTS zerochain_hashes (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    event_hash data_type TEXT NOT NULL UNIQUE,
                                    round_id data_type INTEGER NOT NULL,
                                    ts_created data_type TEXT,
                                    hash_inside data_type TEXT,
                                    type_id data_type TEXT,
                                    declaration_hash data_type TEXT,
                                    emission_hash data_type TEXT,
                                    value data_type REAL,
                                    to_addr data_type TEXT,
                                    signatures data_type INTEGER,
                                    ticker data_type TEXT,
                                    size data_type INT,
                                    version data_type INT,
                                    type data_type TEXT,
                                    subtype data_type TEXT,
                                    decimals data_type INT,
                                    total_supply data_type TEXT,
                                    flags data_type NONE,
                                    sign_count data_type INT,
                                    tsd_total_size data_type INT
                                    );"""

sql_create_flags_table = """ CREATE TABLE IF NOT EXISTS flags (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    last_hash data_type TEXT,
                                    current_day data_type TEXT,
                                    day_counter data_type INTEGER,
                                    month_counter data_type INTEGER,
                                    hash_line_counter data_type INTEGER,
                                    daily_events data_type INTEGER,
                                    cumulative_cell_emission data_type REAL
                                    );"""




def create_database():
    con = create_connection(database)
    if con is not None:
        create_table(con, sql_create_zerochain_hashes_data_table)
    con = create_connection(database)
    if con is not None:
        create_table(con, sql_create_flags_table)
        print("tables created")
    return



def add_last_hash(hash, old_hash_line):
 #        print(data)
#         hash, old_hash_line = data


         con = sqlite3.connect('zerochain.db') #replace the last hash in database
         with con:
           cur = con.cursor()
           tabletoedit = "flags"
           tieto=[hash]
           cur.execute((""" INSERT OR IGNORE INTO flags (id, last_hash) VALUES (?,?)"""),[1,hash])
           print("last hash was :",hash)
           cur.execute((""" UPDATE flags SET last_hash=? WHERE id=1"""),[hash])
           con.commit()

           query = """ SELECT hash_line_counter FROM {table} ORDER BY id ASC LIMIT 1""".format(table="flags")
           cur.execute(query)
           old_hash_line, = cur.fetchone()
           old_hash_line += 1
           con.cursor()
           cur.execute((""" UPDATE flags SET hash_line_counter=? WHERE id=1"""), [old_hash_line,])
           con.commit()
           return



#cellframe-node-cli dag event list -net Backbone -chain zerochain poablock_poa -from events
#cellframe-node-cli dag event dump -event 0x528D14831C03C2FC8CB859BBD9C208273A5004940B80FC110175B770352B5BAB -net Backbone -chain zerochain -FROM THREM


def read_events_to_database():
#    nodeaddress,ts_done = nodeaddress
       #       print("Stealing node information from cli")
#              command = fire_and_split_command("cellframe-node-cli srv_stake list keys -net ","Backbone", True)
#              list_items=len(command)
#              print("List items :",command)
#              real_node_address = nodeaddress[1:17]
#              real_node_address = real_node_address[:4] + '::' + real_node_address[4:16]
#              real_node_address = real_node_address[:10] + '::' + real_node_address[10:14]         #convert node address back to original form with all those ::'s
#              real_node_address = real_node_address[:18] + '::' + nodeaddress[13:17]
#              real_node_address.lstrip()
#        create_database()
        con = create_connection(database)

        input("Ready to launch?...")

        file = open("zerochain_events.txt","r")
        ## DO THIS FIRST
        ##  cellframe-node-cli block list -net Backbone -chain main >> all_blocks.txt

        with open(r"zerochain_events.txt", 'r') as fp: ##count lines in our file
           for count, line in enumerate(fp):
               pass
               count=count+1

        print("Lines",count)



        cur = con.cursor() #lets first see where we left last time and then we can continue from there
        query = """ SELECT hash_line_counter FROM flags WHERE id=1"""
        cur.execute(query)
        old_hash_line, = cur.fetchone()
        print("Old hash line :",old_hash_line)
        lines_to_go = count-old_hash_line

        if lines_to_go < 5: #if not enough events, don't bother
            print("not enough hash lines")
            return

        print("We have ",lines_to_go,"new hashes in Zerochain")
        input("Should we go or stop?")

        if old_hash_line != 0:
            for y in range(old_hash_line+5):
              temp = file.readline() #lets read lines until we reach position where last time we ended
        #      print("temp :",temp)

#        input("stop here")


        for x in range(count):

          block_hash = file.readline()
          block_hash = block_hash[1:67]
 #         print("x = ",x," Count = ",count)
          #print("******************* NOW Using:",block_hash[:20],"...",block_hash[20:0],"******************************")
          print("******************* Zerochain NOW Using:",block_hash)
          print(len(block_hash))
          input("is that correct?")
          if len(block_hash) != 66: #if our hash is somethign other than hash --> exit
             return 0


          condition, hash = parse_block_hash(block_hash) #lets try to read info about the hash

          if condition != False:
              old_hash_line += 1
              add_last_hash(hash,old_hash_line)

          else:
              print("We had a broken block. Still write into database")
              old_hash_line += 1
              add_last_hash(hash,old_hash_line)


        return




our_file=os.path.isfile("zerochain.db")
if our_file != True:
   print("Database not found. Let's make one")
   create_database()
   initialize_database()

#parse_block_hash("0x2065730DD4D5B07B66B8722B7BF672346FEB14803EA0B71875FEA7108131384E")
read_events_to_database()















