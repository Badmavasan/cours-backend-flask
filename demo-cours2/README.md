# Flask CRUD API with User and Todo

A simple Flask REST API with SQLAlchemy ORM and MySQL database.

## Database Credentials

| Field    | Value       |
|----------|-------------|
| Host     | localhost   |
| Port     | 3306        |
| Database | flaskdb     |
| Username | flaskuser   |
| Password | flaskpass   |
| Root Password | rootpass |

## Setup

### 1. Start MySQL with Docker

Build and run the MySQL container:

```bash
# Build the image
docker build -t flask-mysql .

# Run the container
docker run -d --name flask-mysql-db -p 3306:3306 flask-mysql
```

Wait a few seconds for MySQL to initialize.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Flask App

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

## Connect to Database

### Using MySQL CLI (inside container)

```bash
docker exec -it flask-mysql-db mysql -u flaskuser -pflaskpass flaskdb
```

### Using MySQL Workbench or DBeaver

- Host: `127.0.0.1`
- Port: `3306`
- Username: `flaskuser`
- Password: `flaskpass`
- Database: `flaskdb`

## API Endpoints

### Users

| Method | Endpoint       | Description        |
|--------|----------------|--------------------|
| GET    | /users         | Get all users      |
| GET    | /users/:id     | Get user by ID     |
| POST   | /users         | Create new user    |
| PUT    | /users/:id     | Update user        |
| DELETE | /users/:id     | Delete user        |

### Todos

| Method | Endpoint              | Description              |
|--------|-----------------------|--------------------------|
| GET    | /todos                | Get all todos            |
| GET    | /todos/:id            | Get todo by ID           |
| GET    | /users/:id/todos      | Get todos for a user     |
| POST   | /todos                | Create new todo          |
| PUT    | /todos/:id            | Update todo              |
| DELETE | /todos/:id            | Delete todo              |

## Example Requests

### Create a User

```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com"}'
```

### Create a Todo

```bash
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "user_id": 1}'
```

### Update a Todo

```bash
curl -X PUT http://localhost:5000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Get User's Todos

```bash
curl http://localhost:5000/users/1/todos
```

## Stop and Remove Container

```bash
docker stop flask-mysql-db
docker rm flask-mysql-db
```
