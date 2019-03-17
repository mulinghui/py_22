from flask import Flask, render_template, request
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


@app.route('/')
def index():

    # 查询作者数据，查询书籍列表数据[可以借助关系字段获取每一个作者对应的书籍]
    author_list = Author.query.all()
    # 渲染模板
    return render_template("author_book.html", author_list=author_list)


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
    app.run()