import re
import json
import os
from pprint import pprint
import networkx as nx
from matplotlib import pyplot as plt
import numpy as np

def md_to_dict(text,n=0,max_depth=100):
    try:
        maxh=max([x.count('#') for x in text.split('\n') if '-' not in x])
    except:
        pass
    try:
        minh=min([x.count('#') for x in text.split('\n') if x.count('#')!=0 and '-' not in x])
    except:
        minh=-1
    if(n==0):
        title=[x for x in text.split('\n') if '# ' in x][0]
        mindmap={}
        mindmap[title]=md_to_dict(text.replace(text[text.find(title):text.find(title)+len(title)+1],'').strip(),n+1)
        return mindmap
    elif(text!='' and n <=max_depth):
        if('\n#' in text):
            mindmap={}
            for branch in text.split('\n'+'#'*minh):
                mindmap['#'*minh+branch.split('\n')[0].replace('#','')]=md_to_dict('\n'.join(branch.split('\n')[1:])[:-1],n+1)
            return mindmap
        else:
            l=min([x.find('-') for x in text.split('\n')])
            mindmap={}
            for branch in text.split('\n'+' '*l+'-'):
                key=branch.split('\n')[0].strip()
                if('m' in key):
                    print(key)
                if(key[0]=='-'):
                    key=key[1:].strip()
                mindmap[key]=md_to_dict('\n'.join(branch.split('\n')[1:]),n+1)
            return mindmap
    else:
        return {}

file = 'test.md'
with open(file,'r') as f:
    text=f.read()

dic=md_to_dict('\n'.join([x for x in text.split('\n') if x!='']))
with open(file[:-3]+'.json','w') as f:
    json.dump(dic,f,indent=1)
