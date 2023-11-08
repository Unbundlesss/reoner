import os
import os.path
import unicodedata
import string
import re


class ImproperlyConfigured(Exception):
    pass


def make_pather(start, *paths):
    """Return a Pather or PatherFile as appropriate"""
    res_path = absolute_join(start, *paths)
    if res_path.is_file():
        return PatherFile(res_path.file.__str__())
    return Pather(res_path.__str__())


def absolute_join(base: string, *paths, **kwargs):
    """
    Find the normalized absolute path of base + paths.
    If base + paths is a file, return the parent directory of that file.
    """

    class PathOrFile(str):
        def __init__(self, in_dir, in_file=None):
            self.dir = in_dir
            self.file = in_file

        def __str__(self):
            return self.dir.__str__()

        def is_file(self):
            return self.file is not None

    real_base = os.path.realpath(base)
    absolute_path = os.path.normpath(os.path.join(real_base, *paths))
    if not os.path.isdir(absolute_path):
        parent = os.path.dirname(absolute_path)
        if os.path.isdir(parent):
            if os.path.isfile(absolute_path):
                return PathOrFile(parent, os.path.basename(absolute_path))
            return PathOrFile(parent)
        raise ImproperlyConfigured("Is not a directory: {}".format(absolute_path))
    if kwargs.get("required") and not os.path.exists(absolute_path):
        raise ImproperlyConfigured("Create required path: {}".format(absolute_path))
    return PathOrFile(absolute_path)


class Pather(os.PathLike):
    """Contains code from django-environs
    https://github.com/joke2k/django-environ/blob/main/environ/environ.py
    """

    def __init__(self, start=".", *paths, **kwargs):
        # super().__init__()
        absolute = absolute_join(start, *paths, **kwargs)
        self.__root__ = absolute

    def get_files(self, ext="aiff") -> list[str]:
        ext = ext.lstrip(".")
        opts: list[str] = os.listdir(self.__root__)
        # return a list of
        opts = [
            f"{i}/" if os.path.isdir(i) else i
            for i in opts
            if os.path.isdir(i) or i.endswith(f".{ext}")
        ]
        # filter out hidden files
        filter(lambda x: not x.startswith("."), opts)
        # sort files
        opts = sorted(opts, key=lambda x: x)

        return opts

    def get_files_full_paths(self, ext="aiff") -> list[str]:
        ext = ext.lstrip(".")
        path = self.__root__
        list_em: list[str] = os.listdir(path)
        opts = [
            f"{path}/{i}" if os.path.isfile(f"{path}/{i}") else None
            for i in list_em
            if i.endswith(f".{ext}")
        ]
        opts = filter(lambda x: x is not None and not x.startswith("."), opts)
        # cast as list otherwise it's an iterable
        opts = sorted(opts, key=lambda x: x)
        return opts

    def path(self, *paths, **kwargs):
        return self.__class__(self.__root__, *paths, **kwargs)

    @staticmethod
    def arg_type(arg):
        if os.path.isdir(arg):
            try:
                return Pather(arg)
            except Exception:
                raise ValueError(Exception)
        elif os.path.isfile(arg):
            try:
                return PatherFile(arg)
            except Exception:
                raise ValueError(Exception)

        else:
            raise ValueError("The argument provided is not a directory or a file.")

    def isdir(self):
        return os.path.isdir(self.__str__())

    def file(self, name, *args, **kwargs):
        """Open a file.

        :param name: Filename appended to `self.root`
        :param args: passed to open()
        :param kwargs: passed to open()

        :rtype: file
        """
        return open(self(name), *args, **kwargs)

    # def cd(self, start="", *paths, **kwargs):
    #     if start:
    #         self.__root__ = absolute_join(start, *paths, **kwargs)
    #     os.chdir(self.__root__)
    #     return self.__root__

    def _change_dir(self, path):
        self.__root__ = absolute_join(self.__root__, path)
        os.chdir(self.__root__)
        return self.__root__

    def cd(self, path=None):
        if path is None:
            path = "."
        self._change_dir(path)

    @property
    def ls(self):
        return sorted(
            filter(lambda x: not x.startswith("."), os.listdir(self.__root__)),
            key=lambda x: x,
        )

    @property
    def root(self):
        """Current directory for this Path"""
        return self.__root__

    def __call__(self, *paths, **kwargs):
        """Retrieve the absolute path, with appended paths
        :param paths: List of sub path of `self.root`
        """
        return absolute_join(self.__root__, *paths, **kwargs)

    def __eq__(self, other):
        return self.__root__ == other.__root__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if not isinstance(other, Pather):
            return Pather(self.__root__, other)
        return Pather(self.__root__, other.__root__)

    def __sub__(self, other):
        if isinstance(other, int):
            return self.path("../" * other)
        elif isinstance(other, str):
            if self.__root__.endswith(other):
                return Pather(self.__root__.rstrip(other))
        raise TypeError(
            "unsupported operand type(s) for -: '{self}' and '{other}' "
            "unless value of {self} ends with value of {other}".format(
                self=type(self), other=type(other)
            )
        )

    def __invert__(self):
        return self.path("..")

    def __contains__(self, item):
        base_path = self.__root__
        if len(base_path) > 1:
            base_path = os.path.join(base_path, "")
        return item.__root__.startswith(base_path)

    def __repr__(self):
        return "<Path:{}>".format(self.__root__)

    def __str__(self):
        return self.__root__

    def __unicode__(self):
        return self.__str__()

    def __getitem__(self, *args, **kwargs):
        return self.__str__().__getitem__(*args, **kwargs)

    def __fspath__(self):
        return self.__str__()

    def rfind(self, *args, **kwargs):
        return self.__str__().rfind(*args, **kwargs)

    def find(self, *args, **kwargs):
        return self.__str__().find(*args, **kwargs)


class PatherFile(Pather):
    def __init__(self, filename, start=".", *paths, **kwargs):
        super().__init__(start, *paths, **kwargs)

        absolute = absolute_join(start, *paths, **kwargs)
        self.__root__ = absolute.__str__()
        self.__filename__ = filename.__str__().strip("/")

    @property
    def root(self):
        """Current directory for this Path"""
        return self.__root__

    def filepath(self):
        return self.__str__()

    def __str__(self):
        return self.__root__ + "/" + self.__filename__


def clean_filename(filename, whitelist=None, replace=""):
    valid_filename_chars = "-_.() %s%s%s" % (
        string.ascii_letters,
        string.digits,
        whitelist,
    )
    char_limit = 255

    # replace spaces
    for r in replace:
        filename = filename.replace(r, "_")

    # keep only valid ascii chars
    cleaned_filename = (
        unicodedata.normalize("NFKD", filename).encode("ASCII", "ignore").decode()
    )

    # keep only whitelisted chars
    cleaned_filename = "".join(c for c in cleaned_filename if c in valid_filename_chars)
    re.sub("_{2,}", "_", filename)
    if len(cleaned_filename) > char_limit:
        print(
            "Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(
                char_limit
            )
        )

    return cleaned_filename[:char_limit]
