from darwin.client import Client
from pathlib import Path
from darwin.dataset.upload_manager import LocalFile
from pathlib import Path


def upload_data(image_folder, api_key, target_slug):
    image_folder = Path(image_folder)
    client = Client.from_api_key(api_key)
    dataset = client.get_remote_dataset(target_slug)
    files = list(image_folder.iterdir())
    dataset.push(files)


def parse_slug(request, target=None):
    target = target if target is not None else request['dataset_info']['slug']
    slug_info = f"{request['team_info']['slug']}/{target}"
    return slug_info 