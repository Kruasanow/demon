
from asyncio.windows_events import NULL
from pickle import NONE
from time import ctime
from flask import Flask, current_app, make_response, render_template, sessions, url_for, request, flash, session, redirect, abort, g
import sqlite3
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from cloudipsp import Api, Checkout
import datetime
import hashlib

DEBUG = True 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbname.db' #31.25
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config.update(SECRET_KEY=os.urandom(24))
app.secret_key = 'hasgj214nfsn12213nrnm,5o12'

db = SQLAlchemy(app)

# >>> from main import db 
# >>> db.create_all()

class rest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rest_name = db.Column(db.String(25), nullable=False, unique=True)
    rest_secname = db.Column(db.String(50), nullable=False, unique=True)
    img = db.Column(db.String(255), nullable=False)
    number = db.Column(db.String(11), nullable=False)
    contact1 = db.Column(db.String(255), nullable=False)
    contact2 = db.Column(db.String(255), nullable=False)
    contact3 = db.Column(db.String(255), nullable=False)
    fID = relationship("users", back_populates="rlt")
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<table is  %r>' % (self.id)

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    psw = db.Column(db.String(100), nullable=False)
    active = db.Column(db.String(40))
    rlt = relationship("rest", back_populates="fID", uselist=False)
    rlt1 = db.Column(db.Integer, db.ForeignKey("table.id"))
    rlt11 = relationship("table", back_populates="chld")
    

    def __init__(self,*args,**kwargs):
        super(users,self).__init__(*args,**kwargs)

class table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idr = db.Column(db.Integer)
    human = db.Column(db.String(255))
    status = db.Column(db.Integer, nullable=False, default=0)
    cost = db.Column(db.Integer, nullable=False, default=0)
    comment = db.Column(db.String(255))
    image = db.Column(db.String(255))
    datatime = db.Column(db.String(255))
    rname = db.Column(db.String(255))
    chld = relationship("users", back_populates="rlt11")

    def __repr__(self):
        return '<table is  %r>' % (self.id)


hight_menu = [
        {"menu": 'login', "url": 'login'},
        {"menu": 'regestration', "url": 'regestration'},
        {"menu": 'about us', "url": 'about_us'}
    ]

class MyUserAdmin(BaseView):
    @expose("/")    
    def first(self):
        return self.render("dimooon/admin/sec.html")
    def __init__(self, session):
        super(MyUserAdmin, self).__init__(users, session)


# ADMIN #
admin = Admin(app)
admin.add_view(ModelView(users, db.session))
admin.add_view(ModelView(table, db.session))
admin.add_view(ModelView(rest, db.session))

@app.route('/', methods = ['get','post'])
def index():
    print(url_for('index'))
    tables = table.query.order_by(table.id).all()
    head_rest = rest.query.order_by(rest.id).all()

    if request.method == "POST":
        global ident
        ident = request.form['choose_rest']
        it = ident
        if int(it) < 18:
            return redirect("/")
        session["ident"] = rest.query.all()[0].rest_name

        arr = []
        tall = table.query.all()
        t = session['ident']

        for i in range(len(tall)): # 10 -18
            if tall[i].rname == t:
                arr.append(tall[i].id) 
        arr2 = []
        for i in range(len(arr)): # 1 - 8
            arr2.append(i+1)
        tabs = []
        for i in range(len(arr2)):
            tabs.append(table.query.get(arr[i]))
            tabs[i].idr = i + 1
            db.session.commit()
          
        try:
            info = rest.query.order_by(rest.id).filter(rest.rest_name == ident).all()
        except:
            return redirect('/')
        # if info == []:
        #     return render_template('index.html', Title = 'Добро Пожаловать!',var = 1)
        return render_template('index.html', Title = 'Добро Пожаловать!', ur = 1, arr2 = arr2, arr = arr, head = head_rest, state1 = "Свободен", state2 = "Занят", var = 2, info = info, info2 = info, menu = hight_menu, tables = tables, answer_true = "Занят", answer_false = "Свободен")
    return render_template('index.html', Title = 'Добро Пожаловать!',ur = 0, var = 3, rest = rest.query.order_by(rest.id).all())

@app.route('/login', methods=['get', 'post'])
def login():
    print(url_for('login'))
    try:
        info = rest.query.order_by(rest.id).filter(rest.rest_name == session['ident']).all()
    except:
        return redirect('/')
    if request.method == "POST":

        check_name = request.form['name']
        session['nameofuser'] = check_name
        check_mail = request.form['email']
        check_pass = request.form['psw']
        check_pass_hash = hashlib.sha256(check_pass.encode()).hexdigest() 

        if session['nameofuser'] == 'admin' and check_pass == '11111111' and check_mail == "11111111@":
            return redirect('/admin')

        get_logged_name = users.query.filter(users.name == check_name).all()
        get_logged_email = users.query.filter(users.email == check_mail).all()
        get_logged_pass = users.query.filter(users.psw == check_pass_hash).all()
        print(get_logged_pass)

        if len(get_logged_name) == 0 or len(get_logged_email) == 0 or len(get_logged_pass) == 0:
            print('1')
            return redirect(url_for('login'))
            # or check_password_hash(get_logged_pass, check_pass) == True
        elif get_logged_email == check_mail or get_logged_name == check_name or get_logged_pass == check_pass:
            print('2')
            return redirect(url_for('user', username = check_name))   

        else:
            print('3')
            with app.test_request_context():
                return redirect(url_for('user', username = check_name))


    return render_template('login.html', Title = 'Авторизация', info = info, info2 = info)


@app.route('/regestration', methods = ["POST","GET"])
def regestration():
    print(url_for('regestration'))
    info = rest.query.order_by(rest.id).filter(rest.rest_name == session["ident"]).all()
    if request.method == "POST":
        name = request.form["name"]
        if len(name) < 4:
            return redirect(url_for('regestration'))
        email = request.form["email"]
        if email.find("@") == 0 or len(email) < 7:
            return redirect(url_for('regestration'))
        psw = request.form["psw"]
        if len(psw) <= 4:
            return redirect(url_for('regestration'))
        psw2 = request.form["psw2"]
        if psw != psw2:
            return redirect(url_for('regestration'))
        pswh = hashlib.sha256(psw.encode()).hexdigest()
        session["psw2h"] = pswh
        user = users(name = name, email = email, psw = pswh)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            db.session.rollback()
            err  = "Ошибка добавления пользователя в БД #1 " + str(e)
            return err
    else:
        return render_template('regestration.html', Title = 'Регистрация', info = info, info2 = info)

@app.route('/user/<username>', methods = ['POST', 'GET'])
def user(username):
    tables = table.query.order_by(table.id).all()
    
    # arr = []
    # tall = table.query.all()
    # t = session['ident']

    # for i in range(len(tall)): # 10 -18
    #     if tall[i].rname == t:
    #                 arr.append(tall[i].id) 
    # arr2 = []
    # for i in range(len(arr)): # 1 - 8
    #     arr2.append(i+1)

    # tabs = []
    # for i in range(len(arr2)):
    #     tabs.append(table.query.get(arr[i]))
    #     tabs[i].idr = i + 1
    #     db.session.commit()

    print(session["ident"])
    info = rest.query.order_by(rest.id).filter(rest.rest_name == session["ident"]).all()
    if session['nameofuser'] == username: 

          
        if request.method == "POST":
            
            

            choosed_table = 0
            choosed_table = request.form['ttb']
            session["chtable"] = request.form['ttb']
            choosed_table = int(choosed_table) - 1

            try:
                month = request.form["month"]
                day = request.form["day"]
                hour = request.form["hour"]
                minute = request.form["minute"]

                date = datetime.datetime(2022, int(month), int(day), int(hour), int(minute), 0)
            except:
                return redirect("/")

            session["newdate"] = date
 
            #---------------------------------------------------------------------------------------------------------#
            h = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
            h1 = session["newdate"].hour * 60 + session["newdate"].minute
            q = h - h1
            call = table.query.filter(table.human == session["nameofuser"])  
            if datetime.datetime.now().day == session["newdate"].day and datetime.datetime.now().month == session["newdate"].month and q > 20:
                call.human = NULL
                call.datetime = NULL 
                call.status = 0
                db.session.commit()
            #---------------------------------------------------------------------------------------------------------#  

            if choosed_table == NONE:
                showtable = 0
            else:
                showtable = 1
            

            session["cht"] = tables[choosed_table].id

            id = tables[choosed_table].idr    # id status comment image
            status = tables[choosed_table].status
            comment = tables[choosed_table].comment
            image = tables[choosed_table].image
            cost = tables[choosed_table].cost
            
            

            return render_template('user.html',title = username, cost = cost, var1 = "Свободен", var2 = "Занят", tables = tables, info = info, info2 = info, id = id, status = status, comment = comment, image = image, showtable = showtable)
    return render_template('user.html',title = username, tables = tables, info = info, info2 = info)


@app.route('/about_us')
def about_us():

    
    chtable = table.query.get(session["cht"])
    chtable.status = 1
    chtable.datatime = str(session["newdate"])
    chtable.human = session["nameofuser"]
    db.session.commit()

    cht = session["chtable"]
    return render_template('about.html', u = session["nameofuser"], time = session["newdate"], cht = cht, Title = "Бронирование стола")


@app.errorhandler(404)
def error404Catch(error):
    return render_template('error404.html', Title = 'Страница не найдена'), 404
#-----LOAD------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)