from typing import List, Dict, Optional, Any, Set
from pathlib import Path
import json
import re
import sys

# Handle import for both module and script execution
try:
    from app.cv.cleaner import normalize_punctuation_for_skills
except ImportError:
    # If running as script, add project root to path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from app.cv.cleaner import normalize_punctuation_for_skills

# Taxonomy file path
TAXONOMY_PATH = Path(__file__).parent.parent.parent / "data" / "skill_taxonomy.json"


def load_taxonomy() -> Dict[str, Any]:
    # Load skill_taxonomy.json file
    if not TAXONOMY_PATH.exists():
        raise FileNotFoundError(f"Taxonomy dosyası bulunamadı: {TAXONOMY_PATH}")
    
    with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)
    
    return taxonomy


def create_ngrams(text: str, max_n: int = 3) -> List[str]:
    # Split text into words
    words = text.split()
    
    # Filter out empty strings only (keep single char words like "C", "R")
    words = [w for w in words if w]
    
    ngrams = []

    # Create n-grams
    for n in range(1, max_n + 1):
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i:i+n])
            ngrams.append(ngram.lower())
    
    return ngrams


# Search in category
def search_in_category(data: Any, target: str) -> Optional[str]:
    
    if isinstance(data,dict):
        #if there is a name field, check if it matches the target
        if "name" in data:
            skill_name = data["name"].lower()
            if skill_name == target:
                return data["name"]

            #if there are aliases, check if any of them match the target
            if "aliases" in data:
                for alias in data["aliases"]:
                    if alias.lower() == target:
                        return data["name"]
        else:
            # nested dict recursive search
            for value in data.values():
                result = search_in_category(value, target)
                if result:
                    return result
    elif isinstance(data,list):
        # list search
        for item in data:
            if isinstance(item,str) and item.lower() == target:
                return item
    return None
            

# search n-gram in taxonomy
def search_in_taxonomy(ngram: str, taxonomy: Dict[str, Any]) -> Optional[str]:

    ngram_lower = ngram.lower()
    for category_name, category_data in taxonomy.items():
        result = search_in_category(category_data, ngram_lower)
        if result:
            return result

    return None


# main extraction function
def extract_skills(text: str) -> List[str]:
    # Normalize punctuation for skill extraction
    normalized_text = normalize_punctuation_for_skills(text)
    
    # Load taxonomy and create n-grams
    taxonomy = load_taxonomy()
    ngrams = create_ngrams(normalized_text, max_n=3)
    found_skills = set()
    
    # Search n-grams in taxonomy
    for ngram in ngrams:
        result = search_in_taxonomy(ngram, taxonomy)
        if result:
            found_skills.add(result)
    
    # Filter single-character skills: only filter them if there's a longer skill starting 
    # with the same character that contains special characters (like C++, C#, Pro/Engineer).
    # This prevents false positives where single-character skills are detected from 
    # compound skills (e.g., "C" from "C++" or "C#"), but keeps valid cases like "R" 
    # even when "REST" is present (since "REST" doesn't contain special characters).
    filtered_skills = set()
    words = normalized_text.split()
    
    # Build a set of all words in normalized text for quick lookup
    words_set = {word.upper() for word in words}
    
    # Special characters that indicate a compound skill (like C++, C#, Pro/Engineer)
    special_chars = ['+', '#', '/', '&', '.', '-']
    
    for skill in found_skills:
        # If it's a single-character skill
        if len(skill) == 1:
            skill_char = skill.upper()
            # Check if it appears as a standalone word in the normalized text
            is_standalone_word = skill_char in words_set
            
            if is_standalone_word:
                # Check if there's a longer skill starting with this character that contains
                # special characters (indicating it's a compound skill like "C++" or "C#")
                has_compound_skill_with_same_start = any(
                    other_skill != skill and 
                    len(other_skill) > 1 and 
                    other_skill.upper().startswith(skill_char) and
                    any(char in other_skill for char in special_chars)
                    for other_skill in found_skills
                )
                
                # Only filter if there's a compound skill starting with the same character
                # Otherwise keep it (e.g., "R" should be kept even if "REST" exists)
                if not has_compound_skill_with_same_start:
                    filtered_skills.add(skill)
        else:
            # Keep all multi-character skills
            filtered_skills.add(skill)

    return sorted(list(filtered_skills))



def get_all_unique_skills_from_taxonomy() -> Set[str]:
    """
    Taxonomy'deki tüm unique skill'leri döndürür.
    """
    taxonomy = load_taxonomy()
    unique_skills = set()
    
    def collect_skills(data: Any) -> None:
        if isinstance(data, dict):
            if "name" in data:
                unique_skills.add(data["name"].lower())
            else:
                for value in data.values():
                    collect_skills(value)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    unique_skills.add(item.lower())
                elif isinstance(item, dict):
                    collect_skills(item)
    
    for category_data in taxonomy.values():
        collect_skills(category_data)
    
    return unique_skills


if __name__ == "__main__":
    # Test with real CV file
    cv_file = Path(__file__).parent.parent.parent / "data" / "test_outputs" / "77828437_cleaned.txt"
    
    if cv_file.exists():
        with open(cv_file, 'r', encoding='utf-8') as f:
            cv_text = f.read()
        
        # Normalize text for skill extraction
        normalized_text = normalize_punctuation_for_skills(cv_text)
        
        # Calculate statistics
        all_words = normalized_text.split()
        unique_words = set(word.lower() for word in all_words)
        all_unique_skills = get_all_unique_skills_from_taxonomy()
        
        # Find how many unique words are skills
        words_that_are_skills = unique_words & all_unique_skills
        
        # Extract skills
        skills = extract_skills(cv_text)
        
        # Print statistics
        print(f"Document has {len(all_words)} words")
        print(f"Unique {len(unique_words)} words")
        print(f"Of these words, {len(words_that_are_skills)} are unique skills")
        print(f"Found {len(skills)} skills")
        
        # Print found skills
        if skills:
            print(f"\n Found {len(skills)} skills:")
            for i, skill in enumerate(skills, 1):
                print(f"  {i}. {skill}")
        else:
            print("\n No skills found.")
    else:
        # Fallback to simple test
        test_text = """
        I am a Python developer with experience in React and Django.
        I also know PostgreSQL and Docker.
        I use Python 3.9 and React 18.
        """
        
        normalized_text = normalize_punctuation_for_skills(test_text)
        all_words = normalized_text.split()
        unique_words = set(word.lower() for word in all_words)
        all_unique_skills = get_all_unique_skills_from_taxonomy()
        words_that_are_skills = unique_words & all_unique_skills
        
        skills = extract_skills(test_text)
        
        print(f"Document has {len(all_words)} words")
        print(f"Unique {len(unique_words)} words")
        print(f"Of these words, {len(words_that_are_skills)} are unique skills")
        print(f"Found {len(skills)} skills")
        
        # Print found skills
        if skills:
            print(f"\nFounded {len(skills)} skills:")
            for i, skill in enumerate(skills, 1):
                print(f"  {i}. {skill}")
        else:
            print("\n No skills found.")
