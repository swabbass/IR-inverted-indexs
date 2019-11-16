DOC_START = '<DOC>'
DOC_END = '</DOC>'
DOC_NO_START = '<DOCNO>'
DOC_NO_END = '</DOCNO>'
TEXT_START = '<TEXT>'
TEXT_END = '</TEXT>'


class TextElement:
    def __init__(self, started=False, ended=False, content=""):
        self.started = started
        self.ended = ended
        self.content = content

    def __repr__(self):
        return '<TEXT started: ' + str(self.started) + ' ended: ' + str(self.ended) + ' />'


class DocElement:
    def __init__(self):
        self.docNo = None
        self.texts = []
        self.currentText = None

    def addAndSetCurrentText(self):
        self.currentText.ended = True
        self.texts.append(self.currentText)
        self.currentText = None

    def __repr__(self):
        return '<DOC no: ' + str(self.docNo) + ' #texts: ' + str(len(self.texts)) + ' />'


class FunnyDocsParser:
    def __init__(self):
        self.docsCount = 0
        self.docs = []
        self.lastValidElement = None
        self.currentElement = None
        self.failedDocs = []

    def clean(self):
        self.docsCount += len(self.docs)
        self.docs = []
        self.currentElement = None

    def parse(self, file):
        with open(file, 'r') as f:
            line = f.readline()
            cnt = 1
            while line:
                if not self._parseLine(line):
                    line = f.readline()
                    while line and DOC_START not in line:
                        line = f.readline()
                    continue
                line = f.readline()
                cnt += 1
        return self

    def _parseLine(self, line):
        stripped = line.strip()
        if DOC_START in stripped:
            self.currentElement = DocElement()
        elif DOC_NO_START in stripped and DOC_NO_END in stripped:
            self.currentElement.docNo = line.replace(DOC_NO_START, '').replace(DOC_NO_END, '').strip()
        # the text is one liner <TEXT> AP891012-0247 ward abbass </TEXT>
        elif TEXT_START in stripped and TEXT_END in stripped:
            self.currentElement.texts.append(
                TextElement(True, True, stripped.replace(TEXT_START, '').replace(TEXT_END, '').strip()))
        elif TEXT_START in stripped:
            if not self.currentElement.currentText:
                self.currentElement.currentText = TextElement(True)
            else:
                if self.currentElement.currentText.started and not self.currentElement.currentText.ended:
                    raise Exception('Already opened text and got another opener')
                elif self.currentElement.currentText.ended:
                    pass
        elif TEXT_END in stripped:
            if self.currentElement.currentText:
                self.currentElement.addAndSetCurrentText()
            else:
                self.failedDocs.append(self.currentElement)
                self.currentElement = None
                return False  # skip this doc at all, hence find the next Doc
        elif DOC_END in stripped:
            if self.currentElement:
                self.docs.append(self.currentElement)
                self.currentElement = None
            else:
                raise Exception('Closing un started <DOC> tag')
        else:  # no tags expecting text content
            if self.currentElement and self.currentElement.currentText:
                self.currentElement.currentText.content += stripped + ' '
            else:
                if len(stripped) == 0:
                    pass
                else:
                    raise Exception('text without current text')
        return True  # all ok keep on reading

    def __repr__(self):
        return 'total valid docs count: ' + str(self.docsCount) + ', failedDocs count: ' + str(len(self.failedDocs))

# print(FunnyDocsParser().parse('./stam/test'))
