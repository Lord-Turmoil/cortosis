import re
from typing import Dict
from lsp_client import LspClient
from utils import uri_to_path


def read_line(file, line):
    with open(file, "r") as f:
        lines = f.readlines()
    return lines[line]


class SymbolInfo:
    def __init__(self, file: str, line: int, props: Dict[str, str]) -> None:
        self.file = file
        self.line = line
        self.props = props


class LspWrapper:
    def __init__(self, client: LspClient) -> None:
        self.client = client
        self.opened = set()
        self.current = None

    def _open_file(self, file):
        if file not in self.opened:
            self.client.did_open(file)
            self.opened.add(file)

    def _hover(self, file, line, char):
        self._open_file(file)
        return self.client.hover(file, line, char)

    def _is_sym(self, sym: str):
        return re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", sym) is not None

    def _is_blacklisted(self, sym: str):
        return sym in [
            "int",
            "float",
            "double",
            "char",
            "void",
            "bool",
            "string",
            "true",
            "false",
            "static",
            "const",
            "extern",
        ]

    def _need_analysis(self, sym: str):
        return self._is_sym(sym) and not self._is_blacklisted(sym)

    def fetch_symbol(self, file, line, char) -> SymbolInfo:
        self._open_file(file)
        props = {}
        definition_locations = self.client.goto_definition(file, line, char)
        if len(definition_locations) == 0:
            return ""
        definition_location = definition_locations[0]
        line = definition_location.range_.start.line
        def_file = uri_to_path(definition_location.uri)
        code = read_line(def_file, line)
        i = 0
        while i < len(code):
            hover = self._hover(def_file, line, i)
            if hover is None:
                i = i + 1
            else:
                sym = code[hover.range_.start.character : hover.range_.end.character]
                if self._need_analysis(sym) and props.get(sym, None) is None:
                    props[sym] = hover.value
                i = hover.range_.end.character + 1
        return SymbolInfo(def_file, line, props)

    def fetch_line(self, file, line) -> Dict[str, SymbolInfo]:
        self._open_file(file)
        info = {}
        code = read_line(file, line)
        i = 0
        while i < len(code):
            hover = self._hover(file, line, i)
            if hover is None:
                i = i + 1
            else:
                sym = code[hover.range_.start.character : hover.range_.end.character]
                if self._need_analysis(sym) and info.get(sym, None) is None:
                    sym_info = self.fetch_symbol(file, line, i)
                    info[sym] = sym_info
                i = hover.range_.end.character + 1
        return info
