"""
AI-based CV Information Extractor using spaCy NER
"""

import spacy
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Handle import for both module and script execution
try:
    from app.cv.parser import parse_cv
except ImportError:
    # If running as script, add project root to path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from app.cv.parser import parse_cv

# spaCy modelini yükle
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model yüklü değil!")
    print("Şu komutu çalıştır: python -m spacy download en_core_web_sm")
    nlp = None


def load_countries() -> Dict[str, List[str]]:
    """Ülke listesini JSON'dan yükle"""
    import json
    countries_file = Path(__file__).parent.parent.parent / "data" / "countries.json"
    if countries_file.exists():
        with open(countries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("countries", {})
    return {}


def extract_with_ai(file_path: str) -> Dict:
    """
    PDF/DOCX dosyasından AI ile entity extraction yapar.
    
    Args:
        file_path: PDF veya DOCX dosya yolu
        
    Returns:
        Dict: {
            "name": str,
            "locations": List[str],  # Şehirler ve ülkeler
            "country": str,  # Bulunan ülke
            "organizations": List[str],  # Şirketler
            "dates": List[str],
            "emails": List[str],
            "all_entities": List[Dict]  # Tüm entity'ler
        }
    """
    if not nlp:
        return {"error": "spaCy model yüklü değil"}
    
    # 1. Dosyayı parse et (mevcut parser'ı kullan)
    text = parse_cv(file_path)
    if not text:
        return {"error": "Dosya parse edilemedi"}
    
    # 2. spaCy ile işle
    doc = nlp(text)
    
    # 3. Entity'leri kategorize et
    entities = {
        "PERSON": [],      # İsimler
        "GPE": [],         # Ülkeler, şehirler (Geopolitical Entity)
        "ORG": [],         # Şirketler, organizasyonlar
        "DATE": [],        # Tarihler
        "EMAIL": [],       # Email (spaCy direkt bulmaz, regex ile)
    }
    
    # spaCy entity'lerini kategorize et
    for ent in doc.ents:
        label = ent.label_
        if label in entities:
            entities[label].append(ent.text)
    
    # Email'i regex ile bul (spaCy direkt bulmaz)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    entities["EMAIL"] = emails
    
    # 4. Ülke bulma (countries.json ile)
    countries_dict = load_countries()
    found_country = None
    
    # Önce GPE'lerden ülke bul
    for gpe in entities["GPE"]:
        gpe_upper = gpe.upper().strip()
        # countries.json ile eşleştir
        for country_name, aliases in countries_dict.items():
            country_upper = country_name.upper()
            # Direkt ülke ismiyle karşılaştır
            if gpe_upper == country_upper:
                found_country = country_name
                break
            # Alias listesinde kontrol et
            for alias in aliases:
                if gpe_upper == alias.upper():
                    found_country = country_name
                    break
            if found_country:
                break
        if found_country:
            break
    
    # Eğer GPE'lerde bulunamazsa, tüm metinde ülke ara (ilk 1000 karakter)
    if not found_country:
        search_text = text[:1000].upper()
        words = search_text.split()
        for word in words:
            word_clean = ''.join(c for c in word if c.isalnum())
            if len(word_clean) >= 2:
                for country_name, aliases in countries_dict.items():
                    country_upper = country_name.upper()
                    if word_clean == country_upper:
                        found_country = country_name
                        break
                    for alias in aliases:
                        if word_clean == alias.upper():
                            found_country = country_name
                            break
                    if found_country:
                        break
                if found_country:
                    break
    
    # 5. Sonuçları döndür
    return {
        "name": entities["PERSON"][0] if entities["PERSON"] else None,
        "locations": list(set(entities["GPE"])),  # Unique şehirler/ülkeler
        "country": found_country,
        "organizations": list(set(entities["ORG"])),
        "dates": list(set(entities["DATE"])),
        "emails": entities["EMAIL"],
        "all_entities": [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            for ent in doc.ents
        ]
    }


if __name__ == "__main__":
    # Test için PDF veya DOCX dosya yolu
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        # Varsayılan test dosyası
        test_file = "/Users/betulguner/Documents/CV/Betül Güner.pdf"
    
    if not Path(test_file).exists():
        print(f"Error: Dosya bulunamadı: {test_file}")
        sys.exit(1)
    
    print("="*60)
    print("AI EXTRACTION (spaCy NER)")
    print("="*60)
    print(f"Processing: {test_file}")
    print()
    
    result = extract_with_ai(test_file)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print("EXTRACTION RESULTS:")
    print("="*60)
    #print(f"Name: {result.get('name')}")
    print(f"Country: {result.get('country')}")
    #print(f"Locations (GPE): {result.get('locations')}")
    #print(f"Organizations: {result.get('organizations')}")
    #print(f"Dates: {result.get('dates')}")
    #print(f"Emails: {result.get('emails')}")
    
    """
    print(f"\nAll Entities (first 30):")
    print("-"*60)
    for ent in result.get('all_entities', []):
        print(f"  {ent['text']:30s} -> {ent['label']}")
    """