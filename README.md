*Vincent RealEstate Solutions*

A modern, visually stunning, and fully responsive real estate web platform built with Django. This project is designed to provide a premium user experience for property buyers, sellers, and renters, with a focus on sleek design, strong branding, and robust functionality.


  *Features*

*Modern, Glassmorphic UI:*  Beautiful glassy hero sections, cards, and search bars for a luxury feel.
*Responsive Design:*  Fully mobile-friendly layouts for all pages and components.
*Featured Listings:*  Premium property cards with images, price badges, and hover effects.
*Advanced Search:*  Floating, glassy search bar with icons, filters (keywords, city, bedrooms, price), and persistent search values.
*Single Listing Pages:*  Modern glass cards, sticky realtor sidebar, image galleries, and bold inquiry CTAs.
*Contact Page:*  Glassmorphism contact form with floating labels, icons, and real estate-themed background.
*User Authentication:*  Register, login, and dashboard for users.
*SEO Optimized:*  Meta tags for all major pages, Open Graph for social sharing.
*WhatsApp Chatbot Widget:*  Floating, modern WhatsApp chat widget for instant support.
*Admin Panel:*  Manage listings, realtors, and contacts with Django admin.



 🏗️ Tech Stack

*Backend:* Django 4.x
*Frontend:* Bootstrap 5, custom CSS (glassmorphism, gradients, icons)
*Database:* PostgreSQL
*Email:* Gmail SMTP (configurable)
*Other:* FontAwesome, Lightbox.js



⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/realestate.git
   cd realestate
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure your database and email in `/settings.py`:**
   - Set your PostgreSQL credentials.
   - Set your Gmail SMTP credentials for contact form emails.
5. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```
7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
8. **Access the site:**
   - Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.


 📁 *Project Structure*


RealEstate/
  ├── accounts/
  ├── bt/
  ├── contacts/
  ├── listings/
  ├── pages/
  ├── realtors/
  ├── templates/
  ├── static/
  ├── media/
  ├── requirements.txt
  └── manage.py
```


Give this repo a if you like the project!