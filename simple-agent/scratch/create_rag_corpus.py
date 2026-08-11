import os
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-61ad25d47240")
LOCATION = "us-central1"
GCS_PATH = f"gs://{PROJECT_ID}-rag-docs/3d_printing_handbook.txt"

def build_corpus():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    try:
        rag.update_rag_engine_config(rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        ))
        print("Updated RAG Engine Config to Serverless mode")
    except Exception as e:
        print("Config update note:", e)

    corpus = rag.create_corpus(
        display_name="3d-printing-handbook-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    print(f"CORPUS_NAME={corpus.name}")

    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PATH],
        transformation_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100),
    )
    print("Import response:", resp)
    return corpus.name

if __name__ == "__main__":
    build_corpus()
