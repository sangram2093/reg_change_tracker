CREATE TABLE regulations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE uploads (
    id SERIAL PRIMARY KEY,
    regulation_id INTEGER NOT NULL REFERENCES regulations(id),
    old_path TEXT,
    new_path TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE summaries (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    old_summary TEXT,
    new_summary TEXT
);

CREATE TABLE entity_graphs (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    old_json TEXT,
    new_json TEXT,
    graph_old TEXT,
    graph_new TEXT
);

INSERT INTO regulations (name) VALUES
('EMIR Refit'),
('MiFID II'),
('SFTR'),
('AWPR')
ON CONFLICT (name) DO NOTHING;
