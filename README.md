# Library Management System API

A RESTful API for managing library resources, built with Django and Django REST Framework.

## Features

- **Books Management**: CRUD operations for books and authors
- **Users Management**: User registration, authentication, and profile management
- **Check-Out/Return System**: Borrow and return books with transaction tracking
- **Role-Based Access**: Admin and Member roles with different permissions
- **Overdue Tracking**: Automatic overdue detection with penalty calculation
- **Email Notifications**: Notifications for checkouts, returns, and overdue books
- **JWT Authentication**: Secure token-based authentication
- **Pagination & Filtering**: Search, filter, and paginate results

## Tech Stack

- Python 3.11+
- Django 4.2
- Django REST Framework
- SQLite (development) / PostgreSQL (production)
- JWT Authentication (SimpleJWT)

## Installation

1. **Clone the repository**
   ```bash
   cd ~/Desktop/library_management_system
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Obtain JWT token |
| POST | `/api/token/refresh/` | Refresh JWT token |
| POST | `/api/token/verify/` | Verify JWT token |

### Users
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/api/v1/users/register/` | Register new user | Public |
| GET | `/api/v1/users/profile/` | Get user profile | Authenticated |
| PUT | `/api/v1/users/profile/` | Update profile | Authenticated |
| GET | `/api/v1/users/` | List all users | Admin |
| POST | `/api/v1/users/` | Create user | Admin |
| GET | `/api/v1/users/{id}/` | Get user details | Admin |
| DELETE | `/api/v1/users/{id}/` | Deactivate user | Admin |

### Books
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/books/` | List all books | Authenticated |
| POST | `/api/v1/books/` | Create book | Admin |
| GET | `/api/v1/books/{id}/` | Get book details | Authenticated |
| PUT | `/api/v1/books/{id}/` | Update book | Admin |
| DELETE | `/api/v1/books/{id}/` | Delete book | Admin |
| GET | `/api/v1/books/available/` | List available books | Authenticated |
| GET | `/api/v1/books/authors/` | List authors | Authenticated |

### Transactions
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/api/v1/transactions/checkout/` | Checkout a book | Authenticated |
| POST | `/api/v1/transactions/return/{id}/` | Return a book | Authenticated |
| GET | `/api/v1/transactions/my-transactions/` | User's transactions | Authenticated |
| GET | `/api/v1/transactions/active/` | User's active loans | Authenticated |
| GET | `/api/v1/transactions/` | All transactions | Admin |
| GET | `/api/v1/transactions/overdue/` | Overdue transactions | Admin |
| GET | `/api/v1/transactions/penalties/` | All penalties | Admin |

## Query Parameters

### Books Filtering
- `?title=<value>` - Filter by title (contains)
- `?author=<value>` - Filter by author name
- `?isbn=<value>` - Filter by exact ISBN
- `?available=true` - Filter by availability
- `?search=<value>` - Search in title, author, ISBN
- `?ordering=title|-published_date` - Order results
- `?page=1&page_size=10` - Pagination

## Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

### Checkout a book
```bash
curl -X POST http://localhost:8000/api/v1/transactions/checkout/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "loan_days": 14
  }'
```

### Return a book
```bash
curl -X POST http://localhost:8000/api/v1/transactions/return/1/ \
  -H "Authorization: Bearer <your_access_token>"
```

## Deployment

### Heroku Deployment

1. Install Heroku CLI and login
2. Create a new Heroku app
   ```bash
   heroku create your-app-name
   ```
3. Set environment variables
   ```bash
   heroku config:set DJANGO_SECRET_KEY=your-secret-key
   heroku config:set DJANGO_ENV=production
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```
4. Add PostgreSQL addon
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```
5. Deploy
   ```bash
   git push heroku main
   ```

## Default Admin Credentials

- Username: `admin`
- Email: `admin@library.com`
- Password: `admin123`

**Note**: Change these credentials in production!

## License

This project is for educational purposes as part of the ALX Backend Engineering Capstone Project.
