CREATE TABLE regulations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE uploads (
    id SERIAL PRIMARY KEY,
    regulation_id INTEGER NOT NULL REFERENCES regulations(id),
    old_path VARCHAR(1024) NOT NULL,
    new_path VARCHAR(1024) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE graphs (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    graph_old_json TEXT NOT NULL,
    graph_new_json TEXT NOT NULL,
    diff_json TEXT
);

CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    summary_text TEXT,
    raw_llm_response TEXT
);

CREATE TABLE kops (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    kop_text TEXT,
    generated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
