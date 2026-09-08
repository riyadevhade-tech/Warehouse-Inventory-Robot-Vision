# 📦 Warehouse Inventory & Robot Vision System

## 📌 Project Overview

The Warehouse Inventory & Robot Vision System is a Python-based smart warehouse management project.

It helps manage inventory, identify low-stock products, analyze warehouse data, display graphs, and demonstrate product identification using computer vision.

## 🎯 Objectives

- Manage warehouse inventory digitally
- Monitor product quantities
- Detect low-stock products
- Calculate inventory value
- Analyze warehouse data
- Display inventory graphs
- Demonstrate robot vision-based product identification
- Provide a professional dashboard

## 🚀 Features

### 1. Inventory Management
- Product ID
- Product Name
- Category
- Quantity
- Price
- Reorder Level
- Warehouse Section

### 2. Low Stock Detection

The system automatically identifies products whose quantity reaches or falls below the reorder level.

### 3. Inventory Analysis

The system calculates:

- Total Products
- Total Stock
- Total Inventory Value
- Category-wise Stock
- Warehouse Section-wise Stock

### 4. Data Visualization

The project generates:

- Product-wise Stock Graph
- Category-wise Stock Graph
- Low Stock Graph

### 5. Robot Vision

The system uses OpenCV to load and display a warehouse product image and demonstrate product identification.

### 6. Professional Dashboard

A Streamlit dashboard displays:

- Inventory KPIs
- Inventory Table
- Low Stock Alerts
- Charts
- Robot Vision Image
- Product Information

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- OpenCV
- Streamlit
- CSV

## 📁 Project Structure

```text
MIDC_Project
│
├── analysis
│   ├── inventory_analysis.py
│   └── inventory_graphs.py
│
├── data
│   └── products.csv
│
├── images
│   └── mouse_01.jpg (2).png
│
├── vision
│   └── robot_vision.py
│
├── dashboard
│   └── app.py
│
├── category_stock.png
├── product_stock.png
├── low_stock.png
├── main.py
└── README.md