CREATE TABLE IF NOT EXISTS corpus_versions (
    corpus_version_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    source_path TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    document_count INTEGER NOT NULL DEFAULT 0,
    excluded_count INTEGER NOT NULL DEFAULT 0,
    metadata_coverage_json TEXT NOT NULL DEFAULT '{}',
    is_legacy INTEGER NOT NULL DEFAULT 0,
    UNIQUE(source_sha256, name)
);
CREATE TABLE IF NOT EXISTS documents (
    corpus_version_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    original_text TEXT,
    indexed_text TEXT,
    text_source TEXT NOT NULL CHECK(text_source IN ('integral','resumo','ausente','legado')),
    source_url TEXT,
    author TEXT,
    document_date TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    exclusion_reason TEXT,
    PRIMARY KEY(corpus_version_id,document_id),
    FOREIGN KEY(corpus_version_id) REFERENCES corpus_versions(corpus_version_id)
);
CREATE TABLE IF NOT EXISTS chunk_sets (
    chunk_set_id TEXT PRIMARY KEY,
    corpus_version_id TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    tokenizer TEXT NOT NULL,
    tokenizer_version TEXT,
    segmentation_unit TEXT NOT NULL,
    window_size INTEGER NOT NULL,
    overlap_size INTEGER NOT NULL,
    state TEXT NOT NULL DEFAULT 'completed' CHECK(state IN ('building','completed','failed','archived')),
    chunk_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(corpus_version_id,config_hash),
    FOREIGN KEY(corpus_version_id) REFERENCES corpus_versions(corpus_version_id)
);
ALTER TABLE document_chunks RENAME TO document_chunks_legacy;
DROP INDEX IF EXISTS idx_chunks_document;
CREATE TABLE document_chunks (
    chunk_set_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    corpus_version_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    text TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    source_sha256 TEXT,
    position_start INTEGER,
    position_end INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(chunk_set_id,chunk_id),
    FOREIGN KEY(chunk_set_id) REFERENCES chunk_sets(chunk_set_id),
    FOREIGN KEY(corpus_version_id,document_id) REFERENCES documents(corpus_version_id,document_id)
);
CREATE INDEX idx_chunks_document ON document_chunks(corpus_version_id,document_id,chunk_set_id);
CREATE INDEX idx_chunks_start ON document_chunks(chunk_set_id,document_id,position_start);
CREATE TABLE IF NOT EXISTS migration_reconciliation (
    reconciliation_id INTEGER PRIMARY KEY,
    migration_name TEXT NOT NULL,
    entity TEXT NOT NULL,
    old_count INTEGER NOT NULL,
    new_count INTEGER NOT NULL,
    details_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO corpus_versions(corpus_version_id,name,source_sha256,source_path,document_count,is_legacy)
SELECT 'legacy-'||substr(COALESCE(source_sha256,''),1,20),'Segmentação legada',COALESCE(source_sha256,''),'legado',COUNT(DISTINCT document_id),1
FROM document_chunks_legacy GROUP BY source_sha256;
INSERT OR IGNORE INTO documents(corpus_version_id,document_id,original_text,indexed_text,text_source,metadata_json)
SELECT 'legacy-'||substr(COALESCE(source_sha256,''),1,20),document_id,NULL,NULL,'legado','{}'
FROM document_chunks_legacy GROUP BY source_sha256,document_id;
INSERT OR IGNORE INTO chunk_sets(chunk_set_id,corpus_version_id,config_hash,tokenizer,tokenizer_version,segmentation_unit,window_size,overlap_size,chunk_count)
SELECT 'legacy-set-'||substr(COALESCE(source_sha256,''),1,20),'legacy-'||substr(COALESCE(source_sha256,''),1,20),'legacy-whitespace-160-32','whitespace-regex',NULL,'whitespace tokens',160,32,COUNT(*)
FROM document_chunks_legacy GROUP BY source_sha256;
INSERT OR IGNORE INTO document_chunks(chunk_set_id,chunk_id,corpus_version_id,document_id,text,metadata_json,source_sha256)
SELECT 'legacy-set-'||substr(COALESCE(source_sha256,''),1,20),chunk_id,'legacy-'||substr(COALESCE(source_sha256,''),1,20),document_id,text,metadata_json,source_sha256
FROM document_chunks_legacy;
INSERT INTO migration_reconciliation(migration_name,entity,old_count,new_count,details_json)
SELECT '009_versioned_corpus','document_chunks',
 (SELECT COUNT(*) FROM document_chunks_legacy),(SELECT COUNT(*) FROM document_chunks),
 json_object('note','Copied legacy chunks. Source documents require explicit re-import to restore full text and metadata.')
WHERE NOT EXISTS(SELECT 1 FROM migration_reconciliation WHERE migration_name='009_versioned_corpus');
