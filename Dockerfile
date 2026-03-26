FROM php:8.2-apache

# Install dependencies and PHP extensions
RUN docker-php-ext-install pdo_mysql mysqli

# Configure Apache to suppress ServerName warning
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Enable Apache modules
RUN a2enmod rewrite

# Set working directory
WORKDIR /var/www/html

# Start Apache
CMD ["apache2-foreground"]
