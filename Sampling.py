import urllib, json
import networkx as nx
import Queue
import pickle
from time import gmtime, strftime


key ="72A55775E8E8C80E598D5A9F7CE8C738"
#steamid="76561197960435530"
time_threhold=1514764800


# if number of friends are smaller than this value, won't extend his/her list anymore
max_friend = 150
max_size = 300
time_threhold=1514764800

def getFrinedList(steamid):
    url="http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=" + key + "&steamid=" + steamid + "&relationship=friend"

    try:
        response=urllib.urlopen(url)
        data = json.loads(response.read())
        if "friendslist" in data:
            data = data["friendslist"]
            data = data["friends"]
        else:
            data = []
    except:
        data=[]


    return data


def addEdge(G,id,friends,weighted=False):
    for f_id in friends:
        f_id=f_id["steamid"]
        G.add_edge(int(id),int(f_id))
    return G

def enqueue(Q,friends):
    for f_id in friends:
        f_id=f_id["steamid"]
        Q.put(f_id)
    return Q





def checkGame(steamid):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key=" + key + "&format=json&steamid=" + str(
        steamid) + \
          "&include_played_free_games=1&appids_filter="
    #url = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key=" + key + "&format=json&steamid=" + str(
    #    steamid)
    temp_dict = {}
    try:
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        data = data['response']
        total_game = data.get('total_count', 0)
        total_game = data.get('game_count', 0)
        if total_game > 1:
            return True
        else:
            return False
    except:
        return False

def checkActive(steamid):
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key="+key+"&format=json&steamids="+steamid

    try:
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        data = data['response']
        if "players" in data:
            data=data["players"]
            data=data[0]
            last = data["lastlogoff"]
            if (last > time_threhold):
                return True
            else:
                return False

    except:
        return False

def addEdgeAdnEnqueue(G,Q,id,friends,weighted=False):
    for f_id in friends:
        f_id=f_id["steamid"]
        if checkGame(f_id):
        #if True:
            #if checkActive(f_id):
            if True:
                G.add_edge(int(id), int(f_id))
                Q.put(f_id)
            else:

                print "skip this one"
                print "now " + str(G.number_of_nodes())+ "nodes"
        else:
            print "skip this one"
            print "now " + str(G.number_of_nodes()) + "nodes"
    return G,Q







def sampler_1(edgelist_file,load_file,seedlist):

    Q=Queue.Queue()
    G = nx.Graph()
    friendlist = {}

    for id in seedlist:
        Q.put(id)

    while (not Q.empty() and nx.number_of_nodes(G) <= max_size):
        if (nx.number_of_nodes(G) % 100 <1):
            print "check point " + str(nx.number_of_nodes(G))

        id = Q.get()
        friends=getFrinedList(id)


        if len(friends) != 0:
            G,Q=addEdgeAdnEnqueue(G,Q,id,friends)
           #G=addEdge(G,id,friends)
        #if (len(friends) < max_friend):
        #    Q=enqueue(Q,friends)
        friendlist[id]=friends



    with open(load_file, 'w') as f:
        pickle.dump([friendlist,G], f)

    edge_G=list(G.edges())
    temp="SteamID_1\tSteamID_2\n"
    for e in edge_G:
        temp=temp+str(e[0])+"\t"+str(e[1])+"\n"

    with open(edgelist_file,'w') as f:
        f.write(temp)



#1. Start with big V
seedlist=[]





run="run_bigv_300/"
with open(run+"test", 'w') as f:
    pickle.dump(run, f)

edgelist_file=run+"dict.txt"
load_file=run+"graph_info.txt"
#1. Start with a normal user (myself)
print strftime("%Y-%m-%d %H:%M:%S", gmtime())
#my id
seedlist=["76561198116611099"]
#cs go player :
#seedlist=["76561198046160451"]

#Big V:
seedlist=['76561198015685843']
sampler_1(edgelist_file,load_file,seedlist)
print strftime("%Y-%m-%d %H:%M:%S", gmtime())


#Shared Game CS
seedlist=["76561198046160451"]