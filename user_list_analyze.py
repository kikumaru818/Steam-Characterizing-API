#Copy right: MENGXUE ZHANG
#Time: 2018/4/27
import urllib, json
import networkx as nx
import Queue
import pickle
from sklearn.feature_extraction import DictVectorizer
from collections import Counter
import operator
import parameters
import itertools
import numpy as np
from sklearn.preprocessing import normalize
import time
import unicodecsv as csv
import seaborn as sns
import embed

myid="76561198116611099"
key ="72A55775E8E8C80E598D5A9F7CE8C738"
feature_map={"steam_id":0,"friend_#":1,"new_friend":2,"steam_level":3,"recent_play_time":4,
        "recent_top_game%":5,"recent_#_game_played":6,"recent_top_game":7,
        "recent_new/recent_all_game":8,"recent_new/all_game_time":9,"average_played_time":10,"top_game":11,"topgame%":12,
        "top_game_score":13,"top_game_cat":14,"recent_top_game_cat":15,"total cost":16,"cost per game":17,
             "total_play_time":18,"total_game_#":19}

feature_map={0:"steam_id",1:"friend_#",2:"new_friend",3:"steam_level",4:"recent_play_time",
        5:"recent_top_game%",6:"recent_#_game_played",7:"recent_top_game",
        8:"recent_new/recent_all_game",9:"recent_new/all_game_time",10:"average_played_time",11:"top_game",12:"topgame%",13:
        "top_game_score",14:"top_game_cat",15:"recent_top_game_cat",16:"total cost",17:"cost per game",18:"total_play_time",
             19:"total_game_#",20:"account age",21:"active_friend_%",22:"Location"}



user_info = {0:0,1:0,2:0,3:1,4:0,5:0,6:0,7:1,8:0,9:0,10:1,11:1,12:1,13:100}
time_threhold=1514764800
time_now = 1524009600
run_folder=""

#game_base={}
#cat_base={}



def clear_database():
    game_base={}
    with open("game_base", 'wb') as f:
        pickle.dump(game_base, f)

with open("game_base", 'rb') as f:
    game_base=pickle.load(f)
with open("cat_base", 'rb') as f:
    cat_base=pickle.load(f)


def get_gameInfo(gameid):

    if gameid in game_base and game_base[gameid] !={}:
        return game_base[gameid]


    url="http://store.steampowered.com/api/appdetails?appids="+str(gameid)
    try:
        if parameters.DEBUG:
            print "update empty game: "+ str(gameid)
        response=urllib.urlopen(url)
        data = json.loads(response.read())
        data=data[str(gameid)]
        if data["success"] is False:
            a={"no": 1, "metacritic": 80, "price": 0, "name": "UNKW"}
            game_base[gameid]=a
            print "no such game"
            return a
        data=data["data"]
        sample={}
        temp = data.get('metacritic', 80)
        if temp != 80:
            temp = temp["score"]

        game_base["metacritic"] = temp
        sample["metacritic"]=temp
        temp=data.get('price_overview', 0)
        if temp != 0:
            sample["price"] = temp["final"] * 1. / 100
        else:
            sample["price"] = temp


        temp=data.get('genres',[{"description":"NA_G"}])
        #temp = data.get('genres', [])
        temp = temp[0:1]
        temp=map(lambda x: x["description"],temp)
        sample["genres"]=temp

        temp = data.get('categories', [{"description": "NA_C"}])
        #temp = data.get('categories', [])
        temp = temp[0:1]
        sample["categories"]=[temp[0]["description"]]

        game_base[gameid]=sample
        sample["id"]=gameid
        sample["name"]=data["name"]

        with open("game_base", 'w') as f:
            pickle.dump(game_base, f)

        return sample
    except Exception as e:
        print e
        if parameters.DEBUG:
            print str(gameid)+" :Empty still empty :C"
            print "Sleep for a while!!!"
            time.sleep(15)
        game_base[gameid] = {}
        with open("game_base", 'w') as f:
            pickle.dump(game_base, f)
        return {}

def ana_gamelist_recent(game_list):
    #for game in game_list:
    #    game.update(get_gameInfo(game["id"]))
    temp_dict={}
    game_list=game_list[1]
    map(lambda x: x.update(get_gameInfo(x["appid"])),game_list)
    game_list=filter(lambda x: "name" in x, game_list)
    count=len(game_list)
    #temp_dict[8]=count

    playtime_list=[d['playtime_2weeks'] for d in game_list]
    total_playtime = sum(playtime_list)
    recent_top_game_time=max(playtime_list)
    recent_top_game_i=playtime_list.index(recent_top_game_time)
    recent_top_game=game_list[recent_top_game_i]["name"]


    new_game_count=sum(x['playtime_2weeks'] == x["playtime_forever"] for x in game_list)

    playtime_list = [d['playtime_forever'] for d in game_list]
    total_playtime_forever= sum(playtime_list)

    temp_dict[4]=total_playtime;
    temp_dict[5]=recent_top_game_time * 1. / total_playtime
    temp_dict[6]=count
    temp_dict[7]=game_list[recent_top_game_i]["appid"]
    temp_dict[8]=new_game_count*1./count
    temp_dict[9]=total_playtime*1./total_playtime_forever

    top_game = game_list[recent_top_game_i]["appid"]

    try:
        if top_game not in game_base:
            game_base[top_game]=game_list[recent_top_game_i]["name"]
        temp = game_base[top_game]["categories"][0]
    except:
        print "Top game error: "+ str(top_game) +"not found"
        game_base.pop(top_game)
        get_gameInfo(top_game)
        temp = game_base[top_game]["categories"][0]

    if temp in cat_base:
        temp = cat_base[temp]
    else:
        cat_base[temp] = len(cat_base)
        cat_base[cat_base[temp]]=temp
        temp = cat_base[temp]
        with open("cat_base", 'wb') as f:
            pickle.dump(cat_base, f)

    temp_dict[15] = temp

    #temp_dict[15] = game_base[top_game]["categories"][0]
    return temp_dict


def ana_gamelist(game_list):
    game_list = game_list[1]
    temp_dict = {}

    #map(lambda x: x.update(get_gameInfo(x["appid"])), game_list)

    game_list = filter(lambda x: "appid" in x, game_list)
    count = len(game_list)

    if count > 1000:
        playtime_list = [d['playtime_forever'] for d in game_list]
        total_playtime_forever = sum(playtime_list)
        top_game_time = max(playtime_list)
        top_game_i = playtime_list.index(top_game_time)
        top_game = game_list[top_game_i]["appid"]

        top_game_dic=game_list[top_game_i]
        a=get_gameInfo(top_game)

        top_game_n = game_base[top_game]["name"]
        top_game_score = game_base[top_game]["metacritic"]
        total_cost = count*20.

        temp_dict[10] = total_playtime_forever * 1.0 / count
        temp_dict[11] = top_game
        temp_dict[12] = top_game_time * 1. / total_playtime_forever
        temp_dict[13] = top_game_score
        temp_dict[19] = count
        temp_dict["crazy"] = 1.
        print "one crazy"
        return temp_dict

    map(lambda x: x.update(get_gameInfo(x["appid"])), game_list)

    playtime_list = [d['playtime_forever'] for d in game_list]
    total_playtime_forever = sum(playtime_list)
    top_game_time = max(playtime_list)
    top_game_i = playtime_list.index(top_game_time)
    top_game = game_list[top_game_i]["appid"]
    try:
        top_game_n=game_base[top_game]["name"]
    except Exception as e:
        get_gameInfo(top_game)

        print e
        print top_game
        game_base[top_game]={"no": 1, "metacritic": 80, "price": 0, "genres": ["NA"], "categories": ["NA"], "name": "NA"}
        top_game_n = game_base[top_game]["name"]
        with open("game_base", 'w') as f:
            pickle.dump(game_base, f)
        return {}
    try:
        top_game_score=game_base[top_game]["metacritic"]
    except:
        print "metacritic"


    genre_list = [d['genres'] for d in game_list if "genres" in d]
    genre_list=list(itertools.chain.from_iterable(genre_list))
    genres=Counter(genre_list)

    cat_list = [d['categories'] for d in game_list if "categories" in d]
    cat_list = list(itertools.chain.from_iterable(cat_list))
    categories=Counter(cat_list)

    genres = sorted(genres.items(), key=operator.itemgetter(1))
    categories=sorted(categories.items(),key=operator.itemgetter(1))

    #top_genre=max(genres.iteritems(), key=operator.itemgetter(1))[0]
    #top_cat =max(categories.iteritems(), key=operator.itemgetter(1))[0]

    total_cost = sum([d["price"] for d in game_list if "price" in d])
    try:
        if total_playtime_forever == 0:
            total_playtime_forever=1
        if  count == 0:
            count = 1
        avg_cost=total_cost*1./ count


        temp_dict[10]=total_playtime_forever*1.0 / count
        temp_dict[11]=top_game
        temp_dict[12]=top_game_time*1./total_playtime_forever
        temp_dict[13]=top_game_score
        temp_dict[19]=count



    except Exception as e:
        print "dead user"
        print e

    temp=game_base[top_game]["categories"][0]
    if temp in cat_base:
        temp=cat_base[temp]
    else:
        cat_base[temp]=len(cat_base)
        cat_base[cat_base[temp]] = temp
        temp=cat_base[temp]
        with open("cat_base", 'wb') as f:
            pickle.dump(cat_base, f)

    temp_dict[14]=temp
    temp_dict[16]=total_cost
    temp_dict[17]=avg_cost
    temp_dict[18]=total_playtime_forever

    top_genre=genres[-1][0]
    top_genre_n=genres[-1][1]

    top_cat=categories[-1][0]
    top_cat_n = categories[-1][1]

    if len(genres) >1:
        s_genre=genres[-2][0]
        temp_dict[s_genre] = genres[-2][1] * 1.0 / len(genre_list)
        if len(genres)>2:
            s_genre = genres[-3][0]
            temp_dict[s_genre] = genres[-3][1] * 1.0 / len(genre_list)
    if len(categories)>1:
        s_cat=categories[-2][0]
        temp_dict[s_cat] = categories[-2][1] * 1.0 / len(cat_list)
        #if len(categories)>2:
        #   s_cat = categories[-3][0]
        #    temp_dict[s_cat] = categories[-3][1] * 1.0 / len(cat_list)

    temp_dict[top_genre]=genres[-1][1]*1.0/len(genre_list)
    temp_dict[top_cat]=categories[-1][1]*1.0/len(cat_list)

    return temp_dict



def getRecentInfo(steamid):
    url = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key=" + key + "&format=json&steamid=" + str(steamid)
    temp_dict={}
    try:
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        data = data['response']
        total_game = data.get('total_count', 0)
        temp_dict[6] = total_game


        if "games" in data:
            game_list = data.values()
            temp = ana_gamelist_recent(game_list)
            temp_dict.update(temp)
    except Exception as e:
        print e
        pass
    return temp_dict


def getForeverInfoFree(steamid):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key=" + key + "&format=json&steamid=" + str(
        steamid) + \
          "&include_played_free_games=1&appids_filter="
    temp_dict = {}
    try:
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        data = data['response']
        total_game = data.get('game_count', 0)
        if total_game == 0:
            return

        if "games" in data:
            game_list = data.values()
            game_list=game_list[1]
            for i in game_list:
                if i["appid"] == 570 and i["play_forever"]>60:
                    game_list=i
                    return game_list


        return []

            # temp_dict[8]=temp_dict[6]*1./temp_dict[8]
    except Exception as e:
        print e
        return []
    return temp_dict




def getForeverInfo(steamid):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key="+key+"&format=json&steamid="+str(steamid)+\
          "&appids_filter="
    temp_dict={}
    try:
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        data = data['response']
        total_game = data.get('game_count', 0)
        if total_game == 0:
            temp_dict["dead"]=1
            return temp_dict


        if "games" in data:
            #freeList=getForeverInfoFree(steamid)
            game_list = data.values()
            if total_game >150 and total_game < 1000:
                game_list = filter(lambda x: x["playtime_forever"] > 60, game_list[1])
                game_list = [1, game_list]



            temp = ana_gamelist(game_list)
            temp_dict.update(temp)

            temp_dict[19]=total_game
    except Exception as e:
        print e
        return temp_dict
    return temp_dict





def getSteamlevel(steamid):
    url="https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key="+key+"&format=json&steamid="+str(steamid)
    temp_dict = {}
    try:
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        data = data['response']

        if "player_level" in data:
            temp_dict[3]=int(data["player_level"])

        return temp_dict
    except Exception as e:
        print e
        pass
    return temp_dict

def getFrinedList(steamid):
    url="http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=" + key + "&steamid=" + str(steamid) + "&relationship=friend"
    temp_dict={}
    try:
        response=urllib.urlopen(url)
        data = json.loads(response.read())
        if "friendslist" in data:
            data = data["friendslist"]
            data = data["friends"]
            count=sum(x["friend_since"] > time_threhold for x in data)
            temp_dict[2]=count
            temp_dict[1]=len(data)

        else:
            temp_dict={}
    except Exception as e:
        print "dead: "
        print e
        temp_dict={"dead":1}


    return temp_dict

def getAcountInfor(steamid):
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=" + key + "&format=json&steamids=" + str(steamid)
    try:
        temp_dict={}
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        data = data['response']
        if "players" in data:
            data = data["players"]
            data = data[0]
            temp=data["timecreated"]
            temp=(time_now-temp)*1./60/60/24
            temp_dict[20]=temp

            temp=data["loccountrycode"]

            if temp in cat_base:
                temp = cat_base[temp]
            else:
                cat_base[temp] = len(cat_base)
                cat_base[cat_base[temp]] = temp
                temp = cat_base[temp]
                with open("cat_base", 'wb') as f:
                    pickle.dump(cat_base, f)

            temp_dict[22] = temp

            return temp_dict

    except:
        temp_dict={"dead":1}
        return temp_dict


def createUser(steamid):

    user = {}
    user[0]=steamid
    user.update(getRecentInfo(steamid))
    user.update(getForeverInfo(steamid))
    user.update(getSteamlevel(steamid))
    user.update(getFrinedList(steamid))
    user.update(getAcountInfor((steamid)))

    if parameters.DEBUG:
        print user

    if len(user) < 10:
        print user
        user=0

    if parameters.DEBUG:
        if user == 0 or 'dead' in user or "dead" in user:
            user = 0
            print "Dead: " + str(steamid)
    return user



def normalizaed(user_list,vocabulary):

    p1=user_list[:,0:vocabulary[21]+1]
    p2=user_list[:,vocabulary[21]+1:-1]

    p1=normalize(p1,axis=0)
    return np.concatenate((p1,p2),axis=1)


def prepareList(user_dict):
    v = DictVectorizer(dtype=np.float, sparse=False)
    user_list = user_dict.values()
    user_list = v.fit_transform(user_list)
    vocab = v.vocabulary_

    return user_list, vocab



#import csv
def printToTable(point_list,outputname=run_folder+"csv_out2.csv"):

    with open(outputname,"wb") as f:
        writer=csv.writer(f)
        writer.writerows(point_list)

def getMean(user_list,vocab):
    final_list=user_list.mean(axis=0)
    final_list=final_list.tolist()
    temp=user_list[:,vocab[7]]
    temp = Counter(temp)
    temp = sorted(temp.items(), key=operator.itemgetter(1))
    try:
        temp=game_base[int(temp[-1][0])]["name"]
    except:
        temp="NA"
    final_list[vocab[7]]=temp


    temp = user_list[:, vocab[11]]
    temp = Counter(temp)

    temp = sorted(temp.items(), key=operator.itemgetter(1))
    temp = game_base[int(temp[-1][0])]["name"]
    final_list[vocab[11]] = temp


    try:
        temp = user_list[:, vocab[14]]
        temp = Counter(temp)
        temp = sorted(temp.items(), key=operator.itemgetter(1))
        temp = cat_base[temp[-1][0]]
        final_list[int(vocab[14])] = temp
    except:
        pass

    temp = user_list[:, vocab[15]]
    temp = Counter(temp)

    temp = sorted(temp.items(), key=operator.itemgetter(1))
    temp = cat_base[temp[-1][0]]
    final_list[vocab[15]] = temp

    temp = user_list[:, vocab[22]]
    temp = Counter(temp)

    temp = sorted(temp.items(), key=operator.itemgetter(1))
    temp = cat_base[temp[-1][0]]
    final_list[vocab[22]] = temp



    return final_list



    print "getMean Done"



def mergeLibryAndPrepare(input_list,output):
    dict={}
    for i in input_list:
        with open(i, 'r') as file:
            user_dict = pickle.load(file)
        dict.update(user_dict)

    with open(output, 'wb') as file:
        pickle.dump(dict, file)





#Step 1: load edges and run the analysis
def loadList1(input_file,outputfile):
    input_file=run_folder+input_file
    outputfile=run_folder+outputfile

    with open(input_file, 'r') as file:
        [list, G] = pickle.load(file)
        node_list = nx.nodes(G)



        user_dict = dict(zip(node_list,[createUser(id) for id in node_list]))

        dead_n=0
        all_user=0
        user_degree=0
        for x in user_dict.keys():
            if user_dict[x]!=0 and 1 in user_dict[x]:
                #all_user=all_user+user_dict[x][1]
                temp=G.degree(x)
                temp=temp+0.
                user_dict[x][21]=temp/user_dict[x][1]

                #user_degree=user_degree+G.degree(x)
            if user_dict[x] == 0:
                user_dict.pop(x)
                dead_n=dead_n+1


        per=dead_n*1./len(node_list)

#        active = len(node_list)*1./all_user


        print "======================\n Threre are "+str(dead_n)+": "+str(per)
#        print "========================\n active % " + str(active)



        with open(outputfile, 'wb') as f:
            pickle.dump(user_dict, f)


#loadList("load1.txt","user_list1.txt")


def entries_to_remove(entries, the_dict):
    for key in entries:
        if key in the_dict:
            del the_dict[key]

def split(input_file):
    input_file=run_folder+input_file

    with open(input_file, 'r') as file:
        user_dict = pickle.load(file)

    crazy_dict={}
    normal={}
    for x in user_dict:
        temp=user_dict[x]
        if 'crazy' in user_dict[x]:
            crazy_dict[x]=temp
        else:
            normal[x]=temp
    print "done"

    with open("test/normal", 'w') as file:
        pickle.dump(normal,file)
    with open("test/crazy", 'w') as file:
        pickle.dump(crazy_dict,file)



#Step 2: prepare the points and run the clustering
from sklearn.cluster import KMeans
def loadList2(input_file,c_size=3):
    input_file=run_folder+input_file

    with open(input_file, 'r') as file:
        user_dict = pickle.load(file)

    v = DictVectorizer(dtype=np.float, sparse=False)
    user_list=user_dict.values()
    user_list2=[]



    entries=[0,7,11,13,22,20,"crazy","Casual","Free to Play","Full controller support","Animation & Modeling"
             "Local Multi-Player","Online Multi-Player","RPG","Simulation","Strategy","Violent","MMO","NA","NA_C","NA_G","Action","Adventure","Indie","Sexual Content","Steam Achievements","Steam Workshop","Utilities"]


    for x in user_list:
        entries_to_remove(entries, x)
    user_list2.append(x)

    user_list = v.fit_transform(user_list)
    vocab = v.vocabulary_

    l = user_list
    l = np.array(l)
    t = l[:, 1]
    #sns.distplot(t)



    points = normalizaed(user_list,vocab)
    points=points.tolist()
    save_dict={}
    save_dict["user_dict"]=user_dict

    points = np.asarray(points)
    kmeans = KMeans(n_clusters=c_size, random_state=0).fit(points)
    label=(kmeans.labels_).tolist()
    points=points.tolist()

    vocab_list = [0] * len(vocab)
    for v in vocab:
        if type(v) is int:
            temp=feature_map[v]
            vocab_list[vocab[v]]=temp
        else:
            vocab_list[vocab[v]] = v

    centrel=kmeans.cluster_centers_
    centrel=centrel.tolist()

    vv = {}
    for i in range(len(vocab_list)):
        vv[vocab_list[i]]=i

    with open(run_folder+extra+"output_float2.txt","wb") as file:
        pickle.dump([points,label,vv,centrel],file)

    with open(input_file, 'r') as file:
        user_dict = pickle.load(file)

    cluster={}
    #user_value_list=user_dict.values()
    user_list, vocab = prepareList(user_dict)
    for i in range(len(label)):
        if label[i] not in cluster:
            cluster[label[i]]=[user_list[i]]
        else:
            cluster[label[i]].append(user_list[i])



    vocab_list = [0] * len(vocab)

    for v in vocab:
        if type(v) is int:
            temp = feature_map[v]
            vocab_list[vocab[v]] = temp
        else:
            vocab_list[vocab[v]] = v

    print_list=[vocab_list]

    j=0
    for i in cluster.values():
        temp=np.array(i)
        temp=getMean(temp,vocab)

        temp[0]=len(cluster[j])*1./len(user_dict)
        print_list.append(temp)
        j=j+1


    a = np.array(print_list)
    a = a.T
    printToTable(a,outputname=run_folder+extra+"csv_out1.csv")
    save_dict["kmeans"] = kmeans
    print "done"

#Step 3: analysis the whole user group
def loadList3(input_file):
    input_file=run_folder+input_file
    #output_file=run_folder+output_file


    with open(input_file, 'r') as file:
        user_dict = pickle.load(file)
    user_list,vocab=prepareList(user_dict)

    final_list = getMean(user_list,vocab)

    vocab_list=[0]*len(vocab)

    for v in vocab:
        if type(v) is int:
            temp=feature_map[v]
            vocab_list[vocab[v]]=temp
        else:
            vocab_list[vocab[v]] = v


    print_list=[vocab_list,final_list]
    a=np.array(print_list)
    a=a.T
    printToTable(a,outputname=run_folder+extra+"csv_out2.csv")


def go_all(root):
    run_folder=root
    loadList1("graph_info.txt", "user_info.txt")
    loadList2("user_info.txt")
    loadList3("user_info.txt","none")
run_folder="myid10000/"
run_folder="run_sharedid_500/2."
run_folder="test/"
extra="1c"

#mergeLibryAndPrepare(input_list=["run_bigv_300/test.txt","run_myid_2000/test.txt","run_sharedid_500/test.txt"],output="merg.txt")
#loadList2("merg.txt",c_size=6)
#loadList3("merg.txt")

f_n = "crazy"
loadList2(f_n,c_size=3)
#embed.print_figure(run_folder)
