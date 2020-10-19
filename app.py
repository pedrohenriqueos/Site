#TODO: segurança do site
from flask import Flask, redirect, url_for, render_template, request, session
import pymysql.cursors
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "teste123"
app.permanent_session_lifetime = timedelta(minutes=5)
connection = pymysql.connect(host='localhost', user='root',password='Pdr0506.',db='site',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

@app.route('/',methods = ["POST","GET"])
def index():
	if request.method=="POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
		else:
			session["produto"] = request.form["ID"]
			return redirect(url_for("produto"))
	else:
		sql = "SELECT IDPRODUTO,preco,desconto,nome,estoque,img,principal FROM PRODUTO WHERE principal=1"
		sql2 = "SELECT IDPRODUTO,preco,desconto,nome,estoque,img,principal FROM PRODUTO WHERE desconto>0"
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		sql3 = "SELECT P.IDPRODUTO,P.preco,P.desconto,P.nome,P.estoque,P.img,P.principal FROM PRODUTO AS P INNER JOIN VENDAS AS V ON P.IDPRODUTO=V.ID_PRODUTO GROUP BY P.IDPRODUTO"
		cursor.execute(sql)
		result = cursor.fetchall()
		cursor.execute(sql2)
		result2 = cursor.fetchall()
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		cursor.execute(sql3)
		result3 = cursor.fetchall()
		return render_template("index.html",dados_principais = result,dados_ofertas = result2,dados_vendidos = result3,name = (session["user"] if "user" in session else None),bar = bar)

@app.route("/search",methods = ["POST","GET"])
def search():
	if request.method=="POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
	else:
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		session["search"] = "%" + session["search"] + "%"
		sql = "SELECT P.nome, P.preco, P.desconto, P.img, P.estoque, P.IDPRODUTO FROM CATEGORIAS AS C INNER JOIN PRODUTO_CATEGORIAS AS PC ON C.IDCATEGORIAS=PC.ID_CATEGORIAS INNER JOIN PRODUTO AS P ON P.IDPRODUTO=PC.ID_PRODUTO WHERE P.descricao LIKE %s"
		cursor.execute(sql,(session["search"]))
		result = cursor.fetchall()
		if result:
			return render_template("categoria.html",bar=bar, name = (session["user"] if "user" in session else None), produtos=result)
		return redirect(url_for("index")) #O ideal seria jogar para a pagina anterior = +1 session


@app.route("/user",methods = ["POST","GET"])
def user():
	if request.method=="POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
	else:
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		return render_template("user.html",bar=bar,name = (session["user"] if "user" in session else None))

@app.route("/user/cadastro",methods= ["POST","GET"])
def cadastro():
	if request.method=="POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
		else:
			sql = "SELECT senha FROM CLIENTE WHERE IDCLIENTE=%s"
			cursor.execute(sql,(session["id"]))
			result = cursor.fetchone()
			if result["senha"]==request.form["tsenha"]:
				if "tasenha" in request.form:				
					if request.form["tsenhanew"]==request.form["tsenhaconf"]:
						sql = "UPDATE CLIENTE SET senha=%s WHERE IDCLIENTE=%s"
						cursor.execute(sql,(request.form["tsenhanew"],session["id"]))
						connection.commit()
						return redirect(url_for("user"))
					else:
						sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
						cursor.execute(sqlbase)
						bar = cursor.fetchall()
						return render_template("cadastro.html",bar=bar,name = session["user"])
				elif "taend" in request.form:
					sql = "UPDATE ENDERECO SET nome=%s, numero=%s, CEP=%s, bairro=%s, cidade=%s, estado=%s, complemento=%s WHERE IDENDERECO=%s"
					sql2 = "SELECT ID_ENDERECO FROM CLIENTE WHERE IDCLIENTE=%s"
					cursor.execute(sql2,(session["id"]))
					result = cursor.fetchone()
					cursor.execute(sql,(request.form["tlong"],request.form["tnumend"],request.form["tcep"],request.form["tbairro"],request.form["tcid"],request.form["test"],request.form["tcomp"],result["ID_ENDERECO"]))
					connection.commit()
					return redirect(url_for("user"))
				else:
					sql = "UPDATE TELEFONE SET ddd=%s, numero=%s WHERE IDTELEFONE=%s"
					sql2 = "SELECT ID_TELEFONE FROM CLIENTE WHERE IDCLIENTE=%s"
					cursor.execute(sql2,(session["id"]))
					result = cursor.fetchone()
					cursor.execute(sql,(request.form["tddd"],request.form["tnum"],result["ID_TELEFONE"]))
					connection.commit()
					return redirect(url_for("user"))
			else:
				sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
				cursor.execute(sqlbase)
				bar = cursor.fetchall()
				return render_template("cadastro.html",bar=bar,name = (session["user"] if "user" in session else None))
	else:
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		return render_template("cadastro.html",bar=bar,name = (session["user"] if "user" in session else None))

@app.route("/user/pedidos",methods=["POST","GET"])
def pedidos():
	if request.method=="POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
	else:
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		sql = "SELECT P.nome,V.quantidade,P.preco FROM CLIENTE AS C INNER JOIN VENDAS AS V ON C.IDCLIENTE=V.ID_CLIENTE INNER JOIN PRODUTO AS P ON V.ID_PRODUTO=P.IDPRODUTO WHERE C.IDCLIENTE=%s"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		cursor.execute(sql,(session["id"]))
		result = cursor.fetchall()
		return render_template("pedidos.html",bar = bar,name = session["user"],pedidos = result)

@app.route("/user/dados",methods = ["POST","GET"])
def dados():
	if request.method=="POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
	else:
		sql = "SELECT nome,email,longradura,numero,CEP,bairro,cidade,estado,complemento,ddd,telefone FROM DADOS WHERE IDCLIENTE=%s"
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		cursor.execute(sql,(session["id"]))
		result = cursor.fetchone()
		return render_template("dados.html",dados = result,bar = bar,name = session["user"])

@app.route("/categoria",methods = ["POST","GET"])
def categoria():
	if request.method=="POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
		else:
			session["produto"] = request.form["ID"]
			return redirect(url_for('produto'))
	else:
		codecat = session['categoria']
		sql = "SELECT P.nome, P.preco, P.desconto, P.img, P.estoque, P.IDPRODUTO FROM CATEGORIAS AS C INNER JOIN PRODUTO_CATEGORIAS AS PC ON C.IDCATEGORIAS=PC.ID_CATEGORIAS INNER JOIN PRODUTO AS P ON P.IDPRODUTO=PC.ID_PRODUTO WHERE C.IDCATEGORIAS=%s"
		cursor.execute(sql,(codecat))
		result = cursor.fetchall()
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		return render_template("categoria.html",produtos = result,bar = bar,name = (session["user"] if "user" in session else None))

@app.route("/produto",methods = ["POST","GET"])
def produto():
	if request.method=="POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
		else:
			if int(request.form["quantidade"])<=0:
				return redirect(url_for("produto"))
			else:
				sqlC = "SELECT ID_PRODUTO,ID_CLIENTE,IDITEM,quantidade FROM ITEM WHERE ID_CLIENTE=%s and ID_PRODUTO=%s"
				cursor.execute(sqlC,(session["id"],request.form["compra"]))
				result = cursor.fetchone()
				if result!=None:
					sql = "UPDATE ITEM SET quantidade=%s WHERE IDITEM=%s"
					cursor.execute(sql,(int(result["quantidade"])+int(request.form["quantidade"]),result["IDITEM"]))
				else:
					sql = "INSERT INTO ITEM (ID_CLIENTE,ID_PRODUTO,quantidade) VALUES(%s,%s,%s)"
					cursor.execute(sql,(session["id"],request.form["compra"],request.form["quantidade"]))
				connection.commit()
				return redirect(url_for("carrinho"))
	else:
		codeprod = session["produto"]
		sql = "SELECT IDPRODUTO, preco,descricao,nome,estoque,img,desconto FROM PRODUTO WHERE IDPRODUTO=%s"
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sql,(codeprod))
		result = cursor.fetchone()
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		return render_template("produto.html",produto = result,name = (session["user"] if "user" in session else None),bar=bar, estoque = result['estoque'])

@app.route("/create",methods = ["POST","GET"])
def create():
	if request.method == "POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
		else:
			user = request.form["tnome"]
			senha = request.form["tsenha"]
			confirm = request.form["tconf"]
			cpf = request.form["tcpf"]
			email = request.form["temail"]
			ddd = request.form["tddd"]
			telefone = request.form["tnum"]
			cep = request.form["tcep"]
			rua = request.form["tlong"]
			numero = request.form["tnumend"]
			bairro = request.form["tbairro"]
			cidade = request.form["tcid"]
			estado = request.form["test"]
			complemento = request.form["tcomp"]
			if confirm == senha:
				sql = "SELECT email FROM CLIENTE WHERE email=%s"
				cursor.execute(sql,(email,))
				result = cursor.fetchone()
				if result!=None:
					sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
					cursor.execute(sqlbase)
					bar = cursor.fetchall()
					return render_template("create.html",bar = bar,name = (session["user"] if "user" in session else None))
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
				sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
				cursor.execute(sqlbase)
				bar = cursor.fetchall()
				return render_template("create.html",bar=bar,name = (session["user"] if "user" in session else None))
	else:
		if "email" in session:
			return redirect(url_for("index"))
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		return render_template("create.html",bar=bar,name = (session["user"] if "user" in session else None))

@app.route("/login",methods = ["POST","GET"])
def login():
	if request.method == "POST":
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
		else:
			email = request.form["tlogin"]
			senha = request.form["tsenhae"]
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
				return redirect(url_for("index"))
			return redirect(url_for("login"))
	else:
		if "email" in session:
			return redirect(url_for("index"))
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		return render_template("login.html",bar=bar,name = (session["user"] if "user" in session else None))

@app.route("/carrinho",methods=["POST","GET"])
def carrinho():
	if request.method=="POST": # Exclusão Mútua
		if "nSearch" in request.form:
			session["search"] = request.form["nSearch"]
			return redirect(url_for("search"))
		elif "categoria" in request.form:
			session["categoria"] = request.form["categoria"]
			return redirect(url_for("categoria"))
		else:
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
				return redirect(url_for("index"))
	elif "email" in session:
		sql = "SELECT I.ID_PRODUTO,I.quantidade,P.preco,P.nome,P.estoque,I.IDITEM,P.img,P.desconto  FROM ITEM AS I INNER JOIN PRODUTO AS P ON I.ID_PRODUTO=P.IDPRODUTO WHERE I.ID_CLIENTE=%s"
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
		sqlbase = "SELECT IDCATEGORIAS, categoria FROM CATEGORIAS"
		cursor.execute(sqlbase)
		bar = cursor.fetchall()
		return render_template("carrinho.html",produtos=result,bar=bar,name = (session["user"] if "user" in session else None))
	else:
		return redirect(url_for("index"))

@app.route("/logout")
def logout():
		session.permanent = False
		session.pop("id",None)
		session.pop("email",None)
		session.pop("senha",None)
		session.pop("user",None)
		return redirect(url_for("index"))