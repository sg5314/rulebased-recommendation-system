"""class User():
    def __init__(self, username):
        self.user_name = username
        self.now_scene_num = 0
        self.like_data = []
        self.not_like_data = []

    def add_data(self, flag, scene_num):
        if flag:
            # Trueの場合は好きなscene画像
            self.like_data.append(scene_num)
        else:
            self.not_like_data.append(scene_num)
        
        self.now_scene_num+=1
    
    def getNowScene(self):
        return self.now_scene_num

    def getUserName(self):
        return self.user_name

us = User('suga')
print(us.getUserName())

us = User('gasu')
print(us.user_name)"""

import numpy as np
x = np.array([[8,9,10],[11,15,18],[22,21,20]])
y = np.array(['data1','data2','data3']).reshape(3,-1)
print(x)
print(y)
print()
tar = np.hstack((x,y))
print(tar)

x = [1,2,3]
y = 'AA'
print(np.hstack((x,y)))
print()
import itertools

l1 = 'a'
l2 = ['A','B','C']
l3 = ['あ','い','う']
p = itertools.product(l1, l2, l3)
for v in p:
    print(v)

def test ():
    return [1,2,3],[1,2,3],[1,2,3]

a,b,c = test()
print(a,b,c)
