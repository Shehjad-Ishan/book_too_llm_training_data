import os
from pathlib import Path
import ebooklib
from ebooklib import epub
from PIL import Image
import io
from tqdm import tqdm
from bs4 import BeautifulSoup

class EPUBImageConverter:
    def __init__(self, input_folder: str, output_folder: str):
        """
        Initialize the EPUB to Image converter
        
        Args:
            input_folder (str): Path to input folder containing EPUBs
            output_folder (str): Path to output folder for images
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        
        # Create output folder if it doesn't exist
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def find_epubs(self) -> list[Path]:
        """Find all EPUB files in the input folder recursively"""
        return list(self.input_folder.rglob("*.epub"))
    
    def extract_images_from_item(self, item, epub_book, output_folder: Path):
        """Extract images from an EPUB item"""
        try:
            if isinstance(item.content, (bytes, bytearray)):
                if item.media_type.startswith('image/'):
                    # Handle direct image files
                    img_data = item.content
                    img_extension = item.media_type.split('/')[-1]
                    
                    # Skip SVG files as we're not handling them
                    if img_extension.lower() == 'svg':
                        return
                    
                    # Make sure extension is valid
                    if img_extension.lower() not in ['jpeg', 'jpg', 'png', 'gif']:
                        img_extension = 'jpg'  # default to jpg if unknown
                    
                    output_path = output_folder / f"{item.id}.{img_extension}"
                    
                    # Try to save using PIL to ensure image data is valid
                    try:
                        img = Image.open(io.BytesIO(img_data))
                        img.save(output_path)
                    except Exception as e:
                        print(f"Failed to save image {item.id}: {str(e)}")
                
                elif item.media_type == 'application/xhtml+xml':
                    # Parse HTML content for embedded images
                    soup = BeautifulSoup(item.content, 'html.parser')
                    images = soup.find_all('img')
                    
                    for img in images:
                        src = img.get('src')
                        if src:
                            # Handle both absolute and relative paths
                            if src.startswith('http'):
                                continue  # Skip external images
                                
                            # Remove any leading '../' or './'
                            src = src.lstrip('./')
                            src = src.lstrip('../')
                            
                            # Find the image in the EPUB
                            for image_item in epub_book.get_items_of_type(ebooklib.ITEM_IMAGE):
                                if src in image_item.file_name:
                                    # Skip SVG files
                                    if image_item.media_type == 'image/svg+xml':
                                        continue
                                        
                                    img_data = image_item.content
                                    img_extension = image_item.media_type.split('/')[-1]
                                    
                                    # Make sure extension is valid
                                    if img_extension.lower() not in ['jpeg', 'jpg', 'png', 'gif']:
                                        img_extension = 'jpg'  # default to jpg if unknown
                                        
                                    output_path = output_folder / f"{image_item.id}.{img_extension}"
                                    
                                    try:
                                        img = Image.open(io.BytesIO(img_data))
                                        img.save(output_path)
                                    except Exception as e:
                                        print(f"Failed to save image {image_item.id}: {str(e)}")
                                    
        except Exception as e:
            print(f"Error processing item: {str(e)}")
    
    def process_epub(self, epub_path: Path):
        """Process a single EPUB file and extract all images"""
        try:
            # Create a subfolder for this EPUB
            epub_output_folder = self.output_folder / epub_path.stem
            epub_output_folder.mkdir(exist_ok=True)
            
            # Read the EPUB
            book = epub.read_epub(str(epub_path))
            
            # Process each item in the EPUB
            for item in tqdm(book.get_items(), 
                           desc=f"Processing {epub_path.name}",
                           unit="items"):
                self.extract_images_from_item(item, book, epub_output_folder)
            
            return True
            
        except Exception as e:
            print(f"Error processing {epub_path}: {str(e)}")
            return False
    
    def process_all_epubs(self):
        """Process all EPUB files in the input folder"""
        epub_files = self.find_epubs()
        print(f"Found {len(epub_files)} EPUB files to process")
        
        successful = 0
        failed = 0
        
        for epub_path in epub_files:
            if self.process_epub(epub_path):
                successful += 1
            else:
                failed += 1
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {successful} EPUBs")
        print(f"Failed to process: {failed} EPUBs")

def main():
    # Configure input and output folders
    input_folder = "c:\\Users\\shehj\\Downloads\\Jung_Carl_Gustav"  # Change this to your input folder path
    output_folder = "book_images"  # Change this to your desired output folder
    
    # Create and run the converter
    converter = EPUBImageConverter(input_folder, output_folder)
    converter.process_all_epubs()

if __name__ == "__main__":
    main()
