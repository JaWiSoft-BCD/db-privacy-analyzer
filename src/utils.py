def progress_tracker(total:int, done:int):
    """
    Track the progress of completion. 
    """
    persentage_done = round(done/total*100, 2)
    print(f"{str(done)} out of {str(total)} done. Completed: {persentage_done}%")

def append_to_file(filename, content):
    """
    Append the given content to the specified file. If the file does not exist, it will be created.
    
    Parameters:
    filename (str): The name of the file to append to.
    content (str): The string to be appended to the file.
    """
    try:
        with open(filename, 'a') as file:
            file.write(content + '\n')
    except FileNotFoundError:
        with open(filename, 'w') as file:
            file.write(content + '\n')