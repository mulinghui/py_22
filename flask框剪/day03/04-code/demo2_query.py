from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

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
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/query24"

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
    # email字段
    email = db.Column(db.String(64), unique=True)
    # password字段
    password = db.Column(db.String(64))
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
    print("——————————")
    # 删除数据库表
    db.drop_all()
    # 创建数据库表
    db.create_all()

    # 添加测试数据

    # 添加管理员角色
    ro1 = Role(name="admin")
    db.session.add(ro1)
    db.session.commit()

    # 添加普通用户角色
    ro2 = Role(name="user")
    db.session.add(ro2)
    db.session.commit()


    # 添加测试用户数据
    us1 = User(name='wang', email='wang@163.com', password='123456', role_id=ro1.id)
    us2 = User(name='zhang', email='zhang@189.com', password='201512', role_id=ro2.id)
    us3 = User(name='chen', email='chen@126.com', password='987654', role_id=ro2.id)
    us4 = User(name='zhou', email='zhou@163.com', password='456789', role_id=ro1.id)
    us5 = User(name='tang', email='tang@itheima.com', password='158104', role_id=ro2.id)
    us6 = User(name='wu', email='wu@gmail.com', password='5623514', role_id=ro2.id)
    us7 = User(name='qian', email='qian@gmail.com', password='1543567', role_id=ro1.id)
    us8 = User(name='liu', email='liu@itheima.com', password='867322', role_id=ro1.id)
    us9 = User(name='li', email='li@163.com', password='4526342', role_id=ro2.id)
    us10 = User(name='sun', email='sun@163.com', password='235523', role_id=ro2.id)
    # 批量添加
    db.session.add_all([us1, us2, us3, us4, us5, us6, us7, us8, us9, us10])
    db.session.commit()

    """
    User.query 是一个基本查询对象 flask_sqlalchemy.BaseQuery
    查询所有用户数据
    users = User.query.all()
    
    
    
    查询有多少个用户
    len(users) = User.query.count()
    
    
    查询第id=1的用户
    user1 = User.query.get(1)
    

    查询id为4的用户[3种方式]
    User.query.get(4)
    
    filter_by：精确过滤，相当于where，后面跟查询条件
    users[0]=User.query.filter_by(id=4).first()
    
    filter: 广泛查询，后面跟查询条件
    注意：必须指明字段来源， == 符号做比较
    User.query.filter(User.id==4).first() 

    
    查询名字结尾字符为g的所有数据[开始startswith /包含contains]
    filter or filter_by 返回是一个查询集，可以看做一句待执行的ＳＱＬ语句
    User.query.filter(User.name.endswith('g')).all() 
    
    User.query.filter(User.name.contains('g')).all() 
    
    
    查询名字不等于wang的所有数据[2种方式]
    
    User.query.filter(User.name != "wang").all() 
    
    
    # 导入方法：from sqlalchemy import not_,or_,and_ 
    
    User.query.filter(not_(User.name == "wang")).all()
    
    
    查询名字和邮箱都以 li 开头的所有数据[2种方式]
    
    # 常用
    User.query.filter(User.name.startswith('li'), User.email.startswith('li')).all() 
    
    User.query.filter(and_(User.name.startswith('li'), User.email.startswith('li'))).all()
    

    查询password是 `123456` 或者 `email` 以 `itheima.com` 结尾的所有数据
    
    # 注意需要导入 or_() 函数
    User.query.filter(or_(User.password == "123456", User.email.endswith('itheima.com'))).all()
    
    查询id为 [1, 3, 5, 7, 9] 的用户列表
    
    # in_(列表) ：判断某个值是否在列表中
    User.query.filter(User.id.in_([1,3,5,7,9])).all() 
    
    查询name为liu的角色数据
    
    # 使用关系字段role关联查询
    User.query.filter(User.name == "liu").first().role 
    
    查询所有用户数据，并以邮箱降序排序
    
    # order_by(需要排序的字段名称) ， desc():降序排序
    User.query.order_by(User.email.desc()).all() 
    

    每页3个，查询第2页的数据[重点]
    
    # paginate()分页函数： 参数1：当前页码， 参数2：每一页多少条数据
    # 返回值：分页对象
    paginate = User.query.paginate(2, 3)
    
    # 获取当前页码的所有数据 [列表]
    paginate.items
    # 获取当前页码
    paginate.page
    # 获取总页数
    paginate.pages
    
    
    
    """

    app.run(debug=True)