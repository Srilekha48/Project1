CREATE TABLE households (
    household_id INT PRIMARY KEY,
    address TEXT,
    income DECIMAL(10,2)
);

CREATE TABLE citizens (
    citizen_id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(10),
    dob DATE,
    household_id INT,
    contact_number VARCHAR(10),
    educational_qualification VARCHAR(255),
    role VARCHAR(100),
    FOREIGN KEY (household_id) REFERENCES households(household_id)
    ON DELETE CASCADE
);


CREATE TABLE land_records (
    land_id INT PRIMARY KEY,
    citizen_id INT,
    area_acres DECIMAL(10,2),
    crop_type VARCHAR(255),
    FOREIGN KEY (citizen_id) REFERENCES citizens(citizen_id)
    ON DELETE CASCADE
);


CREATE TABLE welfare_schemes (
    scheme_id INT PRIMARY KEY,
    scheme_name VARCHAR(255),
    beneficiaries TEXT,
                                                                                                                  budget DECIMAL(15,2)
);

CREATE TABLE scheme_enrollments (
    enrollment_id INT PRIMARY KEY,
    citizen_id INT,
    scheme_id INT,
    enrollment_date DATE,
    FOREIGN KEY (citizen_id) REFERENCES citizens(citizen_id)
    ON DELETE CASCADE,
    FOREIGN KEY (scheme_id) REFERENCES welfare_schemes(scheme_id)
    ON DELETE CASCADE
);


CREATE TABLE panchayat_committee_members (
    member_id INT PRIMARY KEY,
    citizen_id INT,
    role VARCHAR(255),
    
    term_start_date DATE,
    term_end_date DATE,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (citizen_id) REFERENCES citizens(citizen_id)
    ON DELETE CASCADE
);

CREATE TABLE citizen_taxes (
    tax_id INT PRIMARY KEY,
    citizen_id INT,
    tax_type VARCHAR(255),
    tax_amount DECIMAL(15,2),
    collection_date DATE,
    FOREIGN KEY (citizen_id) REFERENCES citizens(citizen_id)
    ON DELETE CASCADE
);



CREATE TABLE expenditures (
    expend_id INT PRIMARY KEY,
    category VARCHAR(255),
    amount DECIMAL(15,2),
    date_of_expenditure DATE
);

CREATE TABLE assets (
    asset_id INT PRIMARY KEY,
    asset_name VARCHAR(255),
    asset_type VARCHAR(255),
    installation_date DATE
);


CREATE TABLE vaccinations (
    vaccination_id INT PRIMARY KEY,
    citizen_id INT,
    vaccine_type VARCHAR(255),
    date_administered DATE,
    FOREIGN KEY (citizen_id) REFERENCES citizens(citizen_id)
);

CREATE TABLE government_monitors (
    monitor_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(10),
    dob DATE,
    household_id INT,
    contact_number VARCHAR(10),
    educational_qualification VARCHAR(255),
    username VARCHAR(255),
    password VARCHAR(255) NOT NULL
);






