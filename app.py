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

class AboutPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default="About Us")
    content = db.Column(db.Text, nullable=False)
    hero_title = db.Column(db.String(100), default="Discover the World of News")
    hero_subtitle = db.Column(db.String(200), default="Explore the Latest Stories")
    hero_image = db.Column(db.String(200))  # Path to the hero image
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AboutPage {self.id}>'

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


def create_default_about_page():
    # Check if about page already exists
    about_page = AboutPage.query.first()
    if not about_page:
        about_page = AboutPage(
            title="About Newscube",
            content="""
            <p>Welcome to Newscube, your trusted source for the latest news and insights from around the world.</p>

            <p>Our team of experienced journalists and contributors work tirelessly to bring you accurate, timely, and relevant stories across a variety of topics including politics, technology, health, culture, and more.</p>

            <p>At Newscube, we believe in the power of information to transform lives and communities. We are committed to upholding the highest standards of journalistic integrity and excellence in everything we do.</p>

            <p>Thank you for choosing Newscube as your news source. We look forward to being your window to the world.</p>
            """,
            hero_title="Discover the World of News",
            hero_subtitle="Explore the Latest Stories"
        )
        db.session.add(about_page)
        db.session.commit()
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


@app.context_processor
def inject_local_content():
    def get_local_articles(limit=3):
        # Try to find articles across several potential "local" categories
        local_slugs = ['local', 'community', 'regional', 'povestea-regiunii', 'reportaje']

        local_categories = Category.query.filter(Category.slug.in_(local_slugs)).all()

        if local_categories:
            category_ids = [cat.id for cat in local_categories]
            return Article.query.filter(
                Article.category_id.in_(category_ids),
                Article.published == True
            ).order_by(Article.created_at.desc()).limit(limit).all()
        else:
            # If no matching categories, just return the latest articles
            return Article.query.filter_by(
                published=True
            ).order_by(Article.created_at.desc()).limit(limit).all()

    return dict(get_local_articles=get_local_articles)
@app.context_processor
def inject_utilities():
    def get_articles_by_category(category_id, limit=3):
        return Article.query.filter_by(
            category_id=category_id,
            published=True
        ).order_by(Article.created_at.desc()).limit(limit).all()

    return dict(get_articles_by_category=get_articles_by_category)


@app.context_processor
def inject_featured_content():
    def get_featured_article():
        # Get the most recent article
        return Article.query.filter_by(published=True).order_by(Article.created_at.desc()).first()

    return dict(get_featured_article=get_featured_article)


@app.context_processor
def inject_article_utilities():
    def get_latest_articles(limit=3):
        return Article.query.filter_by(published=True).order_by(Article.created_at.desc()).limit(limit).all()

    return dict(get_latest_articles=get_latest_articles)


@app.context_processor
def inject_article_by_title_util():
    def get_article_by_title(title):
        return Article.query.filter(
            Article.title.like('%' + title + '%'),
            Article.published == True
        ).first()

    return dict(get_article_by_title=get_article_by_title)


@app.route('/admin/about/delete', methods=['GET'])
@admin_required
def admin_delete_about():
    try:
        # Get the about page
        about_page = AboutPage.query.first()

        if about_page:
            # Option 1: Delete the record completely
            # db.session.delete(about_page)

            # Option 2: Reset to default content (better approach)
            about_page.title = "About Newscube"
            about_page.content = """
            <p>Welcome to Newscube, your trusted source for the latest news and insights from around the world.</p>

            <p>Our team of experienced journalists and contributors work tirelessly to bring you accurate, timely, and relevant stories across a variety of topics including politics, technology, health, culture, and more.</p>

            <p>At Newscube, we believe in the power of information to transform lives and communities. We are committed to upholding the highest standards of journalistic integrity and excellence in everything we do.</p>

            <p>Thank you for choosing Newscube as your news source. We look forward to being your window to the world.</p>
            """
            about_page.hero_title = "Discover the World of News"
            about_page.hero_subtitle = "Explore the Latest Stories"
            about_page.hero_image = None  # Reset image

            db.session.commit()
            flash('About page content has been reset to default.', 'success')
        else:
            # If no about page exists, create the default one
            create_default_about_page()
            flash('Default About page has been created.', 'success')

        return redirect(url_for('admin_about'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting About page: {str(e)}', 'error')
        return redirect(url_for('admin_about'))

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


@app.route('/about')
def about():
    # Force database refresh
    db.session.expire_all()

    # Get a fresh copy of the about page
    about_page = AboutPage.query.first()

    if not about_page:
        create_default_about_page()
        about_page = AboutPage.query.first()

    # Get some recent articles to display
    recent_articles = Article.query.filter_by(published=True).order_by(Article.created_at.desc()).limit(3).all()

    # Debug - print the about page content to console
    print(f"Loading About page with title: {about_page.title}")
    print(f"Content: {about_page.content[:100]}...")

    return render_template('about.html', about_page=about_page, recent_articles=recent_articles)


@app.route('/admin/about', methods=['GET', 'POST'])
@admin_required
def admin_about():
    about_page = AboutPage.query.first()
    if not about_page:
        create_default_about_page()
        about_page = AboutPage.query.first()

    if request.method == 'POST':
        # Print debugging info
        print("Admin submitting About page update...")
        print(f"New title: {request.form['title']}")
        print(f"New content length: {len(request.form['content'])}")

        # Update the about page
        about_page.title = request.form['title']
        about_page.content = request.form['content']
        about_page.hero_title = request.form['hero_title']
        about_page.hero_subtitle = request.form['hero_subtitle']

        # Handle hero image upload
        if 'hero_image' in request.files:
            file = request.files['hero_image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old image if it exists
                if about_page.hero_image:
                    old_file_path = os.path.join('static', about_page.hero_image)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                about_page.hero_image = 'uploads/' + filename

        # Commit changes with error handling
        try:
            db.session.commit()
            print("About page successfully updated in database")
            flash('About page updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"ERROR updating about page: {str(e)}")
            flash(f'Error updating about page: {str(e)}', 'error')

        return redirect(url_for('admin_about'))

    return render_template('admin/edit_about.html', about_page=about_page)


@app.context_processor
def inject_about_page():
    def get_about_page():
        return AboutPage.query.first()

    return dict(get_about_page=get_about_page)


@app.context_processor
def inject_about_page():
    def get_about_page():
        return AboutPage.query.first()

    return dict(get_about_page=get_about_page)
@app.route('/test-about')
def test_about():
    about_page = AboutPage.query.first()
    return render_template('test_about.html', about_page=about_page)
@app.route('/test-about-db')
def test_about_db():
    about_page = AboutPage.query.first()
    if not about_page:
        return "No About page found in database!"

    result = {
        "id": about_page.id,
        "title": about_page.title,
        "hero_title": about_page.hero_title,
        "hero_subtitle": about_page.hero_subtitle,
        "content_preview": about_page.content[:100] + "...",
        "updated_at": about_page.updated_at
    }

    return jsonify(result)



@app.route('/contact')
def contact():
    return render_template('contact.html')

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_categories()
        create_default_about_page()

        # Create a default breaking news message if none exists
        if not BreakingNews.query.first():
            default_news = BreakingNews(
                content="Welcome to our news portal! Stay updated with the latest news and events from around the world.",
                active=True
            )
            db.session.add(default_news)
            db.session.commit()
    app.run(debug=True)