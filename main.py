import itertools
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd

depth0 = pd.read_csv('0.txt', sep='\t')
depth1 = pd.read_csv('1.txt', sep='\t')
depth2 = pd.read_csv('2.txt', sep='\t')
columnList=['id','uploader','age','category','length','views','rating','#ratings','#comments','vid1','vid2'
    ,'vid3','vid4','vid5','vid6','vid7','vid8','vid9','vid10','vid11','vid12','vid13','vid14','vid15',
                'vid16','vid17','vid18','vid19','vid20']
depth0.columns=columnList
depth0['age']=depth0['age']/365 # changed from days to years
depth0['length']=depth0['length']/60 # changed from seconds to minutes
depth1.columns=columnList
depth1['age']=depth1['age']/365
depth1['length']=depth1['length']/60
depth2.columns=columnList
depth2['age']=depth2['age']/365
depth2['length']=depth2['length']/60

def doQuery(): # returns whether user wants to do another query
    cont=input("Would you like to do a query? If yes, type '1'. If no, type '2.'")
    if int(cont)==1:
        return True
    elif int(cont)==2:
        return False
    else:
        print("Please type 1 or 2.")
        return doQuery()
def fileName(file): # returns file user wants to do query on
    if file=="depth0":
        df=depth0
    elif file=="depth1":
        df=depth1
    elif file=="depth2":
        df=depth2
    return df
def conditions(): #returns list of conditions that user wants
    conds=[]
    cont = input("Would you like to apply a search filter? If yes, enter 1. If not, enter 2.")
    if int(cont) == 1:
        expression = input("Enter a search condition. To do an entity search, enter something like \n "
                           "'rating==4.0'. To do a ranged query, enter something like 'rating<4.0'.")
        conds.append(expression)
        return conds+conditions()
    elif int(cont) == 2:
        return conds
    else:
        print("Please type 1 or 2.")
        return conds+conditions()
def applyFilter(conditionList,df): # returns all videos satisfying entity search, range query conditions
    for c in conditionList:
        if c is not None:
            df=df.query(c)
    return df
def findPairs(file,pairs):
    ids=['id','vid1','vid2','vid3','vid4','vid5','vid6','vid7','vid8','vid9','vid10','vid11','vid12',
             'vid13','vid14','vid15','vid16','vid17','vid18','vid19','vid20']
    relatedIDs=file[ids].copy() # lists only video id and related IDs, transposed for easier iteration
    for i in range(relatedIDs.shape[0]): # goes through each row
        for j in range(relatedIDs.shape[1]): # goes through each column
            tuple=(relatedIDs.iat[i,0],relatedIDs.iat[i,j])
            if (relatedIDs.iat[i,j] is np.nan)==False:
                pairs.append(tuple)
    return pairs
def pageRank(file,pairs,k):
    g=nx.Graph()
    g.add_edges_from(pairs)
    pr=nx.pagerank(g)
    sortedpr=sorted(pr.items(),key=lambda x:x[1],reverse=True)
    vids=[v[0] for v in sortedpr[:k]] # list of the k most influential vids
    df=depth0.loc[depth0['id'].isin(vids)]
    if file is not depth0:
        df=pd.concat([df,depth1.loc[depth1['id'].isin(vids)]]) # adds tuples from depth1 if user wants them
        if file is depth2:
            df = pd.concat([df, depth2.loc[depth2['id'].isin(vids)]])
    return df
def queryType(): # returns type of query user wants to do
    type = input("What type of query would you like to perform? "
                      "If entity search, type 'es.' If ranged query, type 'rq.' \n"
                 "If influence rank, type 'ir.'")
    if type == "es":
        return "es"
    elif type == "rq":
        return "rq"
    elif type=="ir":
        return "ir"
    else:
        print("Please enter a valid input.")
        queryType()
def queryMenu():
    cont=doQuery()
    while(cont):
        type=queryType()
        if type=="es" or type=="rq":
            f = input("Enter the file name.")
            file = fileName(f)
            cList=conditions()
            print(applyFilter(cList,file).to_string())
        elif type=="ir":
            pairs=[]
            depth=input("Enter the depth that you want to search to.")
            num=input("Enter the number of videos you want to find (the ___ most influential).")
            cList=conditions()
            d0=applyFilter(cList,depth0) # applies search filters to depth0
            pairs=findPairs(d0,pairs)
            if depth!="depth0":
                d1=applyFilter(cList,depth1)
                pairs.extend(findPairs(d1,pairs)) # adds tuples from depth1 if user wants them
                if depth == "depth2":
                    d2=applyFilter(cList,depth2)
                    pairs.extend(findPairs(d2,pairs))
            print(pageRank(fileName(depth),pairs,int(num)).to_string())
        cont=doQuery() # user can perform multiple queries
def relevantVidCategories(df): # prints the categories of the relevant videos of videos in a dataframe
    relevantVids=[df.iloc[:,i] for i in range(9,29)]
    relevantVids=list(itertools.chain.from_iterable(relevantVids))
    allRelevant=pd.DataFrame()
    for ind in range(0,len(relevantVids)):
        relevant0 = depth0.loc[depth0['id']==relevantVids[ind]]
        if relevant0.empty: # only searches depth1 and depth2 if necessary
            relevant1 = depth1.loc[depth1['id']==relevantVids[ind]]
            if relevant1.empty:
                relevant2 = depth2.loc[depth2['id']==relevantVids[ind]]
                allRelevant = pd.concat([allRelevant, relevant2])
            else:
                allRelevant=pd.concat([allRelevant,relevant1])
        else:
            allRelevant=pd.concat([allRelevant,relevant0])
    return Counter(allRelevant['category'])
def influenceAnalysis(): # analysis of most influential videos
    count0=Counter(depth0['category'])
    count1=Counter(depth1['category'])
    count2=Counter(depth2['category'])
    print("overall category distribution: ", count0+count1+count2) # prints number of videos in each category across depths 0-2
    pairs=findPairs(depth0,[])
    pairs.extend(findPairs(depth1,pairs))
    pairs.extend(findPairs(depth2,pairs))
    top250=pageRank(depth2, pairs, 250) # finds the 250 most influential videos
    topMusic=top250.loc[top250['category']=='Music']
    topEntertainment = top250.loc[top250['category'] == 'Entertainment']
    topComedy=top250.loc[top250['category']=='Comedy']
    topSports = top250.loc[top250['category'] == 'Sports']
    topNews=top250.loc[top250['category']=='News & Politics']
    top250Relevant=relevantVidCategories(top250)
    topMusicRelevant=relevantVidCategories(topMusic)
    topEntertainmentRelevant=relevantVidCategories(topEntertainment)
    topComedyRelevant=relevantVidCategories(topComedy)
    topNewsRelevant=relevantVidCategories(topNews)
    topSportsRelevant=relevantVidCategories(topSports)
    print("top 250 relevant vids category distribution: ", top250Relevant)
    print("top music relevant vids category distribution: ", topMusicRelevant)
    print("top entertainment relevant vids category distribution: ", topEntertainmentRelevant)
    print("top comedy relevant vids category distribution: ", topComedyRelevant)
    print("top news relevant vids category distribution: ", topNewsRelevant)
    print("top sports relevant vids category distribution: ", topSportsRelevant)
queryMenu()
influenceAnalysis()