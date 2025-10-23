from flask import Flask, request, jsonify, render_template, send_from_directory
import mysql.connector
import os
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db_config = {
    'host': 'localhost',
    'user': 'root',        
    'password': 'hioka'    
}

def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS culinary_blog CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
    conn.database = "culinary_blog"

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            meal_type ENUM('Завтрак','Обед','Ужин','Закуска','Десерт') NOT NULL,
            image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ База и таблица готовы")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    conn = mysql.connector.connect(**db_config, database="culinary_blog")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recipes ORDER BY created_at DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/api/recipes', methods=['POST'])
def add_recipe():
    title = request.form.get('title')
    ingredients = request.form.get('ingredients')
    instructions = request.form.get('instructions')
    meal_type = request.form.get('meal_type')
    image_url = None

    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = f'/uploads/{filename}'

    conn = mysql.connector.connect(**db_config, database="culinary_blog")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipes (title, ingredients, instructions, meal_type, image_url, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (title, ingredients, instructions, meal_type, image_url, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    title = request.form.get('title')
    ingredients = request.form.get('ingredients')
    instructions = request.form.get('instructions')
    meal_type = request.form.get('meal_type')
    image_url = None

    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = f'/uploads/{filename}'

    conn = mysql.connector.connect(**db_config, database="culinary_blog")
    cursor = conn.cursor()
    if image_url:
        cursor.execute("""
            UPDATE recipes
            SET title=%s, ingredients=%s, instructions=%s, meal_type=%s, image_url=%s
            WHERE id=%s
        """, (title, ingredients, instructions, meal_type, image_url, recipe_id))
    else:
        cursor.execute("""
            UPDATE recipes
            SET title=%s, ingredients=%s, instructions=%s, meal_type=%s
            WHERE id=%s
        """, (title, ingredients, instructions, meal_type, recipe_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    conn = mysql.connector.connect(**db_config, database="culinary_blog")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recipes WHERE id=%s", (recipe_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'deleted'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()   
    app.run(debug=True)
