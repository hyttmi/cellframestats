import sqlite3

def parse_node_address(address):   ## removes :: from node address and returns clean version of it
    node_address=address.replace("::","")
    additional='N'
    node_address=additional+node_address # Add 'N' in font of node address as Qlite doesn't like tables which name begins with number
    return node_address

def create_connection(db_file): #make connection to the database and return con object or none.
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)
    return con


#
#       TIMELINE.HTML
#       STATS.HTML
#
#
#

def generate_alerts_json():
    file = open("alert_data.json", "w")
    database = r"alerts.db"
    con = create_connection(database)
    with ((con)):

        cur = con.cursor()
        query = """ SELECT id FROM alerts ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID
        cur.execute(query)
        row_id, = cur.fetchone()  # get number of alerts we have
        file.write("var esp_data = [\n")

        for x in range(1, row_id + 1):
               query = "SELECT date,type,text1,wallet1,wallet2,value,ticker,text2 FROM alerts WHERE id=?"
               cur.execute(query,[x])
               date,type,text1,wallet1,wallet2,value,ticker,text2 = cur.fetchone()
               file.write('{')
               file.write("\n")
               color = "#00a"

# types
# 0 = bridge
# 1 = staked
# 2 = delegation
# 10 = sent
# 40 = appeared in non-validators list
# 1000 = comment
               column1 = date
               column2 = color
               column3 = wallet1
               column4 = text1
               column5 = str(value)
               column6 = ticker
               column7 = text2
               column8 = wallet2


               if type == 0:
                  column2 = "#0a0"
                  column6 = str(value)
                  column7 = ticker

               if type == 1:
                  column2 = "#0a0"
                  column6 = str(value)
                  column7 = ticker
                  column5 = wallet2
                  column8 = text2

               if type == 2:
                  column2 = "#0a0"
                  column6 = str(value)
                  column7 = ticker
                  column5 = wallet2
                  column8 = text2

               if type == 10:
                  column2 = "#b00"
                  column5 = text2
                  column6 = str(value)
                  column7 = ticker

               if type == 1000 or type == 40:
                  column2 = "#00a"
                  column3 = wallet2
                  column5 = text2
                  column6 = ""
                  column7 = ""
                  column8 = text1


               file.write('"date": "')
               file.write(column1)
               file.write('",')
               file.write("\n")


               file.write('"type": "')
               file.write(column2)
               file.write('",')
               file.write("\n")


               file.write('"text1": "')
               file.write(column3)
               file.write('",')
               file.write("\n")


               file.write('"wallet1": "')
               file.write(column4)
               file.write('",')
               file.write("\n")


               file.write('"wallet2": "')
               file.write(column5)
               file.write('",')
               file.write("\n")


               file.write('"value": "')
               file.write(column6)
               file.write('",')
               file.write("\n")


               file.write('"ticker": "')
               file.write(column7)
               file.write('",')
               file.write("\n")


               file.write('"text2": "')
               file.write(column8)
               file.write('",')
               file.write("\n")


               file.write('},')
               file.write("\n")



        file.write("]")
        file.close()

        return

def generate_timeline_page():
    file = open("timeline.html", "w")
    database = r"cellframe.db"
    con = create_connection(database)
    with ((con)):
        file.write(""" <!DOCTYPE html>\n""")
        file.write(""" <html> \n""")
        file.write(""" <head>\n""")
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
        file.write("""   <title>Cellframe timeline</title>\n""")
        file.write(""" \n""")
        file.write("""   <style>\n""")
        file.write("""     body, html {\n""")
        file.write("""       font-family: arial;\n""")
        file.write("""       font-size: 11pt;\n""")
        file.write("""     }\n""")
        file.write("""     span {\n""")
        file.write("""       color: red;\n""")
        file.write("""     }\n""")
        file.write("""     span.large {\n""")
        file.write("""       font-size: 200%;\n""")
        file.write("""     }\n""")
        file.write(""" \n""")
        file.write("""     .vis-item.vis-background.negative {\n""")
        file.write("""       background-color: rgba(255, 0, 0, 0.2);\n""")
        file.write("""     }\n""")
        file.write(""" \n""")
        file.write("""     .vis-item.orange {\n""")
        file.write("""       background-color: gold;\n""")
        file.write("""       border-color: orange;\n""")
        file.write("""     }\n""")
        file.write(""" \n""")
        file.write("""     .vis-item.custom {\n""")
        file.write("""       background-color: #1FAE67;\n""")
        file.write("""       border-color: purple;\n""")
        file.write("""       color: white;\n""")
        file.write("""     }\n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" </style>\n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" 	<meta charset="utf-8">\n""")
        file.write(""" 	<meta name="viewport" content="width=device-width, initial-scale=1">\n""")
        file.write(""" 	<meta name="generator" content="RocketCake">\n""")
        file.write("""         <link rel="shortcut icon" type="image/x-icon" href="http://cellframestats.com/favicon.ico">	<title>Timeline</title>\n""")
        file.write(""" 	<link rel="stylesheet" type="text/css" href="css/timeline_html.css">\n""")
        file.write("""         <script src="js/vis-timeline-graph2d.min.js"></script>\n""")
        file.write("""         <link href="css/vis-timeline-graph2d.min.css" rel="stylesheet" type="text/css" />\n""")
        file.write(""" </head>\n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" <body>\n""")
        file.write(""" <div class="textstyle1">\n""")
        file.write(""" <div id="container_white_top"><div id="container_white_top_padding" ><div class="textstyle1">  <span class="textstyle2"><br/></span>\n""")
        file.write(""" </div>\n""")
        file.write(""" </div></div><div id="container_menubar"><div id="container_menubar_padding" ><div class="textstyle1">  <div id="menu_buttons">\n""")
        file.write("""     <div  class="menuholder1"><a href="javascript:void(0);">\n""")
        file.write(""" 	<div id="menuentry_6779c72"  class="menustyle1 menu_buttons_mainMenuEntry mobileEntry">\n""")
        file.write(""" 		<div class="menuentry_text1">\n""")
        file.write("""       <span class="textstyle3">Menu &#9660;</span>\n""")
        file.write(""" 		</div>\n""")
        file.write(""" 	</div>\n""")
        file.write(""" </a>\n""")
        file.write(""" <a href="index.html" style="text-decoration:none">\n""")
        file.write(""" 	<div id="menuentry_5aa64af4"  class="menustyle1 menu_buttons_mainMenuEntry normalEntry">\n""")
        file.write(""" 		<div class="menuentry_text2">\n""")
        file.write("""       <span class="textstyle4">Home</span>\n""")
        file.write(""" 		</div>\n""")
        file.write(""" 	</div>\n""")
        file.write(""" </a>\n""")
        file.write(""" <a href="stats.html" style="text-decoration:none">\n""")
        file.write(""" 	<div id="menuentry_7dd98ee0"  class="menustyle2 menu_buttons_mainMenuEntry normalEntry">\n""")
        file.write(""" 		<div class="menuentry_text2">\n""")
        file.write("""       <span class="textstyle4">Stats</span>\n""")
        file.write(""" 		</div>\n""")
        file.write(""" 	</div>\n""")
        file.write(""" </a>\n""")
        file.write(""" <a href="zerochain.html" style="text-decoration:none">\n""")
        file.write(""" 	<div id="menuentry_23dd7d16"  class="menustyle3 menu_buttons_mainMenuEntry normalEntry">\n""")
        file.write(""" 		<div class="menuentry_text2">\n""")
        file.write("""       <span class="textstyle4">Zerochain</span>\n""")
        file.write(""" 		</div>\n""")
        file.write(""" 	</div>\n""")
        file.write(""" </a>\n""")
        file.write(""" <a href="nodes.html" style="text-decoration:none">\n""")
        file.write(""" 	<div id="menuentry_15070e93"  class="menustyle4 menu_buttons_mainMenuEntry normalEntry">\n""")
        file.write(""" 		<div class="menuentry_text2">\n""")
        file.write("""       <span class="textstyle4">Nodes</span>\n""")
        file.write(""" 		</div>\n""")
        file.write(""" 	</div>\n""")
        file.write(""" </a>\n""")
        file.write(""" <a href="richlist.html" style="text-decoration:none">\n""")
        file.write(""" 	<div id="menuentry_5687a04e"  class="menustyle5 menu_buttons_mainMenuEntry normalEntry">\n""")
        file.write(""" 		<div class="menuentry_text2">\n""")
        file.write("""       <span class="textstyle4">Richlist</span>\n""")
        file.write(""" 		</div>\n""")
        file.write(""" 	</div>\n""")
        file.write(""" </a>\n""")
        file.write(""" <a href="javascript:void(0);">\n""")
        file.write(""" 	<div id="menuentry_2baa17b4"  class="menustyle6 menu_buttons_mainMenuEntry normalEntry">\n""")
        file.write(""" 		<div class="menuentry_text2">\n""")
        file.write("""       <span class="textstyle4">Timeline</span>\n""")
        file.write(""" 		</div>\n""")
        file.write(""" 	</div>\n""")
        file.write(""" </a>\n""")
        file.write(""" \n""")
        file.write(""" 	<script type="text/javascript" src="rc_images/wsp_menu.js"></script>\n""")
        file.write(""" 	<script type="text/javascript">\n""")
        file.write(""" 		var js_menu_buttons= new wsp_menu('menu_buttons', 'menu_buttons', 10, null, true);\n""")
        file.write(""" \n""")
        file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_6779c72', ["      <span class=\"textstyle5\">Home</span> ", 'index.html', '',\n""")
        file.write(""" 		                                   "      <span class=\"textstyle5\">Stats</span> ", 'stats.html', '',\n""")
        file.write(""" 		                                   "      <span class=\"textstyle5\">Zerochain</span> ", 'zerochain.html', '',\n""")
        file.write(""" 		                                   "      <span class=\"textstyle5\">Nodes</span> ", 'nodes.html', '',\n""")
        file.write(""" 		                                   "      <span class=\"textstyle5\">Richlist</span> ", 'richlist.html', '',\n""")
        file.write(""" 		                                   "      <span class=\"textstyle5\">Timeline</span> ", 'javascript:void(0);', '']);\n""")
        file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_5aa64af4', []);\n""")
        file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_7dd98ee0', []);\n""")
        file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_23dd7d16', []);\n""")
        file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_15070e93', []);\n""")
        file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_5687a04e', []);\n""")
        file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_2baa17b4', []);\n""")
        file.write(""" \n""")
        file.write(""" 	</script>\n""")
        file.write("""       </div>\n""")
        file.write("""     </div>\n""")
        file.write(""" </div>\n""")
        file.write(""" \n""")
        file.write(""" <div style="clear:both"></div></div></div><div id="container_waves"><div id="container_waves_padding" ></div></div><span class="textstyle6"><br/></span>  </div>\n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" <div id="visualization"></div>\n""")
        file.write(""" \n""")
        file.write(""" <script>\n""")
        file.write("""   // create a couple of HTML items in various ways\n""")
        file.write(""" \n""")
        file.write("""   var item0 = document.createElement('div');\n""")
        file.write("""   item0.appendChild(document.createTextNode('item 1'));\n""")
        file.write(""" \n""")
        file.write("""   var item2 = document.createElement('div');\n""")
        file.write("""   item2.innerHTML = '<span>Zerochain genesis block</span>';\n""")
        file.write(""" \n""")
        file.write("""   var item1 = document.createElement('div');\n""")
        file.write("""   item1.innerHTML = '<span>Backbone genesis block</span>';\n""")
        file.write(""" \n""")

        cur = con.cursor()
        query = """ SELECT id FROM cellframe_data ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID
        cur.execute(query)
        row_id, = cur.fetchone()  # get number of nodes
        for x in range(1, row_id + 1):

            cur = con.cursor()
            query = """ SELECT address FROM cellframe_data WHERE id=?""".format()  ##GET THE BIGGEST ROW ID
            cur.execute(query, [x])
            correct_address, = cur.fetchone()  # get number of nodes
            #address = parse_node_address(correct_address)
            print(correct_address)
            #query = """ SELECT first_block FROM {table} ORDER BY id ASC LIMIT 1""".format(
            #    table=address)  ##GET THE BIGGEST ROW ID
            #cur.execute(query)
            #date, = cur.fetchone()  # get number of nodes
            #print(date)

            file.write("""   var item""")
            file.write(str(x))
            file.write(""" = '""")
            file.write(correct_address)
            file.write("""<br><img src="rc_images/server.png" style="width: 48px; height: 48px;">';\n""")


        file.write(""" \n""")
        #file.write("""   var item7 = 'item7<br><a href="https://visjs.org" target="_blank">click here</a>';\n""")
        file.write(""" \n""")
        file.write("""   // create data and a Timeline\n""")
        file.write("""   var container = document.getElementById('visualization');\n""")
        file.write("""   var items = new vis.DataSet([\n""")
        file.write("""     {id: 'A', content: 'Testnet', start: '2022-04-06', end: '2023-07-11', type: 'background'},\n""")
        file.write("""     {id: 'B', content: 'Mainnet launch', start: '2023-07-12', end: '2023-10-30', type: 'background', className: 'negative'},\n""")


        cur = con.cursor()
        query = """ SELECT id,address FROM cellframe_data ORDER BY id DESC LIMIT 1""".format()  ##GET THE BIGGEST ROW ID
        cur.execute(query)
        row_id, correct_address, = cur.fetchone() #get number of nodes

        for x in range(1,row_id+1):
                cur = con.cursor()
                query = """ SELECT address FROM cellframe_data WHERE id=?""".format()  ##GET THE BIGGEST ROW ID
                cur.execute(query,[x])
                correct_address, = cur.fetchone()  # get number of nodes
                address = parse_node_address(correct_address)
                print(address)
                query = """ SELECT first_block FROM {table} ORDER BY id ASC LIMIT 1""".format(table=address)  ##GET THE BIGGEST ROW ID
                cur.execute(query)
                date, = cur.fetchone()  # get number of nodes
                print(date)

                date = date.split(".");
                print(date)
                day = date[0]
                month = date[1]
                year = date[2]
                new_date = str(year) + "." + str(month) + "." + str(day)

                file.write("""     {id: """)
                file.write(str(x))
                file.write(""", content: item""")
                file.write(str(x))
                file.write(""", start: '""")
                file.write(str(new_date))
                file.write("""','className': 'orange'},\n""")

        file.write("""   ]);\n""")
        #file.write("""   var options = {orientation: {axis: "both"},start: "6.1.2023"}""")
        #file.write("""   var options = {start: "6.6.2023"}""")
        file.write(""" var options = { """)
        file.write("""  orientation: {axis: 'both'},""")
        file.write("""  height: '600px',""")
        file.write("""  width: '100%',""")
        file.write("""  start: '06.01.2023',""")
        file.write("""  max: '12.31.2030',""")
        file.write("""  min: '01.01.2022'""")
        #file.write("""   {start: "06.01.2023"}""")
        file.write("""};\n""")
        file.write("""   var timeline = new vis.Timeline(container, items, options);\n""")
        file.write(""" </script>\n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" \n""")
        file.write(""" </body>\n""")
        file.write(""" </html>\n""")
        file.close()



    return

def generate_stats2_page():
    file = open("stats.html", "w")
    database = r"cellframe.db"


    con = create_connection(database)
    cur = con.cursor()
    query = """SELECT current_day, hash_line_counter, block_reward FROM flags WHERE id=0"""
    cur.execute(query)
    day, hash_line_counter, block_reward = cur.fetchone()
    con.close()
    print(day)


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
    file.write(""" 	<meta charset="utf-8"> \n""")
    file.write(""" 	<meta name="viewport" content="width=device-width, initial-scale=1"> \n""")
    file.write(""" 	<meta name="generator" content="RocketCake"> \n""")
    file.write("""   <link rel="shortcut icon" type="image/x-icon" href="http://cellframestats.com/favicon.ico">	<title>Cellframe Statistics</title> \n""")
    file.write(""" 	<link rel="stylesheet" type="text/css" href="css/stats_html.css"> \n""")
    file.write("""         <link  rel="stylesheet" href="css/tabulator2.min.css"> \n""")
    file.write("""         <script type="text/javascript" src="js/tabulator.min.js"></script> \n""")
    file.write("""         <script type="text/javascript" src="delegations_data.json"></script> \n""")
    file.write(""" </head> \n""")
    file.write(""" <body> \n""")
    file.write(""" <div class="textstyle1"> \n""")
    file.write(""" <div id="container_white_top"><div id="container_white_top_padding" ><div class="textstyle1">  <span class="textstyle2"><br/></span> \n""")
    file.write(""" </div> \n""")
    file.write(""" </div></div><div id="container_menubar"><div id="container_menubar_padding" ><div class="textstyle1">  <div id="menu_buttons"> \n""")
    file.write("""     <div  class="menuholder1"><a href="javascript:void(0);"> \n""")
    file.write(""" 	<div id="menuentry_74966c12"  class="menustyle1 menu_buttons_mainMenuEntry mobileEntry"> \n""")
    file.write(""" 		<div class="menuentry_text1"> \n""")
    file.write("""       <span class="textstyle3">Menu &#9660;</span> \n""")
    file.write(""" 		</div> \n""")
    file.write(""" 	</div> \n""")
    file.write(""" </a> \n""")
    file.write(""" <a href="index.html" style="text-decoration:none">\n """)
    file.write(""" 	<div id="menuentry_586c6f3e"  class="menustyle1 menu_buttons_mainMenuEntry normalEntry"> \n""")
    file.write(""" 		<div class="menuentry_text2"> \n""")
    file.write("""       <span class="textstyle4">Home</span> \n""")
    file.write(""" 		</div> \n""")
    file.write(""" 	</div> \n""")
    file.write(""" </a> \n""")
    file.write(""" <a href="javascript:void(0);"> \n""")
    file.write(""" 	<div id="menuentry_373652be"  class="menustyle2 menu_buttons_mainMenuEntry normalEntry"> \n""")
    file.write(""" 		<div class="menuentry_text2"> \n""")
    file.write("""       <span class="textstyle4">Stats</span> \n""")
    file.write(""" 		</div> \n""")
    file.write(""" 	</div> \n""")
    file.write(""" </a> \n""")
    file.write(""" <a href="zerochain.html" style="text-decoration:none"> \n""")
    file.write(""" 	<div id="menuentry_1461f761"  class="menustyle3 menu_buttons_mainMenuEntry normalEntry"> \n""")
    file.write(""" 		<div class="menuentry_text2"> \n""")
    file.write("""       <span class="textstyle4">Zerochain</span> \n""")
    file.write(""" 		</div> \n""")
    file.write(""" 	</div> \n""")
    file.write(""" </a> \n""")
    file.write(""" <a href="nodes.html" style="text-decoration:none"> \n""")
    file.write(""" 	<div id="menuentry_36092453"  class="menustyle4 menu_buttons_mainMenuEntry normalEntry"> \n""")
    file.write(""" 		<div class="menuentry_text2"> \n""")
    file.write("""       <span class="textstyle4">Nodes</span> \n""")
    file.write(""" 		</div> \n""")
    file.write(""" 	</div> \n""")
    file.write(""" </a> \n""")
    file.write(""" <a href="richlist.html" style="text-decoration:none"> \n""")
    file.write(""" 	<div id="menuentry_598a7e43"  class="menustyle5 menu_buttons_mainMenuEntry normalEntry"> \n""")
    file.write(""" 		<div class="menuentry_text2"> \n""")
    file.write("""       <span class="textstyle4">Richlist</span> \n""")
    file.write(""" 		</div> \n""")
    file.write(""" 	</div> \n""")
    file.write(""" </a> \n""")
    file.write(""" <a href="timeline.html" style="text-decoration:none"> \n""")
    file.write(""" 	<div id="menuentry_7833a8d7"  class="menustyle6 menu_buttons_mainMenuEntry normalEntry"> \n""")
    file.write(""" 		<div class="menuentry_text2"> \n""")
    file.write("""       <span class="textstyle4">Timeline</span> \n""")
    file.write(""" 		</div>\n """)
    file.write(""" 	</div> \n""")
    file.write(""" </a> \n""")
    file.write("""  \n""")
    file.write(""" 	<script type="text/javascript" src="rc_images/wsp_menu.js"></script> \n""")
    file.write(""" 	<script type="text/javascript"> \n""")
    file.write(""" 		var js_menu_buttons= new wsp_menu('menu_buttons', 'menu_buttons', 10, null, true); \n""")
    file.write("""  \n""")
    file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_74966c12', ["      <span class=\"textstyle5\">Home</span> ", 'index.html', '', \n""")
    file.write(""" 		                                   "      <span class=\"textstyle5\">Stats</span> ", 'javascript:void(0);', '', \n""")
    file.write(""" 		                                   "      <span class=\"textstyle5\">Zerochain</span> ", 'zerochain.html', '', \n""")
    file.write(""" 		                                   "      <span class=\"textstyle5\">Nodes</span> ", 'nodes.html', '', \n""")
    file.write(""" 		                                   "      <span class=\"textstyle5\">Richlist</span> ", 'richlist.html', '', \n""")
    file.write(""" 		                                   "      <span class=\"textstyle5\">Timeline</span> ", 'timeline.html', '']); \n""")
    file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_586c6f3e', []);\n """)
    file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_373652be', []);\n """)
    file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_1461f761', []); \n""")
    file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_36092453', []); \n""")
    file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_598a7e43', []); \n""")
    file.write(""" 		js_menu_buttons.createMenuForItem('menuentry_7833a8d7', []); \n""")
    file.write(""" \n """)
    file.write(""" 	</script> \n""")
    file.write("""       </div>\n """)
    file.write("""     </div>\n """)
    file.write(""" </div> \n""")
    file.write(""" \n """)
    file.write(""" <div style="clear:both"></div>\n """)
    file.write(""" </div> \n""")
    file.write("""  \n""")
    file.write("""   <div id="container_waves"> \n""")
    file.write("""     <div id="container_waves_padding" ></div>\n """)
    file.write("""   </div> \n""")
    file.write("""  \n""")
    file.write(""" <span class="textstyle6"><br/></span>  </div>\n """)
    file.write("""  \n""")
    file.write("""  \n""")
    file.write("""  \n""")
    file.write(""" <span class="textstyle7"></span></br></br></br><table id="table_5e4cdda2" cellpadding="3" cellspacing="1" >	<tr> \n""")
    file.write(""" 		<td width="36%" height="12px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_527f20b2"> \n""")
    file.write("""     <div class="textstyle1"> \n""")
    file.write("""       <span class="textstyle8">Block reward</span> \n""")
    file.write("""       </div> \n""")
    file.write("""     </div> \n""")
    file.write(""" 		</td>\n """)
    file.write(""" 		<td width="25%" height="12px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_11306332"> \n""")
    file.write("""     <div class="textstyle1"> \n""")
    file.write("""       <span class="textstyle8">Block height</span> \n""")
    file.write("""       </div> \n""")
    file.write("""     </div> \n""")
    file.write(""" 		</td> \n""")
    file.write(""" 		<td width="37%" height="12px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_35785fb2"> \n""")
    file.write("""     <div class="textstyle1"> \n""")
    file.write("""       <span class="textstyle8">Reserved</span> \n""")
    file.write("""       </div> \n""")
    file.write("""     </div> \n""")
    file.write(""" 		</td> \n""")
    file.write(""" 	</tr> \n""")
    file.write(""" 	<tr> \n""")
    file.write(""" 		<td width="36%" height="22px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_2467d57c"> \n""")
    file.write("""     <div class="textstyle1"> \n""")
    file.write("""       <span class="textstyle6">""")
    file.write(str(block_reward))
    file.write("""</span> \n""")
    file.write("""       </div> \n""")
    file.write("""     </div> \n""")
    file.write(""" 		</td> \n""")
    file.write(""" 		<td width="25%" height="22px" style="vertical-align: middle; overflow:hidden; ">  <div id="cell_6c4bae7a"> \n""")
    file.write("""     <div class="textstyle1"> \n""")
    file.write("""       <span class="textstyle6">""")
    file.write(str(hash_line_counter))
    file.write("""</span>\n """)
    file.write("""       </div> \n""")
    file.write("""     </div> \n""")
    file.write(""" 		</td>\n """)
    file.write(""" 		<td width="37%" height="22px" > \n""")
    file.write(""" 		</td> \n""")
    file.write(""" 	</tr> \n""")
    file.write(""" </table><span class="textstyle7"><br/><br/></span><div id="container_delegations"><div id="container_delegations_padding" > \n""")
    file.write("""  \n""")
    file.write(""" <div class ='container'>  \n""")
    file.write("""         <div id = "example-table"></div>  \n""")
    file.write("""         <!------------------------------------------------------------------->  \n""")
    file.write("""         <script type = "text/javascript">  \n""")
    file.write("""         var local_data = esp_data; <!-- name inside json file --> \n""")
    file.write("""          var table = new Tabulator("#example-table", {  \n""")
    file.write("""             data: local_data,  \n""")
    file.write("""             pagination: "local",  \n""")
    file.write("""             paginationSize: 10, \n""")
    file.write("""              layout: "fitDataFill", \n""")
    file.write("""                    // layout: "fitColumns",  \n""")
    file.write("""         placeholder: "No Data Available", \n""")
    file.write("""          columns: [ \n """)
    file.write("""             {title: "id", field: "id", align: "center", width: 60}, \n""")
    file.write("""              {title: "Date", field: "date", width: 140}, \n""")
    file.write("""              {title: "Delegator wallet", field: "wallet", width: 230, clickPopup:"Wallet address where this delegation came from."},  \n""")
    file.write("""             {title: "mCELL delegated", field: "value", width: 150},\n """)
    file.write("""              {title: "to node", field: "node", sorter: "number", width: 200, clickPopup:"Node address which received this delegation."}, \n""")
    file.write("""   ], \n""")
    file.write("""          });  \n""")
    file.write("""         </script> \n""")
    file.write("""          <!---------------------------rc_images/rwb_1.jpg-------------------------------------------->  \n""")
    file.write("""         </div> \n""")
    file.write("""  \n""")
    file.write("""  \n""")
    file.write("""  \n""")
    file.write("""  \n""")
    file.write("""  \n""")
    file.write("""  \n""")
    file.write("""  \n""")
    file.write(""" </div></div><span class="textstyle7"><br/><br/><br/> \n""")
    file.write(""" </span><table id="table_5aae4bdf" cellpadding="3" cellspacing="1" >	<tr> \n""")
    file.write(""" 		<td width="100%" height="22px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_1617a48">\n """)
    file.write("""     <div class="textstyle1"> \n""")
    file.write("""       <span class="textstyle8">Backbone charts</span> \n""")
    file.write("""       </div> \n""")
    file.write("""     </div> \n""")
    file.write(""" 		</td> \n""")
    file.write(""" 	</tr>\n """)
    file.write(""" </table><span class="textstyle7"><br/></span><div id="gallery_225eae90"> \n""")
    file.write(""" 	<script type="text/javascript" src="rc_images/wsp_gallery.js"></script> \n""")
    file.write(""" <div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('stats_charts/dailyblocks.png',869,372,true, 'gallery_225eae90');"><img src="stats_charts/dailyblocks.png" id="gallery_225eae90_img1" width="869" height="372" /> </a></div><div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('stats_charts/transactions.png',1043,412,true, 'gallery_225eae90');"><img src="stats_charts/transactions.png" id="gallery_225eae90_img2" width="960" height="379" /> </a></div><div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('stats_charts/network_weight365.png',1043,412,true, 'gallery_225eae90');"><img src="stats_charts/network_weight365.png" id="gallery_225eae90_img3" width="960" height="379" /> </a></div><div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('stats_charts/cumulative_blocks.png',1043,412,true, 'gallery_225eae90');"><img src="stats_charts/cumulative_blocks.png" id="gallery_225eae90_img4" width="960" height="379" /> </a></div></div><span class="textstyle7"><br/><br/><br/></span><table id="table_1281ecf4" cellpadding="3" cellspacing="1" >	<tr> \n""")
    file.write(""" 		<td width="100%" height="22px" style="vertical-align: middle; overflow:hidden; background-color:#04044D; ">  <div id="cell_542acab3"> \n""")
    file.write("""     <div class="textstyle1"> \n""")
    file.write("""       <span class="textstyle8">Zerochain charts</span> \n""")
    file.write("""       </div> \n""")
    file.write("""     </div> \n""")
    file.write(""" 		</td> \n""")
    file.write(""" 	</tr>\n """)
    file.write(""" </table><span class="textstyle7"><br/><br/></span><div id="gallery_793d4efd">\n """)
    file.write(""" 	<script type="text/javascript" src="rc_images/wsp_gallery.js"></script> \n""")
    file.write(""" <div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('stats_charts/zerochain_events.png',1043,412,true, 'gallery_793d4efd');"><img src="stats_charts/zerochain_events.png" id="gallery_793d4efd_img1" width="960" height="379" /> </a></div><div class="galleryimgcontainer" ><a href="javascript:wsp_gallery.openlayer('stats_charts/cumulative_cell_emission.png',1043,412,true, 'gallery_793d4efd');"><img src="stats_charts/cumulative_cell_emission.png" id="gallery_793d4efd_img2" width="960" height="379" /> </a></div></div><span class="textstyle7"><br/><br/></span>  </div> \n""")
    file.write(""" </body> \n""")
    file.write(""" </html> \n""")
    file.close()
    return





