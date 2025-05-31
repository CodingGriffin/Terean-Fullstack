import io
import os
import zipfile
import asyncio
from typing import AsyncGenerator, List, Optional, Tuple
import aiofiles
from fastapi import BackgroundTasks
from email.mime.base import MIMEBase
from email import encoders
import logging

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024 * 1024  # 1MB chunks


class StreamingZip:
    """
    Creates a zip file on-the-fly and streams it without loading everything into memory.
    Uses a temporary file to avoid memory issues with large archives.
    """
    
    def __init__(self, files_to_zip: List[Tuple[str, str]], chunk_size: int = CHUNK_SIZE):
        """
        Initialize streaming zip creator.
        
        Args:
            files_to_zip: List of tuples (file_path, archive_name)
            chunk_size: Size of chunks to yield
        """
        self.files_to_zip = files_to_zip
        self.chunk_size = chunk_size
        
    async def generate(self) -> AsyncGenerator[bytes, None]:
        """Generate zip file chunks asynchronously."""
        import tempfile
        
        # Create a temporary file for the zip
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_path = temp_file.name
            
        try:
            # Create zip file
            with zipfile.ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
                for file_path, archive_name in self.files_to_zip:
                    if os.path.exists(file_path):
                        zip_file.write(file_path, archive_name)
                    else:
                        logger.warning(f"File not found: {file_path}")
            
            # Stream the zip file
            async with aiofiles.open(temp_path, 'rb') as f:
                while chunk := await f.read(self.chunk_size):
                    yield chunk
                    
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.error(f"Error cleaning up temp file: {e}")


async def create_streaming_zip_response(files_to_zip: List[Tuple[str, str]], filename: str):
    """
    Create a streaming response for zip file download.
    
    Args:
        files_to_zip: List of tuples (file_path, archive_name)
        filename: Name for the downloaded zip file
        
    Returns:
        StreamingResponse object
    """
    from fastapi.responses import StreamingResponse
    
    streamer = StreamingZip(files_to_zip)
    
    return StreamingResponse(
        streamer.generate(),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def create_email_attachment_stream(file_path: str, chunk_size: int = CHUNK_SIZE) -> MIMEBase:
    """
    Create an email attachment without loading the entire file into memory.
    Uses chunked base64 encoding.
    
    Args:
        file_path: Path to the file to attach
        chunk_size: Size of chunks to read
        
    Returns:
        MIMEBase object with encoded file
    """
    import base64
    from io import BytesIO
    
    part = MIMEBase('application', 'octet-stream')
    
    # Use a BytesIO buffer for chunked encoding
    encoded_buffer = BytesIO()
    
    with open(file_path, 'rb') as f:
        # Base64 encoder that writes to our buffer
        encoder = base64.b64encode
        
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            encoded_chunk = encoder(chunk)
            encoded_buffer.write(encoded_chunk)
    
    # Set the payload with the encoded data
    encoded_buffer.seek(0)
    part.set_payload(encoded_buffer.read().decode('ascii'))
    
    # Add header
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
    part.add_header('Content-Transfer-Encoding', 'base64')
    
    return part


async def process_large_sgy_file_streaming(
    file_path: str, 
    geophone_spacing: float,
    max_frequency: float,
    max_slowness: float,
    num_freq_points: int,
    num_slow_points: int
) -> dict:
    """
    Process large SEG-Y files in chunks to avoid loading entire file into memory.
    This is a placeholder that would need to be implemented with actual SEG-Y 
    processing logic that supports streaming.
    
    Args:
        file_path: Path to SEG-Y file
        geophone_spacing: Spacing between geophones
        max_frequency: Maximum frequency for processing
        max_slowness: Maximum slowness value
        num_freq_points: Number of frequency points
        num_slow_points: Number of slowness points
        
    Returns:
        Processing results
    """
    # NOTE: This would require modifying the tereancore library to support
    # streaming/chunked processing of SEG-Y files. For now, this is a 
    # placeholder showing the interface.
    
    logger.warning("Streaming SEG-Y processing not yet implemented - falling back to regular processing")
    
    # The actual implementation would process the file in chunks
    # For example:
    # - Read SEG-Y header
    # - Process traces in batches
    # - Accumulate results without loading entire dataset
    
    from tereancore.sgy_utils import load_segy_segyio, preprocess_streams
    from tereancore.vspect import vspect_stream
    
    # Current non-streaming implementation (loads entire file)
    stream_data = load_segy_segyio([file_path])
    preprocess_streams(stream_data)
    
    results = vspect_stream(
        stream=stream_data[0],
        geophone_dist=geophone_spacing,
        f_min=0.0,
        f_max=max_frequency,
        f_points=num_freq_points,
        p_points=num_slow_points,
        p_max=max_slowness,
        reduce_nyquist_to_f_max=True,
        ratio_grids=True,
        normalize_grids=True,
    )
    
    return results


class ChunkedFileProcessor:
    """
    Base class for processing large files in chunks.
    Can be extended for specific file types (SEG-Y, velocity models, etc.)
    """
    
    def __init__(self, file_path: str, chunk_size: int = CHUNK_SIZE):
        self.file_path = file_path
        self.chunk_size = chunk_size
        
    async def process_chunks(self, process_func):
        """
        Process file in chunks using provided processing function.
        
        Args:
            process_func: Async function that processes a chunk of data
            
        Returns:
            Accumulated results from all chunks
        """
        results = []
        
        async with aiofiles.open(self.file_path, 'rb') as f:
            while chunk := await f.read(self.chunk_size):
                result = await process_func(chunk)
                results.append(result)
                
        return results
        
    async def get_file_size(self) -> int:
        """Get file size without loading it."""
        return os.path.getsize(self.file_path) 