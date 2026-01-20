import re
from typing import Optional
import unicodedata
import string

def clean_text(raw_text: str) -> str:

    if not raw_text: # if the text is empty, return an empty string
        return ""
    
    text = unicodedata.normalize('NFKD', raw_text) # normalize the text
    text = re.sub(r'\n{3,}', '\n\n', text) # replace multiple newlines (3+) with double newline
    text = re.sub(r'[ \t]+', ' ', text) # replace multiple spaces/tabs with a single space (but keep newlines)
    text = re.sub(r' +\n', '\n', text) # remove spaces before newlines
    text = re.sub(r'\n +', '\n', text) # remove spaces after newlines
    text = text.strip() # remove leading and trailing whitespace

    return text


def remove_special_characters(text: str, keep_newlines: bool = True) -> str:
    if not text:
        return ""
    
    # Kontrol karakterlerini temizle (non-printable characters)
    # \x00-\x08: kontrol karakterleri (0-8)
    # \x0b-\x0c: vertical tab ve form feed (11-12)
    # \x0e-\x1f: diğer kontrol karakterleri (14-31)
    # \x7f: DEL karakteri
    # Tab (\x09) ve newline (\x0a) korunur (eğer keep_newlines True ise)
    if keep_newlines:
        # Satır sonlarını koru, sadece kontrol karakterlerini temizle
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    else:
        # Satır sonlarını da temizle
        text = re.sub(r'[\x00-\x1f\x7f]', '', text)
    
    # Carriage return (\r) karakterini temizle (Windows satır sonları için)
    text = re.sub(r'\r', '', text)
    
    return text.strip()


def normalize_punctuation_for_skills(text: str) -> str:
    if not text:
        return ""
    
    # Özel karakterleri koru (C++, C#, Pro/Engineer, GD&T)
    # Önce özel durumları handle et
    text = text.replace('C++', 'C_PLUS_PLUS_TEMP')
    text = text.replace('C#', 'C_SHARP_TEMP')
    text = text.replace('Pro/Engineer', 'Pro_SLASH_Engineer_TEMP')
    text = text.replace('GD&T', 'GD_AMPERSAND_T_TEMP')
    
    # Noktalama işaretlerini boşlukla değiştir
    # Ancak "/" ve "&" karakterlerini koru (bazı skill'lerde kullanılıyor)
    punctuation_to_replace = string.punctuation.replace('/', '').replace('&', '')
    text = text.translate(str.maketrans(punctuation_to_replace, ' ' * len(punctuation_to_replace)))
    
    # Özel durumları geri getir (slash ve ampersand'ı koru)
    text = text.replace('C_PLUS_PLUS_TEMP', 'C++')
    text = text.replace('C_SHARP_TEMP', 'C#')
    text = text.replace('Pro_SLASH_Engineer_TEMP', 'Pro/Engineer')
    text = text.replace('GD_AMPERSAND_T_TEMP', 'GD&T')
    
    # Çoklu boşlukları tek boşluğa çevir
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


if __name__ == "__main__":
    test_text = "  Python    Developer  \n\n\n  React  "
    cleaned_text = clean_text(test_text)

    print(f"Orijinal: {repr(test_text)}")
    print(f"Temizlenmiş: {repr(cleaned_text)}")
    print(f"Görsel: {cleaned_text}")
    
    print("\n" + "=" * 50)
    # remove_special_characters testi
    test_special = "Python\x00\x01Developer\nReact@email.com +90-555-123-4567"
    cleaned_special = remove_special_characters(test_special, keep_newlines=True)
    print("remove_special_characters TESTİ (keep_newlines=True):")
    print(f"Orijinal: {repr(test_special)}")
    print(f"Temizlenmiş: {repr(cleaned_special)}")
    print(f"Görsel: {cleaned_special}")
    
    print("\n" + "=" * 50)
    cleaned_special_no_nl = remove_special_characters(test_special, keep_newlines=False)
    print("remove_special_characters TESTİ (keep_newlines=False):")
    print(f"Orijinal: {repr(test_special)}")
    print(f"Temizlenmiş: {repr(cleaned_special_no_nl)}")
    print(f"Görsel: {cleaned_special_no_nl}")
