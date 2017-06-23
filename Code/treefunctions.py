# -*- coding: utf-8 -*-
"""
Created on Mon May 29 16:01:44 2017

@author: RNPMV01
"""

def is_link(df,transaction):
    if df[df['id'] == transaction]['type'].iloc[0] == 'T ':
        return True
    else:
        return False

def get_trans(df,player):
    player_trans = [tran for tran in df[df['player'] == player]['id']]
    return player_trans

def get_links(df,player):
    player_links = [tran for tran in df[df['player'] == player]['id'] if is_link(df,tran)]
    return player_links

def get_info(df,transaction,info):
    fact = df[df['id'] == transaction][info].iloc[0]
    return fact

def find_transaction(df,player,year,to_team):
    try:
        transaction = df[(df['year'] == year) & (df['to-team'] == to_team) & (df['player'] == player)]['id'].iloc[0]
    except IndexError:
        raise IndexError('This never happened...')
    return transaction

def get_team(df,trans_id,current_player,direction):
    if direction == 'from':
        team = df[(df['id'] == trans_id) & (df['player'] == current_player)]['from-team'].iloc[0]
    elif direction == 'to':
        team = df[(df['id'] == trans_id) & (df['player'] == current_player)]['to-team'].iloc[0]
    else:
        team = 'No Team'
    return team

def get_end(df,player,direction,links_only=False,transifempty=True):

    if links_only:
        player_trans = get_links(df,player)
        if player_trans == [] and transifempty:
            player_trans = get_trans(df,player)
            direction = 'forward'
    else:
        player_trans = get_trans(df,player)

    if player_trans == []:
        raise Exception('No such player exists')

    dates = [get_info(df,trans,'date') for trans in player_trans]

    if direction == 'backward':
        date = max(dates)
    elif direction == 'forward':
        date = min(dates)

    transaction = player_trans[dates.index(date)]
    return transaction

def get_players(df,transaction,player,teammates=False):
    players = []
    if teammates == False:
        direction = 'to'
    else:
        direction = 'from'
    team = get_team(df,transaction,player,direction)
    for guy in df[df['id'] == transaction]['player']:
        team1 = get_team(df,transaction,guy,'to')
        if teammates = False:
            if guy != player and team1 != team:
                players.append(guy)
        else:
            if guy != player and team1 == team:
                players.append(guy)
    return players

def find_closest(df,current,player,links_only,direction):

    if links_only == False:
        transactions = get_trans(df,player)
    else:
        transactions = get_links(df,player)

    current_date = get_info(df,current,'date')
    dates = [get_info(df,trans,'date') for trans in transactions]

    if direction == 'forward':
        closest = 99999999
        closest_transaction = current
        for i in xrange(0,len(dates)):
            if dates[i] > current_date and dates[i] < closest:
                closest = dates[i]
                closest_transaction = transactions[i]

    elif direction == 'backward':
        closest = 0
        closest_transaction = current
        for i in xrange(0,len(dates)):
            if dates[i] < current_date and dates[i] > closest:
                closest = dates[i]
                closest_transaction = transactions[i]

    return closest_transaction

def make_leaf(df,transaction,player,direction):
    leaf = {'is_leaf'       : True,
            'player'        : player,
            'date'          : get_info(df,transaction,'date')
            }

    if direction == 'backward':
        last_link = find_closest(df,transaction,player,True,'forward')

        leaf['to_team']         = get_team(df,transaction,player,direction='to')
        leaf['how_got_here']    = get_info(df,transaction,'type')
        leaf['next_link']       = {'date'       :get_info(df,last_link,'date'),
                                   'id'         :last_link,
                                   'destination':get_team(df,last_link,player,direction='to')
                                   }
    else:
        last_link = find_closest(df,transaction,player,True,'backward')

        leaf['from-team']       = get_team(df,transaction,player,direction='from')
        leaf['how_goes']        = get_info(df,transaction,'type')
        leaf['prev_link']       = {'date'   : get_info(df,last_link,'date'),
                                   'id'     : last_link,
                                   'origin' : get_team(df,last_link,player,direction='from')
                                   }
    return leaf

def make_node(df,transaction,player,direction):

    node = {'is_leaf'       : False,
            'date'          : get_info(df,transaction,'date'),
            'player'        : player,
            'traded_for'    : get_players(df,transaction,player),
            'traded_with'   : get_players(df,transaction,player,teammates=True),
            'from_team'     : get_team(df,transaction,player,direction='from'),
            'to_team'       : get_team(df,transaction,player,direction='to')
            }

    if direction == 'backward':

        last_link = find_closest(df,transaction,player,True,'forward')
        node['next_link'] = {'date'         :get_info(df,last_link,'date'),
                             'id'           :last_link,
                             'destination'  :get_team(df,last_link,player,direction='to')
                             }

    elif direction == 'forward':

        prev_link = find_closest(df,transaction,player,False,'backward')
        node['prev_link'] = {'date'         :get_info(df,prev_link,'date'),
                             'id'           :prev_link,
                             'origin'       :get_team(df,prev_link,player,direction='from')
                             }

    return node

def traverse(df,transaction,player,direction):
    if not is_link(df,transaction):
        return make_leaf(df,transaction,player,direction)

    node = make_node(df,transaction,player,direction)

    for guy in node['traded_for']:
        if guy != 'Cash':
            next_transation = find_closest(df,transaction,guy,False,direction)
            if next_transation == transaction:
                node[guy] = '%s is a minor-league bum or is still with team' %(guy)

            else:
                node[guy] = traverse(df,next_transation,guy,direction)
    return node

def nodes_and_edges(path,nodes=None,edges=None,init=True):
    if type(path) == str:
        return
    if path['is_leaf'] == True:
        return
    if init:
        nodes = []
        edges = []
        nodes.append(path['player'])

    for player in path['traded_for']:
        if player != 'Cash':
            edges.append((player,path['player']))
            if path['traded_with'] != []:
                for teammate in path['traded_with']:
                    if teammate != 'Cash' :
                        edges.append((player,teammate))
            nodes.append(player)
            nodes_and_edges(path[player],nodes=nodes,edges=edges,init=False)

    return nodes,edges
