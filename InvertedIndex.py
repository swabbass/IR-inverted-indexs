import os

from FunnyParser import FunnyDocsParser

parser = FunnyDocsParser()


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


class Node:
    def __init__(self, left=None, data=None, right=None):
        self.left = left
        self.right = right
        self.data = data

    def isFullNode(self):
        return self.data and self.left and self.right

    def isCleanNode(self):
        return not (self.data or self.left or self.right)

    def __repr__(self):
        return '(' + str(self.left) + '<----- (' + str(self.data) + ') ---->' + str(self.right) + ')'


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
        tokenizedText = tokenize(t.content.strip())
        indexTokens(doc, tokenizedText, invertedIndex)


def indexFile(filePath, invertedIndex, globalID):
    result = parser.parse(filePath)
    print(str(result))
    for doc in result.docs:
        docNo = doc.docNo
        texts = doc.texts
        if len(texts) > 0:
            globalID += 1
            doc = Doc(globalID, docNo)
            indexTexts(doc, texts, invertedIndex)
    return globalID


def loadFiles():
    directoryPath = "./stam"
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
    return invertedIndex


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


def executeQuery(queryTree, invertedIndex):
    if not queryTree:
        return []
    op = None
    if queryTree.data == 'AND':
        op = AND
    elif queryTree.data == 'OR':
        op = OR
    elif queryTree.data == 'NOT':
        op = NOT

    if op:
        return op(executeQuery(queryTree.left, invertedIndex), executeQuery(queryTree.right, invertedIndex))
    else:
        return invertedIndex[queryTree.data]


def BooleanQueries(invertedIndex):
    with open("BooleanQueries.txt", 'r') as f:  # Reading file
        for query in f:
            query = '( ( iran OR africa ) NOT ( sanctions OR support ) )'
            queryTree = parseQuery(query.strip().split(' '))
            print(query)
            print(queryTree)
            break
            # print(executeQuery(queryTree, invertedIndex))


def isDataNode(node):
    return (node.data not in ['AND', 'OR', 'NOT']) and not node.left and not node.right


def parseQuery(query):
    if len(query) == 0:
        return None
    if query[0] == '(':
        node = parseQuery(query[1:])  # always move forward
        return node  # do nothing when return
    elif query[0] in ['AND', 'OR', 'NOT']:
        node = parseQuery(query[1:])  # always move forward
        # returned with valid node so we need to fill operator
        if node.isFullNode():
            # if it is a full node; has data and left and right not null
            # then we should check the left side if it is full or data node only (some sort of full)
            # then create new node nesting the returned one in the right and set the operation
            if node.left.isFullNode() or isDataNode(node.left):
                node = Node(data=query[0], right=node)
            else:
                # the left is not full node and not data node
                # so it has to be in ((None <--- (None) ---> None) < --- (Operator) --- > ( Something ) ) structure
                node.left.data = query[0]
        else:
            # node is not full so lets set the op example :(None) < --- (None)  --- > ( Something )
            node.data = query[0]
        return node
    elif query[0] == ')':
        if len(query) == 1:  # last ) so we create new node
            return Node()
        else:
            node = parseQuery(query[1:])  # always move forward

            # on the recursion back if we face ) then it should be a new node unless its full
            if not node.left and node.right and node.data:
                node.left = Node()
            return node
    else:
        node = parseQuery(query[1:])  # always move forward
        mainNode = node
        #  when returned node is valid has not full left branch then deal the left side
        if node.left and not node.left.isFullNode():
            node = node.left

        # fill what is needed
        if (not node.right and not node.left) or node.left:
            node.right = Node(data=query[0])
        elif node.right:
            node.left = Node(data=query[0])
        return mainNode


invertedIndex = InvertedIndex()
print(invertedIndex)
