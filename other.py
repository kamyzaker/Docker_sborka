import os

def check_way(city):
    format = ['jpg', 'jpeg', 'webp']
    base_path = 'C:/Users/Home/Desktop/CITY/'
    for fmt in format:
        file_path = f'{base_path}{city}.{fmt}'
        if os.path.exists(file_path): return file_path
    return None