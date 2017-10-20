class AssemblerException(Exception):
    def __init__(self, data):
        super().__init__("Exception occured when assembling the code.")
        self.clang_data = data