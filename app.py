import os
import re
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.urls import quote  # This is likely the replacement for url_quote
from werkzeug.utils import secure_filename


# Admin credentials (in a real app, these would be stored securely in a database)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpass123"  # In production, use hashed passwords
UPLOAD_FOLDER = 'static/uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class BreakingNews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BreakingNews {self.content[:20]}...>'
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    youtube_link = db.Column(db.String(200))
    excerpt = db.Column(db.String(200))
    image_path = db.Column(db.String(200))  # New field for image path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('articles', lazy=True))

    def __repr__(self):
        return f'<Article {self.title}>'


def create_default_categories():
    # List of categories matching your navigation
    categories = [
        {"name": "Agricultura", "slug": "agricultura"},
        {"name": "Tehnologie", "slug": "tehnologie"},
        {"name": "Sanatate", "slug": "sanatate"},
        {"name": "Politic", "slug": "politic"},
        {"name": "Social", "slug": "social"},
        {"name": "Comunicate", "slug": "comunicate"},
        {"name": "Povestea Regiunii", "slug": "povestea-regiunii"},
        {"name": "Reportaje", "slug": "reportaje"},
    ]
    for category_data in categories:
        # Check if category already exists
        exists = Category.query.filter_by(slug=category_data["slug"]).first()
        if not exists:
            category = Category(name=category_data["name"], slug=category_data["slug"])
            db.session.add(category)

    db.session.commit()
# Login required decorator for admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access the admin area.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/upload-tinymce-image', methods=['POST'])
@admin_required
def upload_tinymce_image():
    if 'file' not in request.files:
        return jsonify({'location': ''})

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'location': url_for('static', filename='uploads/' + filename)})

    return jsonify({'location': ''})
def extract_youtube_id(url):
    if not url:
        return None
    # Extract YouTube video ID from URL
    pattern = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None


# Public routes
from flask import request  # Make sure this import is at the top


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 7  # Number of articles per page

    # Get total count for pagination
    total = Article.query.filter_by(published=True).count()

    # Get paginated articles
    articles = Article.query.filter_by(published=True).order_by(
        Article.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('index.html', articles=articles, page=page)


@app.context_processor
def inject_categories():
    def get_categories():
        return Category.query.all()
    return dict(get_categories=get_categories)


@app.route('/admin/breaking-news', methods=['GET', 'POST'])
@admin_required
def admin_breaking_news():
    # Get current active breaking news
    current_news = BreakingNews.query.filter_by(active=True).order_by(BreakingNews.created_at.desc()).first()

    # Get history of breaking news for reference
    breaking_news_history = BreakingNews.query.filter(BreakingNews.active == False).order_by(
        BreakingNews.created_at.desc()).limit(10).all()

    if request.method == 'POST':
        content = request.form['content']
        active = 'active' in request.form

        # Deactivate all current breaking news if we're activating a new one
        if active:
            BreakingNews.query.update({'active': False})

        # Create new breaking news entry
        breaking_news = BreakingNews(content=content, active=active)
        db.session.add(breaking_news)
        db.session.commit()

        flash('Breaking news updated successfully!', 'success')
        return redirect(url_for('admin_breaking_news'))

    return render_template('admin/manage_breaking_news.html',
                           current_news=current_news,
                           breaking_news_history=breaking_news_history)


@app.route('/admin/breaking-news/reuse/<int:id>')
@admin_required
def admin_reuse_breaking_news(id):
    # Get the breaking news to reuse
    breaking_news = BreakingNews.query.get_or_404(id)

    # Deactivate all current breaking news
    BreakingNews.query.update({'active': False})

    # Create a new breaking news with the same content

    new_breaking_news = BreakingNews(
        content=breaking_news.content,
        active=True
    )

    db.session.add(new_breaking_news)
    db.session.commit()

    flash('Breaking news reactivated successfully!', 'success')
    return redirect(url_for('admin_breaking_news'))


@app.route('/article/<int:id>')
def article(id):
    article = Article.query.get_or_404(id)
    # Prevent users from accessing unpublished articles
    if not article.published and 'admin_logged_in' not in session:
        flash('This article is not available.', 'error')
        return redirect(url_for('index'))
    youtube_id = extract_youtube_id(article.youtube_link)
    return render_template('article.html', article=article, youtube_id=youtube_id)

@app.context_processor
def inject_breaking_news():
    breaking_news = BreakingNews.query.filter_by(active=True).order_by(BreakingNews.created_at.desc()).first()
    return dict(breaking_news=breaking_news)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Successfully logged in as admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/dashboard.html', articles=articles)


@app.route('/admin/create', methods=['GET', 'POST'])
@admin_required
def admin_create_article():
    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        youtube_link = request.form['youtube_link']
        category_id = request.form['category_id']
        published = 'published' in request.form

        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_path = 'uploads/' + filename

        if not title or not content or not category_id:
            flash('Title, content, and category are required!', 'error')
            return redirect(url_for('admin_create_article'))

        article = Article(
            title=title,
            content=content,
            youtube_link=youtube_link,
            image_path=image_path,
            published=published,
            category_id=category_id
        )

        db.session.add(article)
        db.session.commit()
        flash('Article created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/create_article.html', categories=categories)


@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_article(id):
    article = Article.query.get_or_404(id)
    categories = Category.query.all()

    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        article.youtube_link = request.form['youtube_link']
        article.category_id = request.form['category_id']
        article.published = 'published' in request.form

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old image if it exists
                if article.image_path:
                    old_file_path = os.path.join('static', article.image_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                article.image_path = 'uploads/' + filename

        db.session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_article.html', article=article, categories=categories)


@app.route('/category/<string:slug>')
def category(slug):
    page = request.args.get('page', 1, type=int)
    per_page = 7  # Number of articles per page

    category = Category.query.filter_by(slug=slug).first_or_404()

    # Get paginated articles for this category
    articles = Article.query.filter_by(
        category_id=category.id,
        published=True
    ).order_by(
        Article.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('category.html', articles=articles, category=category, page=page)

@app.route('/admin/delete/<int:id>')
@admin_required
def admin_delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':# Add this to your app initialization
    with app.app_context():
        db.create_all()
        create_default_categories()

        # Create a default breaking news message if none exists
        if not BreakingNews.query.first():
            default_news = BreakingNews(
                content="Welcome to our news portal! Stay updated with the latest news and events from around the world.",
                active=True
            )
            db.session.add(default_news)
            db.session.commit()
    app.run(debug=True)