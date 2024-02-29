from cellframe_charting import *
from generate_nodes_html import *
#from generate_richlist import *
from generate_zerochain_html import *
from organize_wallets import *
from generate_html import *
from wallets_json import *

#######################################
#    Let's create some cool charts    #
#######################################

generate_alerts_json()
input("stop")



# ZEROCHAIN
chart_zerochain_events()
chart_cumulative_cell_emission()

#stats page charts
chart_daily_transactions()
chart_cumulative_blocks()
chart_daily_blocks()
chart_network_weight()

#richlist pie charts
top10_pie_chart_cell()
top10_pie_chart_mcell()
nodes_pie_chart()

#HTML GENERATORS
generate_timeline_page()
generate_node2_main_html()
generate_nodes_json()
generate_stats2_page()   #works
generate_zerochain2_page()      #MAKES JSON FILE NOW
create_all_node_pages() #works

#RICHLIST AND WALLET STUFF
move_wallets()
null_to_zero()
calculate_sums()

chart_activated_wallets()
create_wallets_json()
create_delegations_json()


#not in use anymore
#generate_richlist()