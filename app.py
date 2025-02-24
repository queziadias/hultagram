from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from models import db, Post

app = Flask(__name__)

# Add a Secret Key for Flash Messages & Sessions
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this to a strong, random key
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photogram.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create the database tables (run only once)
with app.app_context():
    db.create_all()

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Homepage - Displays All Posts
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# Create a New Post (Handles File Upload)
@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        file = request.files['image']
        caption = request.form.get('caption')

        if file:
            filename = secure_filename(file.filename)

            # Ensure the upload directory exists before saving the file
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            new_post = Post(image_filename=filename, caption=caption)
            db.session.add(new_post)
            db.session.commit()

            flash("Post created successfully!", "success")  # Uses session (needs SECRET_KEY)
            return redirect(url_for('index'))

    return render_template('create.html')

# Like a Post (Updates the Like Count)
@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    post = Post.query.get(post_id)
    if post:
        post.likes += 1
        db.session.commit()
    return redirect(url_for('index'))

# View a Single Post (Detail Page)
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get(post_id)
    return render_template('post_detail.html', post=post)

# Delete a Post
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('index'))

# Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
