from copy import copy
import json
import os
import re
from pprint import pprint as print
from typing import Union

import networkx as nx
import numpy as np
from dpath.util import get
from matplotlib import pyplot as plt


def md_to_dict(text, order, n=0, max_depth=100):
    try:
        maxh = max([x.count('#') for x in text.split('\n') if '-' not in x])
    except:
        pass
    try:
        minh = min([x.count('#') for x in text.split('\n')
                    if x.count('#') != 0 and '-' not in x])
    except:
        minh = -1
    if(n == 0):
        title = [x for x in text.split('\n') if '# ' in x][0]
        mindmap = {}
        mindmap[title] = md_to_dict(text.replace(
            text[text.find(title):text.find(title)+len(title)+1], '').strip(), order, n+1)
        return mindmap
    elif(text != '' and n <= max_depth):
        if('\n#' in text):
            mindmap = {}
            for branch in text.split('\n'+'#'*minh+' '):
                if(branch.split('\n')[0] not in order):
                    mindmap['#'*minh+' '+branch.split('\n')[0].replace('#', '')] = md_to_dict(
                        '\n'.join(branch.split('\n')[1:])[:-1], order, n+1)
                else:
                    mindmap[branch.split('\n')[0]] = md_to_dict(
                        '\n'.join(branch.split('\n')[1:])[:-1], order, n+1)
            return mindmap
        else:
            l = min([x.find('-') for x in text.split('\n')])
            mindmap = {}
            for branch in text.split('\n'+' '*l+'-'):
                key = branch.split('\n')[0].strip()
                if(key[0] == '-'):
                    key = key[1:].strip()
                mindmap[key] = md_to_dict(
                    '\n'.join(branch.split('\n')[1:]), order, n+1)
            return mindmap
    else:
        return {}


def gen_order(text):
    return[x.strip() for x in text.split('\n') if x.strip() != '']


def get_config(fpath: str) -> dict:
    with open(fpath, 'r') as f:
        data = [x.strip() for x in f.read().split('<!-- $$ -->\n')]

    return dict(zip(['start', 'text', 'line', 'end'], data))



def find_path(dict_obj, key,order, i=None, path=[]):
    idx=order.index(key)
    prevkey=None
    if(idx==0):
        return [key]
    keys=list(dict_obj.keys())
    if key in keys:
        return [key]
    for org in order[:idx][::-1]:
        if(len(org) > 0 and org[0] == '-'):
            el = org[1:].strip()
        else:
            el=org
        if el in keys:
            if(el==key):
                return [el]
            else:
                return [el]+find_path(dict_obj[el],key,order[order.index(org)+1:])
    else:
        raise KeyError(key)


def gen_coords(dic: dict, order: Union[list, np.array]):
    coords = {}
    for line in order:
        hn = line.count('#')
        text = line.replace('#', '').strip()
        if(len(text) > 0 and text[0] == '-'):
            text = text[1:].strip()
        path=find_path(dic, line,order)
        coords[line] = {
            'text': text,
            'path': path,
            'type': str(line.count('#')),
            'x': None,
            'y': None
        }
    return coords


def dict_to_mindmap(dic: dict, order: Union[list, np.array], name=None, config=None, n=0):
    if config == None:
        config = get_config('base.html')
    elif type(config) == str:
        config = get_config(config)
    coords=gen_coords(dic,order)
    for el in order:




file = 'minitest.md'
with open(file, 'r') as f:
    text = f.read()
order = gen_order(text)

dic = md_to_dict('\n'.join([x for x in text.split('\n') if x != '']), order)
print(gen_coords(dic, order))
html = dict_to_mindmap(dic, order)
with open(file[:-3]+'.json', 'w') as f:
    json.dump(dic, f, indent=1)
with open(file[:-3]+'.html', 'w') as f:
    f.write(html)
