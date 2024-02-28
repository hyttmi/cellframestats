import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker



def create_connection(db_file): #make connection to the database and return con object or none.
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)
    return con

def chart_activated_wallets(): #chart for stats
    database = r"cellframe.db"

    con = create_connection(database)
    with con:
        cur = con.cursor()

        query3 = """SELECT date, wallets FROM wallet_count ORDER BY id DESC LIMIT 60"""
        cur.execute(query3)
        results = cur.fetchall()

        dates = [result[0] for result in results]
        weight = [result[1] for result in results]

        dates.reverse()
        weight.reverse()

        plt.style.use('seaborn-ticks')

        fig, ax = plt.subplots(tight_layout=True, figsize=(15, 6))

        ax.set_ylabel('Total CF20 wallets')

        ax.plot(weight, lw=1, color='maroon')

        # helper function for the formatter
        def listifed_formatter(x, pos=None):
            try:
                return dates[int(x)]
            except IndexError:
                return ''

        # make and use the formatter
        mt = mticker.FuncFormatter(listifed_formatter)
        ax.xaxis.set_major_formatter(mt)

        # set the default ticker to only put ticks on the integers
        loc = ax.xaxis.get_major_locator()
        loc.set_params(integer=True)
        # rotate the labels
        [lab.set_rotation(30) for lab in ax.get_xticklabels()]

        plt.title('Total wallets in CF20 / 60 days')
        plt.ylabel('# of wallets')
        # plt.xticks([0, 5, 10, 15, 20, 25])
        plt.grid(True)
        plt.savefig('stats_charts/total_wallets.png',format="png",dpi=70,bbox_inches="tight")             # DAILY BLOCKS / 30 DAYS
        #plt.show()

        plt.close()
        return



def chart_network_weight(): #chart for stats
    database = r"cellframe.db"
#    print(plt.style.available)
    con = create_connection(database)
    with con:
        cur = con.cursor()

        query3 = """SELECT date, network_weight FROM transactions ORDER BY id DESC LIMIT 365"""
        cur.execute(query3)
        results = cur.fetchall()

        dates = [result[0] for result in results]
        weight = [result[1] for result in results]

        dates.reverse()
        weight.reverse()

        plt.style.use('seaborn-ticks')

        fig, ax = plt.subplots(tight_layout=True, figsize=(15, 6))

        ax.set_ylabel('Network weight')

        ax.plot(weight, lw=1, color='maroon')

        # helper function for the formatter
        def listifed_formatter(x, pos=None):
            try:
                return dates[int(x)]
            except IndexError:
                return ''

        # make and use the formatter
        mt = mticker.FuncFormatter(listifed_formatter)
        ax.xaxis.set_major_formatter(mt)

        # set the default ticker to only put ticks on the integers
        loc = ax.xaxis.get_major_locator()
        loc.set_params(integer=True)
        # rotate the labels
        [lab.set_rotation(30) for lab in ax.get_xticklabels()]

        plt.title('Network total weight / 365 days')
        plt.ylabel('Network weight')
        # plt.xticks([0, 5, 10, 15, 20, 25])
        plt.grid(True)
        plt.savefig('stats_charts/network_weight365.png',format="png",dpi=70,bbox_inches="tight")             # DAILY BLOCKS / 30 DAYS
        #plt.show()

        plt.close()
        return


def chart_cumulative_blocks(): #chart for stats
    database = r"cellframe.db"

    con = create_connection(database)
    with con:
        cur = con.cursor()
        query2 = """SELECT date, cumulative_transactions FROM transactions ORDER BY id DESC LIMIT 365"""
        cur.execute(query2)
        results = cur.fetchall()

        dates = [result[0] for result in results]
        total_blocks = [result[1] for result in results]
        dates.reverse()
        total_blocks.reverse()
        plt.style.use('seaborn-ticks')

        fig, ax = plt.subplots(tight_layout=True, figsize=(15, 6))

        ax.set_ylabel('Blocks')

        ax.plot(total_blocks, lw=1, color='maroon')

        # helper function for the formatter
        def listifed_formatter(x, pos=None):
            try:
                return dates[int(x)]
            except IndexError:
                return ''

        # make and use the formatter
        mt = mticker.FuncFormatter(listifed_formatter)
        ax.xaxis.set_major_formatter(mt)

        # set the default ticker to only put ticks on the integers
        loc = ax.xaxis.get_major_locator()
        loc.set_params(integer=True)
        # rotate the labels
        [lab.set_rotation(30) for lab in ax.get_xticklabels()]

    #    plt.figure(figsize=(15, 6))
        # plt.plot(transactions,linewidth=1,color="maroon")
        plt.plot(total_blocks, linewidth=0.3, color="maroon")
        plt.title('Network cumulative blocks / 356 days')
        plt.ylabel('Blocks')
        plt.grid(True)

        plt.savefig('stats_charts/cumulative_blocks.png', format="png", dpi=70,bbox_inches="tight")  # CUMULATIVE BLOCKS / 365 DAYS
        #plt.show()
        plt.close()
        return

def chart_daily_blocks(): #chart for stats
    database = r"cellframe.db"

    con = create_connection(database)
    with con:
        cur = con.cursor()
        query2 = """SELECT date, daily_transactions FROM transactions ORDER BY id DESC LIMIT 30"""
        cur.execute(query2)
        results = cur.fetchall()
        dates = [result[0] for result in results]
        transactions = [result[1] for result in results]
        dates.reverse()
        transactions.reverse()
        plt.style.use('seaborn-ticks')

        plt.figure(figsize=(15, 6))
        # plt.plot(transactions,linewidth=1,color="maroon")
        plt.bar(dates, transactions, width=0.3, color="maroon")
        plt.title('Daily blocks / 30 days')
        plt.ylabel('Blocks')
        plt.xticks([0, 5, 10, 15, 20, 25])
        plt.grid(True)
        plt.savefig('stats_charts/dailyblocks.png',format="png",dpi=70,bbox_inches="tight")             # DAILY BLOCKS / 30 DAYS
        #print(transactions)
        #plt.show()

        plt.close()
        return


def top10_pie_chart_cell():
    database = r"cellframe.db"
    con = create_connection(database)
    cur = con.cursor()
    with con:
        query = """ SELECT cell_balance FROM {table} ORDER BY cell_balance DESC LIMIT 30""".format(
            table="wallet_data_organized")
        cur.execute(query)
        total_mcell = cur.fetchall()
   #     print(total_mcell[1])
        sum0 = float('.'.join(str(ele) for ele in total_mcell[0]))
        sum1 = float('.'.join(str(ele) for ele in total_mcell[1]))
        sum2 = float('.'.join(str(ele) for ele in total_mcell[2]))
        sum3 = float('.'.join(str(ele) for ele in total_mcell[3]))
        sum4 = float('.'.join(str(ele) for ele in total_mcell[4]))
        sum5 = float('.'.join(str(ele) for ele in total_mcell[5]))
        sum6 = float('.'.join(str(ele) for ele in total_mcell[6]))
        sum7 = float('.'.join(str(ele) for ele in total_mcell[7]))
        sum8 = float('.'.join(str(ele) for ele in total_mcell[8]))
        sum9 = float('.'.join(str(ele) for ele in total_mcell[9]))
        grand_total10 = float(sum0) + float(sum1) + float(sum2) + float(sum3) + float(sum4) + float(sum5) + float(
            sum6) + float(sum7) + float(sum8) + float(sum9)
        print(grand_total10)

        sum0 = float('.'.join(str(ele) for ele in total_mcell[10]))
        sum1 = float('.'.join(str(ele) for ele in total_mcell[11]))
        sum2 = float('.'.join(str(ele) for ele in total_mcell[12]))
        sum3 = float('.'.join(str(ele) for ele in total_mcell[13]))
        sum4 = float('.'.join(str(ele) for ele in total_mcell[14]))
        sum5 = float('.'.join(str(ele) for ele in total_mcell[15]))
        sum6 = float('.'.join(str(ele) for ele in total_mcell[16]))
        sum7 = float('.'.join(str(ele) for ele in total_mcell[17]))
        sum8 = float('.'.join(str(ele) for ele in total_mcell[18]))
        sum9 = float('.'.join(str(ele) for ele in total_mcell[19]))
        sum10 = float('.'.join(str(ele) for ele in total_mcell[20]))
        sum11 = float('.'.join(str(ele) for ele in total_mcell[21]))
        sum12 = float('.'.join(str(ele) for ele in total_mcell[22]))
        sum13 = float('.'.join(str(ele) for ele in total_mcell[23]))
        sum14 = float('.'.join(str(ele) for ele in total_mcell[24]))
        sum15 = float('.'.join(str(ele) for ele in total_mcell[25]))
        sum16 = float('.'.join(str(ele) for ele in total_mcell[26]))
        sum17 = float('.'.join(str(ele) for ele in total_mcell[27]))
        sum18 = float('.'.join(str(ele) for ele in total_mcell[28]))
        sum19 = float('.'.join(str(ele) for ele in total_mcell[29]))
        grand_total_a = float(sum0) + float(sum1) + float(sum2) + float(sum3) + float(sum4) + float(sum5) + float(
            sum6) + float(sum7) + float(sum8)
        grand_total_a = grand_total_a + float(sum9) + float(sum10) + float(sum11) + float(sum12) + float(sum13) + float(
            sum14)
        grand_total_20_30 = grand_total_a + float(sum15) + float(sum16) + float(sum17) + float(sum18) + float(sum19)
#        print(grand_total_20_30)

        query = """ SELECT cell_total FROM {table} """.format(table="balances_total")
        cur.execute(query)
        total_mcell, = cur.fetchone()

        ten_percentage = (grand_total10 / total_mcell) * 100
 #       print("10%", ten_percentage)
        twenty_percentage = (grand_total_20_30 / total_mcell) * 100
  #      print("20-30", twenty_percentage)
        y = np.array([100 - ten_percentage - twenty_percentage, ten_percentage, twenty_percentage])
        mylabels = ["rest of CELL wallets", "top 10 wallets", "20-30 wallets"]

        plt.pie(y, labels=mylabels, autopct='%1.1f%%')
        name = "stats_charts/10-20-30_wallets_cell.png"
        plt.savefig(name, format="png", dpi=70, bbox_inches="tight")
        plt.close()
        return


def chart_cumulative_cell_emission(): #chart for stats
    database = r"zerochain.db"

    con = create_connection(database)
    with con:
        cur = con.cursor()
        query2 = """SELECT current_day,cumulative_cell_emission FROM flags ORDER BY id DESC LIMIT 365"""
        cur.execute(query2)
        results = cur.fetchall()

        dates = [result[0] for result in results]
        daily_events = [result[1] for result in results]
        dates.reverse()
        daily_events.reverse()
        plt.style.use('seaborn-ticks')

        fig, ax = plt.subplots(tight_layout=True, figsize=(15, 6))

        ax.set_ylabel('Events')

        ax.plot(daily_events, lw=1, color='maroon')

        # helper function for the formatter
        def listifed_formatter(x, pos=None):
            try:
                return dates[int(x)]
            except IndexError:
                return ''

        # make and use the formatter
        mt = mticker.FuncFormatter(listifed_formatter)
        ax.xaxis.set_major_formatter(mt)

        # set the default ticker to only put ticks on the integers
        loc = ax.xaxis.get_major_locator()
        loc.set_params(integer=True)
        # rotate the labels
        [lab.set_rotation(30) for lab in ax.get_xticklabels()]

    #    plt.figure(figsize=(15, 6))
        # plt.plot(transactions,linewidth=1,color="maroon")
        plt.plot(daily_events, linewidth=0.3, color="maroon")
        plt.title('Cumulative CELL emissions from Zerochain / 356 days')
        plt.ylabel('CELL')
        plt.grid(True)

        plt.savefig('stats_charts/cumulative_cell_emission.png', format="png", dpi=70,bbox_inches="tight")  # CUMULATIVE BLOCKS / 365 DAYS
        #plt.show()
        plt.close()
        return



def chart_zerochain_events(): #chart for stats
    database = r"zerochain.db"

    con = create_connection(database)
    with con:
        cur = con.cursor()
        query2 = """SELECT current_day,daily_events FROM flags ORDER BY id DESC LIMIT 365"""
        cur.execute(query2)
        results = cur.fetchall()

        dates = [result[0] for result in results]
        daily_events = [result[1] for result in results]
        dates.reverse()
        daily_events.reverse()
        plt.style.use('seaborn-ticks')

        fig, ax = plt.subplots(tight_layout=True, figsize=(15, 6))

        ax.set_ylabel('Events')

        ax.plot(daily_events, lw=1, color='maroon')

        # helper function for the formatter
        def listifed_formatter(x, pos=None):
            try:
                return dates[int(x)]
            except IndexError:
                return ''

        # make and use the formatter
        mt = mticker.FuncFormatter(listifed_formatter)
        ax.xaxis.set_major_formatter(mt)

        # set the default ticker to only put ticks on the integers
        loc = ax.xaxis.get_major_locator()
        loc.set_params(integer=True)
        # rotate the labels
        [lab.set_rotation(30) for lab in ax.get_xticklabels()]

    #    plt.figure(figsize=(15, 6))
        # plt.plot(transactions,linewidth=1,color="maroon")
        plt.plot(daily_events, linewidth=0.3, color="maroon")
        plt.title('Zerochain daily events / 356 days')
        plt.ylabel('Events')
        plt.grid(True)

        plt.savefig('stats_charts/zerochain_events.png', format="png", dpi=70,bbox_inches="tight")  # CUMULATIVE BLOCKS / 365 DAYS
        #plt.show()
        plt.close()
        return



def chart_daily_transactions(): #chart for stats
    database = r"cellframe.db"

    con = create_connection(database)
    with con:
        cur = con.cursor()
        query2 = """SELECT date, daily_transactions FROM transactions ORDER BY id DESC LIMIT 365"""
        cur.execute(query2)
        results = cur.fetchall()

        dates = [result[0] for result in results]
        total_blocks = [result[1] for result in results]
        dates.reverse()
        total_blocks.reverse()
        plt.style.use('seaborn-ticks')

        fig, ax = plt.subplots(tight_layout=True, figsize=(15, 6))

        ax.set_ylabel('Blocks')

        ax.plot(total_blocks, lw=1, color='maroon')

        # helper function for the formatter
        def listifed_formatter(x, pos=None):
            try:
                return dates[int(x)]
            except IndexError:
                return ''

        # make and use the formatter
        mt = mticker.FuncFormatter(listifed_formatter)
        ax.xaxis.set_major_formatter(mt)

        # set the default ticker to only put ticks on the integers
        loc = ax.xaxis.get_major_locator()
        loc.set_params(integer=True)
        # rotate the labels
        [lab.set_rotation(30) for lab in ax.get_xticklabels()]

    #    plt.figure(figsize=(15, 6))
        # plt.plot(transactions,linewidth=1,color="maroon")
        plt.plot(total_blocks, linewidth=0.3, color="maroon")
        plt.title('Daily blocks / 356 days')
        plt.ylabel('TXs')
        plt.grid(True)

        plt.savefig('stats_charts/transactions.png', format="png", dpi=70,bbox_inches="tight")  # CUMULATIVE BLOCKS / 365 DAYS
        #plt.show()
        plt.close()
        return

def top10_pie_chart_mcell():
    database = r"cellframe.db"
    con = create_connection(database)
    cur = con.cursor()
    with con:
        query = """ SELECT mcell_balance FROM {table} ORDER BY mcell_balance DESC LIMIT 30""".format(table="wallet_data_organized")
        cur.execute(query)
        total_mcell = cur.fetchall()
 #       print(total_mcell[1])
        sum0=float('.'.join(str(ele) for ele in total_mcell[0]))
        sum1=float('.'.join(str(ele) for ele in total_mcell[1]))
        sum2=float('.'.join(str(ele) for ele in total_mcell[2]))
        sum3=float('.'.join(str(ele) for ele in total_mcell[3]))
        sum4=float('.'.join(str(ele) for ele in total_mcell[4]))
        sum5=float('.'.join(str(ele) for ele in total_mcell[5]))
        sum6=float('.'.join(str(ele) for ele in total_mcell[6]))
        sum7=float('.'.join(str(ele) for ele in total_mcell[7]))
        sum8=float('.'.join(str(ele) for ele in total_mcell[8]))
        sum9=float('.'.join(str(ele) for ele in total_mcell[9]))
        grand_total10 = float(sum0)+ float(sum1)+float(sum2)+ float(sum3)+float(sum4)+ float(sum5)+float(sum6)+ float(sum7)+float(sum8)+float(sum9)
        print(grand_total10)

        sum0=float('.'.join(str(ele) for ele in total_mcell[10]))
        sum1=float('.'.join(str(ele) for ele in total_mcell[11]))
        sum2=float('.'.join(str(ele) for ele in total_mcell[12]))
        sum3=float('.'.join(str(ele) for ele in total_mcell[13]))
        sum4=float('.'.join(str(ele) for ele in total_mcell[14]))
        sum5=float('.'.join(str(ele) for ele in total_mcell[15]))
        sum6=float('.'.join(str(ele) for ele in total_mcell[16]))
        sum7=float('.'.join(str(ele) for ele in total_mcell[17]))
        sum8=float('.'.join(str(ele) for ele in total_mcell[18]))
        sum9=float('.'.join(str(ele) for ele in total_mcell[19]))
        sum10=float('.'.join(str(ele) for ele in total_mcell[20]))
        sum11=float('.'.join(str(ele) for ele in total_mcell[21]))
        sum12=float('.'.join(str(ele) for ele in total_mcell[22]))
        sum13=float('.'.join(str(ele) for ele in total_mcell[23]))
        sum14=float('.'.join(str(ele) for ele in total_mcell[24]))
        sum15=float('.'.join(str(ele) for ele in total_mcell[25]))
        sum16=float('.'.join(str(ele) for ele in total_mcell[26]))
        sum17=float('.'.join(str(ele) for ele in total_mcell[27]))
        sum18=float('.'.join(str(ele) for ele in total_mcell[28]))
        sum19=float('.'.join(str(ele) for ele in total_mcell[29]))
        grand_total_a = float(sum0)+ float(sum1)+float(sum2)+ float(sum3)+float(sum4)+ float(sum5)+float(sum6)+ float(sum7)+float(sum8)
        grand_total_a = grand_total_a + float(sum9) + float(sum10) + float(sum11) + float(sum12) + float(sum13) + float(sum14)
        grand_total_20_30 = grand_total_a + float(sum15) + float(sum16) + float(sum17)+ float(sum18)+ float(sum19)
        print(grand_total_20_30)

        query = """ SELECT mcell_total FROM {table} """.format(table="balances_total")
        cur.execute(query)
        total_mcell, = cur.fetchone()

        ten_percentage = (grand_total10 / total_mcell) * 100
   #     print("10%",ten_percentage)
        twenty_percentage = (grand_total_20_30 / total_mcell) * 100
  #      print("20-30",twenty_percentage)
        y = np.array([100 - ten_percentage-twenty_percentage, ten_percentage,twenty_percentage])
        mylabels = ["rest of mCELL wallets", "top 10 wallets", "20-30 wallets"]

        plt.pie(y, labels=mylabels, autopct='%1.1f%%')
        name = "stats_charts/10-20-30_wallets_mcell.png"
        plt.savefig(name, format="png", dpi=70, bbox_inches="tight")
        plt.close()
        return




def nodes_pie_chart():
    database = r"cellframe.db"
    con = create_connection(database)
    cur = con.cursor()
    with con:
        query = """ SELECT network_weight FROM {table} ORDER BY id DESC LIMIT 1""".format(table="transactions")
        cur.execute(query)
        network_weight, = cur.fetchone()

    database = r"cellframe.db"
    con = create_connection(database)
    cur = con.cursor()
    with con:
        query = """ SELECT mcell_total FROM {table} """.format(table="balances_total")
        cur.execute(query)
        total_mcell, = cur.fetchone()

    node_percentage = (network_weight/total_mcell)*100
    y = np.array([100-node_percentage, node_percentage])
    myexplode = [0, 0.2]
    mylabels = ["Total mCELL", "Validators"]

    #fig, ax = plt.subplots()
    plt.pie(y, labels=mylabels, autopct='%1.1f%%', explode = myexplode)
    name="stats_charts/validators_total_mcell.png"
    plt.savefig(name, format="png", dpi=70, bbox_inches="tight")
    #plt.show()
    return

def chart_block_validations(node_address):
        database = r"cellframe.db"
        con = create_connection(database)
        cur = con.cursor()
        with con:
            query = """ SELECT date, all_time_blocks FROM {table} ORDER BY id DESC LIMIT 100""".format(table=node_address)
            cur.execute(query)
            results = cur.fetchall()
            # print(results)
            dates = [result[0] for result in results]
            total_blocks = [result[1] for result in results]

            total_blocks.reverse()
            dates.reverse()

            plt.style.use('seaborn-ticks')

            fig, ax = plt.subplots(tight_layout=True, figsize=(10, 5))
            # ax.set_xlabel('date')
            ax.set_ylabel('validations')
            ln1, = ax.plot(total_blocks, lw=1, color='maroon')

            # helper function for the formatter
            def listifed_formatter(x, pos=None):
                try:
                    return dates[int(x)]
                except IndexError:
                    return ''

            # make and use the formatter
            mt = mticker.FuncFormatter(listifed_formatter)
            ax.xaxis.set_major_formatter(mt)

            # set the default ticker to only put ticks on the integers
            loc = ax.xaxis.get_major_locator()
            loc.set_params(integer=True)
            # rotate the labels
            [lab.set_rotation(30) for lab in ax.get_xticklabels()]

            plt.title('Block validations / 100 days')

            plt.grid(True)
            name = "nodes/charts/"
            name = name + str(node_address)
            name = name + "blocks.png"
            plt.savefig(name, format="png", dpi=70, bbox_inches="tight")  # BLOCK VALIDATIONS / 100 DAYS
            # plt.show()
            plt.close()
            return


def chart_daily_validations(node_address):
    database = r"cellframe.db"  # DAILY VALIDATIONS BAR CHART / 10 DAYS
    con = create_connection(database)
    cur = con.cursor()
    with con:
        query2 = """SELECT date, blocks FROM {table} ORDER BY id DESC LIMIT 10""".format(table=node_address)
        cur.execute(query2)
        results = cur.fetchall()

        dates = [result[0] for result in results]
        transactions = [result[1] for result in results]
        dates.reverse()
        transactions.reverse()
        plt.style.use('seaborn-ticks')

        plt.figure(figsize=(15, 7))
        plt.bar(dates, transactions, color='maroon', width=0.2)
       # plt.title('Validations / 10 days')
        plt.ylabel('validations')
        plt.grid(True)
        # plt.yticks(ticks=plt.yticks()[0], labels=plt.yticks()[0].astype(int))

        labels = []
        for i in range(len(transactions)):
            if i % 2 == 0:
                labels.append(transactions[i])
            else:
                labels.append("")
        plt.yticks(ticks=plt.yticks()[0], labels=plt.yticks()[0].astype(int))

        name = "nodes/charts/"
        name = name + str(node_address)
        name = name + "blocks10.png"
        plt.savefig(name, format="png",dpi=70,bbox_inches="tight")                   # DAILY VALIDATIONS BAR CHART / 10 DAYS
        #plt.show()
        plt.close()
        return


def chart_node_weight(node_address):
    database = r"cellframe.db"

    con = create_connection(database)
    cur = con.cursor()
    with con:
        query = """ SELECT date, weight FROM {table} ORDER BY id DESC LIMIT 60""".format(table=node_address)
        cur.execute(query)
        results = cur.fetchall()
   #     print(results)

        dates = [result[0] for result in results]
        node_weight = [result[1] for result in results]

        node_weight.reverse()
        dates.reverse()
        plt.style.use('seaborn-ticks')

        fig, ax = plt.subplots(tight_layout=True, figsize=(10, 5))
        # ax.set_xlabel('date')
        ax.set_ylabel('weight')
        ln1, = ax.plot(node_weight, lw=1, color='maroon')

        # helper function for the formatter
        def listifed_formatter(x, pos=None):
            try:
                return dates[int(x)]
            except IndexError:
                return ''

        # make and use the formatter
        mt = mticker.FuncFormatter(listifed_formatter)
        ax.xaxis.set_major_formatter(mt)

        # set the default ticker to only put ticks on the integers
        loc = ax.xaxis.get_major_locator()
        loc.set_params(integer=True)

        # rotate the labels
        [lab.set_rotation(30) for lab in ax.get_xticklabels()]

        name = "nodes/charts/"
        name = name + str(node_address)
        name = name + "weight.png"

        plt.savefig(name, format="png", dpi=70, bbox_inches="tight")
#        plt.show()
        plt.close()

        return
