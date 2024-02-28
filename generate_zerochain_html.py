import sqlite3
import numpy as np

######################################
#                                    #
#   Generate ZEROCHAIN events page   #
#                                    #
######################################
def generate_zerochain2_page():

    file = open("zerochain_data.json", "w")
    row_id = 11000
    con = sqlite3.connect('zerochain.db')
    with con:
        cur=con.cursor()
        query = """ SELECT id FROM zerochain_hashes ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID
        cur.execute(query)
        row_id, = cur.fetchone() #get number of nodes
        print("ROW",row_id)


        file.write("var esp_data = [\n")



        mista = row_id
        mihin = row_id - 1000

        for x in range(mista,mihin,-1):    #WE will print 1000 lines only


            # then we need to see if we get declaration or emission and create table accordingly
            cur = con.cursor()
            query = """SELECT ts_created,round_id,type_id,signatures,tsd_total_size,value,ticker,to_addr,event_hash,emission_hash FROM zerochain_hashes WHERE id=?"""
            cur.execute(query,[x])
            ts_created,round_id,type_id,signatures,tsd_total_size,value,ticker,to_addr,event_hash,emission_hash = cur.fetchone()

            file.write('{')
            file.write("\n")

            file.write('"date": "')
            file.write(str(ts_created))
            file.write('",')
            file.write("\n")


            file.write('"round": "')
            file.write(str(round_id))
            file.write('",')
            file.write("\n")


            file.write('"tds_total_size": "')
            file.write(str(tsd_total_size))
            file.write('",')
            file.write("\n")


            file.write('"event_hash": "')
            file.write(str(event_hash[:20]))
            file.write(".....")
            file.write(str(event_hash[-20:]))

            file.write('",')
            file.write("\n")


            file.write('"emission_hash": "')
            file.write(str(emission_hash[:20]))
            file.write(".....")
            file.write(str(emission_hash[-20:]))
            file.write('",')
            file.write("\n")


            file.write('"signatures": "')
            file.write(str(signatures))
            file.write('",')
            file.write("\n")


            file.write('"info": "')
            file.write(str(type_id))
            file.write('",')
            file.write("\n")


            file.write('"to": "')
            file.write(str(to_addr[:20]))
            file.write(".....")
            file.write(str(to_addr[-20:]))
            file.write('",')
            file.write("\n")


            file.write('"value": "')
            file.write(str(value))
            file.write('",')
            file.write("\n")


            file.write('"ticker": "')
            file.write(str(ticker))
            file.write('",')
            file.write("\n")

            file.write('},')
            file.write("\n")


        file.write("]")
        file.close()

        return






