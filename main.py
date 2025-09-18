from flask import Flask, render_template, redirect, request, flash, url_for
import fdb

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
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicado = request.form['ano_publicado']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM lIVRO WHERE LIVRO.TITULO = ?', (titulo,))
        if cursor.fetchone():
            flash('Esse livro já está cadastrado')
            return redirect(url_for('novo'))
        cursor.execute("insert into livro(titulo, autor, ano_publicado) values (?,?,?)",
                       (titulo, autor, ano_publicado))
        con.commit()
    finally:
        cursor.close()
    flash('O livro foi cadastrado com sucesso')
    return redirect(url_for('index'))

@app.route('/atualizar')
def atualizar():
    return render_template('editar.html', titulo='Editar livro')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
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
        cursor = con.cursor()  # Abre o cursor

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


@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    try:
        cursor.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            flash('Esse e-mail já está cadastrado!', 'error')
            return redirect(url_for('novo_usuario'))

        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
            (nome, email, senha)
        )
        con.commit()
    finally:
        cursor.close()

    flash('Usuário cadastrado com sucesso!', 'success')
    return redirect(url_for('lista_usuario'))

if __name__ == '__main__':
    app.run(debug=True)