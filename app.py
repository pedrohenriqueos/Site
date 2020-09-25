from flask import Flask, redirect, url_for, render_template, request, session , flash
import pymysql.cursors
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "teste123"
app.permanent_session_lifetime = timedelta(minutes=5)
connection = pymysql.connect(host='localhost', user='root',password='Pdr0506.',db='site',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

@app.route('/',methods = ["POST","GET"])
def index():
	if request.method == "POST":
		session["produto"] = request.form["nome"]
		return redirect(url_for("produto"))
	elif "email" in session:
		return redirect(url_for("user"))
	sql = "SELECT IDPRODUTO,preco,descricao,desconto,nome,estoque FROM PRODUTO"
	cursor.execute(sql)
	result = cursor.fetchall()
	return render_template("index.html",dados=result)

@app.route("/create",methods = ["POST","GET"])
def create():
	if request.method == "POST":
		user = request.form["nome"]
		senha = request.form["pass"]
		confirm = request.form["pass2"]
		cpf = request.form["cpf"]
		email = request.form["email"]
		ddd = request.form["ddd"]
		telefone = request.form["telefone"]
		cep = request.form["CEP"]
		rua = request.form["rua"]
		numero = request.form["num"]
		bairro = request.form["bairro"]
		cidade = request.form["cidade"]
		estado = request.form["estado"]
		complemento = request.form["complemento"]
		if confirm == senha:
			sql = "SELECT email FROM CLIENTE WHERE email=%s"
			cursor.execute(sql,(email,))
			result = cursor.fetchone()
			if result!=None:
				return render_template("create.html")
			sqlT = "INSERT INTO TELEFONE (`ddd`,`numero`) VALUES(%s,%s)"
			cursor.execute(sqlT,(ddd,telefone))
			id_Telefone = cursor.lastrowid
			sqlE = "INSERT INTO ENDERECO (`nome`,`numero`,`CEP`,`bairro`,`cidade`,`estado`,`complemento`) VALUES(%s,%s,%s,%s,%s,%s,%s)"
			cursor.execute(sqlE,(rua,numero,cep,bairro,cidade,estado,complemento))
			id_Endereco = cursor.lastrowid
			sql = "INSERT INTO CLIENTE (`nome`,`CPF`,`ID_ENDERECO`,`ID_TELEFONE`,`senha`,`email`) VALUES(%s,%s,%s,%s,%s,%s)"
			cursor.execute(sql,(user,cpf,id_Endereco,id_Telefone,senha,email))
			connection.commit()
			return redirect(url_for("login"))
		else:
			return render_template("create.html")
	else:
		if "email" in session:
			#flash("Already Logged In!")
			return redirect(url_for("user"))
		return render_template("create.html")

@app.route("/login",methods = ["POST","GET"])
def login():
	if request.method == "POST":
		email = request.form["email"]
		senha = request.form["pass"]
		sql = "SELECT IDCLIENTE, senha, nome FROM CLIENTE WHERE email=%s"
		cursor.execute(sql,(email,))
		result = cursor.fetchone()
		if result==None:
			return redirect(url_for("login"))
		if result["senha"]==senha:
			session.permanent = True
			session["email"] = email
			session["user"] = result["nome"]
			session["id"] = result["IDCLIENTE"]
			return redirect(url_for("user"))
		return redirect(url_for("login"))
	else:
		if "email" in session:
			return redirect(url_for("user"))
		return render_template("login.html")

@app.route("/user",methods = ["POST","GET"] )
def user():
	if request.method=="POST":
		session["produto"] = request.form["nome"]
		return redirect(url_for("produto"))
	elif "email" in session:
		user = session["user"]
		sql = "SELECT IDPRODUTO, preco, descricao, desconto, nome, estoque FROM PRODUTO"
		cursor.execute(sql)
		result = cursor.fetchall()
		size = list(range(len(result)))
		return render_template("user.html",name = user,dados = result,sz = size)
	else:
		return redirect(url_for("login"))

@app.route("/produto",methods = ["POST","GET"] )
def produto():
	if request.method=="POST":
		sqlC = "SELECT ID_PRODUTO,ID_CLIENTE,IDITEM,quantidade FROM ITEM WHERE ID_CLIENTE=%s and ID_PRODUTO=%s"
		cursor.execute(sqlC,(session["id"],request.form["compra"]))
		result = cursor.fetchone()
		if result!=None:
			sql = "UPDATE ITEM SET quantidade=%s WHERE IDITEM=%s"
			cursor.execute(sql,(int(result["quantidade"])+int(request.form["quantidade"]),result["IDITEM"]))
		else:
			sql = "INSERT INTO ITEM (`ID_CLIENTE`,`ID_PRODUTO`,`quantidade`) VALUES(%s,%s,%s)"
			cursor.execute(sql,(session["id"],request.form["compra"],request.form["quantidade"]))
		connection.commit()
		return redirect(url_for("index"))
	else:
		codeprod = session["produto"]
		session.pop("produto",None)
		sql = "SELECT IDPRODUTO AS code, preco AS preço, descricao, desconto, nome, estoque FROM PRODUTO WHERE IDPRODUTO=%s"
		cursor.execute(sql,(codeprod,))
		result = cursor.fetchone()
		return render_template("produto.html",produto = result,name = (session["user"] if "user" in session else None))

@app.route("/carrinho",methods=["POST","GET"])
def carrinho():
	if request.method=="POST": # Exclusão Mútua
		if "remove" in request.form:
			sql = "DELETE FROM ITEM WHERE IDITEM=%s"
			cursor.execute(sql,(request.form["remove"]))
			connection.commit()
			return redirect(url_for("carrinho"))
		else:
			sqlP = "SELECT IDPRODUTO, estoque, quantidade FROM PRODUTO INNER JOIN ITEM ON IDPRODUTO=ID_PRODUTO WHERE ID_CLIENTE=%s"
			cursor.execute(sqlP,(session["id"]))
			produtos = cursor.fetchall()
			sql = "UPDATE PRODUTO SET estoque=%s WHERE IDPRODUTO=%s"
			for produto in produtos:
				cursor.execute(sql,(produto["estoque"]-produto["quantidade"],produto["IDPRODUTO"]))
			sql = "DELETE FROM ITEM WHERE ID_CLIENTE=%s"
			cursor.execute(sql,(session["id"]))
			connection.commit()
			return redirect(url_for("user"))
	elif "email" in session:
		sql = "SELECT I.ID_PRODUTO,I.quantidade,P.preco,P.nome,P.estoque,I.IDITEM FROM ITEM I INNER JOIN PRODUTO P ON I.ID_PRODUTO=P.IDPRODUTO WHERE I.ID_CLIENTE=%s"
		cursor.execute(sql,(session["id"]))
		result = cursor.fetchall()
		flag = False
		for produto in result:
			if produto["quantidade"]>produto["estoque"]:
				sql = "UPDATE ITEM SET quantidade=%s WHERE IDITEM=%s"
				produto["quantidade"] = produto["estoque"]
				cursor.execute(sql,(produto["quantidade"],produto["IDITEM"]))
				flag = True
		if flag==True:
			connection.commit()
		return render_template("carrinho.html",produtos=result,name=session["user"])
	else:
		return redirect(url_for("index"))

@app.route("/logout")
def logout():
		session.permanent = False
		session.pop("id",None)
		session.pop("email",None)
		session.pop("senha",None)
		session.pop("user",None)
		return redirect(url_for("login"))
