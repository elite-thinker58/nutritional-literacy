CREATE DATABASE IF NOT EXISTS nutritional_literature;
USE nutritional_literature;

CREATE TABLE items (
    item_id INT PRIMARY KEY,
    item_name VARCHAR(150) NOT NULL,
    category VARCHAR(120) NOT NULL,
    description TEXT
);

CREATE TABLE ingredients (
    ingredient_id INT PRIMARY KEY,
    item_id INT NOT NULL,
    ingredient_name VARCHAR(250) NOT NULL,
    short_description TEXT,
    source_url VARCHAR(1000),
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    UNIQUE (item_id, ingredient_name)
);

CREATE TABLE concerning_ingredients (
    concerning_id INT PRIMARY KEY,
    ingredient_name VARCHAR(250) NOT NULL UNIQUE,
    ingredient_type VARCHAR(250),
    common_food_context TEXT,
    why_concerning TEXT,
    health_evidence_level VARCHAR(250),
    status_in_india TEXT,
    status_in_other_countries TEXT,
    consumer_guidance TEXT,
    source_urls TEXT
);
