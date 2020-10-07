import os
import sys
import fnmatch
import shutil


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Delete(metaclass=SingletonMeta):
    def __init__(self):
        self.cntOfFiles = 0
        self.cntOfDirs = 0
        self.cntOfEmptyDirs = 0
        self.cntOfTotal = 0

    def dir(self, name):
        if not os.access(name, os.W_OK):
            return
        print("[ info ] delete directory:\t" + name)
        shutil.rmtree(name)
        self.cntOfDirs += 1
        self.cntOfTotal += 1

    def emptyDir(self, name):
        if not os.access(name, os.W_OK):
            return
        print("[ info ] delete empty directory:" + name)
        os.rmdir(name)
        self.cntOfEmptyDirs += 1
        self.cntOfTotal += 1

    def file(self, name):
        if not os.access(name, os.W_OK):
            return
        print("[ info ] delete file:\t\t" + name)
        os.remove(name)
        self.cntOfFiles += 1
        self.cntOfTotal += 1

    def print(self):
        print("Files deleted:\t\t\t" + "{:6d}".format(self.cntOfFiles))
        print("Directories deleted:\t\t" + "{:6d}".format(self.cntOfDirs))
        print("Empty directories deleted: \t" +
              "{:6d}".format(self.cntOfEmptyDirs))
        print("Total objects deleted:\t\t" + "{:6d}".format(self.cntOfTotal))


class Cleaner(object):
    def __init__(self, path):
        self.Path = path

    def exec(self):
        IgnoreFile = self.Path + "\.gitignore"
        try:
            print("Opening '" + IgnoreFile + "'...")
            masks = self.__masksFromFile(IgnoreFile)
        except FileNotFoundError:
            sys.exit("[error] " + IgnoreFile + "doesn't exist")
        print("Loading masks...")
        print("Cleaning rubbish...")
        delete = Delete()
        for root, dirs, files in os.walk(self.Path, topdown=False):
            for name in files:
                absoluteName = os.path.join(root, name)
                if self.__checkMatch(absoluteName, masks):
                    delete.file(absoluteName)
        for name in dirs:
            absoluteName = os.path.join(root, name)
            if self.__isDirEmpty(absoluteName):
                delete.emptyDir(absoluteName)
            if self.__checkMatch(absoluteName, masks):
                delete.dir(absoluteName)

    def __masksFromFile(self, fileName):
        masksFile = open(fileName, 'r')
        masks = []
        for line in masksFile:
            ch1 = line[0]
            if ch1 != '#':
                if ch1 == '/' or ch1 == '\\':
                    line = '*' + line
                masks.append(line.rstrip())
        masksFile.close()
        return masks

    def __checkMatch(self, name, masks):
        for mask in masks:
            if fnmatch.fnmatch(name, mask):
                return True
        return False

    def __isDirEmpty(self, name):
        return not os.listdir(name)


def main():
    IgnoreFile = ".gitignore"
    Path = "."
    delete = Delete()
    for root, dirs, files in os.walk(Path, topdown=False):
        for name in files:
            absoluteName = os.path.join(root, name)
            if name == IgnoreFile:
                cleaner = Cleaner(root)
                cleaner.exec()
        if not dirs and not files:
            delete.emptyDir(root)
    delete.print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
