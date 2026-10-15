"""Construção e consulta retomável de índices vetoriais Chroma."""
from __future__ import annotations
import hashlib, json, uuid
from .db import connect
from .embedding_retrieval import EmbeddingStore, embed

def create_index(paths, chunk_set_id: str, model: str, client=None, batch_size: int=128) -> dict:
    if not model.strip(): raise ValueError("modelo de embeddings é obrigatório")
    index_id="vi-"+hashlib.sha256(f"{chunk_set_id}:{model}".encode()).hexdigest()[:20]
    collection_name="chunks_"+hashlib.sha256(index_id.encode()).hexdigest()[:32]
    job_id=uuid.uuid4().hex
    with connect(paths.database) as con:
        chunks=con.execute("SELECT chunk_id,document_id,text FROM document_chunks WHERE chunk_set_id=? ORDER BY chunk_id",(chunk_set_id,)).fetchall()
        if not chunks: raise ValueError("segmentação sem chunks")
        con.execute("INSERT INTO vector_indexes(index_id,chunk_set_id,collection_name,provider,model,parameters_json,state,total_items) VALUES (?,?,?,?,?,?, 'building',?) ON CONFLICT(index_id) DO UPDATE SET state='building',error=NULL,total_items=excluded.total_items,updated_at=CURRENT_TIMESTAMP",(index_id,chunk_set_id,collection_name,"openai",model,json.dumps({"batch_size":batch_size,"storage":"chromadb"}),len(chunks)))
        con.execute("INSERT INTO experiment_jobs(job_id,index_id,kind,state,progress_total,progress_done,attempts) VALUES (?,?, 'index-build','running',?,0,1)",(job_id,index_id,len(chunks)))
    collection=EmbeddingStore(paths.embeddings)._client().get_or_create_collection(collection_name,metadata={"chunk_set_id":chunk_set_id,"model":model,"hnsw:space":"cosine"})
    try:
        for start in range(0,len(chunks),batch_size):
            with connect(paths.database) as con:
                job_state=con.execute("SELECT state FROM experiment_jobs WHERE job_id=?",(job_id,)).fetchone()
            if not job_state or job_state['state']!='running':
                with connect(paths.database) as con: con.execute("UPDATE vector_indexes SET state='failed',error='cancelled by operator',updated_at=CURRENT_TIMESTAMP WHERE index_id=?",(index_id,))
                return {"index_id":index_id,"state":"cancelled","completed_items":start}
            batch=chunks[start:start+batch_size]
            existing=set(collection.get(ids=[r["chunk_id"] for r in batch])["ids"])
            missing=[r for r in batch if r["chunk_id"] not in existing]
            if missing:
                vectors=embed([r["text"] for r in missing],model,client)
                if vectors.ndim!=2 or not vectors.shape[1] or not __import__('numpy').isfinite(vectors).all(): raise ValueError("embedding contém dimensão inválida ou valor não finito")
                dimension=int(vectors.shape[1])
                collection.add(ids=[r["chunk_id"] for r in missing],documents=[r["text"] for r in missing],embeddings=vectors.tolist(),metadatas=[{"document_id":r["document_id"],"chunk_set_id":chunk_set_id} for r in missing])
            else:
                sample=collection.get(ids=[batch[0]["chunk_id"]],include=["embeddings"])
                stored_embeddings=sample.get("embeddings")
                dimension=len(stored_embeddings[0]) if stored_embeddings is not None and len(stored_embeddings)>0 else None
            with connect(paths.database) as con:
                con.execute("UPDATE vector_indexes SET completed_items=?,dimensions=COALESCE(dimensions,?),updated_at=CURRENT_TIMESTAMP WHERE index_id=?",(min(start+batch_size,len(chunks)),dimension,index_id))
                con.execute("UPDATE experiment_jobs SET progress_done=?,heartbeat_at=CURRENT_TIMESTAMP WHERE job_id=?",(min(start+batch_size,len(chunks)),job_id))
        if collection.count()!=len(chunks): raise ValueError(f"contagem Chroma divergente: {collection.count()} != {len(chunks)}")
        with connect(paths.database) as con:
            con.execute("UPDATE vector_indexes SET state='completed',completed_items=total_items,updated_at=CURRENT_TIMESTAMP WHERE index_id=?",(index_id,))
            con.execute("UPDATE experiment_jobs SET state='completed',finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(job_id,))
    except Exception as exc:
        with connect(paths.database) as con:
            con.execute("UPDATE vector_indexes SET state='failed',error=?,updated_at=CURRENT_TIMESTAMP WHERE index_id=?",(str(exc),index_id))
            con.execute("UPDATE experiment_jobs SET state='failed',error=?,finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(str(exc),job_id))
        raise
    with connect(paths.database) as con:
        manifest=con.execute("SELECT dimensions,total_items FROM vector_indexes WHERE index_id=?",(index_id,)).fetchone()
    return {"index_id":index_id,"collection_name":collection_name,"count":collection.count(),"dimensions":manifest['dimensions'],"expected_count":manifest['total_items']}

def set_index_state(paths,index_id:str,state:str):
    if state not in {'archived','completed'}:raise ValueError("estado de índice inválido")
    with connect(paths.database) as con:
        row=con.execute("SELECT * FROM vector_indexes WHERE index_id=?",(index_id,)).fetchone()
        if not row:raise ValueError("índice inexistente")
        if state=='completed':
            collection=EmbeddingStore(paths.embeddings)._client().get_collection(row['collection_name'])
            if collection.count()!=row['total_items']:raise ValueError("contagem vetorial não corresponde ao manifesto; reconstrução necessária")
            if not row['dimensions']:raise ValueError("dimensão não registrada; reconstrução necessária")
            sample=collection.get(limit=1,include=['embeddings'])
            stored_embeddings=sample.get('embeddings')
            if stored_embeddings is not None and len(stored_embeddings)>0 and len(stored_embeddings[0])!=row['dimensions']:raise ValueError("dimensão dos vetores diverge do manifesto")
        con.execute("UPDATE vector_indexes SET state=?,updated_at=CURRENT_TIMESTAMP WHERE index_id=?",(state,index_id))
