import easyocr
from pathlib import Path
import os
from datetime import datetime
import logging
from tqdm import tqdm

def setup_logging():
    """Setup logging configuration"""
    log_file = f"ocr_processing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def create_output_path(input_path: Path, input_root: Path, output_root: Path) -> Path:
    """Create corresponding output path maintaining folder structure"""
    relative_path = input_path.relative_to(input_root)
    output_path = output_root / relative_path.with_suffix('.txt')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path

def process_image(reader, image_path: Path, output_path: Path):
    """Process single image and save OCR results"""
    try:
        logging.info(f"Processing: {image_path}")
        result = reader.readtext(str(image_path), detail=0)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write metadata header
            f.write(f"Source Image: {image_path.name}\n")
            f.write(f"Processing Date (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Processed by: {os.getlogin()}\n")
            f.write("-" * 50 + "\n\n")
            
            # Write OCR results
            for text in result:
                f.write(text + '\n')
        
        logging.info(f"Saved: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error processing {image_path}: {str(e)}")
        return False

def main():
    # Setup logging
    setup_logging()
    
    # Initialize EasyOCR
    logging.info("Initializing EasyOCR...")
    reader = easyocr.Reader(['ch_sim', 'en'])
    
    # Define input and output root directories
    input_root = Path(r"c:\Users\shehj\Downloads\output_text_jung\book_images")
    output_root = Path(r"c:\Users\shehj\Downloads\output_text_jung\text_output")
    
    # Create output root directory
    output_root.mkdir(parents=True, exist_ok=True)
    
    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    
    # Find all images first
    image_list = list(input_root.rglob('*'))
    image_list = [img for img in image_list if img.suffix.lower() in image_extensions]
    
    # Counter for processed files
    successful = 0
    failed = 0
    
    # Process all images with progress bar
    for image_path in tqdm(image_list, desc="Processing Images", unit="image"):
        # Create corresponding output path
        output_path = create_output_path(image_path, input_root, output_root)
        
        # Process the image
        if process_image(reader, image_path, output_path):
            successful += 1
        else:
            failed += 1
    
    # Log summary
    logging.info(f"\nProcessing Complete!")
    logging.info(f"Successfully processed: {successful} files")
    logging.info(f"Failed to process: {failed} files")
    logging.info(f"Output directory: {output_root}")

if __name__ == "__main__":
    main()