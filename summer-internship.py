import sqlite3
import csv
import requests
import re
import os
import matplotlib.pyplot as plt

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def addToTable(cur,conn):
    cur.execute("CREATE TABLE IF NOT EXISTS company (location INT, month INT, state TEXT, gross_revenue REAL, fixed_cost REAL, variable_cost REAL, rental_cost INT, number_of_products INT, owned TEXT)")
    with open('/Users/emily/Desktop/casestudy/summer_internship_takehome.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ',')
        linecount = 0
        for row in csv_reader:
            if linecount == 0:
                linecount += 1
                continue
            location = row[0]
            month = row[1]
            state = row[2]
            grossrevenue = row[3]
            fixedcost = row[4]
            variablecost = row[5]
            rentalcost = row[6]
            numberofproducts = row[7]
            owned = row[8]
            cur.execute("INSERT INTO company (location, month, state, gross_revenue, fixed_cost, variable_cost, rental_cost, number_of_products, owned) VALUES (?,?,?,?,?,?,?,?,?)",(location, month, state, grossrevenue, fixedcost, variablecost, rentalcost, numberofproducts, owned,))
            linecount += 1
        conn.commit()

def calculateAnnualProfitMargin(cur,conn):
    cur.execute("CREATE TABLE IF NOT EXISTS AnnualProfitMarginPerStore (store INT, annualProfitMargin REAL)")
    for store in range(1,334):
        gross_revenue = 0
        fixed_cost = 0
        variable_cost = 0
        rental_cost = 0
        cur.execute("SELECT gross_revenue FROM company WHERE location=?", (store,))
        gross_revenue_list = cur.fetchall() 
        cur.execute("SELECT fixed_cost FROM company WHERE location=?", (store,))
        fixed_cost_list = cur.fetchall()
        cur.execute("SELECT variable_cost FROM company WHERE location=?", (store,))
        variable_cost_list = cur.fetchall()
        cur.execute("SELECT rental_cost FROM company WHERE location=?", (store,))
        rental_cost_list = cur.fetchall()
        for i in range(12):
            gross_revenue += gross_revenue_list[i][0]
            fixed_cost += fixed_cost_list[i][0]
            variable_cost += variable_cost_list[i][0]
            rental_cost += rental_cost_list[i][0]
        numerator = gross_revenue - fixed_cost - variable_cost - rental_cost
        profit_margin = (numerator/gross_revenue)*100
        cur.execute("INSERT INTO AnnualProfitMarginPerStore(store, annualProfitMargin) VALUES (?,?)", (store, profit_margin,))
        conn.commit()

def calculateMeanAnnualProfitMargin(cur,conn):
    cur.execute("SELECT annualProfitMargin FROM AnnualProfitMarginPerStore")
    profit_margin_list = cur.fetchall()
    profit_margin_sum = 0
    for profit_margin in profit_margin_list:
        profit_margin_sum += profit_margin[0]
    mean = profit_margin_sum/333
    print("The mean annual profit margin of a typical store before rent-adjustment is: " + str(mean))

def calculateMedianAnnualProfitMargin(cur,conn):
    cur.execute("SELECT annualProfitMargin FROM AnnualProfitMarginPerStore")
    profit_margin_list = cur.fetchall()
    new_list = []
    for item in profit_margin_list:
        new_list.append(item[0])
    new_list.sort()
    median = new_list[166]
    print("The median annual profit margin of a typical store before rent-adjustment is: " + str(median))

def createBoxPlotAnnualProfitMargin(cur,conn):
    cur.execute("SELECT annualProfitMargin FROM AnnualProfitMarginPerStore")
    bigList = cur.fetchall()
    data = []
    for i in range(len(bigList)):
        data.append(bigList[i][0])
    
    plt.boxplot(data)
    plt.title('Annual Profit Margin Distribution')
    plt.show()

def createMonthlyAggregateRevenueVisualization(cur, conn):
    monthRevenueDict = {}
    positions = []
    for i in range(1,13):
        positions.append(i)
        revenueTotal = 0
        cur.execute('SELECT gross_revenue FROM company WHERE month=?', (i,))
        monthRevenueList = cur.fetchall()
        for num in monthRevenueList:
            revenueTotal += num[0]
        monthRevenueDict[i] = revenueTotal
    aggregateRevenueList = list(monthRevenueDict.values())
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    fig = plt.figure(figsize=(15,8))
    plt.bar(positions, aggregateRevenueList, width=0.5)
    plt.xticks(positions, months)
    plt.xticks(rotation = -75)
    plt.xlabel('Month')
    plt.ylabel('Aggregate Revenue in $')
    plt.suptitle('Monthly Aggregate Revenue Across All Stores')
    plt.show()

def createQuarterlyAggregateRevenueVisualization(cur, conn):
    quarterRevenueDict = {}
    for i in range(1, 13, 3):
        revenueTotal = 0
        cur.execute("SELECT gross_revenue FROM company WHERE month=? OR month=? OR month=?", (i, i+1, i+2,))
        quarterRevenueList = cur.fetchall()
        for num in quarterRevenueList:
            revenueTotal += num[0]
        quarterRevenueDict[i] = revenueTotal
    quarterRevenueList = list(quarterRevenueDict.values())
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    positions = [0,1,2,3]
    fig = plt.figure(figsize=(15,8))
    plt.bar(positions, quarterRevenueList)
    plt.xticks(positions,quarters)
    plt.xlabel('Quarter')
    plt.ylabel('Aggregate Revenue in $')
    plt.suptitle('Quarterly Aggregate Revenue Across All Stores')
    plt.show()

def calculateRentAdjustedAnnualProfitMargin(cur,conn):
    cur.execute("SELECT rental_cost FROM company WHERE owned= 'FALSE'")
    rentalCostValues = cur.fetchall()
    cur.execute("SELECT fixed_cost FROM company WHERE owned= 'FALSE'")
    fixedCostValues = cur.fetchall()
    totalRentalCost = 0
    totalFixedCost = 0
    for i in range(len(rentalCostValues)):
        totalRentalCost += rentalCostValues[i][0]
        totalFixedCost += fixedCostValues[i][0]
    decimal = totalRentalCost/totalFixedCost
    for store in range(1,334):
        gross_revenue = 0
        fixed_cost = 0
        variable_cost = 0
        rental_cost = 0
        annualProfitMargin = 0
        cur.execute("SELECT gross_revenue FROM company WHERE location=?", (store,))
        gross_revenue_list = cur.fetchall() 
        cur.execute("SELECT fixed_cost FROM company WHERE location=?", (store,))
        fixed_cost_list = cur.fetchall()
        cur.execute("SELECT variable_cost FROM company WHERE location=?", (store,))
        variable_cost_list = cur.fetchall()
        cur.execute("SELECT rental_cost FROM company WHERE location=?", (store,))
        rental_cost_list = cur.fetchall()
        for i in range(12):
            rental_price = rental_cost_list[i][0]
            if rental_price == 0:
                adjustedRentalCost = fixed_cost_list[i][0] * decimal
            else:
                adjustedRentalCost = rental_cost_list[i][0]
            gross_revenue += gross_revenue_list[i][0]
            variable_cost += variable_cost_list[i][0]
            rental_cost += adjustedRentalCost
            fixed_cost += fixed_cost_list[i][0]
        numerator = gross_revenue - fixed_cost - variable_cost - rental_cost
        profit_margin = (numerator/gross_revenue)*100
        cur.execute("CREATE TABLE IF NOT EXISTS AdjustedAnnualProfitMargin (store INT, AdjustedAnnualProfitMargin REAL)")
        cur.execute("INSERT INTO AdjustedAnnualProfitMargin(store, AdjustedAnnualProfitMargin) VALUES (?,?)", (store, profit_margin,))
        conn.commit()

def calculateMeanAnnualProfitMarginAfterAdjustment(cur,conn):
    cur.execute("SELECT AdjustedAnnualProfitMargin FROM AdjustedAnnualProfitMargin")
    profit_margin_list = cur.fetchall()
    profit_margin_sum = 0
    for profit_margin in profit_margin_list:
        profit_margin_sum += profit_margin[0]
    mean = profit_margin_sum/333
    print("The mean annual profit margin of a typical store after rent-adjustment is: " + str(mean))

def calculateMedianAnnualProfitMarginAfterAdjustment(cur,conn):
    cur.execute("SELECT AdjustedAnnualProfitMargin FROM AdjustedAnnualProfitMargin")
    profit_margin_list = cur.fetchall()
    new_list = []
    for item in profit_margin_list:
        new_list.append(item[0])
    new_list.sort()
    median = new_list[166]
    print("The median annual profit margin of a typical store after rent-adjustment is: " + str(median))

def createStoresPerStateDict(cur,conn):
    cur.execute("SELECT state FROM company")
    statesList = cur.fetchall()
    storeDict = {}
    for i in range(len(statesList)):
        if statesList[i][0] in storeDict:
            storeDict[statesList[i][0]] += 1
        else:
            storeDict[statesList[i][0]] = 1
    for i in storeDict:
        newNum = storeDict[i]
        newNum = int(newNum/12)
        storeDict[i] = newNum
    return storeDict

def createStoresPerStateVisualization(storeDict):
    positions = []
    sortedDict = {}
    for i in range(len(storeDict)):
        positions.append(i)
    key_list = list(storeDict.keys())
    value_list = list(storeDict.values())
    fig = plt.figure(figsize=(15,8))
    plt.bar(positions, value_list, width=.5)
    plt.xticks(positions, key_list)
    plt.xlabel('State')
    plt.ylabel('Number of Stores')
    plt.suptitle('Number of Stores Per State')
    plt.show()

def createProfitsByAdjustedProfitMarginNumbers(cur,conn):
    cur.execute("SELECT AdjustedAnnualProfitMargin FROM AdjustedAnnualProfitMargin")
    TupAdjustedAnnualProfitMarginList = cur.fetchall()
    productsList = []
    adjustedAnnualProfitMarginList = []
    for store in range(1,334):
        cur.execute("SELECT number_of_products FROM company WHERE location=?", (store,))
        allProductsList = cur.fetchall()
        totalProducts = 0
        for i in range(12):
            totalProducts += allProductsList[i][0]
        productsList.append(totalProducts/12)
        adjustedAnnualProfitMarginList.append(TupAdjustedAnnualProfitMarginList[store-1][0])
    pairedDict = {}
    for i in range(len(productsList)):
        pairedDict[adjustedAnnualProfitMarginList[i]] = productsList[i]
    sorted_dict = sorted(pairedDict.items(), key=lambda x:x[1], reverse=False)
    key_list = []
    value_list = []
    for i in range(len(sorted_dict)):
        key_list.append(sorted_dict[i][1])    
        value_list.append(sorted_dict[i][0])         
    return key_list, value_list

def makeVisualizationForStoresAndProfitMargin(key_list, value_list):
    positions = []
    for i in range(len(key_list)):
        positions.append(i)
    fig = plt.figure(figsize=(15,8))
    plt.bar(positions, value_list, width=.5)  
    plt.xlabel('Number of Products Per Store')
    plt.ylabel('Rent-Adjusted Annual Profit Margin')
    plt.suptitle('Correlation Between Rent-Adjusted Annual Profit Margin and Number of Products Per Store (3810-4789)')
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.show()

def getFixedCostDividedByRevenueDict(cur,conn):
    stateValuesDict = {}
    percentDict = {}
    for store in range(1,334):
        cur.execute("SELECT state, fixed_cost, gross_revenue FROM company WHERE location=?", (store,))
        all_variables = cur.fetchall()  
        key = ""
        for i in range(12):
            key = all_variables[i][0]
            if key in stateValuesDict:
                resultsTup = stateValuesDict[key]
                fixed_cost = resultsTup[0] + all_variables[i][1]
                revenue = resultsTup[1] + all_variables[i][2] 
                new_tup = (fixed_cost, revenue)
                stateValuesDict[key] = new_tup
            else:
                stateValuesDict[key] = (all_variables[i][1], all_variables[i][2])
    for key in stateValuesDict:
        tup = stateValuesDict[key]
        fixed_cost = tup[0]
        revenue = tup[1]
        percent = (fixed_cost/revenue)*100
        percentDict[key] = percent
    return percentDict

def getAverageAdjustedProfitMarginPerState(storeDict,cur,conn):
    stateProfitMarginDict = {}
    finalDict = {}
    cur.execute("SELECT company.state, AdjustedAnnualProfitMargin.AdjustedAnnualProfitMargin FROM company INNER JOIN AdjustedAnnualProfitMargin ON company.location=AdjustedAnnualProfitMargin.store")
    all_list = cur.fetchall()
    for i in range(0,len(all_list), 12):
        key = all_list[i][0]
        if key in stateProfitMarginDict:
            oldProfitMargin = stateProfitMarginDict[key]
            newProfitMargin = oldProfitMargin + all_list[i][1]
            stateProfitMarginDict[key] = newProfitMargin
        else:
            stateProfitMarginDict[key] = all_list[i][1]
    for key in stateProfitMarginDict:
        bigProfitMargin = stateProfitMarginDict[key]
        divideBy = storeDict[key]
        newProfitMargin = bigProfitMargin/divideBy
        finalDict[key] = newProfitMargin
    return finalDict

def createCorrelationVisualization (fixedCostDividedByRevenueDict, profitMarginPerStateDict):
    positions1 = [0,1,2,3,4,5,6]
    positions2 = [.3,1.3,2.3,3.3,4.3,5.3,6.3]
    positions3 = [.15,1.15,2.15,3.15,4.15,5.15,6.15]
    fixedCostDividedByRevenueList = list(fixedCostDividedByRevenueDict.values())
    profitMarginPerStateList = list(profitMarginPerStateDict.values())
    state_list = list(fixedCostDividedByRevenueDict.keys())
    fig = plt.figure(figsize=(15,8))
    plt.bar(positions1, fixedCostDividedByRevenueList, width=.3)
    plt.bar(positions2, profitMarginPerStateList, width=.3, color = 'r')
    plt.xticks(positions3, state_list)
    labels = ["Average Fixed Cost/Revenue", "Average Rent Adjusted Profit Margin"]
    plt.legend(labels, loc=1)
    plt.xlabel('State')
    plt.ylabel('Percentage')
    plt.suptitle('Rent-Adjusted Profit Margin And Fixed Cost To Revenue Percentage By State')
    plt.show()

def main():
    cur, conn = setUpDatabase('CompanyData.db')
    addToTable(cur,conn)
    calculateAnnualProfitMargin(cur,conn)
    calculateMeanAnnualProfitMargin(cur,conn)
    calculateMedianAnnualProfitMargin(cur,conn)
    createBoxPlotAnnualProfitMargin(cur,conn)
    createMonthlyAggregateRevenueVisualization(cur, conn)  
    createQuarterlyAggregateRevenueVisualization(cur, conn) 
    calculateRentAdjustedAnnualProfitMargin(cur,conn)
    calculateMeanAnnualProfitMarginAfterAdjustment(cur,conn)
    calculateMedianAnnualProfitMarginAfterAdjustment(cur,conn)
    storeDict = createStoresPerStateDict(cur,conn)   
    createStoresPerStateVisualization(storeDict)
    key_list, value_list = createProfitsByAdjustedProfitMarginNumbers(cur,conn)
    makeVisualizationForStoresAndProfitMargin(key_list, value_list)  
    fixedCostDividedByRevenueDict = getFixedCostDividedByRevenueDict(cur,conn)
    profitMarginPerStateDict = getAverageAdjustedProfitMarginPerState(storeDict,cur,conn)
    createCorrelationVisualization (fixedCostDividedByRevenueDict, profitMarginPerStateDict)

if __name__ == '__main__':
    main()