-- Order of sql command that I gave below is not the same as the order in which they are executed, Run independent tables with no 
-- foreign key constraints first and then run the tables with foreign key constraints. No harm done if you run the tables with foreign
-- but an error gets thrown and then you can run it later.

-- Create Users Table
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Create Profiles Table
CREATE TABLE Profiles (
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    gender VARCHAR(10),
    fname VARCHAR(50),
    mname VARCHAR(50),
    lname VARCHAR(50),
    age INT,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Create Vaccines Table
CREATE TABLE Vaccines (
    vaccine_id INT PRIMARY KEY AUTO_INCREMENT,
    description TEXT,
    min_age INT,
    max_age INT,
    name VARCHAR(100)
);

-- Create Inventory Table
CREATE TABLE Inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    expiration_date DATE,
    quantity INT
);

-- Create Appointments Table
CREATE TABLE Appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_date DATE,
    time_slot TIME,
    vaccine_id INT,
    profile_id INT,
    schedule_id INT,
    FOREIGN KEY (vaccine_id) REFERENCES Vaccines(vaccine_id),
    FOREIGN KEY (profile_id) REFERENCES Profiles(profile_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedules(schedule_id)
);

-- Create Schedules Table
CREATE TABLE Schedules (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE,
    dose_number INT,
    centre_id INT,
    FOREIGN KEY (centre_id) REFERENCES VaccineCentres(centre_id)
);

-- Create VaccineCentres Table
CREATE TABLE VaccineCentres (
    centre_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    address TEXT,
    district VARCHAR(50),
    pincode VARCHAR(10)
);

-- Create Includes Table (Vaccines ↔ Schedules)
CREATE TABLE Includes (
    vaccine_id INT,
    schedule_id INT,
    PRIMARY KEY (vaccine_id, schedule_id),
    FOREIGN KEY (vaccine_id) REFERENCES Vaccines(vaccine_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedules(schedule_id)
);

-- Create AvailableAt Table (Vaccines ↔ VaccineCentres)
CREATE TABLE AvailableAt (
    vaccine_id INT,
    centre_id INT,
    PRIMARY KEY (vaccine_id, centre_id),
    FOREIGN KEY (vaccine_id) REFERENCES Vaccines(vaccine_id),
    FOREIGN KEY (centre_id) REFERENCES VaccineCentres(centre_id)
);

-- Create StoredAt Table (Vaccines ↔ Inventory)
CREATE TABLE StoredAt (
    inventory_id INT,
    vaccine_id INT,
    PRIMARY KEY (inventory_id, vaccine_id),
    FOREIGN KEY (inventory_id) REFERENCES Inventory(inventory_id),
    FOREIGN KEY (vaccine_id) REFERENCES Vaccines(vaccine_id)
);
