import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
    

def find_best_match(user_tags, predefined_tags):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Encode all tags into vector embeddings
    predefined_embeddings = model.encode(predefined_tags, convert_to_numpy=True)
    user_embeddings = model.encode(user_tags, convert_to_numpy=True)
    
    # Create FAISS index
    dimension = predefined_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(predefined_embeddings)
    
    # Search for nearest neighbors
    distances, indices = index.search(user_embeddings, 1)
    
    best_matches = {}
    for i, user_tag in enumerate(user_tags):
        best_match = predefined_tags[indices[i][0]]
        best_score = 1 / (1 + distances[i][0])  # Convert L2 distance to similarity score
        
        best_matches[user_tag] = {'match': best_match, 'accuracy': best_score}
    
    return best_matches

# Example usage
predefined_tags = ["Abortion", "LGBTQ", "Cheap", "Gun Control"]
user_tags = ["Pro-Life", "Crime Rate", "Gay", "Budget", "Pro-Choice", "People", "Manga"]

matches = find_best_match(user_tags, predefined_tags)
print(matches)
