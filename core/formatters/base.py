import os
from datetime import datetime


class BaseFormatter:

    file_extension = ""
    write_mode = "w"
    encoding = "utf-8"

    def format(self, ppt_data):
        raise NotImplementedError

    def save(self, content, output_dir, prefix="ppt"):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}{self.file_extension}"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, self.write_mode, encoding=self.encoding) as f:
            f.write(content)
        return filepath
