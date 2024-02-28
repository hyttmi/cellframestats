
from generate_nodes_html import *
#from generate_richlist import *
from cellframe_charting import *
from generate_zerochain_html import *

def parse_node_address(address):   ## removes :: from node address and returns clean version of it
    node_address=address.replace("::","")
    additional='N'
    node_address=additional+node_address # Add 'N' in font of node address as Qlite doesn't like tables which name begins with number
    return node_address

#
#    NODES.JSON
#
#    NODES MAIN
#    ALL NODES + INDIVIDUAL NODE PAGES
#    AT THE BOTTOM = CREATE NODE PAGE 3 CHARTS
#





def generate_nodes_json():
    file = open("user_data.json", "w")

    database = r"cellframe.db"
    con = create_connection(database)

    with con:
        cur = con.cursor()
        query = """ SELECT id FROM cellframe_data ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID
        cur.execute(query)
        row_id, = cur.fetchone() #get number of nodes
        file.write("var esp_data = [\n")
        for x in range(1,row_id+1):

            query = """ SELECT address,staked_amount,weight,fresh,node_active_status,country FROM cellframe_data WHERE id=?"""
            cur.execute(query,[x])
            address,staked_amount,weight,fresh,node_active_status,country = cur.fetchone()
            table_name = parse_node_address(address)
            weight = round(weight,2)

            query = """ SELECT first_block,node_version,week_count FROM {table} ORDER BY id ASC LIMIT 1""".format(table=table_name)
            cur.execute(query)
            first_block,node_version,week = cur.fetchone()

            query = """ SELECT blocks,all_time_blocks,daily_signatures,all_time_signatures,daily_rewards,all_time_rewards FROM {table} ORDER BY id DESC LIMIT 1""".format(table=table_name)
            cur.execute(query)
            blocks,all_time_blocks,daily_signatures,all_time_signatures,daily_rewards,all_time_rewards = cur.fetchone()
            daily_rewards = round(daily_rewards,2)
            all_time_rewards = round(all_time_rewards,2)
            query = """ SELECT SUM(blocks)
                            FROM (SELECT blocks FROM
                            {table} ORDER BY id
                            DESC LIMIT 7);""".format(table=table_name);
            cur.execute(query)
            weekly_blocks, = cur.fetchone()

            query = """ SELECT SUM(blocks)
                        FROM (SELECT blocks FROM
                        {table} ORDER BY id
                         DESC LIMIT 30);""".format(table=table_name);

            cur.execute(query)
            monthly_blocks, = cur.fetchone()

            query = """ SELECT SUM(daily_signatures)
                        FROM (SELECT daily_signatures FROM
                        {table} ORDER BY id
                         DESC LIMIT 7);""".format(table=table_name);

            cur.execute(query)
            weekly_signatures, = cur.fetchone()

            query = """ SELECT SUM(daily_signatures)
                        FROM (SELECT daily_signatures FROM
                        {table} ORDER BY id
                         DESC LIMIT 30);""".format(table=table_name);

            cur.execute(query)
            monhtly_signatures, = cur.fetchone()


            query = """ SELECT SUM(daily_rewards)
                        FROM (SELECT daily_rewards FROM
                        {table} ORDER BY id
                         DESC LIMIT 7);""".format(table=table_name);

            cur.execute(query)
            weekly_rewards, = cur.fetchone()
            weekly_rewards = int(weekly_rewards)

            query = """ SELECT SUM(daily_rewards)
                        FROM (SELECT daily_rewards FROM
                        {table} ORDER BY id
                         DESC LIMIT 30);""".format(table=table_name);

            cur.execute(query)
            monhtly_rewards, = cur.fetchone()
            monhtly_rewards = int(monhtly_rewards)
            weblink = table_name + ".html"

            print(x)
            print("Address",address)
            print("weblink",weblink)
            print("Staked amount",staked_amount)
            print("Weight",weight)
            print("Fresh",fresh)
            print("Active",node_active_status)
            print("Country",country)
            print("-----")
            print("week",week)
            print("block",blocks)
            print("7 day blocks",weekly_blocks)
            print("30 day blocks",monthly_blocks)
            print("all_time_blocks",all_time_blocks)
            print("first_block",first_block)
            print("node_version",node_version)
            print("daily signatures",daily_signatures)
            print("7 day signatures",weekly_signatures)
            print("30 day signatures",monhtly_signatures)
            print("all_time_signatures",all_time_signatures)
            print("daily rewards",daily_rewards)
            print("7 day rewards",weekly_rewards)
            print("30 day rewards",monhtly_rewards)
            print("all time rewards",all_time_rewards)



            alias = ""

            file.write('{')
            file.write("\n")
            file.write('"address": "')
            file.write(address)
            file.write('",')
            file.write("\n")

            file.write('"weblink": "')
            file.write(weblink)
            file.write('",')
            file.write("\n")

            file.write('"alias": "')
            file.write(alias)
            file.write('",')
            file.write("\n")

            file.write('"country": "')
            file.write(country)
            file.write('",')
            file.write("\n")

            file.write('"version": "')
            file.write(node_version)
            file.write('",')
            file.write("\n")

            file.write('"status": "')
            if node_active_status == 1:
                status = 0
            else:
                status = 1
            file.write(str(status))
            file.write('",')
            file.write("\n")



            # when we calculate node performance, we need to know how many blocks there has been in the last 7 days
            query = """ SELECT SUM(daily_transactions)
                            FROM (SELECT daily_transactions FROM
                            {table} ORDER BY id
                            DESC LIMIT 7);""".format(table="transactions");

            cur.execute(query)
            last_seven_day_blocks, = cur.fetchone()


            performance2 = ((week / last_seven_day_blocks) * 100)  / weight
            performance = round(performance2,2) #round with only 2 decimals


            file.write('"performance": "')
            file.write(str(performance))
            file.write('",')
            file.write("\n")

            file.write('"stake": "')
            file.write(str(staked_amount))
            file.write('",')
            file.write("\n")


            file.write('"own_stake": "')
            file.write(str(staked_amount))
            file.write('",')
            file.write("\n")

            file.write('"delegators": "')
            file.write("1")
            file.write('",')
            file.write("\n")

            file.write('"today": "')
            file.write(str(blocks))
            file.write('",')
            file.write("\n")

            file.write('"week": "')
            file.write(str(weekly_blocks))
            file.write('",')
            file.write("\n")

            file.write('"month": "')
            file.write(str(monthly_blocks))
            file.write('",')
            file.write("\n")

            file.write('"all_time": "')
            file.write(str(all_time_blocks))
            file.write('",')
            file.write("\n")

            file.write('"signs_today": "')
            file.write(str(daily_signatures))
            file.write('",')
            file.write("\n")

            file.write('"signs_week": "')
            file.write(str(weekly_signatures))
            file.write('",')
            file.write("\n")

            file.write('"signs_month": "')
            file.write(str(monhtly_signatures))
            file.write('",')
            file.write("\n")

            file.write('"signs_all_time": "')
            file.write(str(all_time_signatures))
            file.write('",')
            file.write("\n")

            file.write('"rewards_today": "')
            file.write(str(daily_rewards))
            file.write('",')
            file.write("\n")

            file.write('"rewards_week": "')
            file.write(str(weekly_rewards))
            file.write('",')
            file.write("\n")

            file.write('"rewards_month": "')
            file.write(str(monhtly_rewards))
            file.write('",')
            file.write("\n")

            file.write('"rewards_all_time": "')
            file.write(str(all_time_rewards))
            file.write('",')
            file.write("\n")

            file.write('},')
            file.write("\n")

            #line = marker1 + address + marker2 + weblink + marker3 + alias + marker4 + country

            #line = str(line)

            #file.write(line)

     #           x += 1
      #          wallets -= 1




        cur = con.cursor()
        query = """ SELECT id FROM cellframe_data ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID
        cur.execute(query)
        row_id, = cur.fetchone() #get number of NON VALIDATING nodes
        for x in range(1,row_id+1):


            query = """ SELECT node_address,country FROM non_validators WHERE id=?"""
            cur.execute(query,[x])
            address,country = cur.fetchone()

            file.write('{')
            file.write("\n")
            file.write('"address": "')
            file.write(address)
            file.write('",')
            file.write("\n")

            file.write('"weblink": "')
            file.write("n/a")
            file.write('",')
            file.write("\n")

            file.write('"alias": "')
            file.write("n/a")
            file.write('",')
            file.write("\n")

            file.write('"country": "')
            if country == None:
                file.write("Unknown")
            else:
                file.write(country)
            file.write('",')
            file.write("\n")

            file.write('"version": "')
            file.write("n/a")
            file.write('",')
            file.write("\n")

            file.write('"status": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"performance": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"stake": "')
            file.write("0")
            file.write('",')
            file.write("\n")


            file.write('"own_stake": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"delegators": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"today": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"week": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"month": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"all_time": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"signs_today": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"signs_week": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"signs_month": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"signs_all_time": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"rewards_today": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"rewards_week": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"rewards_month": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('"rewards_all_time": "')
            file.write("0")
            file.write('",')
            file.write("\n")

            file.write('},')
            file.write("\n")


        file.write("]")
        file.close()
        #break




def generate_node2_main_html():
    ####################################################
    #                                                  #
    #  THIS PART WILL GENERATE HTML PAGE WHERE ALL     #
    #  THE NODES ARE TOGETHER. IT WILL ALSO GENERATE   #
    #   INDIVIDUAL NODES HTML PAGES                    #
    #                                                  #
    ####################################################

     file = open("nodes.html", "w")

     database = r"cellframe.db"
     con = create_connection(database)

     file.write(""" <!DOCTYPE html> \n""")
     file.write(""" <html>  \n""")
     file.write(""" <head> \n""")
     file.write("""<!-- Google tag (gtag.js) -->\n""")
     file.write("""<script async src="https://www.googletagmanager.com/gtag/js?id=G-FEPK7JS9E3"></script>\n""")
     file.write("""<script> \n""")
     file.write("""     window.dataLayer = window.dataLayer || []; \n""")
     file.write("""     function gtag(){dataLayer.push(arguments);} \n""")
     file.write("""     gtag('js', new Date()); \n""")
     file.write(""" \n""")
     file.write("""     gtag('config', 'G-FEPK7JS9E3'); \n""")
     file.write("""</script> \n """)
     file.write(""" """)
     file.write("""         <title>Cellframe nodes</title>\n """)

     file.write("""  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.3/dist/leaflet.css"  \n""")
     file.write("""  integrity="sha512-Rksm5RenBEKSKFjgI3a41vrjkw4EVPlJ3+OiI65vTjIdo9brlAacEuKOiQ5OFh7cOI1bkDwLqdLw3Zg0cRJAAQ==" crossorigin/> \n""")
     file.write("""  <!-- Make sure you put this AFTER Leaflet's CSS --> \n""")
     file.write("""  <script src="https://unpkg.com/leaflet@1.3.3/dist/leaflet.js" \n """)
     file.write("""  integrity="sha512-tAGcCfR4Sc5ZP5ZoVz0quoZDYX5aCtEm/eu1KhSLj2c9eFrylXZknQYmxUssFaVJKvvc0dJQixhGjG2yXWiV9Q==" crossorigin></script> \n""")


     file.write(""" 	<meta charset="utf-8"> \n""")
     file.write(""" 	<meta name="viewport" content="width=device-width, initial-scale=1">\n """)
     file.write(""" 	<meta name="generator" content="RocketCake"> \n""")
     file.write("""         <link rel="shortcut icon" type="image/x-icon" href="http://cellframestats.com/favicon.ico">	\n """)
     file.write(""" 	<link rel="stylesheet" type="text/css" href="css/nodes_html.css"> \n""")
     file.write(""" 		<link  rel="stylesheet" href="css/nodes_tabulator.min.css"> \n""")
     file.write(""" 		<script type="text/javascript" src="js/tabulator.min.js"></script> \n""")
     file.write(""" 		<script type="text/javascript" src="user_data.json"></script>  \n""")
     file.write(""" </head> \n""")

     file.write(""" <body> \n""")
     file.write(""" <div class="textstyle1"> \n""")
     file.write(""" <div id="container_white_top"><div id="container_white_top_padding" ><div class="textstyle1">  <span class="textstyle2"><br/></span> \n""")
     file.write(""" </div> \n""")
     file.write(""" </div></div><div id="container_menubar"><div id="container_menubar_padding" ><div class="textstyle1">  <div id="menu_buttons"> \n""")
     file.write("""     <div  class="menuholder1"><a href="javascript:void(0);"> \n""")
     file.write(""" 	<div id="menuentry_715b4194"  class="menustyle1 menu_buttons_mainMenuEntry mobileEntry"> \n""")
     file.write(""" 		<div class="menuentry_text1"> \n""")
     file.write("""       <span class="textstyle3">Menu &#9660;</span> \n""")
     file.write(""" 		</div> \n""")
     file.write(""" 	</div> \n""")
     file.write(""" </a> \n""")
     file.write(""" <a href="index.html" style="text-decoration:none"> \n""")
     file.write(""" 	<div id="menuentry_e185fff"  class="menustyle1 menu_buttons_mainMenuEntry normalEntry"> \n""")
     file.write(""" 		<div class="menuentry_text2"> \n""")
     file.write("""       <span class="textstyle4">Home</span> \n""")
     file.write(""" 		</div> \n""")
     file.write(""" 	</div> \n""")
     file.write(""" </a> \n""")
     file.write(""" <a href="stats.html" style="text-decoration:none"> \n""")
     file.write(""" 	<div id="menuentry_59d6beb3"  class="menustyle2 menu_buttons_mainMenuEntry normalEntry"> \n""")
     file.write(""" 		<div class="menuentry_text2"> \n""")
     file.write("""       <span class="textstyle4">Stats</span> \n""")
     file.write(""" 		</div> \n""")
     file.write(""" 	</div> \n""")
     file.write(""" </a> \n""")
     file.write(""" <a href="zerochain.html" style="text-decoration:none"> \n""")
     file.write(""" 	<div id="menuentry_7c09b130"  class="menustyle3 menu_buttons_mainMenuEntry normalEntry"> \n""")
     file.write(""" 		<div class="menuentry_text2"> \n""")
     file.write("""       <span class="textstyle4">Zerochain</span> \n""")
     file.write(""" 		</div> \n""")
     file.write(""" 	</div> \n""")
     file.write(""" </a> \n""")
     file.write(""" <a href="javascript:void(0);"> \n""")
     file.write(""" 	<div id="menuentry_eb0c707"  class="menustyle4 menu_buttons_mainMenuEntry normalEntry"> \n""")
     file.write(""" 		<div class="menuentry_text2">\n """)
     file.write("""       <span class="textstyle4">Nodes</span> \n""")
     file.write(""" 		</div> \n""")
     file.write(""" 	</div> \n""")
     file.write(""" </a> \n""")
     file.write(""" <a href="richlist.html" style="text-decoration:none"> \n""")
     file.write(""" 	<div id="menuentry_4581182d"  class="menustyle5 menu_buttons_mainMenuEntry normalEntry"> \n""")
     file.write(""" 		<div class="menuentry_text2"> \n""")
     file.write("""       <span class="textstyle4">Richlist</span> \n""")
     file.write(""" 		</div> \n""")
     file.write(""" 	</div> \n""")
     file.write(""" </a> \n""")
     file.write(""" <a href="timeline.html" style="text-decoration:none"> \n""")
     file.write(""" 	<div id="menuentry_51d96f85"  class="menustyle6 menu_buttons_mainMenuEntry normalEntry"> \n""")
     file.write(""" 		<div class="menuentry_text2"> \n""")
     file.write("""       <span class="textstyle4">Timeline</span> \n""")
     file.write(""" 		</div> \n""")
     file.write(""" 	</div> \n""")
     file.write(""" </a> \n""")
     file.write("""  \n""")
     file.write(""" 	<script type="text/javascript" src="rc_images/wsp_menu.js"></script> \n""")
     file.write(""" 	<script type="text/javascript"> \n""")
     file.write(""" 		var js_menu_buttons= new wsp_menu('menu_buttons', 'menu_buttons', 10, null, true); \n""")
     file.write("""  \n""")
     file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_715b4194', ["      <span class=\"textstyle5\">Home</span> ", 'index.html', '', \n""")
     file.write(""" 		                                   "      <span class=\"textstyle5\">Stats</span> ", 'stats.html', '', \n""")
     file.write(""" 		                                   "      <span class=\"textstyle5\">Zerochain</span> ", 'zerochain.html', '', \n""")
     file.write(""" 		                                   "      <span class=\"textstyle5\">Nodes</span> ", 'javascript:void(0);', '', \n""")
     file.write(""" 		                                   "      <span class=\"textstyle5\">Richlist</span> ", 'richlist.html', '',\n """)
     file.write(""" 		                                   "      <span class=\"textstyle5\">Timeline</span> ", 'timeline.html', '']); \n""")
     file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_e185fff', []); \n""")
     file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_59d6beb3', []); \n""")
     file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_7c09b130', []); \n""")
     file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_eb0c707', []); \n""")
     file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_4581182d', []); \n""")
     file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_51d96f85', []); \n""")
     file.write("""  \n""")
     file.write(""" 	</script> \n""")
     file.write("""       </div> \n""")
     file.write("""     </div> \n""")
     file.write(""" </div> \n""")
     file.write(""" <div style="clear:both"></div></div></div><div id="container_waves"><div id="container_waves_padding" ></div></div><span class="textstyle6"><br/>\n""")
     file.write(""" </span><div id="container_nodes_legend"><div id="container_nodes_legend_padding" ><div class="textstyle1">\n""")
     file.write(""" <img src="rc_images/node_legend.png" width="415" height="43" id="img_legend" alt="" title="" /><span class="textstyle7"><br/></span></div> \n""")
     file.write(""" <div style="clear:both"></div></div></div><span class="textstyle7"><br/></span>  </div> \n""")
     file.write(""" <div class="textstyle8"> \n""")
     file.write(""" <div id="container_nodes_table"><div id="container_nodes_table_padding" ><div class="textstyle1">  <span class="textstyle7"> </span> \n""")
     file.write("""  \n""")


     file.write("""  <div id="map" style="width: 900px; height: 400px;margin:0 auto;"></div>\n""")
     # file.write("""  <div class="textstyle2"><div id="map" style="width: 900px; height: 400px;margin:0 auto;"></div> """)
     file.write(""" <script> \n""")
     file.write(""" var map = L.map('map').setView([51.505, -0.09], 20);\n""")
     file.write(""" var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {\n""")
     file.write(""" 		    maxZoom: 5, \n""")
     file.write("""  		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'\n""")
     file.write(""" 	        }).addTo(map); \n""")
     file.write("""  \n""")

     ##############################################
     #                                            #
     #  Let's mark all the validators to our map  #
     #                                            #
     ##############################################
     con = sqlite3.connect('cellframe.db')
     with con:
        cur = con.cursor()
        query = """ SELECT id FROM cellframe_data ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID
        cur.execute(query)
        result = cur.fetchone()
        row_id, = result

        for x in range(row_id):
            cur = con.cursor()
            query = """ SELECT address,latitude, longitude, node_active_status FROM cellframe_data WHERE id=?""".format()
            cur.execute(query, [row_id])
            print("ROW ID", row_id)
            result = cur.fetchone()
            node_address, latitude, longitude, node_active_status = result
            file.write(""" var circle = L.circle([""")
            file.write(str(latitude))
            file.write(""",""")
            file.write(str(longitude))
            file.write("""], {color: 'blue',fillColor: '""")
            if node_active_status == 1:
                file.write("""#f03""")
            else:
                file.write("""#00f""")
            file.write("""',fillOpacity: 0.7,radius: 50000}).addTo(map); circle.bindPopup(" """)
            file.write(node_address)
            file.write(""" ");  """)

            row_id = row_id - 1
     #################################################
     #                                               #
     #  And also mark the non_validators to the map  #
     #                                               #
     #################################################
     # con = sqlite3.connect('/home/timo/coding/cellframe/cellframe.db')
     # with con:
     #    cur = con.cursor()
     query = """ SELECT id FROM non_validators ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID in non_validators
     cur.execute(query)
     result = cur.fetchone()
     row_id, = result

     for x in range(row_id):
        cur = con.cursor()
        query = """ SELECT node_address,latitude, longitude FROM non_validators WHERE id=?""".format()
        cur.execute(query, [row_id])
        print("ROW ID in non_validators", row_id)
        result = cur.fetchone()
        node_address, latitude, longitude = result
        testi = isinstance(latitude, str)
        if testi == False:
            print("latitude", latitude)
            print("type is :", type(latitude))
            file.write(""" var circle = L.circle([""")
            file.write(str(latitude))
            file.write(""",""")
            file.write(str(longitude))
            file.write("""], {color: 'green',fillColor: '""")
            # if node_active_status==1:
            #    file.write("""#f03""")
            # else:
            file.write("""#0f0""")
            file.write("""',fillOpacity: 0.7,radius: 30000}).addTo(map); circle.bindPopup(" """)
            file.write(node_address)
            file.write(""" ");  """)
            row_id = row_id - 1
            print("this was correct location")
        else:
            row_id = row_id - 1
            print("noo not the zero ones")

     file.write("""  </script><br></br> \n""")
     file.write(""" <div id="example-table"></div> \n""")
     file.write(""" 			<!-- ---------------------------------------------------------------- --> \n""")
     file.write(""" 			<script type="text/javascript">					 \n""")
     file.write(""" 				var local_data = esp_data;  <!-- name inside json file -->	 \n""")
     file.write(""" 				var table = new Tabulator("#example-table", { \n""")
     file.write(""" 					data: local_data, \n""")
     #file.write("""                                         rowClickPopup:"Im a Popup", \n""")
     file.write(""" 					pagination:"local", \n""")
     file.write(""" 					paginationSize:30, \n""")
     file.write(""" 					layout:"fitDataFill", \n""")
     file.write(""" 					//layout:"fitColumns", \n""")
     file.write("""                                         responsiveLayout:"collapse", \n""")
     file.write("""                                         responsiveLayoutCollapseStartOpen:false, \n""")
     file.write(""" 					placeholder:"No Data Available",								 \n""")
     file.write(""" 					columns:[ \n""")
     file.write("""                                         {formatter:"responsiveCollapse", width:30, minWidth:30, hozAlign:"center", resizable:false, headerSort:false}, \n""")
     file.write(""" 					{formatter:"rownum", align:"center", width:40}, \n""")
     file.write(""" 					{title:"Address",   field:"weblink",width:160,headerSort:false, responsive:0, \n""")
     file.write(""" formatter:"link", formatterParams:{labelField:"address",urlPrefix:"nodes/",target:"_self",} \n""")
     file.write("""                                         }, \n""")
     file.write("""  """)
     file.write("""                                         {title:"Alias",   field:"alias",width:250,headerSort:false, responsive:0,clickPopup:"Contact Trader76 @ Telegram if you wish to see your website / alias written in here"}, \n""")
     file.write(""" 					{title:"Country",  field:"country",width:230}, \n""")
     file.write(""" 					{title:"Version", field:"version", width:70,headerSort:false, responsive:0}, \n""")
     file.write("""                                         {title:"Status", field:"status",  hozAlign:"center", formatter:"tickCross",width:70}, \n""")
     file.write("""                                         {title:"Perf.", field:"performance", width:70,headerClickPopup:"Node performance is calculated from the number of (blocks / week)/node signatures. It should be around 1.0. Higher than that, the node is very lucky and lower means either lots of down time, bad luck or node has been offline for some time. When the network produces only few blocks, this number tends to fluctuate and doesn't represent real situation."}, \n""")
     file.write("""                                         {title:"Stake value", field:"stake", sorter:"number", width:100}, \n""")
     file.write("""                                         {title:"Self staked", field:"own_stake", width:100}, \n""")
     file.write("""                                         {title:"Delegators", field:"delegators",headerSort:false, responsive:0, width:70}, \n""")
     file.write("""                                         {title:"today", field:"today", width:70}, \n""")
     file.write("""                                         {title:"week", field:"week", width:70}, \n""")
     file.write("""                                         {title:"month", field:"month", width:70}, \n""")
     file.write("""                                         {title:"all time", field:"all_time", width:80}, \n""")
     file.write("""                                         {title:"signatures today", field:"signs_today", width:60}, \n""")
     file.write("""                                         {title:"signatures/week", field:"signs_week", width:70}, \n""")
     file.write("""                                         {title:"signatures/month", field:"signs_month", width:70}, \n""")
     file.write("""                                         {title:"signatures/all time", field:"signs_all_time", width:80}, \n""")
     file.write("""                                         {title:"rewards today", field:"rewards_today", width:60}, \n""")
     file.write("""                                         {title:"rewards/week", field:"rewards_week", width:70}, \n""")
     file.write("""                                         {title:"rewards/month", field:"rewards_month", width:70}, \n""")
     file.write("""                                         {title:"rewards/all", field:"rewards_all_time", width:80}, \n""")
     file.write(""" 					],					 \n""")
     file.write(""" """)
     file.write(""" initialSort:[{column:"stake", dir:"desc"}],""")
     file.write(""" 				});					 \n""")
     file.write(""" 			</script> \n""")
     file.write(""" 			<!-- -------------------------------------------------------------------- --> \n""")
     file.write(""" 		</div> \n""")
     file.write("""  \n""")
     file.write("""  \n""")
     file.write("""  \n""")
     file.write("""  \n""")
     file.write("""  \n""")
     file.write("""  \n""")
     file.write("""  \n""")
     file.write("""  <br></br>\n""")
     file.write(""" </div> \n""")
     file.write(""" </div></div>  </div> \n""")
     file.write(""" </body> \n""")
     file.write(""" </html>\n """)


     #file.write("""   """)
     #file.write("""   """)
     #file.write("""  </script> """)

     #file.write(""" </div></div></div>  </div></body></html>  """)
     #file.write("""   """)
     file.close()
     return





def create_all_node_pages():
    con = sqlite3.connect('cellframe.db')
    with con:
        cur = con.cursor()
        query = """ SELECT id FROM cellframe_data ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID to see how many validators we need to go through
        cur.execute(query)
        result = cur.fetchone()
        row_id, = result #how many node pages we need to create


        for x in range(1,row_id+1): #row_id):
            cur = con.cursor()
            query = """SELECT address FROM cellframe_data WHERE id=?"""
            cur.execute(query, [x])
            print("ROW ID in non_validators", row_id)
            node_address, = cur.fetchone()
            print("Node",node_address)
#            node = parse_node_address(node_address)
            print("NODE",node_address)
            create_individual_node_page(node_address)








def create_individual_node_page(node_address):
    filename = parse_node_address(node_address)
    filename3 = filename
    print(node_address)
    node_address2=node_address
    filename = "nodes/"+filename
    filename = filename+".html"
    print(filename)
    file2 = open(filename, "w")
    node_address = parse_node_address(node_address)
    con = sqlite3.connect('cellframe.db')
    with con:
        cur = con.cursor()

        query = """ SELECT ip,port,pinner,pkey, node_active_status, auto_update FROM {table} WHERE address=?""".format(table="cellframe_data")
        cur.execute(query,[node_address2])
        ip,port,pinner,pkey,node_active_status,auto_update = cur.fetchone()
        print("IP :",ip, type(ip))


        query = """ SELECT id,blocks,all_time_blocks FROM {table} ORDER BY id DESC LIMIT 1""".format(table=node_address)
        cur.execute(query)
        days, blocks,all_time_blocks, = cur.fetchone()

        query = """ SELECT first_block FROM {table} ORDER BY id ASC LIMIT 1""".format(table=node_address)
        cur.execute(query)
        first_block, = cur.fetchone()
        print("First block validated:",first_block, "blocks :",blocks)


        query = """ SELECT week_count, month_count, node_version,tx_hash FROM {table} WHERE id=1""".format(table=node_address)
        cur.execute(query)
        week, month, node_version,tx_hash = cur.fetchone()

        query = """ SELECT stake_value FROM {table} ORDER BY id DESC LIMIT 1""".format(
            table=node_address)
        cur.execute(query)
        stake_value, = cur.fetchone()

        query = """ SELECT weight FROM {table} ORDER BY id DESC LIMIT 1""".format(table=node_address)
        cur.execute(query)
        weight, = cur.fetchone()



        print("Node:",node_address,"all time blocks:", all_time_blocks, "blocks:",blocks," weekly:",week, "monthly",month)
        stake_value=(float(stake_value))*1000
        print("Staked amount", stake_value)
        print("Node active? :",node_active_status)


        file2.write(""" <!DOCTYPE html>\n""")
        file2.write(""" <html> \n""")
        file2.write(""" <head>\n""")
        file2.write(""" 	<meta charset="utf-8">\n""")
        file2.write(""" 	<meta name="viewport" content="width=device-width, initial-scale=1">\n""")
        file2.write(""" 	<meta name="generator" content="RocketCake">\n""")
        file2.write("""   <link rel="shortcut icon" type="image/x-icon" href="http://cellframestats.com/favicon.ico">	<title>Cellframe NODE</title>\n""")
        file2.write(""" 	<link rel="stylesheet" type="text/css" href="http://www.cellframestats.com/nodes/common_html.css">\n""")
        file2.write(""" </head>\n""")
        file2.write(""" <body>\n""")
        file2.write(""" <div class="textstyle1">\n""")
        file2.write(""" <div id="container_white_top"><div id="container_white_top_padding" ><div class="textstyle1">  <span class="textstyle2"><br/></span>\n""")
        file2.write(""" </div>\n""")
        file2.write(""" </div></div><div id="container_menubar"><div id="container_menubar_padding" ><div class="textstyle1">  <div id="menu_buttons">\n""")
        file2.write("""     <div  class="menuholder1"><a href="javascript:void(0);">\n""")
        file2.write(""" 	<div id="menuentry_64d8baf5"  class="menustyle1 menu_buttons_mainMenuEntry mobileEntry">\n""")
        file2.write(""" 		<div class="menuentry_text1">\n""")
        file2.write("""       <span class="textstyle3">Menu &#9660;</span>\n""")
        file2.write(""" 		</div>\n""")
        file2.write(""" 	</div>\n""")
        file2.write(""" </a>\n""")
        file2.write(""" <a href="../index.html" style="text-decoration:none">\n""")
        file2.write(""" 	<div id="menuentry_7b016bd8"  class="menustyle1 menu_buttons_mainMenuEntry normalEntry">\n""")
        file2.write(""" 		<div class="menuentry_text2">\n""")
        file2.write("""       <span class="textstyle4">Home</span>\n""")
        file2.write(""" 		</div>\n""")
        file2.write(""" 	</div>\n""")
        file2.write(""" </a>\n""")
        file2.write(""" <a href="../stats.html" style="text-decoration:none">\n""")
        file2.write(""" 	<div id="menuentry_2d828b8a"  class="menustyle2 menu_buttons_mainMenuEntry normalEntry">\n""")
        file2.write(""" 		<div class="menuentry_text2">\n""")
        file2.write("""       <span class="textstyle4">Stats</span>\n""")
        file2.write(""" 		</div>\n""")
        file2.write(""" 	</div>\n""")
        file2.write(""" </a>\n""")
        file2.write(""" <a href="../zerochain.html" style="text-decoration:none">\n""")
        file2.write(""" 	<div id="menuentry_746fb"  class="menustyle3 menu_buttons_mainMenuEntry normalEntry">\n""")
        file2.write(""" 		<div class="menuentry_text2">\n""")
        file2.write("""       <span class="textstyle4">Zerochain</span>\n""")
        file2.write(""" 		</div>\n""")
        file2.write(""" 	</div>\n""")
        file2.write(""" </a>\n""")
        file2.write(""" <a href="../nodes.html" style="text-decoration:none">\n""")
        file2.write(""" 	<div id="menuentry_7d6eadac"  class="menustyle4 menu_buttons_mainMenuEntry normalEntry">\n""")
        file2.write(""" 		<div class="menuentry_text2">\n""")
        file2.write("""       <span class="textstyle4">Nodes</span>\n""")
        file2.write(""" 		</div>\n""")
        file2.write(""" 	</div>\n""")
        file2.write(""" </a>\n""")
        file2.write(""" <a href="../richlist.html" style="text-decoration:none">\n""")
        file2.write(""" 	<div id="menuentry_8948010"  class="menustyle5 menu_buttons_mainMenuEntry normalEntry">\n""")
        file2.write(""" 		<div class="menuentry_text2">\n""")
        file2.write("""       <span class="textstyle4">Richlist</span>\n""")
        file2.write(""" 		</div>\n""")
        file2.write(""" 	</div>\n""")
        file2.write(""" </a>\n""")
        file2.write(""" <a href="../timeline.html" style="text-decoration:none">\n""")
        file2.write(""" 	<div id="menuentry_40741c7"  class="menustyle6 menu_buttons_mainMenuEntry normalEntry">\n""")
        file2.write(""" 		<div class="menuentry_text2">\n""")
        file2.write("""       <span class="textstyle4">Timeline</span>\n""")
        file2.write(""" 		</div>\n""")
        file2.write(""" 	</div>\n""")
        file2.write(""" </a>\n""")
        file2.write(""" \n""")
        file2.write(""" 	<script type="text/javascript" src="../rc_images/wsp_menu.js"></script>\n""")
        file2.write(""" 	<script type="text/javascript">\n""")
        file2.write(""" 		var js_menu_buttons= new wsp_menu('menu_buttons', 'menu_buttons', 10, null, true);\n""")
        file2.write(""" \n""")
        file2.write(""" 		js_menu_buttons.createMenuForItem('menuentry_64d8baf5', ["      <span class=\"textstyle5\">Home</span> ", 'index.html', '',\n""")
        file2.write(""" 		                                   "      <span class=\"textstyle5\">Stats</span> ", 'stats.html', '',\n""")
        file2.write(""" 		                                   "      <span class=\"textstyle5\">Zerochain</span> ", 'zerochain.html', '',\n""")
        file2.write(""" 		                                   "      <span class=\"textstyle5\">Nodes</span> ", 'nodes.html', '',\n""")
        file2.write(""" 		                                   "      <span class=\"textstyle5\">Richlist</span> ", 'richlist.html', '',\n""")
        file2.write(""" 		                                   "      <span class=\"textstyle5\">Timeline</span> ", 'timeline.html', '']);\n""")
        file2.write(""" 		js_menu_buttons.createMenuForItem('menuentry_7b016bd8', []);\n""")
        file2.write(""" 		js_menu_buttons.createMenuForItem('menuentry_2d828b8a', []);\n""")
        file2.write(""" 		js_menu_buttons.createMenuForItem('menuentry_746fb', []);\n""")
        file2.write(""" 		js_menu_buttons.createMenuForItem('menuentry_7d6eadac', []);\n""")
        file2.write(""" 		js_menu_buttons.createMenuForItem('menuentry_8948010', []);\n""")
        file2.write(""" 		js_menu_buttons.createMenuForItem('menuentry_40741c7', []);\n""")
        file2.write(""" \n""")
        file2.write(""" 	</script>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" </div>\n""")
        file2.write(""" <div style="clear:both"></div></div></div><div id="container_waves"><div id="container_waves_padding" ></div></div>""")

        # END OF MENU PART


        file2.write(""" <span class="textstyle6"><br/><br/></span><table id="table_45286c53" cellpadding="3" cellspacing="1" >	<tr>\n""")
        file2.write(""" 		<td width="33%" height="28px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_5db600f5">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle7">""")
        file2.write(node_address)
        file2.write("""</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="16%" height="28px" style="vertical-align: middle; overflow:hidden; background-color:""")

        if node_active_status == 1:
            file2.write("""#a6192e""")
        else:
            file2.write("""#008040""")

        file2.write("""; ">  <div id="cell_2c1b845">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle7">""")   #Active</span>\n""")
        if node_active_status == 1:
            file2.write("""Inactive""")
        else:
            file2.write("""Active""")


        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="24%" height="28px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_517e11b4">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle8">Staked amount</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="28px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_7dca7163">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle8"> """)
        file2.write(str(stake_value))
        file2.write(""" CELL</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" 	<tr>\n""")
        file2.write(""" 		<td width="33%" height="165px" rowspan="7" style="vertical-align: middle; overflow:hidden; ">\n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" <main><img decoding="async" id="random-image" src="" alt="Random image"></main>\n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" <script>\n""")
        file2.write(""" const imgEl = document.getElementById('random-image');\n""")
        file2.write(""" const srcArray = [\n""")
        file2.write(""" 'randomimage/randomimage1.png', \n""")
        file2.write(""" 'randomimage/randomimage2.png', \n""")
        file2.write(""" 'randomimage/randomimage3.png', \n""")
        file2.write(""" 'randomimage/randomimage4.png', \n""")
        file2.write(""" 'randomimage/randomimage5.png', \n""")
        file2.write(""" 'randomimage/randomimage6.png', \n""")
        file2.write(""" 'randomimage/randomimage7.png', \n""")
        file2.write(""" 'randomimage/randomimage8.png' \n""")
        file2.write(""" \n""")
        file2.write(""" ];\n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" let index;\n""")
        file2.write(""" randomImage();\n""")
        file2.write(""" function randomImage() {\n""")
        file2.write(""" const randomIndex = Math.floor(Math.random()*srcArray.length);\n""")
        file2.write(""" if (randomIndex !== index) {\n""")
        file2.write(""" imgEl.src = srcArray[randomIndex];\n""")
        file2.write(""" index = randomIndex;\n""")
        file2.write(""" } else {\n""")
        file2.write(""" randomImage();\n""")
        file2.write(""" }}</script>\n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" \n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="16%" height="12px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="24%" height="12px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_423e072a">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">Node weight</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="12px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_50e330bf">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        file2.write(str(weight))
        file2.write("""%</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" \n""")
        file2.write(""" 		<td width="16%" height="14px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="24%" height="14px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_7a6892a9">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">Days online</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="14px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_219c7478">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        file2.write(str(days))
        file2.write("""</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" \n""")
        file2.write(""" 		<td width="16%" height="28px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="24%" height="28px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_1f0f9a1a">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">First block signed</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="28px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_54d0cbe2">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        file2.write(str(first_block))
        file2.write("""</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" \n""")
        file2.write(""" 		<td width="25%" height="28px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="28px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_5bd5f3a7">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">Auto updating</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="28px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_6f37d553">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        if auto_update==0:
            file2.write("""TRUE""")
        else:
            file2.write("""False""")
        file2.write("""</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" \n""")
        file2.write(""" 		<td width="25%" height="14px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="14px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_f78176a">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">Tax %</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="14px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_6b6ccfbc">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        #file2.write() TAX IN HERE
        file2.write("""0.0%</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" \n""")
        file2.write(""" 		<td width="25%" height="14px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="14px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="14px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" \n""")
        file2.write(""" 		<td width="25%" height="13px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="13px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="25%" height="13px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" </table><span class="textstyle6"><br/></span><span class="textstyle9"><br/></span><span class="textstyle6">pkey hash : """)
        file2.write(str(pkey))
        file2.write("""<br/><br/>Stake tx : """)
        file2.write(str(tx_hash))
        file2.write("""<br/><br/></span><table id="table_75086607" cellpadding="3" cellspacing="1" >	<tr>\n""")
        file2.write(""" 		<td width="33%" height="22px" colspan="3" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_3b86ec59">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle8">Total blocks 1st signed by this node</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" 	<tr>\n""")
        file2.write(""" 		<td width="33%" height="18px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_54adee20">\n""")
        file2.write("""     <div class="textstyle10">\n""")
        file2.write("""       <span class="textstyle6">Today</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="17%" height="18px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_4458f57e">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        file2.write(str(blocks))
        file2.write("""</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="48%" height="18px" style="vertical-align: top; overflow:hidden; ">  <div id="cell_5b808294">\n""")
        file2.write("""     <div class="textstyle11">\n""")
        file2.write("""       <span class="textstyle6">blocks</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" 	<tr>\n""")
        file2.write(""" 		<td width="33%" height="18px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_174428cf">\n""")
        file2.write("""     <div class="textstyle10">\n""")
        file2.write("""       <span class="textstyle6">In 7 days</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="17%" height="18px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_b131709">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        file2.write(str(week))
        file2.write("""</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="48%" height="18px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" 	<tr>\n""")
        file2.write(""" 		<td width="33%" height="15px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_27239954">\n""")
        file2.write("""     <div class="textstyle10">\n""")
        file2.write("""       <span class="textstyle6">In 30 days</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="17%" height="15px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_7944c2d2">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        file2.write(str(month))
        file2.write("""</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="48%" height="15px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" 	<tr>\n""")
        file2.write(""" 		<td width="33%" height="28px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_6c5a1430">\n""")
        file2.write("""     <div class="textstyle10">\n""")
        file2.write("""       <span class="textstyle6">All time signatures</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="17%" height="28px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_10d7e9f6">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle6">""")
        file2.write(str(all_time_blocks))
        file2.write("""</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="48%" height="28px" >\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" 	<tr>\n""")
        file2.write(""" 		<td width="33%" height="42px" colspan="3" style="vertical-align: top; overflow:hidden; ">\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" </table><span class="textstyle9"><br/></span><table id="table_6a12a657" cellpadding="3" cellspacing="1" >	<tr>\n""")
        file2.write(""" 		<td width="33%" height="28px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_1cf05bdd">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle8">Node weight over the last 60 days</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="33%" height="28px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_7d92a935">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle8">Validated blocks / 30 days</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 		<td width="33%" height="28px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_736a7d">\n""")
        file2.write("""     <div class="textstyle1">\n""")
        file2.write("""       <span class="textstyle8">Cumulative block validations</span>\n""")
        file2.write("""       </div>\n""")
        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" 	<tr>\n""")
        file2.write(""" 		<td width="33%" height="183px" colspan="3" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_4e60c97e">\n""")
        file2.write("""     <div class="textstyle11">\n""")
        file2.write(""" <div id="gallery_735d33b0">\n""")
        file2.write(""" 	<script type="text/javascript" src="wsp_gallery.js"></script>\n""")
        #original line below
        #file2.write(""" <div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('charts/n5c72d63b6ae5618eweight.png',693,342,true, 'gallery_735d33b0');"><img src="charts/n5c72d63b6ae5618eweight.png" id="gallery_735d33b0_img1" width="640" height="360" /> </a></div><div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('charts/n5c72d63b6ae5618eblocks10.png',850,408,true, 'gallery_735d33b0');"><img src="charts/n5c72d63b6ae5618eblocks10.png" id="gallery_735d33b0_img2" width="640" height="360" /> </a></div><div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('charts/n5c72d63b6ae5618eblocks.png',693,342,true, 'gallery_735d33b0');"><img src="charts/n5c72d63b6ae5618eblocks.png" id="gallery_735d33b0_img3" width="640" height="360" /> </a></div></div>      </div>\n""")
        #
        # INDIVIDUAL NOES PAGE GALLERY AT THE BOTTOM
        #
        file2.write(""" <div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('charts/""")
        file2.write(str(filename3))
        file2.write("""weight.png',693,342,true, 'gallery_735d33b0');">""")
        file2.write("""<img src="charts/""")
        file2.write(str(filename3))
        file2.write("""weight.png" id="gallery_735d33b0_img1" width="640" height="360" /> </a></div><div class="galleryimgcontainer" >""")
        file2.write("""<a href="javascript:wsp_gallery.openlayer('charts/""")
        file2.write(str(filename3))
        file2.write("""blocks10.png',850,408,true, 'gallery_735d33b0');">""")
        file2.write("""<img src="charts/""")
        file2.write(str(filename3))
        file2.write("""blocks10.png" id="gallery_735d33b0_img2" width="640" height="360" /> </a></div><div class="galleryimgcontainer" >""")
        file2.write("""<a href="javascript:wsp_gallery.openlayer('charts/""")
        file2.write(str(filename3))
        file2.write("""blocks.png',693,342,true, 'gallery_735d33b0');">""")
        file2.write("""<img src="charts/""")
        file2.write(str(filename3))
        file2.write("""blocks.png" id="gallery_735d33b0_img3" width="640" height="360" /> </a></div></div>      </div>\n""")

        file2.write("""     </div>\n""")
        file2.write(""" 		</td>\n""")
        file2.write(""" 	</tr>\n""")
        file2.write(""" </table><span class="textstyle9"><br/></span>  </div>\n""")
        file2.write(""" </body>\n""")
        file2.write(""" </html>\n""")






        chart_block_validations(node_address)
        chart_daily_validations(node_address)
        chart_node_weight(node_address)

        file2.close()
