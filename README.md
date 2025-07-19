# 🎬 CineMatch

CineMatch is a movie recommendation and discovery platform built with Django. It allows users to browse, view details, and rate movies fetched from **The Movie Database (TMDB)** API. The goal is to create a personalized and engaging movie discovery experience.

---

## 📸 Preview

![Logo](movies/static/movies/logo.png)

---

## 🚀 Features

- Browse a curated list of popular movies
- Movie detail pages with descriptions, genres, directors, and posters
- Pagination for movie lists
- Admin panel to manage movie data
- Posters automatically fetched from TMDB
- Rating system (coming soon)
- Movie recommendations (planned)

---

## 🛠️ Tech Stack

- **Backend**: Django, Python
- **Frontend**: HTML, Bootstrap, Django Templating
- **Database**: MySQL
- **External API**: [TMDB API](https://www.themoviedb.org/documentation/api)

---

## 📁 Project Structure
cinematch/                                
├── movies/ # Main app                                                                          
│ ├── management/ # Custom management command to import movies                                    
│ ├── templates/                                                    
│ ├── static/                                                                
│ ├── models.py                                                            
│ ├── views.py                                                  
│ ├── urls.py                                                                      
│ └── ...                                                                      
├── cinematch/ # Project settings                                                                          
│ └── settings.py                                                          
├── db.sqlite3                                                                          
└── manage.py                                                                          

