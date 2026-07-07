import cloudinary
import cloudinary.uploader

from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


class AvatarService:
    @staticmethod
    def upload_avatar(file, username: str) -> str:
        """
        Завантажує зображення в Cloudinary у публічну папку
        "ContactsApp/<username>" (перезаписуючи попереднє фото)
        і повертає готове URL для збереження в user.avatar.
        """
        public_id = f"ContactsApp/{username}"

        upload_result = cloudinary.uploader.upload(
            file, public_id=public_id, overwrite=True
        )

        avatar_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250,
            height=250,
            crop="fill",
            version=upload_result.get("version"),
        )
        return avatar_url


avatar_service = AvatarService()
