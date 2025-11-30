from flask import Flask, jsonify, render_template , request
app = Flask(__name__)

from flask import Flask , Request , jsonify , request , render_template , make_response
import sqlite3
import hashlib
import secrets
import string
import jwt
import datetime

conn = sqlite3.connect("users.db")
cursor  = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT , username TEXT UNIQUE NOT NULL,password TEXT NOT NULL)""")
conn.commit()
conn.close()
conn = sqlite3.connect("upload.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS uploads ( author TEXT NOT NULL , description TEXT , contents TEXT NOT NULL) """)
conn.commit()
conn.close()
SECRET_KEY = "aZ7kP0mH3qR9tYcB4xL2"
app = Flask(__name__)
@app.route('/',methods=['GET'])
def main():       
   cookie = request.cookies.get('session')
   try:
      payload = jwt.decode(cookie,SECRET_KEY,algorithms=['HS256'])
   except jwt.ExpiredSignatureError:
      return render_template("login.html",msg="세션이 만료 됬습니다 다시 로그인 하세요.")
   except jwt.exceptions.DecodeError:
      return render_template("login.html",msg="세션이 잘못 되었습니다 다시 로그인 하세요.")
   except:
      return render_template("login.html")
   conn = sqlite3.connect("upload.db")
   cursor = conn.cursor()
   cursor.execute("""SELECT * FROM uploads""")
   uploads = cursor.fetchall()
   cursor.close()
   author = [row[0] for row in uploads]
   description = [row[1] for row in uploads]
   contents = [row[2] for row in uploads]
   return render_template("index.html",author=author,description=description,contents=contents)
@app.route('/login',methods=['POST'])
def login():
   id  = request.form.get("id")
   password = request.form.get("password")
   try:
      hash_object = hashlib.sha256()
      hash_object.update(password.encode())
      hashed_password = hash_object.hexdigest()              
      conn = sqlite3.connect("users.db")
      cursor  = conn.cursor()
      cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? ",(id,hashed_password))
      result = cursor.fetchone()
      conn.close()
      if result:
         print("로그인 성공")
         payload = {
                'id': id,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
            }
         print("토큰획득")
         token = jwt.encode(payload=payload, key="aZ7kP0mH3qR9tYcB4xL2", algorithm="HS256")
         
         res = make_response()
         res.set_cookie('session',token)
         return res
      else:
         print("로그인 실패")
         return render_template("login.html",msg="아이디 또는 비밀번호가 잘못 되었습니다.")
   except:
      print("오류")
      return render_template("login.html",msg="문제가 발생했습니다 다시 시도하세요.")
@app.route('/register',methods=['POST'])
def register():
   name = request.form.get("name")        
   pwd = request.form.get("pwd")
   hash_object = hashlib.sha256()
   hash_object.update(pwd.encode())
   hashed_pwd = hash_object.hexdigest()
   conn = sqlite3.connect("users.db")    
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM users WHERE username = ?",(name,))
   result = cursor.fetchone()     
   if result:
      print("아이디가 이미 존재합니다.")
      conn.close()
      return "already exist id"
   else:
      print("계정 생성에 성공했습니다")
      print(name)
      print(pwd)

      cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",(name,hashed_pwd))
      conn.commit()
      conn.close()  
      return render_template('index.html')
@app.route('/auth',methods=['GET'])
def auth():
   return render_template('login.html')
@app.route('/regist',methods=['GET'])
def regist():
   return render_template('register.html')
@app.route('/upload',methods=["GET","POST"])
def upload():
   if request.method == "GET":
      return render_template('upload.html')
   elif request.method == "POST":
      session = request.cookies.get('session')
      decoded_token = jwt.decode(session,key=SECRET_KEY,algorithms="HS256")
      id = decoded_token['id']
      print(id)
      description = request.form.get("description")
      content = request.form.get("content")
      conn = sqlite3.connect("upload.db")
      cursor = conn.cursor()
      cursor.execute("INSERT INTO uploads (author , description , contents) VALUES (? , ? ,?)",(id,description,content))
      conn.commit()
      return "success"
   
if __name__ == '__main__':   
   app.run(host='127.0.0.1',port=5000)