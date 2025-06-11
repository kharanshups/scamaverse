from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid # Import uuid for unique IDs

# --- Setup ---
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scamaverse.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_trp(likes, dislikes):
    """
    Calculates TRP based on likes and dislikes on a scale of 1 to 10.
    If likes == dislikes, TRP is 5.
    If total votes are 0, TRP is 5 (neutral).
    """
    total_votes = likes + dislikes
    if total_votes == 0:
        return 5 # Neutral if no votes

    if likes == dislikes:
        return 5

    # Scale ratio (0 to 1) to TRP (1 to 10)
    # If ratio is 0 (all dislikes), TRP is 1
    # If ratio is 1 (all likes), TRP is 10
    # Add a small epsilon to total_votes to avoid division by zero if it somehow becomes 0.
    ratio = likes / (total_votes + 1e-9) # Add small epsilon to prevent division by zero
    trp = 1 + (ratio * 9)
    return round(trp)

# --- Static News Posts (in-memory for simplicity, replace with DB in real app) ---
# Each news item now has a unique 'id', 'likes', 'dislikes', 'posted_by', and 'verified' status
news_items = []

# Global list to store user votes (user_id, post_id, vote_type)
# In a real app, this would be in a database table (e.g., a UserVote model)
user_votes = []

# Initialize some static posts with full details
# This block runs only once when the app starts
if not news_items: # Only add if news_items is empty
    news_items.extend([
        {
            "id": str(uuid.uuid4()), # Unique ID for each post
            "title": "BMRCL Hikes Fare by 200%",
            "description": "2 km of usable metro line, unlimited fare growth. Bangalore says: thanks, I guess?",
            "category": "Infrastructure",
            "timestamp": datetime(2025, 6, 1, 10, 0, 0), # Specific datetime for ordering
            "likes": 25,
            "dislikes": 5,
            "posted_by": "Scamaverse News",
            "verified": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Pak Lady Comes to Marry Sachin",
            "description": "Meanwhile, democracy silently weeps in the background. A tale of borderless love, or just another headline?",
            "category": "Entertainment",
            "timestamp": datetime(2025, 6, 2, 12, 30, 0),
            "likes": 50,
            "dislikes": 50,
            "posted_by": "Scamaverse News",
            "verified": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "💰 Bihar's Magic Trick — Now You See It, Now You Don't",
            "description": "A magician’s hand is quicker than the eye. Bihar’s loot is quicker than the CAG. Billions disappear into thin air, leaving taxpayers bewildered.",
            "category": "Finance",
            "timestamp": datetime(2025, 6, 3, 15, 45, 0),
            "likes": 15,
            "dislikes": 8,
            "posted_by": "Scamaverse News",
            "verified": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Floating Roads in Monsoon: Bengaluru's New Attraction?",
            "description": "After every heavy rain, Bengaluru roads transform into scenic canals. Urban planning at its finest, or a secret tourism initiative?",
            "category": "Urban Planning",
            "timestamp": datetime(2025, 6, 4, 9, 0, 0),
            "likes": 30,
            "dislikes": 10,
            "posted_by": "Scamaverse News",
            "verified": True
        }
    ])

# Calculate initial TRP for static news items
for item in news_items:
    item['trp'] = calculate_trp(item['likes'], item['dislikes'])


# --- Routes ---
@app.route('/')
@login_required
def index():
    user_id = current_user.id # Get the current user's ID
    sorted_news = sorted(news_items, key=lambda x: x['timestamp'], reverse=True)
    
    for item in sorted_news:
        # Determine user's vote status for this post
        # 'none' if no vote, 'like' if liked, 'dislike' if disliked
        user_vote_on_this_post = next((v['vote_type'] for v in user_votes if v['user_id'] == user_id and v['post_id'] == item['id']), 'none')
        item['user_vote_status'] = user_vote_on_this_post
        
    return render_template('index.html', news_items=sorted_news, user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        return "⚠️ Invalid credentials"

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return "⚠️ Username already taken.", 409

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        
        image_file = request.files.get('image')
        filename = None

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            # Ensure the uploads folder exists
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'])
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            image_file.save(os.path.join(upload_path, filename))

        if title and description and category:
            new_post = {
                'id': str(uuid.uuid4()), # Generate a unique ID for the new post
                'title': title,
                'description': description,
                'category': category,
                'trp': 5, # Initial TRP for new posts is 5 (neutral)
                'timestamp': datetime.now(),
                'image': filename,
                'posted_by': current_user.username, # Set posted_by to current user's username
                'verified': False, # User-submitted posts are not verified by default
                'likes': 0,
                'dislikes': 0
            }
            news_items.append(new_post)
            return redirect(url_for('index'))

    return render_template('submit.html')

@app.route('/gallery')
def gallery():
    user_id = current_user.id if current_user.is_authenticated else None
    image_posts = [item for item in news_items if item.get("image")]
    
    for post in image_posts:
        post['trp'] = calculate_trp(post['likes'], post['dislikes'])
        user_vote_on_this_post = 'none'
        if user_id: # Only check if user is authenticated
             user_vote_on_this_post = next((v['vote_type'] for v in user_votes if v['user_id'] == user_id and v['post_id'] == post['id']), 'none')
        post['user_vote_status'] = user_vote_on_this_post

    return render_template("gallery.html", posts=image_posts)

@app.route('/vote/<string:post_id>/<action>', methods=['POST'])
@login_required
def vote(post_id, action):
    """
    Handles liking or disliking a post, ensuring a user can only have one vote per post.
    Allows changing votes and undoing votes.
    """
    user_id = current_user.id

    post = next((item for item in news_items if item['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Find if the current user has already voted on this post
    existing_vote = next((v for v in user_votes if v['user_id'] == user_id and v['post_id'] == post_id), None)
    
    current_user_vote_status = 'none' # Default status to return

    if existing_vote:
        if existing_vote['vote_type'] == action:
            # User is trying to vote the same way again, so undo the vote
            if action == 'like':
                post['likes'] -= 1
            else: # action == 'dislike'
                post['dislikes'] -= 1
            user_votes.remove(existing_vote)
            current_user_vote_status = 'none' # Vote removed
        else:
            # User is changing their vote
            if action == 'like':
                post['dislikes'] -= 1 # Decrement old dislike
                post['likes'] += 1    # Increment new like
            else: # action == 'dislike'
                post['likes'] -= 1    # Decrement old like
                post['dislikes'] += 1 # Increment new dislike
            existing_vote['vote_type'] = action # Update vote type
            current_user_vote_status = action # Vote changed
    else:
        # First vote by this user on this post
        if action == 'like':
            post['likes'] += 1
        elif action == 'dislike':
            post['dislikes'] += 1
        else:
            return jsonify({"error": "Invalid action"}), 400
        user_votes.append({'user_id': user_id, 'post_id': post_id, 'vote_type': action})
        current_user_vote_status = action # New vote added

    post['trp'] = calculate_trp(post['likes'], post['dislikes'])
    
    # In a real application, you would save these changes to your database
    # For this example, we're modifying the in-memory news_items list and user_votes list directly.

    return jsonify({
        "likes": post['likes'],
        "dislikes": post['dislikes'],
        "trp": post['trp'],
        "user_vote_status": current_user_vote_status # Send back user's new vote status
    })

# --- Main ---
if __name__ == '__main__':
    # You would typically create tables here if using a real DB and not just in-memory
    # with app.app_context():
    #    db.create_all()
    app.run(debug=True)
