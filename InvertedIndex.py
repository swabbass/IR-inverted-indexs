import os
import xml.etree.ElementTree as ElementTree


class Doc:
    def __init__(self, id, docNo):
        self.id = id
        self.docNo = docNo

    def __repr__(self):
        return '(' + str(self.id) + ', ' + str(self.docNo) + ')'


def tokenize(text):
    text = text.replace('\n', ' ')
    lines = text.split(' ')
    return filter(lambda word: len(word) > 0, lines)


def indexTokens(doc, tokenizedText, invertedIndex):
    for word in tokenizedText:
        if word not in invertedIndex:
            invertedIndex[word] = [doc]
        else:
            if invertedIndex[word][-1].id != doc.id:
                invertedIndex[word].append(doc)


def indexTexts(doc, texts, invertedIndex):
    for t in texts:
        tokenizedText = tokenize(t.text.strip())
        indexTokens(doc, tokenizedText, invertedIndex)


def indexFile(filePath, invertedIndex, globalID):
    with open(filePath, 'r') as f:  # Reading file
        xml = f.read()
    xml = '<ROOT>' + xml + '</ROOT>'
    root = ElementTree.fromstring(xml)
    for doc in root:
        globalID += 1
        docNo = doc.find("DOCNO").text.strip()
        texts = doc.findall("TEXT")
        doc = Doc(globalID, docNo)
        indexTexts(doc, texts, invertedIndex)
        # print(tokenizedText)
    return globalID


def loadFiles():
    directoryPath = "./AP_Coll_Parsed"
    files = []
    for r, d, f in os.walk(directoryPath):
        for file in f:
            files.append(os.path.join(r, file))
    return files


def InvertedIndex():
    invertedIndex = dict()
    files = loadFiles()
    limit = 1
    globalId = 0
    for file in files:
        print(file)
        if limit > 0:
            limit -= 1
            globalId = indexFile(file, invertedIndex, globalId)
        else:
            break


InvertedIndex()
