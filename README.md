# 🕵️ Scamaverse

**Expose the Fraud. Empower the People.**

Scamaverse is a minimal and stylish web app that lets users report and explore scam stories, from the absurd to the alarming. Users can register, log in, post scam incidents with images, and browse a gallery of memes that highlight the harsh realities — all while enjoying a smooth dark-themed UI.

---

## 📸 Features

- 📝 **Submit Scams**: Add title, category, description, TRP rating, and upload proof (images).
- 🔒 **User Auth**: Register/Login securely with session-based authentication.
- 🧾 **Profile Page**: View your username and logout easily.
- 🎨 **Dark/Light Theme Toggle**: Switch themes to match your mood.
- 🖼️ **Meme Gallery**: A scrollable, lazy-loaded image gallery with brief summaries.
- ✅ **Verified Post Tags**: Verified posts display a checkmark for trust factor.

---

## 🚀 Pages

| Route           | Description                        |
|----------------|------------------------------------|
| `/`            | Homepage with scam feed and posts  |
| `/register`    | New user registration              |
| `/login`       | User login                         |
| `/profile`     | Logged-in user info + logout       |
| `/submit`      | Submit a new scam post             |
| `/gallery`     | Explore meme-style scam posts      |

---

## 🧩 Tech Stack

- **Frontend**: HTML + CSS (Dark Theme UI)
- **Backend**: Python + Flask
- **Templating**: Jinja2
- **Storage**: Image uploads saved to `static/uploads`

---

## 🛠️ Installation

1. Clone the repo**
   
   git clone https://github.com/yourusername/scamaverse.git
   cd scamaverse

2. Create virtual environment & activate it

    python3 -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate

3. Install dependencies

    pip install -r requirements.txt

4. Run the app

    flask run

    or use
    
    python3 app.py


scamaverse/
│
├── static/
│   └── uploads/          # Uploaded scam images
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── gallery.html
│
├── app.py                # Main Flask app
├── requirements.txt      # Python dependencies
└── README.md

