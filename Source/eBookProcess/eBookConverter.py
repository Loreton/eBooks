# xxx!/usr/bin/python3
#
# updated by ...: Loreto Notarantonio
# Version ......: 23-03-2020 17.05.39
#
# Progamma per convertire  un ebook  in text

# https://pypi.org/project/epub-conversion/
def ePubConverter(base_path):
    import epub_conversion as Converter
    converter = Converter(base_path + "/")
    converter.convert("my_succinct_text_file.gz")

def ePubConverter_lineByline(base_path):
    from epub_conversion.utils import open_book, convert_epub_to_lines, convert_lines_to_text

    local_tree_list = Ln.TreeList(base_path, 'eBook')
    for relative_folder_path in local_tree_list:
        full_folder_path  = os.path.join(base_path, relative_folder_path).rstrip(os.path.sep)

        files   = [f for f in os.listdir(full_folder_path) if os.path.isfile(os.path.join(full_folder_path, f))]
        folders = [f for f in os.listdir(full_folder_path) if os.path.isdir(os.path.join(full_folder_path, f))]

    for file in files:
        filename=os.path.join(full_folder_path, file)
        book = open_book(filename)
        lines = convert_epub_to_lines(book)
        ltext = convert_lines_to_text(lines)


