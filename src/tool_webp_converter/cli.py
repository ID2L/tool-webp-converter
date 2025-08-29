import click
import logging
from pathlib import Path
from .convert import compress_image_to_webp

# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}


def process_directory(input_dir: Path, output_dir: Path | None, quality: int, recursive: bool = False):
    """
    Process all image files in a directory.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        quality: Quality for lossy compression
        recursive: Whether to process subdirectories recursively
    """
    processed_count = 0
    error_count = 0
    
    image_files = []
    # Get all image files in the directory
    if recursive:
        for ext in SUPPORTED_FORMATS:
            image_files.extend(input_dir.rglob(f"*{ext}"))
    else:
        for ext in SUPPORTED_FORMATS:
            image_files.extend(input_dir.glob(f"*{ext}"))
    
    if not image_files:
        logging.warning(f"No supported image files found in {input_dir}")
        return processed_count, error_count
    
    logging.info(f"Found {len(image_files)} image files to process")
    logging.debug(f"image_files: {image_files}")
    
    if output_dir is None:
        root_output_dir = input_dir
    else:
        root_output_dir = output_dir


    for image_file in image_files:
        try:
            # Maintain directory structure relative to input_dir
            if recursive:
                relative_path = image_file.relative_to(input_dir)
                file_output_dir = root_output_dir / relative_path.parent
            else:
                file_output_dir = root_output_dir
            
            # Create output directory if it doesn't exist
            file_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Skip if output file already exists
            output_file = file_output_dir / f"{image_file.stem}.webp"
            if output_file.exists():
                logging.info(f"Skipping {image_file.name} (output already exists)")
                continue
            
            # Process the image
            compress_image_to_webp(
                input_path=image_file,
                output_dir=file_output_dir,
                quality=quality
            )
            processed_count += 1
            
        except Exception as e:
            logging.error(f"Error processing {image_file}: {e}")
            error_count += 1
    
    return processed_count, error_count


@click.command()
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='Output directory (defaults to input file directory)')
@click.option('--quality', '-q', type=click.IntRange(1, 100), default=80,
              help='Quality for lossy compression (1-100, default: 80)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--recursive', '-r', is_flag=True, help='Process directories recursively')
def main(input_path: Path, output_dir: Path, quality: int, verbose: bool, recursive: bool):
    """
    Compress an image to WebP format using optimal compression.
    
    The tool will try both lossless and lossy compression and save the smaller file.
    If INPUT_PATH is a directory, all image files in it will be processed.
    
    INPUT_PATH: Path to the input image file or directory
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    try:
        if input_path.is_file():
            # Process single file
            result_path = compress_image_to_webp(
                input_path=input_path,
                output_dir=output_dir,
                quality=quality
            )
            click.echo(f"✅ Successfully compressed: {result_path}")
            
        elif input_path.is_dir():
            # Process directory
            logging.info(f"Processing directory: {input_path}")
            processed_count, error_count = process_directory(
                input_dir=input_path,
                output_dir=output_dir,
                quality=quality,
                recursive=recursive
            )
            
            if error_count > 0:
                click.echo(f"⚠️  Completed with {error_count} errors")
            else:
                click.echo(f"✅ Successfully processed {processed_count} files")
                
        else:
            click.echo(f"❌ Error: {input_path} is neither a file nor a directory", err=True)
            exit(1)
        
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        exit(1)


if __name__ == '__main__':
    main()
