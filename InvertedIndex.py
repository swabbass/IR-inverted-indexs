import os
from lxml import etree


class Doc:
    def __init__(self, id, docNo):
        self.id = id
        self.docNo = docNo

    def __lt__(self, other):
        return other.id > self.id

    def __le__(self, other):
        return other.id >= self.id

    def __eq__(self, other):
        return self.id == other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

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
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(xml, parser=parser)
    for doc in root:
        try:
            docNo = doc.find("DOCNO").text.strip()
            texts = doc.findall("TEXT")
            if len(texts) > 0:
                globalID += 1
                doc = Doc(globalID, docNo)
                indexTexts(doc, texts, invertedIndex)
            # print(tokenizedText)
        except:
            print('errorrrrrr ', etree.tostring(doc))
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
    limit = 2000
    globalId = 0
    for file in files:
        if limit > 0:
            limit -= 1
            globalId = indexFile(file, invertedIndex, globalId)
            print(file)
        else:
            break


def AND(left, right):
    i, j = 0, 0
    result = []
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            i += 1
        elif right[j] < left[i]:
            j += 1
        else:
            result.append(right[j])
            j += 1
            i += 1
    return result


def OR(left, right):
    i, j = 0, 0
    result = []

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        elif right[j] < left[i]:
            result.append(right[j])
            j += 1
        else:
            result.append(right[j])
            j += 1
            i += 1

    # if left has no elements then merge the right elements
    if j < len(right):
        result.extend(right[j:])

    # if right has no elements then merge the left elements
    if i < len(left):
        result.extend(left[i:])
    return result


def NOT(left, right):
    i = 0
    j = 0
    result = []
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        elif right[j] < left[i]:
            j += 1
        else:
            j += 1
            i += 1
    # if right has no elements then merge the left elements
    if i < len(left):
        result.extend(left[i:])
    return result


left = [Doc(1, ""), Doc(4, ""), Doc(5, "")]
right = [Doc(0, ""), Doc(1, ""), Doc(2, ""), Doc(4, ""), Doc(7, "")]

print(AND(left, right))
print(OR(left, right))
print(NOT(left, right))
