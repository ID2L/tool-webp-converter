import click
import logging
from pathlib import Path
from .convert import compress_image_to_webp


@click.command()
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='Output directory (defaults to input file directory)')
@click.option('--quality', '-q', type=click.IntRange(1, 100), default=80,
              help='Quality for lossy compression (1-100, default: 80)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(input_path: Path, output_dir: Path, quality: int, verbose: bool):
    """
    Compress an image to WebP format using optimal compression.
    
    The tool will try both lossless and lossy compression and save the smaller file.
    
    INPUT_PATH: Path to the input image file
    """
    # Configure logging
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    try:
        result_path = compress_image_to_webp(
            input_path=input_path,
            output_dir=output_dir,
            quality=quality
        )
        click.echo(f"✅ Successfully compressed: {result_path}")
        
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        exit(1)


if __name__ == '__main__':
    main()
