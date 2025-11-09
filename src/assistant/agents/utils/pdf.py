import math
import os

import click
from PyPDF2 import PdfReader, PdfWriter


def split_pdf_by_count(input_path, num_splits, output_directory):
    """
    Split a PDF file into a specified number of approximately equal parts.

    Parameters:
    - input_path (str): Path to the input PDF file
    - num_splits (int): Number of files to split the PDF into
    - output_directory (str): Directory to save the split PDF files

    Returns:
    - list: List of paths to the created PDF files
    """
    # Validate input
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get base filename without extension
    base_filename, _ = os.path.splitext(os.path.basename(input_path))

    # Open the PDF file
    pdf = PdfReader(input_path)
    total_pages = len(pdf.pages)

    # Calculate pages per split (may not be equal for all splits)
    pages_per_split = math.ceil(total_pages / num_splits)

    output_files = []

    for i in range(num_splits):
        output = PdfWriter()

        # Calculate start and end page for this split
        start_page = i * pages_per_split
        end_page = min((i + 1) * pages_per_split, total_pages)

        # If this split would be empty, break the loop
        if start_page >= total_pages:
            break

        # Add pages to the output
        for page_num in range(start_page, end_page):
            output.add_page(pdf.pages[page_num])

        # Generate output filename
        output_filename = f"{base_filename}_part_{i + 1}.pdf"
        output_path = os.path.join(output_directory, output_filename)

        # Write the split PDF to file
        with open(output_path, "wb") as output_file:
            output.write(output_file)

        output_files.append(output_path)

        click.echo(f"Created: {output_path} (Pages {start_page + 1}-{end_page})")

    return output_files


@click.command()
@click.option("--input-pdf", required=True, help="Path to the input PDF file")
@click.option(
    "--num-splits",
    required=True,
    type=int,
    help="Number of files to split the PDF into",
)
@click.option(
    "--output-folder", required=True, help="Directory to save the split PDF files"
)
def split_pdf_cli(input_pdf, num_splits, output_folder):
    """Split a PDF file into a specified number of parts."""
    if num_splits <= 0:
        click.echo("Error: Number of splits must be greater than 0")
        return

    try:
        output_files = split_pdf_by_count(input_pdf, num_splits, output_folder)
        click.echo(f"Successfully split PDF into {len(output_files)} parts")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


if __name__ == "__main__":
    split_pdf_cli()
