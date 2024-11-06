import logging
import asyncio
import os


def get_file_size(file_path):
    """Get human-readable file size."""
    size_bytes = os.path.getsize(file_path)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


async def compress_audio(input_path, output_path):
    """Compress audio using ffmpeg with Opus codec."""
    try:
        input_size = get_file_size(input_path)
        logging.info(f"Compressing audio. Input file size: {input_size}")

        # Construir el comando de ffmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-acodec",
            "libopus",
            "-ac",
            "1",
            "-b:a",
            "12k",
            "-application",
            "voip",
            output_path,
        ]

        # Ejecutar ffmpeg de manera asíncrona
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Esperar a que el proceso termine
        stdout, stderr = await process.communicate()

        # Verificar si el proceso terminó correctamente
        if process.returncode != 0:
            logging.error(f"Error compressing audio: {stderr.decode()}")
            raise Exception(f"ffmpeg exited with code {process.returncode}")

        output_size = get_file_size(output_path)
        logging.info(f"Audio compression complete. Output file size: {output_size}")
        return output_path

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise


async def extract_audio(input_path, output_path):
    """Extract audio from video using ffmpeg."""
    try:
        input_size = get_file_size(input_path)
        logging.info(f"Extracting audio from video. Input file size: {input_size}")

        # Construir el comando de ffmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vn",  # No incluir video en la salida
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            output_path,
        ]

        # Ejecutar ffmpeg de manera asíncrona
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Esperar a que el proceso termine
        stdout, stderr = await process.communicate()

        # Verificar si el proceso terminó correctamente
        if process.returncode != 0:
            logging.error(f"Error extracting audio: {stderr.decode()}")
            raise Exception(f"ffmpeg exited with code {process.returncode}")

        output_size = get_file_size(output_path)
        logging.info(f"Audio extraction complete. Output file size: {output_size}")
        return output_path

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise
