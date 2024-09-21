
import unittest
import os
import tempfile
from features.file_management import FileManager

class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(self.temp_dir)

    def test_read_write_file(self):
        test_content = "Hello, World!"
        test_file = "test.txt"
        self.file_manager.write_file(test_file, test_content)
        read_content = self.file_manager.read_file(test_file)
        self.assertEqual(test_content, read_content)

    def test_list_files(self):
        test_files = ["file1.txt", "file2.txt", "file3.txt"]
        for file in test_files:
            self.file_manager.write_file(file, "content")
        listed_files = self.file_manager.list_files()
        self.assertEqual(set(test_files), set(listed_files))

    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
