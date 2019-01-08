# run black on the code snippet:
import os


def correct_pep8(snippet):
    """ get code snippet and run black over it to improve its format"""
    print(os.getcwd())
    f = open(r"\badCode\snippet.py", "w")
    f.write(snippet)
    os.system("echo off black .")
    snippet = ""
    for line in f:
        print(line)
        snippet += line + "\n"
    f.truncate(0)
    return snippet


if __name__ == "__main__":
    correct_pep8(
        """
    a = [1,2,3,4,5])\n
                 print(a**2)
                 """
    )
