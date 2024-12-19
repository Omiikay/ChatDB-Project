# ChatDB - A Smart Helper for Learning and Running Database Queries

ChatDB is an interactive ChatGPT-like application that assists users in learning how to query data in database systems, including SQL and NoSQL databases. Unlike traditional query interfaces, ChatDB offers a natural language approach to database interactions while maintaining the ability to execute queries and display results in real-time.

## 🌟 Features

### 1. Database Exploration
- Select and explore different databases (MySQL and MongoDB)
- View tables/collections and their attributes
- Browse sample data to understand database structure

### 2. Query Assistance
- Generate sample queries using various SQL/NoSQL constructs
- Support for different query types including:
  - GROUP BY operations
  - HAVING clauses
  - ORDER BY statements
  - Aggregation functions
  - WHERE conditions
  - JOIN operations
  
### 3. Natural Language Processing
- Input queries in natural language
- Pattern recognition for query generation
- Converts natural language to SQL/MongoDB queries
- Real-time query execution and results display

### 4. Interactive Learning
- Dynamic query template generation
- Explanation of query components
- Error handling with helpful feedback
- Sample query generation based on database content

## 📁 Project Structure

```
/
├── README.txt          		# this file
├── requirements.txt    		# List of dependencies
├── application/
│   ├── __init__.py     		# Application initialization
│   ├── static/        			# static files (CSS, JS, images...)
│   │   ├── images/
│   │   │   └── logo.png
│   │   ├── style.css
│   │   └── script.js
│   ├── templates/      		# HTML template
│   │   └── index.html
│   ├── mongo_component/        	# components for mongodb
│   │   ├── mongoApi.py			# functions to interact with mongo db
│   │   └── mongoQueryBuilder.py	# builder standard mongo query
│   ├── mysql_component/        	# components for mysqldb
│   │   ├── mysqlApi.py			# functions to interact with mysql db
│   │   └── mysqlQueryBuilder.py	# builder standard mysql query
│   ├── toolkit/         		
│   │   ├── sampleGeneratator.py 	# generate samples 
│   │   └── templateBuilder.py		# templates queries, and input parsing
│   ├── constant.py         		# Environment variables & configuration
│   └── chatbot.py         		# chatbot module
└── app.py              		# start the Flask application  

```

  
## 🛠️ Technology Stack

- **Frontend**: HTML, CSS, JavaScript, jQuery
- **Backend**: Python Flask
- **Databases**: 
  - MySQL for relational data
  - MongoDB for NoSQL operations
- **Additional Libraries**:
  - flask_pymongo for MongoDB integration
  - flask_pymysql for MySQL connectivity
  - pandas for data processing
  - Regular expressions (re) for pattern matching

## 🚀 Setup and Installation

1. Clone the repository
```bash
git clone [repository-url]
cd chatdb
```

2. Install required dependencies
```bash
pip install -r requirements.txt
```

3. Configure database connections
- Update MySQL configuration in `constant.py`
- Set MongoDB connection string in `constant.py`

4. Run the application
```bash
python app.py
```

5. Open your browser and navigate to: `http://127.0.0.1:5001`.


## 📖 Usage

1. **Database Selection**
   - Choose between MySQL and MongoDB interfaces
   - Upload your dataset through the web interface

2. **Query Exploration**
   - Use the "Show Samples" option to see example queries
   - Learn different query patterns and structures

3. **Natural Language Queries**
   - Type queries in natural language
   - Example: "Show me the total sales by product category"
   - View generated database queries and results

---
Made with ❤️ by Team ChatDB 40
