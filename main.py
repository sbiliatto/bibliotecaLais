from flask import Flask, render_template, redirect, request, flash, url_for, session, send_from_directory, send_file
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

host = 'localhost'
database = r'C:\Users\Aluno\Desktop\BANCO.FDB'
user ='sysdba'
password ='sysdba'

con = fdb.connect(user= user, password=password, host=host, database= database)

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("select id_livro, titulo, autor, ano_publicado from livro")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('livros.html', livros=livros)


@app.route('/novo')
def novo():
    return render_template('novo.html', titulo= 'Novo Livro')



@app.route('/criar', methods=['POST'])
def criar():
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))


    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicado = request.form['ano_publicado']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM lIVRO WHERE LIVRO.TITULO = ?', (titulo,))
        if cursor.fetchone():
            flash('Esse livro já está cadastrado')
            return redirect(url_for('novo'))
        cursor.execute("INSERT INTO livro (TITULO, AUTOR, ANO_PUBLICADO) VALUES (?, ?, ?) RETURNING id_livro",
            (titulo, autor, ano_publicado)
        )
        id_livro = cursor.fetchone()[0]
        con.commit()

        arquivo = request.files['arquivo']
        arquivo.save(f'uploads/capa{id_livro}.jpg')

    finally:
        cursor.close()
    flash('O livro foi cadastrado com sucesso')
    return redirect(url_for('index'))

@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)

@app.route('/atualizar')
def atualizar():
    return render_template('editar.html', titulo='Editar livro')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))


    cursor = con.cursor()
    cursor.execute('select id_livro, titulo, autor, ano_publicado from livro where id_livro =?', (id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash("Livro não foi encontrado")
        return redirect(url_for('index'))


    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicado = request.form['ano_publicacao']

        cursor.execute("update livro set titulo = ?, autor = ?, ano_publicado = ? where id_livro = ?" ,
        (titulo, autor, ano_publicado, id))

        con.commit()
        flash("Livro atualizado com sucesso")
        return  redirect(url_for('index'))
    cursor.close()
    return render_template('editar.html', livro=livro, titulo= 'Editar livro')

@app.route('/deletar/<int:id>', methods=('POST',))
def deletar(id):
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))


    cursor = con.cursor()
    try:
        cursor.execute('DELETE FROM livro WHERE id_livro = ?', (id,))
        con.commit()
        flash('Livro excluído com sucesso!', 'success')
    except Exception as e:
        con.rollback()
        flash('Erro ao excluir o livro.', 'error')
    finally:
        cursor.close()

    return redirect(url_for('index'))

@app.route('/livros/relatorio', methods=['GET'])
def relatorio():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicado FROM livro")
    livro = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')
    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
    pdf.ln(5)  # Espaço após a linha
    pdf.set_font("Arial", size=12)
    for livro in livro:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)
    contador_livros = len(livro)
    pdf.ln(10)  # Espaço antes do contador
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livros}", ln=True, align='C')
    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')


@app.route('/lista_usuario')
def lista_usuario():
    cursor = con.cursor()
    cursor.execute("SELECT id, nome, email, senha FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('usuario.html', usuarios=usuarios)


@app.route('/novo_usuario')
def novo_usuario():
    return render_template('novousuario.html', titulo='Novo Usuário')


@app.route('/criar_usuario', methods=['GET', 'POST'])
def criar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_cripto = generate_password_hash(senha).decode('utf-8')

        cursor = con.cursor()
        try:
            cursor.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,))
            if cursor.fetchone():
                flash('Esse e-mail já está cadastrado!', 'error')
                return redirect(url_for('novo_usuario'))

            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha_cripto)
            )
            con.commit()
        finally:
            cursor.close()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('lista_usuario'))
    return redirect(url_for('novo_usuario'))





@app.route('/atualizar_usuario')
def atualizar_usuario():
    return render_template('editar_usuario.html', titulo='Editar Usuario')

@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    cursor = con.cursor()
    cursor.execute('select id, nome, email, senha from usuarios where id =?', (id,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        flash("Usuário não foi encontrado")
        return redirect(url_for('lista_usuario'))


    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        cursor.execute("update usuarios set nome = ?, email = ?, senha = ? where id = ?" ,
        (nome, email, senha, id))

        con.commit()
        flash("Usuário atualizado com sucesso")
        return  redirect(url_for('lista_usuario'))
    cursor.close()
    return render_template('editar_usuario.html', usuario=usuario, titulo= 'Editar Usuário')

@app.route('/deletar_usuario/<int:id>', methods=('POST',))
def deletar_usuario(id):
        cursor = con.cursor()

        try:
            cursor.execute('DELETE FROM usuarios WHERE id = ?', (id,))
            con.commit()
            flash('Usuário excluído com sucesso!', 'success')
        except Exception as e:
            con.rollback()
            flash('Erro ao excluir o usuário.', 'error')
        finally:
            cursor.close()

        return redirect(url_for('lista_usuario'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cursor = con.cursor()
        try:
            cursor.execute("SELECT senha, id FROM usuarios WHERE email = ?", (email,))
            usuario = cursor.fetchone()

            if usuario and check_password_hash(usuario[0], senha):
                session['id_usuario'] = usuario[1]
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('lista_usuario'))

            else:
                flash('E-mail ou senha incorretos. Tente novamente.', 'error')
                return redirect(url_for('lista_usuario'))
        finally:
            cursor.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop("id_usuario",None)
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)