from typing import Dict, List, Optional
import re
import json
import unicodedata
from pathlib import Path

# spaCy NER için (opsiyonel - yoksa fallback kullanılır)
try:
    import spacy
    try:
        nlp_spacy = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        nlp_spacy = None
        SPACY_AVAILABLE = False
except ImportError:
    nlp_spacy = None
    SPACY_AVAILABLE = False

# spaCy NER için (opsiyonel - yoksa fallback kullanılır)
try:
    import spacy
    try:
        nlp_spacy = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        nlp_spacy = None
        SPACY_AVAILABLE = False
except ImportError:
    nlp_spacy = None
    SPACY_AVAILABLE = False

def extract_name(text:str) -> Optional[str]:
    lines = text.split('\n')[:15]  # İlk 15 satıra genişlet

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Email, telefon, link içeren satırları atla
        if '@' in line or re.search(r'\d{3}', line) or 'http' in line.lower():
            continue
        
        # Başlık satırlarını atla (tamamen büyük harf ve kısa)
        if line.isupper() and len(line) < 20:
            continue

        words = line.split()
        # 2-4 kelimeli satırları kontrol et
        if 2 <= len(words) <= 4:
            # Her kelime büyük harfle başlıyor mu?
            if all(word and word[0].isupper() for word in words):
                # Çok uzun değilse (60 karakterden az)
                if len(line) < 60:
                    return line
        
        # İsim satırın içinde olabilir (örn: "Betül Güner kodlayıp...")
        # İlk 2 kelimeyi kontrol et
        if len(words) >= 2:
            first_two = ' '.join(words[:2])
            # İlk iki kelime büyük harfle başlıyor ve mantıklı uzunluktaysa
            if all(word and word[0].isupper() for word in words[:2]):
                if 5 <= len(first_two) <= 30:
                    return first_two
    
    return None

def extract_name_from_email(email:str) ->Optional[str]:
    if not email:
        return None

    local_part = email.split('@')[0]
    name_part = re.sub(r'\d+', '', local_part)

    if name_part and 3 <= len(name_part) <= 20:
        return name_part.capitalize()
    
    return None

def load_countries() -> Dict[str, List[str]]:
    """Ülke listesini JSON'dan yükle"""
    countries_file = Path(__file__).parent.parent.parent / "data" / "countries.json"
    if countries_file.exists():
        with open(countries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("countries", {})
    return {}

def find_country_in_text(text: str, countries_dict: Dict[str, List[str]]) -> Optional[str]:
    """
    Metinde ülke ismini bulur.
    text: "/" sonrası kısım (örn: "TÜRKİYE GOOGLE...")
    countries_dict: Ülke listesi dictionary'si
    
    Returns: Ülke ismi (örn: "TÜRKİYE") veya None
    """
    if not text or not countries_dict:
        return None
    
    text_upper = text.upper().strip()
    words = text_upper.split()
    
    # İlk kelimeyi öncelikli kontrol et (çoğu durumda ülke ilk kelimedir)
    if words:
        first_word = words[0]
        # Tüm ülkeleri kontrol et
        for country_name, aliases in countries_dict.items():
            country_upper = country_name.upper()
            # Direkt ülke ismiyle karşılaştır
            if first_word == country_upper:
                return country_name
            # Alias listesinde kontrol et
            for alias in aliases:
                if first_word == alias.upper():
                    return country_name
    
    # Eğer ilk kelime eşleşmezse, tam eşleşme kontrolü (ilk 1-3 kelime kombinasyonları)
    for i in range(1, min(4, len(words) + 1)):
        phrase = ' '.join(words[:i])
        phrase_upper = phrase.upper()
        # Tüm ülkeleri kontrol et
        for country_name, aliases in countries_dict.items():
            country_upper = country_name.upper()
            # Direkt ülke ismiyle karşılaştır
            if phrase_upper == country_upper:
                return country_name
            # Alias listesinde kontrol et
            for alias in aliases:
                if phrase_upper == alias.upper():
                    return country_name
    
    # Son olarak tüm kelimeleri kontrol et
    for word in words:
        # Kelime çok kısa değilse (en az 2 karakter)
        if len(word) >= 2:
            word_upper = word.upper()
            # Tüm ülkeleri kontrol et
            for country_name, aliases in countries_dict.items():
                country_upper = country_name.upper()
                # Direkt ülke ismiyle karşılaştır
                if word_upper == country_upper:
                    return country_name
                # Alias listesinde kontrol et
                for alias in aliases:
                    if word_upper == alias.upper():
                        return country_name
    
    return None

def find_country_with_spacy(text: str, countries_dict: Dict[str, List[str]]) -> Optional[str]:
    """
    spaCy NER kullanarak ülke bulur.
    Sadece ülke bulma için kullanılır.
    ai_extractor.py'deki mantıkla aynı.
    """
    found_country = None
    
    # Önce spaCy ile dene (eğer yüklüyse)
    if SPACY_AVAILABLE and nlp_spacy:
        try:
            # İlk 2000 karakteri işle (performans için)
            text_sample = text[:2000]
            doc = nlp_spacy(text_sample)
            
            # GPE (Geopolitical Entity) entity'lerini bul
            gpe_entities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
            
            # GPE'leri countries.json ile eşleştir
            for gpe in gpe_entities:
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
        except Exception:
            # spaCy hata verirse devam et (fallback kullanılacak)
            pass
    
    # Eğer spaCy ile bulunamazsa veya spaCy yüklü değilse, fallback yöntemi kullan
    if not found_country:
        search_text = text[:1000]
        # Önce "/" içeren satırları kontrol et (ülke genelde orada)
        if '/' in search_text:
            # "/" sonrası kısmı al
            slash_idx = search_text.find('/')
            after_slash = search_text[slash_idx + 1:].strip()
            # İlk kelimeyi al (ülke genelde ilk kelime)
            first_word_after_slash = after_slash.split()[0] if after_slash.split() else ""
            
            # countries.json ile eşleştir (hem tam kelime hem de substring)
            # Unicode normalize et (özel karakterleri düzelt)
            first_word_normalized = unicodedata.normalize('NFKD', first_word_after_slash.upper())
            first_word_clean = ''.join(c for c in first_word_normalized if not unicodedata.combining(c))
            
            for country_name, aliases in countries_dict.items():
                country_upper = country_name.upper()
                country_normalized = unicodedata.normalize('NFKD', country_upper)
                country_clean = ''.join(c for c in country_normalized if not unicodedata.combining(c))
                
                # Tam kelime eşleşmesi (normalize edilmiş)
                if first_word_clean == country_clean:
                    found_country = country_name
                    break
                # Substring eşleşmesi
                if country_clean in first_word_clean or first_word_clean in country_clean:
                    found_country = country_name
                    break
                # Alias kontrolü
                for alias in aliases:
                    alias_upper = alias.upper()
                    alias_normalized = unicodedata.normalize('NFKD', alias_upper)
                    alias_clean = ''.join(c for c in alias_normalized if not unicodedata.combining(c))
                    if first_word_clean == alias_clean or alias_clean in first_word_clean or first_word_clean in alias_clean:
                        found_country = country_name
                        break
                if found_country:
                    break
        
        # Eğer hala bulunamazsa, kelime kelime ara
        if not found_country:
            search_text_upper = text[:1000].upper()
            words = search_text_upper.split()
            for word in words:
                # Özel karakterleri temizle ama Türkçe karakterleri koru
                word_clean = word.strip('.,;:!?()[]{}')
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
    
    return found_country

def extract_location(text:str) -> Optional[str]:
    """
    CV'den konum bilgisini çıkarır.
    Sadece şehir ve region bilgisini döndürür (ülke bilgisi ayrı field olarak tutulur).
    """
    lines = text.split('\n')
    
    # Şehir ve region'ı bul ("/" içeren satırlarda)
    city = None
    region = None
    
    # Email veya telefon içeren satırı bul 
    contact_line_idx = None
    for i, line in enumerate(lines):
        if '@' in line or re.search(r'\+?\d', line):
            contact_line_idx = i 
            break

    # Önce email/telefon satırının yakınına bak (öncelikli)
    if contact_line_idx is not None:
        start_idx = max(0, contact_line_idx - 1)
        end_idx = min(len(lines), contact_line_idx + 3)
        
        # Yakındaki satırları kontrol et - "/" içeren formatları ara
        for i in range(start_idx, end_idx):
            line = lines[i].strip()
            
            # "/" içeren formatları kontrol et
            if '/' in line:
                # "/" karakterini bul
                slash_idx = line.find('/')
                if slash_idx > 0:
                    # "/" öncesi kısmı al (City, Region)
                    before_slash = line[:slash_idx].strip()
                    
                    # City ve Region'ı parse et
                    # Önce basit pattern: "CITY,REGION" (virgül sonrası boşluk olmadan)
                    simple_pattern = r'([A-ZÇĞİÖŞÜ]{2,})[,\s]+([A-ZÇĞİÖŞÜ]{2,})'
                    city_region_match = re.search(simple_pattern, before_slash)
                    
                    # Eğer basit pattern eşleşmezse, daha karmaşık pattern'i dene
                    if not city_region_match:
                        city_region_pattern = r'([A-ZÇĞİÖŞÜ]{2,}(?:\s+[A-ZÇĞİÖŞÜ]{2,})*)[,\s]+([A-ZÇĞİÖŞÜ]{2,}(?:\s+[A-ZÇĞİÖŞÜ]{2,})*)'
                        city_region_match = re.search(city_region_pattern, before_slash)
                    
                    if city_region_match:
                        city = city_region_match.group(1).strip()
                        region = city_region_match.group(2).strip()
                        break

    # Bulunamazsa tüm metinde "/" içeren formatları ara
    if not city or not region:
        for line in lines:
            line = line.strip()
            if '/' in line:
                slash_idx = line.find('/')
                if slash_idx > 0:
                    before_slash = line[:slash_idx].strip()
                    
                    simple_pattern = r'([A-ZÇĞİÖŞÜ]{2,})[,\s]+([A-ZÇĞİÖŞÜ]{2,})'
                    city_region_match = re.search(simple_pattern, before_slash)
                    
                    if not city_region_match:
                        city_region_pattern = r'([A-ZÇĞİÖŞÜ]{2,}(?:\s+[A-ZÇĞİÖŞÜ]{2,})*)[,\s]+([A-ZÇĞİÖŞÜ]{2,}(?:\s+[A-ZÇĞİÖŞÜ]{2,})*)'
                        city_region_match = re.search(city_region_pattern, before_slash)
                    
                    if city_region_match:
                        city = city_region_match.group(1).strip()
                        region = city_region_match.group(2).strip()
                        break
    
    # Sonucu birleştir (ülke bilgisi location'a eklenmez, ayrı field olarak tutulur)
    if city and region:
        return f"{city}, {region}"
    
    return None

def extract_personal_info(text:str) -> Dict:
    """
    CV metninden kişisel bilgileri çıkarır.
    
    Returns:
        Dict: {
            "name": str veya None,
            "email": str veya None,
            "phone": str veya None,
            "location": str veya None,
            "links": {
                "github": str veya None,
                "linkedin": str veya None,
                "website": str veya None
            }
        }
    """
    result = {
        "name": None,
        "email": None,
        "phone": None,
        "location": None,
        "links": {
            "github": None,
            "linkedin": None,
            "website": None
        }
    }
    
    # Önce email'i extract et (name extraction'da kullanılacak)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        result["email"] = email_match.group()
    
    # İsim extraction (email'den sonra, çünkü email'den isim çıkarabiliriz)
    name = extract_name(text)
    if not name and result["email"]:
        name = extract_name_from_email(result["email"])
    result["name"] = name

    result["location"] = extract_location(text)

    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}'
    phone_match = re.search(phone_pattern,text)
    if phone_match:
        result["phone"] = phone_match.group()

    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/([\w-]+)'
    github_match = re.search(github_pattern,text)
    if github_match:
        result["links"]["github"] = github_match.group(1)

    # LinkedIn: Link iki satıra bölünmüş olabilir (arada başlık olabilir)
    # Pattern: Türkçe karakterleri de desteklemeli
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-çğıöşü]+(?:-[\w\-çğıöşü]+)*'
    
    # Önce normal pattern'i dene (tam URL)
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        result["links"]["linkedin"] = linkedin_match.group()
    else:
        # Eğer bulunamazsa, satırları birleştirip tekrar dene (bölünmüş link için)
        lines = text.split('\n')
        for i in range(len(lines) - 2):  # -2 çünkü 2 satır sonrasına bakacağız
            current_line = lines[i].strip()
            # Eğer mevcut satır linkedin.com içeriyor ve "-" ile bitiyorsa
            if 'linkedin.com/in/' in current_line.lower() and current_line.endswith('-'):
                # Sonraki 2 satırı kontrol et (arada başlık olabilir)
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    # Başlık satırlarını atla (tamamen büyük harf ve kısa)
                    if next_line.isupper() and len(next_line) < 20:
                        continue
                    # Eğer sonraki satır harf/sayı/tire içeriyorsa ve çok uzun değilse (link devamı)
                    if next_line and len(next_line) < 50 and re.match(r'^[\w\-çğıöşü]+', next_line):
                        # Satırları birleştir (boşluk olmadan)
                        combined = current_line + next_line
                        linkedin_match = re.search(linkedin_pattern, combined, re.IGNORECASE)
                        if linkedin_match:
                            result["links"]["linkedin"] = linkedin_match.group()
                            break
                if result["links"]["linkedin"]:
                    break

    # Website: GitHub ve LinkedIn hariç, gerçek website URL'leri
    # Önce GitHub ve LinkedIn'i exclude et
    text_without_social = re.sub(r'(?:https?://)?(?:www\.)?(github|linkedin)\.com/[^\s]+', '', text, flags=re.IGNORECASE)
    
    # Website pattern: http/https ile başlayan, github/linkedin olmayan URL'ler
    website_pattern = r'https?://(?!www\.(?:github|linkedin)\.com)[^\s/$.?#]+\.[a-z]{2,}[^\s]*'
    website_match = re.search(website_pattern, text_without_social, re.IGNORECASE)
    if website_match:
        result["links"]["website"] = website_match.group()
    return result


if __name__ == "__main__":
    # Test için CV dosyasını oku
    from pathlib import Path
    cv_file = Path("data/test_outputs/Betül Güner_cleaned.txt")
    #cv_file = Path("data/test_outputs/77828437_cleaned.txt")
    
    if cv_file.exists():
        with open(cv_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        result = extract_personal_info(text)
        
        # Ülkeyi ayrı bul (location'dan bağımsız) - find_country_with_spacy içindeki fallback mantığıyla
        countries_dict = load_countries()
        found_country = find_country_with_spacy(text, countries_dict)
        
        print("Extracted Info:")
        print(f"Name: {result['name']}")
        print(f"Email: {result['email']}")
        print(f"Phone: {result['phone']}")
        print(f"Location: {result['location']}")
        print(f"Country: {found_country if found_country else 'Not found'}")
        print(f"Links: {result['links']}")