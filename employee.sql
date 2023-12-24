CREATE TABLE IF NOT EXISTS department (
department_ID SERIAL PRIMARY KEY,
department_name VARCHAR(180) NOT NULL
);

CREATE TABLE IF NOT EXISTS employee (
employee_ID SERIAL PRIMARY KEY,
name VARCHAR(80) NOT NULL,
department_ID INTEGER NOT NULL REFERENCES department(department_ID)
);

CREATE TABLE IF NOT EXISTS boss (
boss_ID SERIAL PRIMARY KEY,
employee_ID INTEGER NOT NULL REFERENCES employee(employee_ID),
departmint_ID INTEGER NOT NULL REFERENCES departmint(departmint_ID)
);
