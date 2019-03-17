from flask import Flask, render_template, request, redirect, url_for
# 1.导入数据库相关类
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

"""
1.导入数据库相关类
2.自定义项目配置类
3.创建app对象并且加载项目配置信息
4.创建数据库对象db
5.自定义模型类 
"""
# 2.自定义项目配置类


class Config(object):
    # 开启debug模式
    DEBUG=True
    # mysql数据库连接配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/author_book24"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


# 3.创建app对象并且加载项目配置信息
app = Flask(__name__)
app.config.from_object(Config)

# 4.创建数据库对象db
db = SQLAlchemy(app)


# 5.自定义模型类
# 作者表[一] --  图书表[多]
class Author(db.Model):
    """作者表"""
    __tablename__ = "author"

    # id字段
    id = db.Column(db.Integer, primary_key=True)
    # name字段
    name = db.Column(db.String(48), unique=True)
    # 关系字段，方便查询
    # author.books : 当前作者编写的书籍[书籍对象列表]
    # book.author : 当前书籍属于哪个作者[作者对象]
    books = db.relationship("Book", backref="author")

    def __repr__(self):
        # 格式输出
        return "Author:  %d %s" % (self.id, self.name)


class Book(db.Model):
    """书籍表"""
    __tablename__ = "books"

    # id字段
    id = db.Column(db.Integer, primary_key=True)
    # name字段
    name = db.Column(db.String(48), unique=True)
    # 定义外键
    author_id = db.Column(db.Integer, db.ForeignKey(Author.id))

    # 关系字段如果在多的一方里面定义的写法：
    # author = db.relationship("Author", backref="books")

    # 关系字段，方便查询
    def __repr__(self):
        # 格式输出
        return "Book:  %d %s" % (self.id, self.name)


# 修改请求方式运行GET&POST请求
@app.route('/', methods=["GET", "POST"])
def index():

    if request.method == "POST":
        # POST请求：添加作者，添加书籍

        # 1.获取参数
        # 1.1 author_name:作者名称， book_name:书籍名称
        author_name = request.form.get("author")
        book_name = request.form.get("book")

        # 2.参数校验
        # 2.1 判断作者书籍名称是否有值
        if not all([author_name, book_name]):
            print("参数不足")
            return "参数不足"

        # 3.逻辑处理
        # 3.1 根据作者名称查询作者是否存在
        author = Author.query.filter(Author.name == author_name).first()

        # 3.2 作者不存在，先添加作者，再添加书籍
        if not author:
            # 先添加作者，并且给属性赋值
            new_author = Author()
            new_author.name = author_name
            # 添加到数据库
            db.session.add(new_author)
            db.session.commit()

            # 再添加书籍
            new_book = Book()
            new_book.name = book_name
            # 注意：作者必须先添加到数据库后，new_author.id才有值
            # 给书籍的外键赋值
            new_book.author_id = new_author.id

            # 添加到数据库
            db.session.add(new_book)
            db.session.commit()

        # 3.3 作者存在，只需添加书籍
        else:
            # 3.4 根据书籍名称查询书籍是否存在
            book = Book.query.filter(Book.name == book_name).first()
            # 3.5 书籍不存在，添加书籍
            if not book:
                # 创建书籍对象，并给各个属性赋值
                new_book = Book()
                new_book.name = book_name
                # 将作者和数据形成关联
                new_book.author_id = author.id

                # 添加到数据库
                db.session.add(new_book)
                db.session.commit()
            else:
                # 3.5 书籍存在，提示不能重复添加
                print("书籍存在,不能重复添加")

        # 上述操作会修改数据库数据，但是页面还未更新，必须重新查询数据并渲染展示

    # GET请求：查询作者数据，模板展示
    # 查询作者数据，查询书籍列表数据[可以借助关系字段获取每一个作者对应的书籍]
    author_list = Author.query.all()
    # 渲染模板
    return render_template("author_book.html", author_list=author_list)


# 127.0.0.1:5000/delete_book/书籍id
@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):

    # 1.根据id查询书籍是否存在
    book = None
    try:
        # 防止在查询数据库的时候数据库报错
        book = Book.query.get(book_id)
    except Exception as e:
        print(e)
        return "查询异常"

    # 2.书籍存在，删除书籍
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            # 数据库回滚
            db.session.rollback()
    # 3.书籍不存在，提示不能删除
    else:
        print("书籍不存在，不能删除")

    # 注意：上述操作会删除数据库数据，但是页面还未更新，必须重新查询数据并渲染展示
    # 可以重定向到首页
    return redirect(url_for("index"))


# 127.0.0.1:5000/delete_author/作者id
@app.route('/delete_author/<int:author_id>')
def delete_author(author_id):
    # 删除作者接口

    # 1.根据作者id查询作者是否存在
    author = None
    try:
        # 防止在查询数据库的时候数据库报错
        author = Author.query.get(author_id)
    except Exception as e:
        print(e)
        return "查询异常"

    # 2.作者存在，先删除书籍，再删除作者
    if author:
        # 先删除书籍，
        for book in author.books:
            db.session.delete(book)

        # 再删除作者
        db.session.delete(author)

        # 数据提交到数据库失败的情况才需要回滚
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            # 数据库回滚
            db.session.rollback()

    else:
        # 3.作者不存在，不允许删除
        print("作者不存在，不允许删除")

    # 注意：上述操作会删除数据库数据，但是页面还未更新，必须重新查询数据并渲染展示
    # 可以重定向到首页
    return redirect(url_for("index"))


if __name__ == '__main__':
    db.drop_all()
    db.create_all()

    # 生成数据
    au1 = Author(name='老王')
    au2 = Author(name='老尹')
    au3 = Author(name='老刘')
    # 把数据提交给用户会话
    db.session.add_all([au1, au2, au3])
    # 提交会话
    db.session.commit()

    bk1 = Book(name='老王回忆录', author_id=au1.id)
    bk2 = Book(name='我读书少，你别骗我', author_id=au1.id)
    bk3 = Book(name='如何才能让自己更骚', author_id=au2.id)
    bk4 = Book(name='怎样征服美丽少女', author_id=au3.id)
    bk5 = Book(name='如何征服英俊少男', author_id=au3.id)
    # 把数据提交给用户会话
    db.session.add_all([bk1, bk2, bk3, bk4, bk5])
    # 提交会话
    db.session.commit()
    print("-------")
    app.run(debug=True)