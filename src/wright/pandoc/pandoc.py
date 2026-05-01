import sh

from wright.proojekt import Proojekt


class Output:
    def __init__(self, filename: str, type: str, stylesheet: str = None):
        self.filename = filename
        self.type = type
        self.stylesheet = stylesheet


class PanDoc:
    """
    Support creating operational documentation using Markdown documents and
    pandoc.
    """

    def __init__(self, project: Proojekt):
        self.project = project
        self._outputs: list[Output] = []
        self._toc = False
        self._toc_depth = None
        self._top_division = None
        self._variables: list[str] = []
        self._geometry = None
        self._documents: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"There was a problem generating the documentation: {exc_val}")
            return False

        try:
            self.generate()
        except Exception as e:
            print(f"Unable to generate documentation file: {e}")
            return False

        return True

    def toc(self, depth: int = 2, division: str = "chapter"):
        """
        Generate a table of contents.
        """
        self._toc = True
        self._toc_depth = depth
        self._top_division = division

    def var(self, value: str):
        """Set a pandoc variable, such as urlcolor or documentclass"""
        self._variables.append(value)

    def geometry(self, geometry: str):
        """Set a pandoc geometry, such as margins"""
        self._geometry = geometry

    def add(self, markdown_path: str):
        """
        Add a Markdown file to the document.  The document will output the
        documents in the order they were added.
        """
        self._documents.append(markdown_path)

    def pdf(self, filename: str):
        """
        Indicate you'd like a PDF document as output, and what the filename
        should be.
        """
        self._outputs.append(Output(filename, "pdf"))

    def word(self, filename: str):
        """
        Indicate you'd like a Word "docx" document as output, and what the
        filename should be.
        """
        self._outputs.append(Output(filename, "word"))

    def html(self, filename: str, css: str = None):
        """
        Indicate you'd like an HTML document as output, and what the filename
        and CSS stylesheet should be.
        """
        self._outputs.append(Output(filename, "html", css))

    def generate(self):
        """Runs pandoc to generate documentation.  Requires the pandoc binary."""
        args = [
            "-f", "gfm-hard_line_breaks"
        ]

        if self._toc:
            args.append("--toc")
            args.append("--toc-depth=%s" % self._toc_depth)
            args.append("--top-level-division=%s" % self._top_division)

        for var in self._variables:
            args.append("--variable=%s" % var)

        if self._geometry:
            args.append("-V")
            args.append("geometry:%s" % self._geometry)


        for output in self._outputs:
            local_args = args[:]

            if output.type == "html":
                local_args.append("-t")
                local_args.append("html5")

                # Produce a standalone HTML document
                local_args.append("-s")

                # Include a stylesheet?
                if output.stylesheet:
                    local_args.append("-c")
                    local_args.append(output.stylesheet)

            # Word and PDF only need the filename
            local_args.append("-o")
            local_args.append(output.filename)

            local_args.extend(self._documents)

            # print(" ".join(local_args))

            process = sh.pandoc(*local_args, _iter="out", _err_to_out=True, _cwd=self.project.working_dir)
            for line in process:
                print(line.strip())


def generate(project: Proojekt):
    """Generate release documentation from Markdown files using pandoc."""
    return PanDoc(project)
