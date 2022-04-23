from flask import Flask, request, Response, abort, render_template, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
from flask_sqlalchemy import SQLAlchemy
import time
import os
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
import itertools




app = Flask(__name__)
"""login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ueser.db'
db = SQLAlchemy(app)

class Post(db.Model):
    user_name = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(30), nullable=False)#30文字以下，nullを許さない
    tree_path = db.Column(db.String(200))
"""

data_result_path = os.getcwd() + '/static/datasets_results/'

database_result_path = os.getcwd() + '/static/'

database_imgs = os.getcwd() + '/static/img/'


dir_list = sorted(os.listdir(os.getcwd() +'\static\img/table_imgs/'))

class User():
    def __init__(self, username):
        self.user_name = username
        self.now_scene_num = 0
        self.LIMIT_SCENE_NUM = 100
        self.like_data = []
        self.not_like_data = []
        self.model = None

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

def data_list(temp):
    return sorted(os.listdir(temp))



def make_data(target_data, target_name, target_label = 'table'):

    # 調査対象データ
    target_data = np.hstack((target_data, target_name))

    # 椅子のデータベース
    chair_datas = np.loadtxt(database_result_path + 'chair_database_results/chair_dataset.csv',delimiter=",")
    chair_datas = chair_datas * 100
    temp = data_list(database_imgs+'chair_imgs/')
    chair_names = np.array(temp).reshape(len(temp),-1)

    chair_datas = np.hstack((chair_datas, chair_names))


    # 机のデータベース
    table_datas = np.loadtxt(database_result_path + 'table_database_results/table_dataset.csv',delimiter=",")
    table_datas = table_datas * 100
    temp = data_list(database_imgs+'table_imgs/')
    table_names = np.array(temp).reshape(len(temp),-1)

    table_datas = np.hstack((table_datas, table_names))


    # キャビネットのデータベース
    cabinet_datas = np.loadtxt(database_result_path + 'cabinet_database_results/cabinet_dataset.csv',delimiter=",")
    cabinet_datas = cabinet_datas * 100
    temp = data_list(database_imgs+'cabinet_imgs/')
    cabinet_names = np.array(temp).reshape(len(temp),-1)

    cabinet_datas = np.hstack((cabinet_datas, cabinet_names))

    if target_label == 'chair':
        cartesian_product = list(itertools.product([target_data], table_datas, cabinet_datas))
    elif target_label == 'table':
        cartesian_product = list(itertools.product(chair_datas, [target_data], cabinet_datas))
    elif target_label == 'cabinet':
        cartesian_product = list(itertools.product(chair_datas, table_datas, [target_data]))

    # イテレータになっているので配列に入れなおす（cartesian_product）
    for con, car_pro in enumerate(cartesian_product):
        car_list = np.array([])
        for car in car_pro:
            car_list = np.append(car_list, car)
        cartesian_product[con] = car_list
    

    for con2, pro in enumerate(cartesian_product):
        num_list = []
        name_list = []
        for con3, div_data in enumerate(pro):
            if con3 != 9 and con3 != 18 and con3 != 27:
                num_list.append(div_data)
            else:
                name_list.append(div_data)
        num_list = np.append(num_list,name_list)
        cartesian_product[con2] = num_list


    cartesian_product = np.array(cartesian_product)

    return cartesian_product





def create_model(like_data_indexs, not_like_data_indexs):
    start = time.time()
    print(like_data_indexs, not_like_data_indexs)


    datas = np.loadtxt(data_result_path + 'img_dataset.csv',delimiter=",")
    print(datas)

    # 「好き」データを用意
    like_data = datas[like_data_indexs]
    like_data = like_data * 100
    like_data_label = np.full(len(like_data), 0)

    # 「嫌い」データを用意
    not_like_data = datas[not_like_data_indexs]
    not_like_data = not_like_data * 100
    not_like_data_label = np.full(len(not_like_data), 1)

    target_names = ['like_data','not_like_data']

    #X (行＝scene番号，列＝特徴量)　行方向に連結
    X = np.vstack((like_data, not_like_data))
    #Y　列方向に連結　1列
    Y = np.hstack((like_data_label, not_like_data_label))

    print('学習スタート')
    #初期値設定
    clf_bst = xgb.XGBClassifier(objective = "binary:logistic")

    # verbose : ログ出力レベル
    # パラメーターを設定
    param_grid = {'max_depth':list(range(1,10)),
                'n_estimators':[50,60,70,80,90,100],
                }

    grid_search_xg = GridSearchCV(clf_bst, param_grid = param_grid, scoring = 'accuracy',verbose=1)# cv=3
    
    grid_search_xg.fit(X, Y)

    print('ベストパラメータ：', grid_search_xg.best_params_)

    #学習
    evals_result = {}
    clf_bst_re = xgb.XGBClassifier(max_depth = grid_search_xg.best_params_['max_depth'], 
                                    n_estimators = grid_search_xg.best_params_['n_estimators'], 
                                    objective = "binary:logistic") # **grid_search_xg.best_params_

    clf_bst_re.fit(X, Y)

    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")

    return clf_bst_re



def extract_match_evaluation(check_datas):
    # マッチする組み合わせを抽出

    check_datas_num = check_datas[:,0:25]
    check_datas_name = check_datas[:,25:28]

    clf_bst_re = us.model

    # クラス1（嫌い）に属する確率
    test_predict = clf_bst_re.predict_proba(check_datas_num)

    data_proba = np.c_[test_predict, check_datas]

    proba_sort = data_proba[data_proba[:,1].argsort()[::-1],:]
    print(proba_sort[3:5])

    match_first = proba_sort[0]
    print('first>>>>>>>>>>>>>',match_first)
    match_second = proba_sort[1]
    print('second>>>>>>>>>>>>>',match_second)
    match_third = proba_sort[2]
    print("third>>>>>>>>>>>>>>",match_third)

    return match_first, match_second, match_third



def recomend_items(select_img_name):
    start = time.time()
    
    # 取り出したい机のインデックス番号
    select_img_index = int(select_img_name.replace('.jpg', ''))
    print(select_img_index)
    #target_table_index = 1

    table_datas = np.loadtxt(database_result_path + 'table_database_results/table_dataset.csv',delimiter=',')# ファイルのパスを指定
    table_datas = table_datas * 100
    table_datas = table_datas.tolist()

    target_table_data = table_datas[select_img_index]

    check_datas = make_data(target_table_data, select_img_name , target_label = 'table')

    # 最もマッチする上位3つの組み合わせ　を出力
    top_1_matches, top_2_matches, top_3_matches  = extract_match_evaluation(check_datas)

    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    print(top_1_matches[-3:], top_2_matches[-3:], top_3_matches[-3:])

    return top_1_matches[-3:], top_2_matches[-3:], top_3_matches[-3:]





@app.route('/recommendation/',methods=['GET', 'POST'])
def recommendation():
    # 推薦
    if request.method == 'POST':
        select_img_name = request.form.get('submit-form')
        print('選択した机画像',select_img_name)
        # 推薦プログラム実行
        top_1_names, top_2_names, top_3_names = recomend_items(select_img_name)
        #chair_datas, [target_data], cabinet_datas)

        # トップ3の画像の名前を送信
        return render_template('select_items_page.html', dir_list = dir_list,select_img_name=select_img_name, no1_chair=top_1_names[0],no1_cabinet=top_1_names[2],no2_chair=top_2_names[0],no2_cabinet=top_2_names[2],no3_chair=top_3_names[0],no3_cabinet=top_3_names[2])
    else:
        return redirect('/')






@app.route('/test/', methods=['GET', 'POST'])
def test():
    return render_template('select_items_page.html', dir_list = dir_list, select_img_name='',no1_chair='',no1_cabinet='',no2_chair='',no2_cabinet='',no3_chair='',no3_cabinet='')






@app.route('/selectscene/',methods=['GET', 'POST'])
def selectscene():
    if request.method == 'POST':
        if request.form['send'] == '好きです':
            us.add_data(True, us.getNowScene())
        else:
            us.add_data(False, us.getNowScene())
        
        if us.LIMIT_SCENE_NUM == us.now_scene_num:
            # 全てのscene画像のチェックが終了

            # モデルを生成（学習データより）
            model = create_model(us.like_data, us.not_like_data)

            us.model = model

            # 家具選択ページへ遷移
            # 椅子のデータ画像収集
            
            return render_template('select_items_page.html', dir_list = dir_list, select_img_name='',no1_chair='',no1_cabinet='',no2_chair='',no2_cabinet='',no3_chair='',no3_cabinet='')

        else:
            temp = str(us.getNowScene()).zfill(4)+'.jpg'
            if us.now_scene_num == (us.LIMIT_SCENE_NUM-1):
                return render_template('select_scene_page.html',scene_now_int = us.getNowScene(), scene_now_num = temp, flag = 'OK')
            else:
                return render_template('select_scene_page.html',scene_now_int = us.getNowScene(), scene_now_num = temp, flag = 'NO')

    else:
        return redirect('/')





# ログインしないと表示されないパス  scene選択ページ
# 初回ログイン or 変更時 のみ
@app.route('/')
def home():
    global us
    us = User('username')
    return render_template('select_scene_page.html',scene_now_int = us.getNowScene(), scene_now_num = str(us.getNowScene()).zfill(4)+'.jpg', flag = 'NO')






if __name__ == '__main__':
    app.run(debug=True)