from pathlib import Path
import random


class OutfitRecommender:
    def __init__(self, dataset_dir="dataset"):
        self.dataset_dir = Path(dataset_dir)

        self.item_folders = {
            "top": "Tops",
            "bottom": "Bottoms",
            "shoes": "Shoes"
        }

        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    def find_matching_image(self, folder_name, target_label):
        folder_path = self.dataset_dir / folder_name

        if not folder_path.exists():
            return None

        matching_images = []

        for file_path in folder_path.iterdir():
            if file_path.is_file():
                filename = file_path.name.lower()
                extension = file_path.suffix.lower()

                if extension in self.allowed_extensions and target_label in filename:
                    matching_images.append(file_path)

        if not matching_images:
            return None

        chosen_image = random.choice(matching_images)

        return chosen_image

    def recommend(self, gender, weather):
        target_label = f"{gender}_{weather}"

        result = {
            "target_label": target_label,
            "items": {},
            "missing": []
        }

        for item_name, folder_name in self.item_folders.items():
            image_path = self.find_matching_image(folder_name, target_label)

            if image_path is None:
                result["missing"].append(item_name)
            else:
                result["items"][item_name] = image_path

        return result