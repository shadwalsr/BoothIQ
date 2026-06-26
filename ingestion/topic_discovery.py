import os
import sys
import json
import pandas as pd
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Ensure the script can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_supabase import get_supabase_client

def main():
    load_dotenv()
    
    # 1. Fetch news articles from Supabase
    print("Connecting to Supabase...")
    supabase = get_supabase_client()
    
    print("Fetching news articles from public.news_articles...")
    # Fetch all news articles. Supabase select returns max 1000 by default unless we handle pagination.
    # Wait, the news articles count is ~5430, so we need to page/fetch in batches.
    all_records = []
    limit = 1000
    offset = 0
    while True:
        print(f"  Fetching rows {offset} to {offset + limit}...")
        res = supabase.table('news_articles').select('*').range(offset, offset + limit - 1).execute()
        data = res.data
        if not data:
            break
        all_records.extend(data)
        if len(data) < limit:
            break
        offset += limit
        
    print(f"Fetched {len(all_records)} news articles.")
    df = pd.DataFrame(all_records)
    
    # Ensure raw/processed directory exists
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    # Fill empty text columns
    df['title'] = df['title'].fillna('')
    df['snippet_text'] = df['snippet_text'].fillna('')
    
    # 2. Prepare text documents
    print("Preparing documents for embedding...")
    docs = []
    for _, row in df.iterrows():
        title = row['title'].strip()
        snippet = row['snippet_text'].strip()
        if title and snippet:
            doc = f"{title} - {snippet}"
        elif snippet:
            doc = snippet
        else:
            doc = title
        docs.append(doc)
        
    df['doc_text'] = docs
    # Filter out empty documents
    df = df[df['doc_text'].str.strip() != '']
    print(f"Documents to process: {len(df)}")
    
    # 3. Generate embeddings
    print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model_name = "all-MiniLM-L6-v2"
    embedding_model = SentenceTransformer(model_name)
    
    print("Encoding documents (this might take a few seconds)...")
    embeddings = embedding_model.encode(df['doc_text'].tolist(), show_progress_bar=True)
    print(f"Generated embeddings shape: {embeddings.shape}")
    
    # 4. Fit BERTopic
    print("Fitting BERTopic model with deterministic UMAP/HDBSCAN...")
    # Set random_state=42 to make UMAP deterministic
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    
    topic_model = BERTopic(
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        embedding_model=embedding_model,
        verbose=True
    )
    
    topics, probs = topic_model.fit_transform(df['doc_text'].tolist(), embeddings)
    df['topic_id'] = topics
    
    # 5. Extract topic definitions
    print("Extracting topic metadata...")
    topic_info = topic_model.get_topic_info()
    print("\nBERTopic Topic Info Summary:")
    print(topic_info.to_string(index=False))
    
    # Build topic details JSON
    discovered_topics = {}
    for _, row in topic_info.iterrows():
        topic_id = int(row['Topic'])
        count = int(row['Count'])
        name = row['Name']
        
        # Get top 10 keywords and their scores
        repr_words = []
        if topic_id != -1:
            words_scores = topic_model.get_topic(topic_id)
            if words_scores:
                repr_words = [word for word, score in words_scores]
        else:
            # For outlier topic -1, just use the auto name or general terms
            repr_words = ["outliers", "noise"]
            
        discovered_topics[str(topic_id)] = {
            "name": name,
            "count": count,
            "representative_words": repr_words
        }
        
    discovered_topics_path = os.path.join(processed_dir, "discovered_topics.json")
    with open(discovered_topics_path, "w", encoding="utf-8") as f:
        json.dump(discovered_topics, f, indent=2)
    print(f"\nDiscovered topics JSON saved to: {discovered_topics_path}")
    
    # 6. Save article assignments
    # We save: article database id, constituency code ac_no, and assigned topic_id
    assignments_df = df[['id', 'ac_no', 'topic_id', 'title']].copy()
    # Fill ac_no NaN with -1 or drop? We keep it to know if any unassigned news is there
    assignments_path = os.path.join(processed_dir, "article_topic_assignments.csv")
    assignments_df.to_csv(assignments_path, index=False)
    print(f"Article topic assignments CSV saved to: {assignments_path}")
    print("\nTopic Discovery completed successfully!")

if __name__ == "__main__":
    main()
