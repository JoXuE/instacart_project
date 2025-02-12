DROP DATABASE IF EXISTS instacart_db;
CREATE DATABASE instacart_db;
USE instacart_db;

-- Eliminar tablas si existen
DROP TABLE IF EXISTS order_products;
DROP TABLE IF EXISTS instacart_orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS aisles;
DROP TABLE IF EXISTS departments;

-- Tabla de Departamentos
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department VARCHAR(255) 
);

-- Tabla de Pasillos (Aisles)
CREATE TABLE aisles (
    aisle_id INT PRIMARY KEY,
    aisle VARCHAR(255) 
);

-- Tabla de Productos
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    aisle_id INT,
    department_id INT,
    FOREIGN KEY (aisle_id) REFERENCES aisles(aisle_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Tabla de Órdenes
CREATE TABLE instacart_orders (
    order_id INT PRIMARY KEY,  
    user_id INT,
    eval_set VARCHAR(50),
    order_number INT,
    order_dow INT,
    order_hour_of_day INT,
    days_since_prior_order FLOAT
);

-- Tabla de Productos en Órdenes
CREATE TABLE order_products (
    order_id INT,
    product_id INT,
    add_to_cart_order INT,
    reordered INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES instacart_orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
