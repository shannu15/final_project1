# final_project1
Dosa restaurant API
My Dosa Restaurant API

Overview

Welcome to the Dosa Restaurant API! This project provides a RESTful API for managing orders and customers of a Dosa restaurant. It enables functionalities like creating, updating, and retrieving orders, as well as managing customer information.

Features

Order Management: Create, update, retrieve, and delete orders.
Customer Management: Add, update, retrieve, and delete customer details.
Item Management: Add, update, retrieve, and delete menu items.
Technology Stack

This project is built using Python and SQLite database. It utilizes the FastAPI framework for building the RESTful API and SQLite for data storage.

Components
FastAPI: A modern, fast (high-performance), web framework for building APIs with Python.
SQLite Database: A lightweight disk-based database that doesn't require a separate server process.
Installation

To get started with the Dosa Restaurant API, follow these steps:

Clone the repository:
bash
Copy code
git clone https://github.com/shannu15/finalterm_project.git
Install dependencies:
bash
Copy code
pip install fastapi
pip install uvicorn
Usage

Running the Server
To start the server, run the following command:

bash
Copy code
uvicorn main:app --reload
The server will start running on http://localhost:8000 by default.

API Endpoints
The API offers the following endpoints:

Orders: CRUD operations for managing orders.
Customers: CRUD operations for managing customer information.
Items: CRUD operations for managing menu items.
For detailed information about each endpoint, refer to the API documentation.

API Documentation
Explore the API documentation to learn about available endpoints and how to interact with them.

Contributing

Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

License

This project is licensed under the MIT License.
