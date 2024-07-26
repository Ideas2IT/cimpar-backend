# write a simple file handling interface in python. It should support files of different types: .txt, .json and csv.
# Methods to support - read, write, compress, get_metadata



class Filehandler:

    def __init__(self, file_name):
        self.file_name = file_name

    def find_file_type(self):
        try:
            file_name, type = self.file_name.split(".")
            return type if type in ("csv", "json", "txt") else None
        except Exception as e:
            logger.error("error details")
            return None

    def read(self):
        file_type = self.find_file_type()
        if file_type == "txt":
            return self.read_text()
        elif file_type == "csv":
            return self.csvt_read()



class FactoryMethod:
    def read(self):
        pass
    def write(self):
        pass

    def write(self):
        pass


class Texthandler(FactoryMethod):
    def read(self):
        #Todo
        pass