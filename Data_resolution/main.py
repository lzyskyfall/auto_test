class component(object):
    def __init__(self, bounds, component_class,pointer, parent):
        self.bounds = bounds
        self.pointer=pointer
        self.component_class = component_class
        self.parent = parent
        self.children = []

    def __eq__(self, other):
        return self.bounds == other.bounds and self.component_class == other.component_class  # 如果两个bounds和class相等则他们相等


import copy
import json
import os
import numpy as np
import re


error_num = 0
total_num = 0
right_num = 0
uncertain_num = 0
zero = 0
uncertain_num_collect = {}
zero_collect = {}
error_collect = {}
final_collect = {}


# 读取数据
def read():
    f = os.listdir('./ATMobile2020-1')
    res = {}
    for file in f:
        if not file.endswith('.json'):
            continue
        data = json.load(open(os.path.join('ATMobile2020-1', file), 'r', encoding='utf-8'))
        res[file.replace('.json', '')] = data
    return res


# 递归查找children
def dfs(root: component, data):
    if 'children' not in data:
        return
    global uncertain_num
    global error_num

    for child in data['children']:

        if child is None:
            continue
        t = r'[a-zA-Z0-9]*\.[a-zA-Z0-9]*'
        if re.match(t, child["class"]) is None:
            uncertain_num += 1
            uncertain_num_collect[child["pointer"]] = child["class"]
        assert child['class'] is not None
        assert 'bounds' in child
        assert 'class' in child
        root_dis(child)
        node = component(child['bounds'], child['class'], child['pointer'], root)
        root.children.append(node)
        dfs(node, child)
    de_children = []
    for c in root.children:
        if c not in de_children:
            de_children.append(c)
    root.children = de_children


# 解析数据
def de_data(data):
    root = data['activity']['root']
    root_dis(root)
    root_node = component(root['bounds'], root['class'], root['pointer'], None)
    dfs(root_node, root)
    return root_node


def root_dis(root):
    global error_num  # 冗余
    global total_num
    global right_num
    global uncertain_num  # class不存在
    global zero  # bounds is zero
    array_zero = np.array([0, 0, 0, 0])
    if 'parent' in root:
        total_num += 1
        array_a = np.array(root['bounds'])
        if (array_a == array_zero).all() is False:
            right_num += 1
        else:
            zero += 1
            zero_collect[root['pointer']] = root["class"]
    else:
        total_num += 1
        array_a = np.array(root['bounds'])
        if (array_a == array_zero).all() is False:
            right_num += 1
        else:
            zero += 1
            zero_collect[root['pointer']] = root["class"]
        left_abscissa = root['bounds'][0]
        left_ordinate = root['bounds'][1]
        right_abscissa = root['bounds'][2]
        right_ordinate = root['bounds'][3]
        if left_abscissa < 0 or right_ordinate < 0 or left_ordinate < 0 or right_abscissa < 0:
            error_num += 1
            error_collect[root['pointer']] = root["class"]
        elif right_abscissa < left_abscissa or right_ordinate < left_ordinate:
            error_num += 1
            error_collect[root['pointer']] = root["class"]


def judgeme(root):
    global uncertain_num_collect
    global error_collect
    global zero_collect
    global uncertain_num
    global error_num
    global final_collect
    if root.pointer in uncertain_num_collect or root.pointer in error_collect or root.pointer in zero_collect:
        print(uncertain_num_collect)
        print(error_collect)
        print(zero_collect)

    else:
        final_collect[root.component_class] = root.bounds
    for child in root.children:
        if child is None:
            continue
        judgeme(child)


# 初始化变量
def clean():
    global uncertain_num_collect
    global error_collect
    global zero_collect
    global uncertain_num
    global error_num
    global final_collect
    global zero
    final_collect.clear()
    uncertain_num_collect.clear()
    zero_collect.clear()
    error_collect.clear()
    zero = 0
    uncertain_num = 0
    error_num = 0


datas = read()
root_nodes = []
num = 0
f = open("result.json", 'w', encoding='utf-8')
final_collects = {}
for id in datas:
    print(id)
    root_nodes.append(de_data(datas[id]))
    judgeme(root_nodes[num])
    print(final_collect)
    final_collects[id] = copy.deepcopy(final_collect)
    clean()
json.dump(final_collects, f, ensure_ascii=False)
