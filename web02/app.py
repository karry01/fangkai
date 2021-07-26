#-*- coding:UTF-8 -*-
import torndb
import tornado.web
import os
from tornado.web import url
import Cookie


db = torndb.Connection("127.0.0.1:3306","qq",user="root",password="password")


class UploadHandler(tornado.web.RequestHandler):
    """
    get方法：渲染页面
    post方法：前后端数据交互
    """
    def get(self,uid):
        sql = 'SELECT * FROM qq where id=%s'
        a = db.get(sql,uid)
        self.render('upload.html',a=a)
    def post(self,uid):
        # picture html 页面name属性
        img_list = self.request.files.get('picture')
        for img in img_list:
            # 图片名
            filename = img['filename']
            # 二进制数据
            content = img['body']
            # 保存路径
            path = './static/images/{}'.format(filename)
            with open(path, 'wb') as f:
                f.write(content)
            url = '/static/images/{}'.format(filename)
            sql = 'UPDATE  qq  set img_url=%s  WHERE id=%s'
            db.execute(sql,url,uid)
        self.redirect(self.reverse_url('qq')) # 跳转到 'cx'
        # sql = 'SELECT * FROM qq'
        # a = db.query(sql)
        # username = self.get_cookie('user')
        # self.render('cx.html',a=a,username=username)

class Login(tornado.web.RequestHandler):
    def get(self):
        username = self.get_cookie('user')
        if username:
            # sql = 'SELECT * FROM qq'
            # a = db.query(sql)
            # self.render('cx.html',a=a,username=username)
            self.redirect(self.reverse_url('qq')) # 跳转到 'cx'
        else:
            #进入else，说明没有进行登录，渲染登录页面到浏览器中
            self.render('login.html')

    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        sql = 'SELECT * FROM qq where username=%s and password =%s'
        a = db.get(sql,username,password)
        if a:         
            self.set_cookie('user',username,expires_days=3600)
            sql = 'SELECT * FROM qq'
            a = db.query(sql)
            self.redirect(self.reverse_url('qq')) # 跳转到 'cx'
            # self.redirect('cx') # 跳转到 'cx'
            #self.render('cx.html',a=a,username=username)
        else:
            #如果用户名和密码不对就重新重定向到登录路由中
            self.write("帐号密码不对")


class adduser(tornado.web.RequestHandler):
    def get(self):
        self.render('register.html')
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        id = self.get_argument('id')
        if username.__len__() > 10 or username.__len__() <= 0 or password.__len__() <= 0:
            self.write('注册失败，用户名长度：1~10，密码长度 > 0')
            self.get()
        else:
            # username_md5 = username
            # password_md5 = password
            # select_sql = 'select username from qq '.format(username_md5)
            # db.insertmany()
            # if (username_md5,) in cursor.fetchall():
            #     db_connect.close()
            #     self.write('用户已存在，请重新输入')
            #     self.get()
            # else:
            insert_sql = "INSERT INTO qq(id,username,password)  VALUES (%s,%s,%s)"
            db.insert(insert_sql,id,username,password)
            # db_connect.commit()
            sql = 'SELECT * FROM qq'
            a = db.query(sql)
            username = self.get_cookie('user')
            self.render('cx.html',a=a,username=username)
class cx(tornado.web.RequestHandler):
    def get(self):
        sql = 'SELECT * FROM qq'
        a = db.query(sql)
        # sql = 'SELECT img_url FROM qq'
        # b = db.query(sql)
        username = self.get_cookie('user')
        self.render('cx.html',a=a,username=username)
    

class edituser(tornado.web.RequestHandler):
    def get(self,uid):
        sql = 'SELECT * FROM qq where id=%s'
        a = db.get(sql,uid)
        self.render('edituser.html',obj=a)
    def post(self,uid):
        username = self.get_argument('username')
        password = self.get_argument('password')
        sql = 'UPDATE  qq  set username =%s,password =%s  WHERE id=%s'
        uid_a=int(uid)
        db.execute(sql,username,password,uid_a)
        self.redirect(self.reverse_url('qq')) # 跳转到 'cx'


class daluser(tornado.web.RequestHandler):
    def get(self,uid):
        sql = 'SELECT * FROM qq where id=%s'
        a = db.get(sql,uid)
        self.render('de.html',obj=a)
    def post(self,uid):
        sql = 'delete from qq where id=%s'
        db.execute(sql,uid)
        self.redirect(self.reverse_url('qq')) # 跳转到 'cx'





current_path = os.path.dirname(__file__)
app = tornado.web.Application([
    url('/login', Login),
    ('/adduser', adduser),
    url('/cx',cx,name='qq'),
    ('/edituser/(?P<uid>\d)/',edituser),
    ('/deluser/(?P<uid>\d)',daluser),
    ('/sc/(?P<uid>\d)',UploadHandler)
    ],
    static_path=os.path.join(current_path, "static"),
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
)

if __name__ == '__main__':
    app.listen(9090)
    tornado.ioloop.IOLoop.current().start()