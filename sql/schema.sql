-- PostgreSQL schema equivalent (Django migrations create these tables)

CREATE TABLE IF NOT EXISTS qa_appsetting (
    id bigint PRIMARY KEY,
    max_question_length integer NOT NULL CHECK (max_question_length >= 10),
    submissions_enabled boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS qa_question (
    id bigserial PRIMARY KEY,
    name varchar(120) NULL,
    question text NOT NULL,
    status varchar(16) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS qa_question_status_created_at_idx
    ON qa_question (status, created_at DESC);
