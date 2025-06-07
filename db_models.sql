CREATE TABLE regulations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE uploads (
    id SERIAL PRIMARY KEY,
    regulation_id INTEGER NOT NULL REFERENCES regulations(id),
    old_path TEXT NOT NULL,
    new_path TEXT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE summaries (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    old_summary TEXT NOT NULL,
    new_summary TEXT NOT NULL
);

CREATE TABLE entity_graphs (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    old_json TEXT NOT NULL,
    new_json TEXT NOT NULL,
    graph_old TEXT NOT NULL,
    graph_new TEXT NOT NULL
);

INSERT INTO regulations (name) VALUES
('EMIR Refit'),
('MiFID II'),
('SFTR')
ON CONFLICT (name) DO NOTHING;
