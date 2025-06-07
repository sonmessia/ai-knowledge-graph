from docling.document_converter import DocumentConverter
import logging
import os


class PDFExtractor:
    def __init__(self):
        self.converter = DocumentConverter()

    def extract_pdf_to_text(self, pdf_path, output_path=None):
        """
        Extract content from PDF to Text with improved table handling.

        Args:
            pdf_path (str): Path to the PDF file
            output_path (str): Path to save the text output

        Returns:
            str: The extracted text content
        """
        logging.info(f"Extracting PDF to Text: {pdf_path}")

        try:
            # Set default output path if none provided
            if output_path is None:
                # Default to project's data directory
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                data_dir = os.path.join(base_dir, "data")
                # Create the data directory if it doesn't exist
                os.makedirs(data_dir, exist_ok=True)
                # Use the PDF filename for the output text file
                pdf_filename = os.path.basename(pdf_path)
                txt_filename = os.path.splitext(pdf_filename)[0] + ".txt"
                output_path = os.path.join(data_dir, txt_filename)
            
            # Original docling extraction
            result = self.converter.convert(pdf_path)
            markdown_content = result.document.export_to_text()
            
            # Make sure parent directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write the final content to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logging.info(f"PDF extraction completed: {output_path}")
            return markdown_content

        except Exception as e:
            logging.error(f"Error extracting PDF: {str(e)}")
            raise
def main():
    """Demonstrate the extraction pipeline."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create an instance of PDFExtractor
    pdf_extractor = PDFExtractor()

    # Define input/output paths
    pdf_path = "/home/hoangsonsdk/ai-knowledge-graph/Curriculum_for_the_Information_Technology.pdf"
    pdf_extractor.extract_pdf_to_text(pdf_path)

if __name__ == "__main__":
    main()
