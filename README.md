# E-Commerce API 🛍️

This is the backend API for a robust and scalable e-commerce platform, built with Django and Django REST Framework.



---

## ✨ Features

* **User Authentication:** Secure user registration and login using JWT.
* **Product Management:** Full CRUD operations for products and categories.
* **Shopping Cart:** Add, view, update, and remove items from the cart.
* **Order Management:** Place orders and view order history.
* **Payment Integration:** (Planned) Integration with a payment gateway.

---

## 🛠️ Technology Stack

* **Backend:** Python, Django, Django REST Framework
* **Database:** PostgreSQL
* **Authentication:** JWT (JSON Web Tokens)
* **Code Quality:** Ruff (for formatting and linting)
* **Environment:** Docker (for deployment)

---

## 🌿 Development Workflow

* Work on the `develop` branch (never push directly to `main`).
* Create a new branch for each feature or fix (e.g., `feature/add-cart-api`).
* Use Conventional Commit messages like `feat:`, `fix:`, `docs:`, etc.
* For more details, see the [Contribution Guidelines](CONTRIBUTING.md).

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

Make sure you have the following installed on your system:
* Python (3.12.x)
* PostgreSQL (17.x)
* Git

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Karimi-Amirhossein/E-Commerce-API]
    cd E-Commerce-API
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows (using a shell like Git Bash) or macOS/Linux
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    * Create a copy of the example environment file: `cp .env.example .env`
    * Open the `.env` file and fill in your database credentials and a new `SECRET_KEY`.

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    Once the server is running, the API will be available at:
    👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 📚 API Documentation

A full API documentation will be available via **Postman Collection** and an interactive **Swagger UI** once implemented.

The Swagger UI will be accessible at `/api/schema/docs/`.

---

## 🤝 Contributing

We welcome contributions! Please read our contribution guidelines to get started. All the rules for our Git workflow, code style, and more are documented there.

**[Read our Contributing Guidelines](CONTRIBUTING.md)**

---

## 📄 License

This project is distributed under the MIT License.
