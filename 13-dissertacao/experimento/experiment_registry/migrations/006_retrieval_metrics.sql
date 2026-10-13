ALTER TABLE retrieval_metrics ADD COLUMN precision_at_1 REAL;
ALTER TABLE retrieval_metrics ADD COLUMN precision_at_5 REAL;
ALTER TABLE retrieval_metrics ADD COLUMN precision_at_10 REAL;
ALTER TABLE retrieval_metrics ADD COLUMN hit_at_1 REAL;
ALTER TABLE retrieval_metrics ADD COLUMN hit_at_5 REAL;
ALTER TABLE retrieval_metrics ADD COLUMN hit_at_10 REAL;
ALTER TABLE retrieval_metrics ADD COLUMN ndcg_at_5 REAL;
ALTER TABLE retrieval_metrics ADD COLUMN ndcg_at_10 REAL;
