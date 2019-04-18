# -*- coding: utf-8 -*-
import sys,time,logging,os
# 设置系统编码为utf8
code = sys.getdefaultencoding()
if code != 'utf8':
    reload(sys)
    sys.setdefaultencoding('utf8')
import os.path
import re,hashlib,torndb
import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado.options import define, options
import tornado.httpserver
import tornado.autoreload
from math import ceil
from Pagination import Pagination
import urlparse
from urllib import unquote
from datetime import datetime
# from furl import furl
import re
define("port", default=9003, help="run on the given port", type=int)
define("mysql_host", default="120.77.170.45", help="blog database host")
define("mysql_database", default="db_fylog", help="blog database name")
define("mysql_user", default="root", help="blog database user")
define("mysql_password", default="deng", help="blog database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers=[
            (r'/login',LoginHandler),
            (r'/data',DataHandler),
            (r'/show',ShowHandler),
            (r'/IPshow',IPHandler),
            (r'/booking',BookingHandler),
            (r'/listbook',BookinglistHandler),
            (r'/testregister',TestregisterHandler)
            ]

        settings =dict(
            blog_title=u'移动定位系统',
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
           # ui_modules={"Entry": EntryModule},
            xsrf_cookies=False,
            cookie_secret="__TODO:_GENERATEf_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/login",
            autoescape=None,
            debug=True)
        tornado.web.Application.__init__(self,handlers,**settings)
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password,time_zone="+8:00")

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        userid = self.get_secure_cookie("userinfo")
        return self.get_secure_cookie("user_id")

class BookinglistHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user_name = self.get_secure_cookie("user_name")
        showmsg = self.get_argument("showmsg","")
        page= int(self.get_argument("page",1))
        pre_page=30

        count =self.db.get('''SELECT count(*) count FROM t_booking''')
        pagination = Pagination(page, pre_page, count.count, self.request)
        startpage = (page-1) * pre_page
        data_order = self.db.query('''
            SELECT  *  FROM t_booking
            order by created_at desc limit %s,%s
            ''',startpage,pre_page)

        return self.render('booklist.html',pagination=pagination,user_name=user_name,msg="",data_order=data_order)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        userid = self.get_secure_cookie("userinfo")
        return self.get_secure_cookie("user_id")

class ShowHandler(BaseHandler):
    def getkeyword(self,url):
        if "baidu" in url:
            mat = re.findall( r'&word=([\S\s]*?)&', url)
            if mat:
                 return unquote(str(mat[0]))
            else:
                return ""
        else:
            return ""
    def getclient(self,ua):
        if "iPhone" in ua:
           return "iPhone"
        elif "Android" in ua:
           return "Android"
        elif "iPad" in ua:
           return "iPad"
        else:
            return "PC"
    @tornado.web.authenticated
    def get(self):
        user_name = self.get_secure_cookie("user_name")
        showmsg = self.get_argument("showmsg","")
        page= int(self.get_argument("page",1))
        keyword = self.get_argument("keyword","")
        curr_url = self.get_argument("curr_url","")
        start = self.get_argument("start", datetime.now().strftime('%Y-%m-%d 00:00:00') )
        end = self.get_argument("end", datetime.now().strftime('%Y-%m-%d 23:59:59'))
        pre_page=30
        if curr_url:
            count =self.db.get('''SELECT count(*) count FROM t_data
             where  (curr_url like %s or ip like %s) AND   created_at between
                 %s and  %s ''',"%" + curr_url + "%","%" + curr_url + "%",start,end)
            pagination = Pagination(page, pre_page, count.count, self.request)
            startpage = (page-1) * pre_page
            data_order = self.db.query('''
                SELECT  *  FROM t_data where (curr_url like %s or ip like %s) and created_at between
                 %s and  %s order by created_at desc limit %s,%s
                ''',"%" + curr_url + "%","%" + curr_url + "%",start,end,startpage,pre_page)
        else:
            count =self.db.get('''SELECT count(*) count FROM t_data where  created_at between
                 %s and  %s
               ''',start,end,)
            pagination = Pagination(page, pre_page, count.count, self.request)
            startpage = (page-1) * pre_page
            data_order = self.db.query('''
                SELECT  *  FROM t_data where created_at between
                 %s and  %s
                order by created_at desc limit %s,%s
                ''',start,end,startpage,pre_page)

        return self.render('list.html',start=start,end=end,getclient=self.getclient,getkeyword=self.getkeyword,pagination=pagination,user_name=user_name,msg="",data_order=data_order,curr_url=curr_url)


class IPHandler(BaseHandler):
    def getkeyword(self,url):
        if "baidu" in url:
            mat = re.findall( r'&word=([\S\s]*?)&', url)
            if mat:
                 return unquote(str(mat[0]))
            else:
                return ""
        else:
            return ""
    def getclient(self,ua):
        if "iPhone" in ua:
           return "iPhone"
        elif "Android" in ua:
           return "Android"
        elif "iPad" in ua:
           return "iPad"
        else:
            return "PC"
    @tornado.web.authenticated
    def get(self):
        user_name = self.get_secure_cookie("user_name")
        showmsg = self.get_argument("showmsg","")
        page= int(self.get_argument("page",1))
        keyword = self.get_argument("keyword","")
        curr_url = self.get_argument("curr_url","")
        start = self.get_argument("start", datetime.now().strftime('%Y-%m-%d 00:00:00') )
        end = self.get_argument("end", datetime.now().strftime('%Y-%m-%d 23:59:59'))
        data_total = []
        if  curr_url:
            data_total = self.db.query(
                """select ip,count(*) all_count
                 from t_data where created_at between
                 %s and  %s  and curr_url like %s group by ip order by count(*) desc """,start,end,"%" + curr_url + "%")

        else:

            data_total = self.db.query(
                """select ip,count(*) all_count
                 from t_data where created_at between
                 %s and  %s   group by ip order by count(*) desc """,start,end)

        return self.render('iplist.html',data_total=data_total,curr_url=curr_url,start=start,end=end)



class BookingHandler(BaseHandler):
    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    def get(self):
        return self.render("test.html")
    def post(self):
        region = self.get_argument("region","")
        industry = self.get_argument("industry","")
        phone = self.get_argument("phone")
        curr_url = self.get_argument("curr_url","N")
        name = self.get_argument("name","")

# window.location.href
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        if  not phone:
            self.write("手机号不能为空哦")
        else:

            result = self.db.execute("""
                INSERT INTO `t_booking` (name, `industry`, `region`, `phone`, `ip`, `curr_url`, `created_at`)
                VALUES
                    (%s, %s, %s, %s, %s, %s, now());

                    """,name,industry,region,phone,remote_ip,curr_url)
            if result > 0:
                self.write("0")
            else:
                self.write("提交失败,请稍候再试!")


class TestregisterHandler(BaseHandler):
    
    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    def get(self):
        page= int(self.get_argument("page",1))
        pre_page=30
        count=self.db.get('''
         select count(*) count from t_text_register
        ''')
        count =self.db.get('''SELECT count(*) count FROM t_booking''')
        pagination = Pagination(page, pre_page, count.count, self.request)
        startpage = (page-1) * pre_page
        text_register=self.db.query('''
        select * from t_text_register order by created_at desc
        ''')
        return self.render('testregister.html',
        text_register=text_register,
        pagination=pagination)
    def post(self):
        dt=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        address=self.get_argument('address','0')
        reg_type=self.get_argument('type','0')
        demand=self.get_argument('demand','0')
        component=self.get_argument('component','0')
        name=self.get_argument('name','')
        tel=self.get_argument('tell','')
        result=self.db.execute('''
        insert into t_text_register(address,type,demand,component,name,tel,created_at)
        values(%s,%s,%s,%s,%s,%s,%s)
        ''',address,reg_type,demand,component,name,tel,dt)
        self.write(str(result))




class DataHandler(BaseHandler):
    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        return self.render("user.html")

    def qs(self,url):
        query = urlparse.urlparse(url).query
        return dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])


    def post(self):
        ref = self.get_argument("ref","")
        ip = self.get_argument("ip","")
        curr_url = self.get_argument("curr_url")
        keyword = ""
        source_from ="直接"

        print ref
        if "m.baidu.com" in ref:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['word'][0]
                print keyword
            except:
                pass
        elif "www.baidu.com" in ref:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['wd'][0]
                print keyword
            except:
                pass
        elif "wap.sogou.com" in ref:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['keyword'][0]
                print keyword
            except:
                pass
        elif "www.so.com" in ref:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['q'][0]
                print keyword
            except:
                pass
        elif "so.m.sm.cn" in ref:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['q'][0]
                print keyword
            except:
                pass
        else:
            if not keyword:
                try:
                    parsed = urlparse.urlparse(str(ref))
                    keyword = urlparse.parse_qs(parsed.query)['query'][0]
                    print keyword
                except:
                    pass

        if not keyword:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['word'][0]
                print keyword
            except:
                pass
        if not keyword:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['q'][0]
                print keyword
            except:
                pass
        if not keyword:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['keyword'][0]
                print keyword
            except:
                pass
        if not keyword:
            try:
                parsed = urlparse.urlparse(str(ref))
                keyword = urlparse.parse_qs(parsed.query)['query'][0]
                print keyword
            except:
                pass


        try:
            parsed_uri = urlparse.urlparse(ref)
            source_from = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        except:
            pass


        ua = self.get_argument("ua","")
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        self.db.execute("""
                INSERT INTO `t_data` ( `ip`, `curr_url`, `ref`, `keyword`, `source_from`, `created_at`,ua)
                VALUES( %s, %s, %s, %s, %s,now(),%s);
            """,remote_ip,curr_url,ref,keyword,source_from,ua)

        return self.write("0")

class LoginHandler(BaseHandler):

    def get(self):
        tag = self.get_argument("tag","")
        if tag=="logout":


            self.clear_all_cookies();
                # self.set_secure_cookie("uid" , str(user.id))
                #               self.set_secure_cookie("username",username)

                #               self.set_secure_cookie("role",home_user_group.tag)
                #               self.set_secure_cookie("user_tag",user.user_tag)
            #self.clear_cookie("zone")
            #self.clear_cookie("housing")
            self.redirect("/login")
        else:
            error=None
            self.render('login.html',error=error)

    def post(self):
        f_email = self.get_argument("username",None)
        f_password = self.get_argument("password",None)

        error=None

        if not f_email:
            error="您的帐户不能为空."
        elif not f_password:
            error="您的密码不能为空."

        elif self.authenticate(f_email,f_password):
            t_user = self.get_user_info(f_email)

            if t_user:
                self.set_secure_cookie("user_id",str(t_user.f_id), expires_days=60)
                self.set_secure_cookie("user_name",str(t_user.f_email), expires_days=60)



                self.redirect(self.get_argument('next','/show'),permanent=True)
            else:
                error="您的帐户已经过期,请与我们联系."
        else:
            error="您的登录信息不正确,请效验后再重试."

        self.render('login.html',error=error)

    def get_user_info(self,f_email):
        t_user = self.db.get('''
                SELECT * FROM t_user
                WHERE f_email=%s
            ''',f_email)
        return t_user
    def validate(self, f_email):
        regex = re.compile(r'^[\w\.=-]+@[\w\.-]+\.[\w]{2,3}$')
        return regex.match(f_email)

    def authenticate(self,username,password):
        hashPassword = self.db.get('SELECT f_pass FROM t_user WHERE f_email = %s', username)
        if hashPassword:
            return password == hashPassword.f_pass

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)


    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()

if __name__=="__main__":
    print "web starting.....http://localhost:9003"
    main()