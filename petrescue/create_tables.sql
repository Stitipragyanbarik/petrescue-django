-- SQL script to create tables for Pet Adoption and Rescue Management Portal
-- Database: petrescue_db (create this database first if not exists)


-- Create Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
);

-- Create Pets table with foreign key to users
CREATE TABLE pets (
    pet_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    species VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Insert sample data (optional)
INSERT INTO users (name, email, password, role) VALUES
('John Doe', 'john@example.com', 'hashed_password1', 'user'),
('Jane Smith', 'jane@example.com', 'hashed_password2', 'rescuer'),
('Admin User', 'admin@example.com', 'hashed_password3', 'admin');

INSERT INTO pets (name, species, age, owner_id) VALUES
('Buddy', 'Dog', 3, 1),
('Whiskers', 'Cat', 2, 2);
