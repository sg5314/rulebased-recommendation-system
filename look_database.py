from app import Post


posts = Post.query.all()
for post in posts:
    print(post.user_name, post.name, post.tree_path)