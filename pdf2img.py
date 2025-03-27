import os
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io
from tqdm import tqdm

class PDFImageConverter:
    def __init__(self, input_folder: str, output_folder: str, dpi: int = 300):
        """
        Initialize the PDF to Image converter
        
        Args:
            input_folder (str): Path to input folder containing PDFs
            output_folder (str): Path to output folder for images
            dpi (int): Resolution of output images (default: 300)
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.dpi = dpi
        
        # Create output folder if it doesn't exist
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def find_pdfs(self) -> list[Path]:
        """Find all PDF files in the input folder recursively"""
        return list(self.input_folder.rglob("*.pdf"))
    
    def convert_page_to_image(self, page, dpi: int = 300) -> Image.Image:
        """Convert a single PDF page to PIL Image"""
        # Get the pixel matrix for the page
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    
    def process_pdf(self, pdf_path: Path):
        """Process a single PDF file and save each page as an image"""
        try:
            # Create a subfolder for this PDF
            pdf_output_folder = self.output_folder / pdf_path.stem
            pdf_output_folder.mkdir(exist_ok=True)
            
            # Open the PDF
            pdf_document = fitz.open(pdf_path)
            
            # Process each page
            for page_num in tqdm(range(len(pdf_document)), 
                               desc=f"Converting {pdf_path.name}",
                               unit="pages"):
                # Get the page
                page = pdf_document[page_num]
                
                # Convert to image
                img = self.convert_page_to_image(page, self.dpi)
                
                # Save the image
                output_path = pdf_output_folder / f"page_{page_num + 1:04d}.png"
                img.save(output_path, "PNG", optimize=True)
            
            pdf_document.close()
            return True
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return False
    
    def process_all_pdfs(self):
        """Process all PDF files in the input folder"""
        pdf_files = self.find_pdfs()
        print(f"Found {len(pdf_files)} PDF files to process")
        
        successful = 0
        failed = 0
        
        for pdf_path in pdf_files:
            if self.process_pdf(pdf_path):
                successful += 1
            else:
                failed += 1
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {successful} PDFs")
        print(f"Failed to process: {failed} PDFs")

def main():
    # Configure input and output folders
    input_folder = "books"  # Change this to your input folder path
    output_folder = "book_images"  # Change this to your desired output folder
    
    # Create and run the converter
    converter = PDFImageConverter(input_folder, output_folder)
    converter.process_all_pdfs()

if __name__ == "__main__":
    main()
