import re
from io import StringIO

from dominate import tags

from .TacticNotationsParser import TacticNotationsParser
from .TacticNotationsVisitor import TacticNotationsVisitor

class TacticNotationsToHTMLVisitor(TacticNotationsVisitor):
    def visitRepeat(self, ctx:TacticNotationsParser.RepeatContext):
        with tags.span(_class="repeat-wrapper"):
            with tags.span(_class="repeat"):
                self.visitChildren(ctx)
            repeat_marker = ctx.LGROUP().getText()[1]
            separator = ctx.ATOM()
            tags.sup(repeat_marker)
            if separator:
                tags.sub(separator.getText())

    def visitCurlies(self, ctx:TacticNotationsParser.CurliesContext):
        sp = tags.span(_class="curlies")
        sp.add("{")
        with sp:
            self.visitChildren(ctx)
        sp.add("}")

    def visitAtomic(self, ctx:TacticNotationsParser.AtomicContext):
        tags.span(ctx.ATOM().getText())

    def visitHole(self, ctx:TacticNotationsParser.HoleContext):
        tags.span(ctx.ID().getText()[1:], _class="hole")

    def visitWhitespace(self, ctx:TacticNotationsParser.WhitespaceContext):
        tags.span(" ")          # TODO: no need for a <span> here

class TacticNotationsToDotsVisitor(TacticNotationsVisitor):
    def __init__(self):
        self.buffer = StringIO()

    def visitRepeat(self, ctx:TacticNotationsParser.RepeatContext):
        separator = ctx.ATOM()
        self.visitChildren(ctx)
        if ctx.LGROUP().getText()[1] == "+":
            spacer = (separator.getText() + " " if separator else "")
            self.buffer.write(spacer + "…" + spacer)
            self.visitChildren(ctx)

    def visitCurlies(self, ctx:TacticNotationsParser.CurliesContext):
        self.buffer.write("{")
        self.visitChildren(ctx)
        self.buffer.write("}")

    def visitAtomic(self, ctx:TacticNotationsParser.AtomicContext):
        self.buffer.write(ctx.ATOM().getText())

    def visitHole(self, ctx:TacticNotationsParser.HoleContext):
        self.buffer.write("‘{}’".format(ctx.ID().getText()[1:]))

    def visitWhitespace(self, ctx:TacticNotationsParser.WhitespaceContext):
        self.buffer.write(" ")

class TacticNotationsToRegexpVisitor(TacticNotationsVisitor):
    def __init__(self):
        self.buffer = StringIO()

    def visitRepeat(self, ctx:TacticNotationsParser.RepeatContext):
        separator = ctx.ATOM()
        repeat_marker = ctx.LGROUP().getText()[1]

        self.buffer.write("(")
        self.visitChildren(ctx)
        self.buffer.write(")")

        if repeat_marker in ["?", "*"]:
            self.buffer.write("?")
        elif repeat_marker in ["+", "*"]:
            self.buffer.write("(")
            self.buffer.write(r"\s*" + re.escape(separator.getText() if separator else " ") + r"\s*")
            self.visitChildren(ctx)
            self.buffer.write(")*")

    def visitCurlies(self, ctx:TacticNotationsParser.CurliesContext):
        self.buffer.write(r"\{")
        self.visitChildren(ctx)
        self.buffer.write(r"\}")

    def visitAtomic(self, ctx:TacticNotationsParser.AtomicContext):
        self.buffer.write(re.escape(ctx.ATOM().getText()))

    def visitHole(self, ctx:TacticNotationsParser.HoleContext):
        self.buffer.write("([^();. \n]+)") # FIXME could allow more things

    def visitWhitespace(self, ctx:TacticNotationsParser.WhitespaceContext):
        self.buffer.write(r"\s+")
