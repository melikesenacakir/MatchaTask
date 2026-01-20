"""
Advanced AI-based CV Extractor using Fine-tuned Models
For LayoutLM:
   pip install transformers torch pillow pdf2image pytesseract
python app/cv/advanced_ai_extractor.py [dosya_yolu]
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional, List

# Handle import for both module and script execution
try:
    from app.cv.parser import parse_cv
    from app.cv.info_extractor import extract_personal_info
    from app.skills.extractor import extract_skills
except ImportError:
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from app.cv.parser import parse_cv
    from app.cv.info_extractor import extract_personal_info
    from app.skills.extractor import extract_skills


def extract_structured_info(text: str) -> Dict:
    """
    Text'ten structured bilgileri çıkarır.
    Mevcut extractor fonksiyonlarını kullanır.
    
    Args:
        text: CV text'i
        
    Returns:
        Dict: Structured bilgiler (isim, email, telefon, location, country, links, skills, summary)
    """
    structured = {
        "personal_info": {},
        "skills": [],
        "summary": None
    }
    
    try:
        # Personal info extraction
        personal_info = extract_personal_info(text)
        structured["personal_info"] = {
            "name": personal_info.get("name"),
            "email": personal_info.get("email"),
            "phone": personal_info.get("phone"),
            "location": personal_info.get("location"),
            "country": personal_info.get("country"),
            "links": personal_info.get("links", {})
        }
    except Exception as e:
        structured["personal_info"] = {"error": f"Extraction hatası: {str(e)}"}
    
    try:
        # Skills extraction
        skills = extract_skills(text)
        structured["skills"] = skills
    except Exception as e:
        structured["skills"] = []
        structured["skills_error"] = f"Skills extraction hatası: {str(e)}"
    
    try:
        # Summary extraction (ilk 3-5 satır veya "HAKKIMDA" bölümü)
        lines = text.split('\n')
        summary_lines = []
        found_summary = False
        
        for i, line in enumerate(lines[:50]):  # İlk 50 satırı kontrol et
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ["hakkımda", "about", "summary", "özgeçmiş", "profil"]):
                # Bu satırdan sonraki 5-10 satırı al
                for j in range(i + 1, min(i + 11, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                        if len(summary_lines) >= 5:
                            break
                found_summary = True
                break
        
        if not found_summary and lines:
            # Eğer summary bulunamazsa, ilk 3-5 satırı al
            summary_lines = [line.strip() for line in lines[:5] if line.strip()]
        
        structured["summary"] = " ".join(summary_lines) if summary_lines else None
    except Exception as e:
        structured["summary"] = None
        structured["summary_error"] = f"Summary extraction hatası: {str(e)}"
    
    return structured


def extract_with_layoutlm(file_path: str) -> Dict:
    """
    LayoutLM modeli ile CV'den bilgi çıkarır.
    
    LayoutLM, document understanding için Microsoft tarafından geliştirilmiş bir modeldir.
    PDF layout'ını anlayarak structured data çıkarır.
    
    Args:
        file_path: PDF dosya yolu
        
    Returns:
        Dict: {
            "success": bool,
            "model": "LayoutLM",
            "extracted_info": Dict,
            "error": str (varsa)
        }
    """
    result = {
        "success": False,
        "model": "LayoutLM",
        "extracted_info": {},
        "error": None
    }
    
    # Gerekli kütüphaneleri kontrol et
    try:
        from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
        from PIL import Image
        import torch
    except ImportError as e:
        result["error"] = f"Gerekli kütüphaneler yüklü değil: {e}"
        result["installation"] = "pip install transformers torch pillow"
        return result
    
    try:
        # Eğer dosya PDF ise, doğrudan text extraction yap (pdf'i image'a çevirmeye çalışma)
        if file_path.lower().endswith('.pdf'):
            text = parse_cv(file_path)
            if text:
                structured_data = extract_structured_info(text)
                result["extracted_info"] = {
                    "structured_data": structured_data,
                    "raw_text": text[:500] + "..." if len(text) > 500 else text,
                    "note": "PDF doğrudan text olarak işlendi (image dönüşümü yapılmadı)"
                }
                result["success"] = True
            else:
                result["extracted_info"] = {
                    "error": "Text extraction başarısız"
                }
                result["success"] = False
            return result
        else:
            # Zaten image dosyası
            image = Image.open(file_path)
        
        print("LayoutLM modeli yükleniyor... (ilk çalıştırmada biraz zaman alabilir)")
        
        # LayoutLMv3 modelini yükle (daha yeni ve gelişmiş versiyon)
        processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
        model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")
        
        print("Image işleniyor...")
        
        # Image'ı process et
        encoding = processor(image, return_tensors="pt", truncation=True, max_length=512)
        
        # Model'e ver ve predict et
        with torch.no_grad():
            outputs = model(**encoding)
        
        # Logits'ten predictions al
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        
        # Token'ları decode et
        input_ids = encoding["input_ids"][0]
        tokens = processor.tokenizer.convert_ids_to_tokens(input_ids)
        
        # Entity'leri extract et (basit yaklaşım)
        extracted_text = []
        for token, pred in zip(tokens, predictions[0]):
            if token not in ["[CLS]", "[SEP]", "[PAD]"]:
                extracted_text.append(token)
        
        # Text'i birleştir ve temizle
        text = " ".join(extracted_text).replace(" ##", "")
        
        # Structured extraction yap
        structured_data = extract_structured_info(text)
        
        result["extracted_info"] = {
            "structured_data": structured_data,
            "raw_text": text[:500] + "..." if len(text) > 500 else text,
            "tokens_count": len(extracted_text),
            "model_version": "layoutlmv3-base"
        }
        result["success"] = True
        
    except Exception as e:
        result["error"] = f"LayoutLM extraction hatası: {str(e)}"
        result["success"] = False
    
    return result


def compare_models(file_path: str) -> Dict:
    """
    Modelleri karşılaştırır.
    
    Args:
        file_path: PDF dosya yolu
        
    Returns:
        Dict: Her modelin sonuçlarını içeren karşılaştırma
    """
    results = {
        "file": file_path,
        "layoutlm": None,
        "comparison": {}
    }
    
    # LayoutLM sonuçları
    print("\n" + "="*60)
    print("1. LayoutLM ile extraction...")
    print("="*60)
    layoutlm_result = extract_with_layoutlm(file_path)
    results["layoutlm"] = layoutlm_result
    if layoutlm_result["success"]:
        print("✓ LayoutLM extraction tamamlandı")
    else:
        print(f"✗ LayoutLM extraction hatası: {layoutlm_result.get('error', 'Bilinmeyen hata')}")
    
    # Karşılaştırma özeti
    results["comparison"] = {
        "layoutlm_available": results["layoutlm"]["success"],
        "total_successful": sum([
            results["layoutlm"]["success"],
        ])
    }
    
    return results


def print_results(result: Dict, model_name: str = ""):
    """
    Sonuçları güzel bir formatta yazdırır.
    
    Args:
        result: Extraction sonucu
        model_name: Model adı (opsiyonel)
    """
    print("\n" + "="*60)
    if model_name:
        print(f"{model_name.upper()} EXTRACTION SONUÇLARI")
    else:
        print("EXTRACTION SONUÇLARI")
    print("="*60)
    
    if result.get("success"):
        print("✓ Status: Başarılı")
        print("\n" + "="*60)
        print("STRUCTURED INFORMATION")
        print("="*60)
        
        extracted_info = result.get("extracted_info", {})
        structured_data = extracted_info.get("structured_data", {})
        
        # Personal Info
        if isinstance(structured_data, dict):
            personal_info = structured_data.get("personal_info", {})
            if personal_info and not personal_info.get("error"):
                print("\n📋 PERSONAL INFORMATION")
                print("-"*60)
                print(f"  İsim:        {personal_info.get('name', 'Bulunamadı')}")
                print(f"  Email:       {personal_info.get('email', 'Bulunamadı')}")
                print(f"  Telefon:     {personal_info.get('phone', 'Bulunamadı')}")
                print(f"  Konum:       {personal_info.get('location', 'Bulunamadı')}")
                print(f"  Ülke:        {personal_info.get('country', 'Bulunamadı')}")
                
                links = personal_info.get("links", {})
                if links:
                    print(f"\n  🔗 Links:")
                    print(f"    GitHub:    {links.get('github', 'Bulunamadı')}")
                    print(f"    LinkedIn:  {links.get('linkedin', 'Bulunamadı')}")
                    print(f"    Website:   {links.get('website', 'Bulunamadı')}")
            elif personal_info.get("error"):
                print(f"\n⚠️  Personal Info Extraction Hatası: {personal_info.get('error')}")
            
            # Skills
            skills = structured_data.get("skills", [])
            if skills:
                print(f"\n💼 SKILLS ({len(skills)} adet)")
                print("-"*60)
                # İlk 20 skill'i göster
                skills_to_show = skills[:20]
                for i, skill in enumerate(skills_to_show, 1):
                    print(f"  {i:2d}. {skill}")
                if len(skills) > 20:
                    print(f"  ... ve {len(skills) - 20} skill daha")
            elif isinstance(structured_data, dict) and "skills" in structured_data:
                print(f"\n💼 SKILLS: Bulunamadı")
            
            # Summary
            summary = structured_data.get("summary")
            if summary:
                print(f"\n📝 SUMMARY")
                print("-"*60)
                # İlk 300 karakteri göster
                summary_display = summary[:300] + "..." if len(summary) > 300 else summary
                print(f"  {summary_display}")
            
            # Eğer structured_data yoksa, raw data göster
            if not structured_data and extracted_info.get("raw_text"):
                print("\n⚠️  Structured extraction yapılamadı, raw text gösteriliyor:")
                print("-"*60)
                raw_text = extracted_info.get("raw_text", "")
                print(f"  {raw_text[:500]}..." if len(raw_text) > 500 else raw_text)
        elif structured_data:
            # Eğer structured_data dict değilse, direkt göster
            print("\nExtracted Information:")
            print("-"*60)
            print(json.dumps(structured_data, indent=2, ensure_ascii=False))
        else:
            # Fallback: extracted_info'yu göster
            print("\nExtracted Information:")
            print("-"*60)
            print(json.dumps(extracted_info, indent=2, ensure_ascii=False))
    else:
        print("✗ Status: Başarısız")
        if result.get("error"):
            print(f"\nHata: {result['error']}")
        if result.get("installation"):
            print(f"\nKurulum: {result['installation']}")


if __name__ == "__main__":
    """
    Test için kullanım:
    python app/cv/advanced_ai_extractor.py [dosya_yolu]
    """
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        # Varsayılan test dosyası
        test_file = "/Users/betulguner/Documents/CV/Betül Güner.pdf"
    
    if not Path(test_file).exists():
        print(f"Error: Dosya bulunamadı: {test_file}")
        print("\nKullanım: python app/cv/advanced_ai_extractor.py [dosya_yolu]")
        sys.exit(1)
    
    print("="*60)
    print("ADVANCED AI EXTRACTION TEST")
    print("="*60)
    print(f"Test dosyası: {test_file}")
    print()
    
    # Sadece LayoutLM (interaktif menü yok)
    print("\n" + "="*60)
    print("LayoutLM ile extraction başlatılıyor...")
    print("="*60)
    result = extract_with_layoutlm(test_file)
    print_results(result, "LayoutLM")
    