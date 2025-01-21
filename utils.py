import zipfile


def is_zip_file_valid(file_path):
    try:
        with zipfile.ZipFile(file_path) as zip_file:
            if zip_file.testzip() is None:
                return True
            else:
                return False
    except Exception:
        return False
