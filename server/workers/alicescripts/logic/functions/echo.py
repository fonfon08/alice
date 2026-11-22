from utils.querys import add_alicescript_output


def run(content):
    # Stores the script output in the DB
    add_alicescript_output(str(content))
