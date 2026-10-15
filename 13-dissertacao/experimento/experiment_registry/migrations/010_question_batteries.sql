ALTER TABLE question_catalog ADD COLUMN eligible INTEGER NOT NULL DEFAULT 1 CHECK(eligible IN (0,1));
ALTER TABLE question_catalog ADD COLUMN current_revision INTEGER NOT NULL DEFAULT 1;
ALTER TABLE question_catalog ADD COLUMN pending_review TEXT;
CREATE TABLE IF NOT EXISTS question_revisions (
    question_id TEXT NOT NULL,
    revision INTEGER NOT NULL,
    question_json TEXT NOT NULL,
    change_reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(question_id,revision),
    FOREIGN KEY(question_id) REFERENCES question_catalog(question_id)
);
CREATE TABLE IF NOT EXISTS question_batteries (
    battery_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    purpose TEXT,
    state TEXT NOT NULL DEFAULT 'draft' CHECK(state IN ('draft','frozen','archived')),
    chunk_set_id TEXT,
    parent_battery_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    frozen_at TEXT,
    FOREIGN KEY(parent_battery_id) REFERENCES question_batteries(battery_id),
    FOREIGN KEY(chunk_set_id) REFERENCES chunk_sets(chunk_set_id)
);
CREATE TABLE IF NOT EXISTS battery_members (
    battery_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    question_revision INTEGER NOT NULL,
    source_member_id TEXT,
    split TEXT NOT NULL DEFAULT 'pilot',
    position INTEGER NOT NULL,
    PRIMARY KEY(battery_id,question_id),
    FOREIGN KEY(battery_id) REFERENCES question_batteries(battery_id),
    FOREIGN KEY(question_id,question_revision) REFERENCES question_revisions(question_id,revision)
);
CREATE TABLE IF NOT EXISTS question_reference_chunks (
    reference_id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL,
    question_revision INTEGER NOT NULL,
    chunk_set_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    relevance_grade INTEGER NOT NULL CHECK(relevance_grade BETWEEN 0 AND 2),
    sufficient INTEGER NOT NULL DEFAULT 0 CHECK(sufficient IN (0,1)),
    annotator TEXT NOT NULL,
    justification TEXT NOT NULL,
    review_state TEXT NOT NULL DEFAULT 'draft' CHECK(review_state IN ('draft','review','validated','adjudicated')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(question_id,question_revision) REFERENCES question_revisions(question_id,revision),
    FOREIGN KEY(chunk_set_id,chunk_id) REFERENCES document_chunks(chunk_set_id,chunk_id)
);
CREATE INDEX idx_question_reference_question ON question_reference_chunks(question_id,question_revision,review_state);
CREATE TABLE IF NOT EXISTS question_validation (
    question_id TEXT NOT NULL,
    question_revision INTEGER NOT NULL,
    chunk_set_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK(decision IN ('respondible','partially_respondible','not_respondible')),
    rationale TEXT NOT NULL,
    search_scope TEXT NOT NULL,
    validated_by TEXT NOT NULL,
    validated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(question_id,question_revision,chunk_set_id),
    FOREIGN KEY(question_id,question_revision) REFERENCES question_revisions(question_id,revision),
    FOREIGN KEY(chunk_set_id) REFERENCES chunk_sets(chunk_set_id)
);
CREATE TRIGGER IF NOT EXISTS question_catalog_revision_after_update
AFTER UPDATE OF query,category,answerability,expected_authors_json,reference_doc_ids_json,reference_chunk_ids_json,relevance_judgments_json,expected_answer_criteria,evaluation_risks,curation_notes ON question_catalog
WHEN OLD.query<>NEW.query OR OLD.category<>NEW.category OR COALESCE(OLD.answerability,'')<>COALESCE(NEW.answerability,'')
 OR OLD.expected_authors_json<>NEW.expected_authors_json OR OLD.reference_doc_ids_json<>NEW.reference_doc_ids_json
 OR OLD.reference_chunk_ids_json<>NEW.reference_chunk_ids_json OR OLD.relevance_judgments_json<>NEW.relevance_judgments_json
 OR COALESCE(OLD.expected_answer_criteria,'')<>COALESCE(NEW.expected_answer_criteria,'')
 OR COALESCE(OLD.evaluation_risks,'')<>COALESCE(NEW.evaluation_risks,'')
 OR COALESCE(OLD.curation_notes,'')<>COALESCE(NEW.curation_notes,'')
BEGIN
 UPDATE question_catalog SET current_revision=current_revision+1,status='revisar' WHERE question_id=NEW.question_id;
 INSERT INTO question_revisions(question_id,revision,question_json,change_reason)
 SELECT question_id,current_revision,json_object('question_id',question_id,'query',query,'category',category,'answerability',answerability), 'catalog edit'
 FROM question_catalog WHERE question_id=NEW.question_id;
END;
