# -*- coding: utf-8 -*-
"""
Created on Mon May 29 15:35:24 2017

@author: RNPMV01
"""

import pandas as pd
import treefunctions
import networkx as nx
#from networkx.drawing.nx_agraph import graphviz_layout
#from networkx.drawing.nx_pydot import pydot_layout
#import pylab as plt
#import pydot

# "C:/ML/Baseball/Data/tran.txt"
# "C:/ML/Baseball/Data/retro_ids.txt"

class TradeTree():

    def __init__(self,data_path,id_path):
        self.df = self.import_df(data_path,id_path)

    def import_df(self,data_path,id_path):

        names = ['date',
                 'time',
                 'approx',
                 'date_sec',
                 'approx_sec',
                 'id',
                 'player',
                 'type',
                 'from-team',
                 'from-league',
                 'to-team',
                 'to-league',
                 'draft-type',
                 'draft-round',
                 'pick-number',
                 'info'
                 ]

        dtype = {'date'         :str,
                 'time'         :str,
                 'approx'       :str,
                 'date_sec'     :str,
                 'approx_sec'   :str,
                 'id'           :int,
                 'player'       :str,
                 'type'         :str,
                 'from-team'    :str,
                 'from-league'  :str,
                 'to-team'      :str,
                 'to-league'    :str,
                 'draft-type'   :str,
                 'draft-round'  :str,
                 'pick-number'  :str,
                 'info'         :str
                 }

        id_names = ['last',
                    'first',
                    'player',
                    'debut'
                    ]

        id_dtypes = {'last'     :str,
                     'first'    :str,
                     'player'   :str,
                     'debut'    :str
                     }

        df = pd.read_table(data_path,sep=',',header=None,names=names,dtype=dtype,na_values='scalar')

        ids = pd.read_table(id_path,names=id_names,dtype=id_dtypes,sep=',')

        df = df.merge(ids,how='left',on=['player'])

        df['year']      = df['date'].str[0:4].astype(int)
        df['month']     = df['date'].str[4:6].astype(int)
        df['day']       = df['date'].str[6:8].astype(int)

        df['date']      = df['date'].astype(int)
        df['player']    = df['player'].fillna('Cash')

        df['name']      = df['first'] + ' ' + df['last']
        df['name']      = df['name'].fillna(df['player'])

        return df

    def fit(self,player,direction,year_team=[]):
        if year_team != []:
            (year,to_team) = (year_team[0],year_team[1])
            transaction = treefunctions.find_transaction(self.df,player,year,to_team)
        else:
            transaction = treefunctions.get_end(self.df,player,direction,links_only=True)
        path = treefunctions.traverse(self.df,transaction,player,direction)
        self.path = path

    def draw_path(self):
        nodes,edges = treefunctions.nodes_and_edges(self.path)
        G = nx.DiGraph()
        G.add_edges_from(edges)
        #nx.draw(G,pos=pydot_layout(G)) # This prompts graphviz executables not found
        nx.draw_networkx(G)
        plt.savefig('test.png',dpi=600)
