# E-commerce Project (ShopHereZone)

## Overview
This project is a robust e-commerce web application built with Django and Django REST Framework. It delivers a seamless shopping experience by incorporating modern features such as OTP-based authentication, dynamic product management, comprehensive cart and order management, secure payment processing via Razorpay, and automated subscription management using Celery.

## Features
- *OTP-based Authentication:*  
  Secure user login implemented using a third-party OTP service.
  
- *Product Management:*  
  - Multiple image uploads for products  
  - Advanced filtering and searching capabilities

- *API Routing:*  
  - Utilizes nested routers for clean and efficient API endpoints

- *Cart & Order Management:*  
  - Full CRUD operations for managing cart items  
  - Conversion of cart items to order items at checkout

- *Payment Integration:*  
  - Razorpay integration with webhook support for secure payment processing

- *Automated Subscription Management:*  
  - Celery is used to send email notifications for subscription renewals  
  - Automatically updates the subscription_active column in the database

## Technologies Used
- *Backend:* Django, Django REST Framework  
- *Payment Gateway:* Razorpay  
- *Task Queue:* Celery (using Redis as the broker)
- *Caching/Broker:* Redis
- *Authentication:* OTP-based (via third-party service)  
- *Database:* Postgresql
