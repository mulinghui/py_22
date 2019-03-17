from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

"""
return __import__("MySQLdb")
from . import _mysql
Reason: image not found
底层使用python2数据库导入失败

MySQLdb： python2的数据库
pymysql： python3的数据库

解决方案：
1.导入pymysql
2.使用install_as_MySQLdb将python2和python3的数据库相互转化使用


After this function is called, any application that imports MySQLdb or
    _mysql will unwittingly actually use pymysql.
任何程序中用到了MySQLdb或者_mysql就会使用pymysql数据给他进行转化
"""

"""
1.自定义项目配置类，添加数据库相应配置
2.创建app对象
3.加载配置类中相关配置信息
4.创建数据库对象
5.自定义 `模型类` 创建出数据库的`表`
"""


# 1.自定义项目配置类，添加数据库相应配置
class Config(object):
    # 以属性的形式添加配置信息
    # mysql数据库相关配置

    # 连接mysql数据库的配置
    # 格式：mysql://账号:密码@ip地址:端口/数据库名称
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/test24"

    # 关闭跟踪数据库修改操作
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 控制终端是否输出原生sql语句
    SQLALCHEMY_ECHO = False


# 2.创建app对象
app = Flask(__name__)

# 3.加载配置类中相关配置信息
app.config.from_object(Config)

# 4.创建数据库对象
db = SQLAlchemy(app)


# 角色 -- 用户 一对多的关系
# 5.自定义 `模型类` 创建出数据库的`表`
# 注意：模型类需要继承db.Model
class Role(db.Model):
    # 角色表[一]

    # 1.设置数据库的表名
    __tablename__ = "role"

    # 2.定义类属性--数据库的字段
    # id字段 db.Integer:32位的整型, primary_key=True：设置主键
    id = db.Column(db.Integer, primary_key=True)
    # name字段 db.String(64):64位的字符串  unique=True：设置唯一字段
    name = db.Column(db.String(64), unique=True)

    """
    需求：
    role.users 当前角色下面有那些用户   返回：用户列表
    user.role  当前用户处于那种角色     返回：角色对象
    
    解决方案：定义关系字段
    仅仅是方便我们查询而用到的字段 只是处于flask面向对象层面，在数据库并不存在一列
    
    backref： 反向引用字段，给另外一张表使用
    """
    users = db.relationship("User", backref="role")

    def __repr__(self):
        # 方便查询打印数据
        # print(role) ----> 角色对象object
        # print(role) ----> "Role: 1 管理员"
        return "Role: %d %s" % (self.id, self.name)


class User(db.Model):
    # 用户表[多]

    # 1.设置表名称 如果没有指明表的名称，默认值是：类名的小写user
    __tablename__ = "users"

    # 2.定义字段
    # id字段
    id = db.Column(db.Integer, primary_key=True)
    # name字段
    name = db.Column(db.String(64), unique=True)
    # 定义外键 db.ForeignKey(Role.id): 角色表的id值作为外键关联
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id))

    # 在多的一方定义关系字段
    # role = db.relationship("Role", backref="users")


    def __repr__(self):
        # 方便查询打印数据
        # print(user) ----> 用户对象object
        # print(user) ----> "User: 1 curry"
        return "User: %d %s" % (self.id, self.name)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':

    # 创建当前py文件中的所有表
    print("hhhhh")
    db.create_all()
    app.run(debug=True)