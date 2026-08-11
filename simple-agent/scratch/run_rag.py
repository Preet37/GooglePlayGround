import os
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-04-61ad25d47240"
LOCATION = "us-central1"
GCS_PATH = f"gs://{PROJECT_ID}-rag-docs/3d_printing_handbook.txt"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# 1. Update config
try:
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )
except Exception as e:
    print("Config note:", e)

# 2. Create Corpus
corpus = rag.create_corpus(
    display_name="3d-printing-handbook-corpus",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"
    ),
)
print("CREATED_CORPUS_NAME:", corpus.name)

# 3. Import File
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
)
print("Imported count:", getattr(resp, "imported_rag_files_count", resp))
