def profile_avatar_directory_path(instance: "Profile", filename: str) -> str:
    return f"profiles/user_{instance.user.pk}/avatars/{filename}"
