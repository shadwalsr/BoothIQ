import os
import json
import re

def generate_mapping():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    topics_path = os.path.join(base_dir, "data", "processed", "discovered_topics.json")
    
    if not os.path.exists(topics_path):
        print(f"Error: {topics_path} not found. Run topic_discovery.py first.")
        return
        
    with open(topics_path, "r", encoding="utf-8") as f:
        topics = json.load(f)
        
    # Heuristic keywords for mapping topics to our taxonomy (exact word matching)
    keywords_map = {
        "inflation": {"inflation", "prices", "fuel", "cost", "costs", "rising", "price"},
        "communal": {"communal", "tension", "tensions", "harmony", "religious", "friction", "clash", "clashes", "security", "incident", "incidents"},
        "development": {"infrastructure", "road", "roads", "connectivity", "development", "developmental", "electricity", 
                        "school", "schools", "hospital", "hospitals", "water", "sanitation", "sanitational", "flood", 
                        "floods", "embankments", "embankment", "bridge", "bridges", "drainage", "growth", "economic", 
                        "trade", "survey", "industries", "mandis", "mandi", "power", "healthcare", "phc", "drinking", 
                        "clean", "hygiene", "primary"},
        "welfare": {"welfare", "scheme", "schemes", "pension", "pensions", "allowance", "housing", "pmay", "mgnrega", 
                    "ujjwala", "gas", "subsidy", "subsidies", "shg", "jeevika", "free", "rations", "assistance", 
                    "support", "benefit", "benefits", "allocations", "allocation"},
        "caste": {"caste", "census", "survey", "backward", "reservation", "reservations", "community", "communities", 
                  "obc", "ebc", "sc", "st"},
        "unemployment": {"jobs", "unemployment", "youth", "placement", "placements", "employment", "recruitment", 
                        "hiring", "vacancies", "job", "career", "careers"}
    }
    
    mapping = {}
    classification_rationale = []
    
    print("Classifying discovered topics (exact word match):")
    for topic_id, details in topics.items():
        if topic_id == "-1":
            mapping[topic_id] = "other"
            classification_rationale.append(f"Topic {topic_id} (Outliers/Noise): Mapped to 'other' (pre-defined outlier category).")
            continue
            
        name = details["name"].lower()
        repr_words = [w.lower() for w in details["representative_words"]]
        
        # Tokenize words using regex to avoid substring matches (e.g. 'st' in 'analysts')
        all_tokens = set(re.findall(r'\b[a-z]+\b', name + " " + " ".join(repr_words)))
        
        # Count keyword hits per category
        hits = {category: 0 for category in keywords_map}
        for category, keywords in keywords_map.items():
            # Intersect sets to find exact word matches
            common_words = all_tokens.intersection(keywords)
            hits[category] = len(common_words)
                    
        # Find category with max hits
        max_category = "other"
        max_hits = 0
        for category, count in hits.items():
            if count > max_hits:
                max_hits = count
                max_category = category
                
        # Assign mapping
        mapping[topic_id] = max_category
        
        # Build rationale description
        top_3_words = repr_words[:4]
        classification_rationale.append(
            f"Topic {topic_id} ({details['name']}): Mapped to '{max_category}' because of keywords {top_3_words}."
        )
        print(f"  Topic {topic_id:4}: Name = {details['name'][:40]:40} -> {max_category} (hits: {max_hits})")
        
    mapping_path = os.path.join(base_dir, "ingestion", "discourse_mapping.json")
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
        
    print(f"\nDiscourse mapping JSON saved to: {mapping_path}")
    
    # Save classification rationale for data dictionary update
    rationale_path = os.path.join(base_dir, "data", "processed", "classification_rationale.txt")
    with open(rationale_path, "w", encoding="utf-8") as f:
        f.write("\n".join(classification_rationale))
    print(f"Classification rationale saved to: {rationale_path}")

if __name__ == "__main__":
    generate_mapping()
