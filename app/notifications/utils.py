from .models import Notification

MAX_EMAIL_SIZE = 5 * 1024 * 1024


def get_attachments(
    notification: Notification, max_email_size=MAX_EMAIL_SIZE
) -> tuple[list, list]:
    if not notification.ticket:
        return [], []
    total_size = 0
    files_to_attach, files_to_links = [], []
    for comment in notification.ticket.get_comments_for_report(prefetch=True):
        for file in comment.files.all():
            size_file = file.file.size
            files_to_attach.append({"file": file, "size": size_file, "type": "file"})
            total_size += size_file
        for image in comment.images.all():
            size_image = image.image.size
            files_to_attach.append({"file": image, "size": size_image, "type": "image"})
            total_size += size_image

    if total_size < max_email_size:
        return [fa["file"] for fa in files_to_attach], files_to_links

    files_to_attach.sort(key=lambda x: x["size"], reverse=True)
    remaining_size = total_size
    while remaining_size > max_email_size and files_to_attach:
        file_attach = files_to_attach.pop(0)
        remaining_size -= file_attach["size"]
        files_to_links.append(file_attach["file"].get_absolute_url())
    files_to_attach = [fa["file"] for fa in files_to_attach]
    return files_to_attach, files_to_links
