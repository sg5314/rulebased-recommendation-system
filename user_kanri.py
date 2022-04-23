


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        # tree_path は 空のまま
        user_name = request.form.get('username')
        name = request.form.get('name')
        tree_path = ''

        # すでに存在するユーザネームか確認
        posts = Post.query.all()
        for post in posts:
            if post.user_name == user_name:
                print('already exists')
                return render_template('create_account.html',alert='already exists')

        new_post = Post(user_name=user_name, name=name, tree_path=tree_path)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')

    else:
        # GETしてきたら，ユーザ登録画面に遷移
        return render_template('create_account.html',alert='')



# ユーザ追加画面へ遷移
@app.route('/create', methods=['GET', 'POST'])
def create():
    return render_template('create_account.html',alert='')

# ログインパス
@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        user_name = request.form.get("username")

        posts = Post.query.all()
        for post in posts:
            if post.user_name == user_name:
                print('find!!')
                if post.tree_path == '':
                    return redirect(url_for('select_scene_mode'))
                else:
                    return redirect(url_for('chose_items'))
            else:
                return redirect('/') 
    else:
        return redirect('/') 




"""
    scene_now_num = us.getNowScene()
    print(scene_now_num)
    us.add_data(True, scene_now_num)
    
    scene_now_num = us.getNowScene()
    scene_now_num = str(scene_now_num).zfill(4) + '.jpg'
    return render_template('select_scene_page.html',username = username, scene_now_num = scene_now_num)
    """