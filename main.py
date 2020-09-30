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
        maxh = max([x.count("#") for x in text.split("\n") if "-" not in x])
    except:
        pass
    try:
        minh = min(
            [
                x.count("#")
                for x in text.split("\n")
                if x.count("#") != 0 and "-" not in x
            ]
        )
    except:
        minh = -1
    if n == 0:
        title = [x for x in text.split("\n") if "# " in x][0]
        mindmap = {}
        mindmap[title] = md_to_dict(
            text.replace(
                text[text.find(title) : text.find(title) + len(title) + 1], ""
            ).strip(),
            order,
            n + 1,
        )
        return mindmap
    elif text != "" and n <= max_depth:
        if "\n#" in text:
            mindmap = {}
            for branch in text.split("\n" + "#" * minh + " "):
                if branch.split("\n")[0] not in order:
                    mindmap[
                        "#" * minh + " " + branch.split("\n")[0].replace("#", "")
                    ] = md_to_dict("\n".join(branch.split("\n")[1:])[:-1], order, n + 1)
                else:
                    mindmap[branch.split("\n")[0]] = md_to_dict(
                        "\n".join(branch.split("\n")[1:])[:-1], order, n + 1
                    )
            return mindmap
        else:
            l = min([x.find("-") for x in text.split("\n")])
            mindmap = {}
            for branch in text.split("\n" + " " * l + "-"):
                key = branch.split("\n")[0].strip()
                if key[0] == "-":
                    key = key[1:].strip()
                mindmap[key] = md_to_dict(
                    "\n".join(branch.split("\n")[1:]), order, n + 1
                )
            return mindmap
    else:
        return {}


def get_maxh(text):
    n = 1
    while n < 7:
        if "#" * n not in text:
            return n - 1
            break
        n += 1


def gen_order(text):
    return [x.strip() for x in text.split("\n") if x.strip() != ""]


def get_config(fpath: str) -> dict:
    with open(fpath, "r") as f:
        data = [("a" + x).strip()[1:] for x in f.read().split("<!-- $$ -->\n")]

    return dict(zip(["start", "text", "line", "end"], data))


def find_path(dict_obj, key, order):
    idx = order.index(key)
    prevkey = None
    if idx == 0:
        if key[0] == "-":
            key = key[1:].strip()
        return [key]
    keys = list(dict_obj.keys())
    if key[0] == "-":
        tmpkey = key[1:].strip()
    else:
        tmpkey = key
    if tmpkey in keys:
        return [key]
    for org in order[:idx][::-1]:
        if len(org) > 0 and org[0] == "-":
            el = org[1:].strip()
        else:
            el = org
        if el in keys:
            if el == key:
                return [el]
            else:
                return [el] + find_path(
                    dict_obj[el], key, order[order.index(org) + 1 :]
                )
    else:
        raise KeyError(key)


def gen_coords(dic: dict, order: Union[list, np.array], maxh=3):
    coords = {}
    y = 0
    for n, line in enumerate(order):
        hn = 0
        if len(line) > 0 and line.replace("-", "").strip()[0] == "#":
            hn = line.count("#")
        text = line.strip()
        if text[0] == "-":
            text = text[1:].strip()[hn:].strip()
        else:
            text = text[hn:].strip()
        if len(text) > 0 and text[0] == "-":
            text = text[1:].strip()
        path = find_path(dic, line, order)
        if hn != 0:
            y = y + 20 + int(7.5 * (maxh - line.count("#") + 1))
        else:
            y = y + 25
        line += "@#$" + str(n)
        coords[line] = {
            "text": text,
            "path": path,
            "type": str(hn),
            "x": str((len(path) - 1) * 100 + 10),
            "y": str(y),
        }
    return coords


def get_srtiped_ppath(uksorder, value, parent):
    if len(value) > 0 and value[0] == "-":
        value = value[1:].strip()
    if len(parent) > 0 and parent[0] == "-":
        parent = parent[1:].strip()
    idx = uksorder.index(value)
    for val in uksorder[:idx][::-1]:
        if parent == val.split("@#$")[0][-len(parent) :]:
            return val
    else:
        return uksorder[0]


def get_ppath(ukorder, uksorder, value, parent):
    if len(value) > 0 and value[0] == "-":
        value = value[1:].strip()
    if len(parent) > 0 and parent[0] == "-":
        parent = parent[1:].strip()
    idx = uksorder.index(value)
    for val in ukorder[:idx][::-1]:

        if parent in val.split("@#$")[0][-len(parent) :]:
            print(parent + " | " + val)
            return val
    else:
        return ukorder[0]


def dict_to_mindmap(
    dic: dict, order: Union[list, np.array], name=None, config=None, n=0, maxh=3
):
    if config == None:
        config = get_config("base.html")
    elif type(config) == str:
        config = get_config(config)
    coords = gen_coords(dic, order, maxh=maxh)
    html = (
        config["start"]
        .replace("$1", coords[order[0] + "@#$0"]["text"])
        .replace(
            "$2", str(int(coords[order[-1] + "@#$" + str(len(order) - 1)]["y"]) + 100)
        )
        .replace("$3", "1920")
    )
    stripedorder = [x[1:].strip() if x[0] == "-" else x for x in order]
    unic_key_order = [x + "@#$" + str(n) for n, x in enumerate(order)]
    unic_key_striped_order = [x + "@#$" + str(n) for n, x in enumerate(stripedorder)]
    for n, org in enumerate(order):
        post = "@#$" + str(n)
        org += post
        coordsval = coords[org]
        if len(coords[org]["path"]) == 0:
            ppath = order[0]
        elif len(coords[org]["path"]) < 2:
            ppath = 0
            ppath = coords[org]["path"][ppath]
        else:
            ppath = -2
            ppath = coords[org]["path"][ppath]
        if len(org) > 0 and org[0] == "-":
            el = org[1:].strip()
        else:
            el = org
        html += "\n" + config["text"].replace("$1", coords[org]["x"]).replace(
            "$2", coords[org]["y"]
        ).replace("$3", coords[org]["type"]).replace("$4", coords[org]["text"])
        html += "\n" + config["line"].replace(
            "$1", str(int(coords[org]["x"]) - 50)
        ).replace("$2", str(int(coords[org]["y"]) - 7)).replace(
            "$3", str(int(coords[org]["x"]) - 10)
        ).replace(
            "$4", str(int(coords[org]["y"]) - 7)
        ).replace(
            "$5",
            get_l_type(
                coords[
                    order[
                        unic_key_striped_order.index(
                            get_srtiped_ppath(unic_key_striped_order, org, ppath)
                        )
                    ]
                    + "@#$"
                    + str(
                        unic_key_striped_order.index(
                            get_srtiped_ppath(unic_key_striped_order, org, ppath)
                        )
                    )
                ]["type"]
            ),
        )
        norg = order[(n + 1) % len(order)] + "@#$" + str((n + 1) % len(order))
        if len(coords[org]["path"]) > len(coords[norg]["path"]):
            html += "\n" + config["line"].replace(
                "$1", str(int(coords[org]["x"]) - 50)
            ).replace(
                "$2",
                str(
                    int(int(
                        coords[
                            order[
                                unic_key_striped_order.index(
                                    get_srtiped_ppath(
                                        unic_key_striped_order, org, ppath
                                    )
                                )
                            ]
                            + "@#$"
                            + str(
                                unic_key_striped_order.index(
                                    get_srtiped_ppath(
                                        unic_key_striped_order, org, ppath
                                    )
                                )
                            )
                        ]["y"]
                    )
                    + (
                        int(
                            coords[
                                get_ppath(
                                    unic_key_order, unic_key_striped_order, org, ppath
                                )
                            ]["type"]
                        )
                        != 0
                    )*(
                        maxh
                        - int(
                            coords[
                                get_ppath(
                                    unic_key_order, unic_key_striped_order, org, ppath
                                )
                            ]["type"]
                        )
                    )
                    % maxh * 2)+(
                        int(
                            coords[
                                get_ppath(
                                    unic_key_order, unic_key_striped_order, org, ppath
                                )
                            ]["type"]
                        )
                        == 0
                    )*(3)
                ),
            ).replace(
                "$3", str(int(coords[org]["x"]) - 50)
            ).replace(
                "$4", str(int(coords[org]["y"]) - 7)
            ).replace(
                "$5",
                get_l_type(
                    coords[
                        order[
                            unic_key_striped_order.index(
                                get_srtiped_ppath(unic_key_striped_order, org, ppath)
                            )
                        ]
                        + "@#$"
                        + str(
                            unic_key_striped_order.index(
                                get_srtiped_ppath(unic_key_striped_order, org, ppath)
                            )
                        )
                    ]["type"]
                ),
            )
    return html + "\n" + config["end"]


def get_l_type(type):
    type = int(type)
    if type == 0:
        return "9"
    else:
        return str(16 - type)


if __name__ == "__main__":
    file = "test.md"
    with open(file, "r") as f:
        text = f.read()
    order = gen_order(text)

    dic = md_to_dict("\n".join([x for x in text.split("\n") if x != ""]), order)
    maxh = get_maxh(text)

    html = dict_to_mindmap(dic, order, maxh=maxh)
    with open(file[:-3] + ".json", "w") as f:
        json.dump(dic, f, indent=1)
    with open(file[:-3] + ".html", "w") as f:
        f.write(html)
