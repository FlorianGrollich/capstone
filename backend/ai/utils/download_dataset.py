import requests
from tqdm import tqdm
from io import BytesIO
from zipfile import ZipFile

def get_dataset(file_url: str, extract_to: str = '.') -> None:
    try:
        # Stream the download to handle large files
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KiB
        zip_buffer = BytesIO()

        print("Downloading...")
        with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
            for chunk in response.iter_content(block_size):
                pbar.update(len(chunk))
                zip_buffer.write(chunk)

        zip_buffer.seek(0)

        # Open the zip file and extract with progress
        with ZipFile(zip_buffer) as zip_file:
            file_list = zip_file.namelist()
            print("Unzipping...")
            for file in tqdm(file_list, unit='file'):
                zip_file.extract(member=file, path=extract_to)

        print(f"Done! Files extracted to: {extract_to}")

    except requests.exceptions.RequestException as e:
        print(f"Download error: {e}")
    except zipfile.BadZipFile as e:
        print(f"ZIP error: {e}")
