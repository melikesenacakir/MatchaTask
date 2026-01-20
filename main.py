"""
MatchaTask AI Service - CV Parser and Skill Extractor

Usage:
    python main.py --cv-path data/raw_cvs/example.pdf
    python main.py --cv-path data/raw_cvs/example.pdf --output-dir data/results
"""

import argparse
import sys
from pathlib import Path
import json
from datetime import datetime

from app.cv.cleaner import clean_text, remove_special_characters
from app.skills.extractor import extract_skills

# Import parser only if needed (for PDF/DOCX files)
def get_parser():
    try:
        from app.cv.parser import parse_cv
        return parse_cv
    except ImportError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="MatchaTask AI Service - CV Parser and Skill Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a PDF file
  python main.py --cv-path data/raw_cvs/example.pdf
  
  # Process a text file
  python main.py --cv-path data/test_outputs/example.txt
  
  # Specify custom output directory
  python main.py --cv-path data/raw_cvs/example.pdf --output-dir data/results
        """
    )
    parser.add_argument(
        "--cv-path",
        type=str,
        required=True,
        help="Path to CV file (PDF, DOCX, or TXT)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/test_outputs",
        help="Directory to save output files (default: data/test_outputs)"
    )
    args = parser.parse_args()

    # Check if file exists
    if not Path(args.cv_path).exists():
        print(f"Error: File not found: {args.cv_path}")
        sys.exit(1)

    cv_path = Path(args.cv_path)
    
    # Step 1: Parse CV or read text file
    print("="*60)
    print("Step 1: Parsing CV...")
    print("="*60)
    
    # If it's a text file, read it directly
    if cv_path.suffix.lower() == '.txt':
        print("Detected text file, reading directly...")
        try:
            with open(cv_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            print("Text file read successfully!")
        except Exception as e:
            print(f"Error reading text file: {e}")
            sys.exit(1)
    else:
        # Parse PDF/DOCX using parser
        print(f"Detected {cv_path.suffix.upper()} file, parsing...")
        parse_cv = get_parser()
        if parse_cv is None:
            print("Error: Parser module not available.")
            print("   Please install required dependencies:")
            print("   pip install PyPDF2 pdfplumber python-docx")
            sys.exit(1)
        
        try:
            raw_text = parse_cv(str(cv_path))
            if not raw_text:
                print("Error: CV could not be parsed!")
                sys.exit(1)
            print("CV parsed successfully!")
        except Exception as e:
            print(f"Error parsing CV: {e}")
            sys.exit(1)
    
    # Step 2: Clean text
    print("\n" + "="*60)
    print("Step 2: Cleaning text...")
    print("="*60)
    try:
        cleaned_text = clean_text(raw_text)
        if not cleaned_text:
            print("Error: Text could not be cleaned!")
            sys.exit(1)
        print("Text cleaned successfully!")
    except Exception as e:
        print(f"Error cleaning text: {e}")
        sys.exit(1)
    
    # Step 3: Remove special characters
    print("\n" + "="*60)
    print("Step 3: Removing special characters...")
    print("="*60)
    try:
        cleaned_special = remove_special_characters(cleaned_text, keep_newlines=True)
        if not cleaned_special:
            print("Error: Special characters could not be removed!")
            sys.exit(1)
        print("Special characters removed successfully!")
    except Exception as e:
        print(f"Error removing special characters: {e}")
        sys.exit(1)
    
    # Step 4: Extract skills
    print("\n" + "="*60)
    print("Step 4: Extracting skills...")
    print("="*60)
    try:
        skills = extract_skills(cleaned_special)
        print(f"Skills extracted successfully! Found {len(skills)} skills.")
    except Exception as e:
        print(f"Error extracting skills: {e}")
        sys.exit(1)
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    word_count = len(cleaned_special.split())
    print(f"Document has {word_count} words")
    print(f"Found {len(skills)} skills")
    
    if skills:
        print(f"\nExtracted Skills ({len(skills)}):")
        for i, skill in enumerate(skills, 1):
            print(f"  {i}. {skill}")
    else:
        print("\nNo skills found.")
    
    # Save outputs
    print("\n" + "="*60)
    print("SAVING OUTPUTS")
    print("="*60)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save cleaned text
    cleaned_file = output_path / f"{cv_path.stem}_cleaned.txt"
    try:
        cleaned_file.write_text(cleaned_special, encoding='utf-8')
        print(f"Cleaned text saved to: {cleaned_file}")
    except Exception as e:
        print(f"Error saving cleaned text: {e}")
    
    # Save skills as JSON
    skills_file = output_path / f"{cv_path.stem}_skills.json"
    try:
        skills_data = {
            "cv_file": str(args.cv_path),
            "extracted_at": datetime.now().isoformat(),
            "total_skills": len(skills),
            "word_count": word_count,
            "skills": skills
        }
        with open(skills_file, 'w', encoding='utf-8') as f:
            json.dump(skills_data, f, indent=2, ensure_ascii=False)
        print(f"Skills saved to: {skills_file}")
    except Exception as e:
        print(f"Error saving skills: {e}")
    
    print("\n" + "="*60)
    print("Pipeline completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
