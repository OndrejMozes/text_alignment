import math
import sys

vowels = {"a","e","i","o","u","y","á","é","ě","í","ó","ů","ú","ý",
          "A","E","I","O","U","Y","Á","É","Ě","Í","Ó","Ů","Ú","Ý"}
lr = {"l","r",
      "L","R"}
consonants = {"b", "c", "č", "d", "ď", "f", "g", "h", "j", "k", "l", "m", "n", "ň", "p", "q", "r", "ř", "s", "š", "t", "ť", "v", "w", "x", "z", "ž", "ch",
              "B", "C", "Č", "D", "Ď", "F", "G", "H", "J", "K", "L", "M", "N", "Ň", "P", "Q", "R", "Ř", "S", "Š", "T", "Ť", "V", "W", "X", "Z", "Ž", "Ch",}
# global variables
formatting = None
input = None
output = None
readWordBuffer = None #The input file is read in lines, while the line is being processed it is stored here
lastWordBuffer = None #Words that could not fit into a block are stored here to be put into the next block

#Run the program with formatting f, input i and output o
def Run(f, i, o):
    OpenFiles(f, i, o)
    formattingMode = formatting.readline()[:-1]
    if formattingMode == "block":
        BlockAlign()
    elif formattingMode == "mask":
        MaskAlign(o)
    else:
        print("Incorrect formatting")
        return        
    CloseFiles()

#Opens the formatting, input and output files as f, i and o respectively
def OpenFiles(f, i, o):
    global formatting
    global input
    global output
    formatting = open(f, 'r', encoding='utf-8')
    input = open(i, 'r', encoding='utf-8')
    output = open(o, 'w', encoding='utf-8')

#Closes the formatting, input and output files
def CloseFiles():
    global formatting
    global input
    global output

    formatting.close()
    input.close()
    output.close()

#Write the input text aligned into blocks of sizes denoted in the formatting file to the output file
def BlockAlign():
    splitLine = ""
    for line in formatting:
        splitLine = line.split()
        for i in range(0,int(splitLine[0])):
            foo = WriteAllignedBlock(int(splitLine[1]), int(splitLine[1]), True)
            if foo == False:
                break
            output.write('\n')
    foo = WriteAllignedBlock(int(splitLine[1]), int(splitLine[1]), True)
    while foo != False:
        output.write('\n')
        foo = WriteAllignedBlock(int(splitLine[1]), int(splitLine[1]), True)

#Write the input text distributed among blocks denoted by Xs in the format file with spaces denoted by Os
def MaskAlign(o):
    blockSize = math.floor(InputWordsLen()/FormattingXCount())
    inputFileNotFinished = True
    global output

    while inputFileNotFinished:
        blockSize = blockSize + 1 # we're okay with increasing the blocksize at the begginning to account for - at the end of split words
        ResetFilesForMaskAlign(o)

        for line in formatting:
            XBuffer = 0
            for char in line:
                if char == 'O':
                    if XBuffer > 0:
                        #the blocksize is increased to account for the -, but we only want one extra space for every block,
                        #for blocks that are multiple blockSize wide, we don't want the extra space for every X in Xbuffer, we only want one extra
                        inputFileNotFinished = WriteAllignedBlock(int(XBuffer*blockSize) - (XBuffer - 1),int(XBuffer*blockSize), False)
                        if not inputFileNotFinished:
                            return
                    WriteNSpaces(blockSize)
                    XBuffer = 0
                elif char == 'X':
                    XBuffer += 1
            if XBuffer > 0:
                #the blocksize is increased to account for the -, but we only want one extra space for every block,
                #for blocks that are multiple blockSize wide, we don't want the extra space for every X in Xbuffer, we only want one extra
                inputFileNotFinished = WriteAllignedBlock(int(XBuffer*blockSize) - (XBuffer - 1),int(XBuffer*blockSize), False)
                if not inputFileNotFinished:
                    return
            output.write('\n') 

#Returns the length of all words in the input file (+ 1 per word for separating words)
def InputWordsLen():
    count = 0
    word = ReadWord()
    while word != False:
        count += len(word) + 1 # at least one space between words
        word = ReadWord()
    return count - 1 # no space after last word

#Returns the total number of Xs in the formatting file
def FormattingXCount():
    count = 0
    line = formatting.readline()
    while len(line) != 0:
        count += line.count('X')
        line = formatting.readline()
    return count

#Seeks input and formatting files back to the start and clears the output file
def ResetFilesForMaskAlign(o):
    global formatting
    global input
    global output
    global readWordBuffer
    global lastWordBuffer
    readWordBuffer = None
    lastWordBuffer = None

    formatting.seek(0)
    input.seek(0)
    formatting.readline() #We already know we are doing mask align, we don't want to read the first line again
    output.close()
    open(o, 'w').close()
    output = open(o, 'w', encoding='utf-8')

#Writes n spaces to the output file
def WriteNSpaces(n):
    for i in range(0,n):
        output.write(" ")

#Returns the next word from the input file. Returns false if the whole input file has already been read
def ReadWord():
    global readWordBuffer
    if readWordBuffer == None or len(readWordBuffer) == 0:
        while True:
            unsplitLine = input.readline()
            if len(unsplitLine) == 0:
                return False
            else:
                unsplitLine = unsplitLine.strip()
                if len(unsplitLine) != 0:
                    readWordBuffer = unsplitLine.split()
                    break    
    return readWordBuffer.pop(0)

#Returns the word split into two parts as a list, the first part being up to cutoffLength long, returns false if splitting failed
def SplitWord(word, cutoffLength):
    splitIndex = GetSplitWordIndex(word,cutoffLength - 1)# -1 to account for - used to denote the splitting of a word
    if splitIndex == 0:
        return False
    splitWordList = [word[:splitIndex] + '-', word[splitIndex:]]
    return splitWordList

#Returns the index of the first character of the second part of the word. See documentation for the rules used to split words
def GetSplitWordIndex(word, cutoffLength):
    syllableIndex = 0
    
    for i in range (0, len(word) - 1):
        if word[i] in vowels or (i>0 and word[i-1] in consonants and word[i] in lr):
            if i < len(word)-2 and word[i+1] in consonants:
                if (word[i+1] == 'c' or word[i+1] == 'C') and (word[i+2] == 'h' or word[i+2] == 'H'):
                    if (i < len(word)-3 and word[i+3] in vowels) or (i<len(word)-4 and word[i+4] in consonants and word[i+3] in lr):
                        if i+1 <= cutoffLength:
                            syllableIndex = i+1
                else:
                    if i < len(word)-2 and word[i+2] in vowels or (i<len(word)-3 and word[i+3] in consonants and word[i+2] in lr):
                        if i+1 <= cutoffLength:
                            syllableIndex = i+1
        elif word[i] in consonants:
            if (i>0 and word[i-1] in vowels) or (i>1 and word[i-2] in consonants and word[i-1] in lr):
                if i < len(word)-2 and word[i+1] in consonants and not(i < len(word)-1 and word[i+1] in lr and word[i+2] in consonants):
                    for x in range(i+2, len(word)):
                        if i + math.floor((x-i)/2) <= cutoffLength and (word[x] in vowels or (x < len(word)-1 and word[x] in lr and word[x+1] in consonants)):
                            foo = int(i + (math.floor(x-i)/2))
                            if (word[foo-1] == 'c' or word[foo-1] == 'C') and (word[foo] == 'h' or word[foo]=='H'):
                                if foo + 1 <= cutoffLength:
                                    syllableIndex = foo + 1
                            else:
                                syllableIndex = foo
                            break
    return syllableIndex    

#Writes a block of size blocksize with at most maxWordLength non-white characters to the output file block aligned.
#If alignLastBlockLeft is true, the last block written to the output file will be aligned left instead of block aligned
#Returns false if the final block has been written
def WriteAllignedBlock(maxWordsLength, blockSize, alignLastBlockLeft):
    if maxWordsLength > blockSize:
        raise ValueError

    global lastWordBuffer
    words = []
    wordsLength = 0
    lastLine = False

    while True:
        if lastWordBuffer == None:
            word = ReadWord()
        else:
            word = lastWordBuffer

        if word == False:
            lastLine = True
            break

        if wordsLength + len(words) + len(word) <= maxWordsLength:
            words.append(word)
            wordsLength += len(word)
            lastWordBuffer = None
        else:
            splitWord = SplitWord(word, maxWordsLength - wordsLength - len(words))
            if splitWord == False:
                if len(words) == 0:
                    output.write(word)
                    lastWordBuffer = None
                    return True
                else:
                    lastWordBuffer = word
            else:
                words.append(splitWord[0])
                wordsLength += len(splitWord[0])
                lastWordBuffer = splitWord[1]
            break
    if lastLine and alignLastBlockLeft:
        if len(words)>0:
            for i in range(0, len(words)-1):
                output.write(words[i])
                output.write(" ")
            output.write(words[len(words) - 1])
            return False
        else:
            return False
    else:
        if len(words)>1:
            numOfSpacesBetweenAllWords = math.floor((blockSize - wordsLength)/(len(words) - 1))
        elif len(words) == 1:
            numOfSpacesBetweenAllWords = 0
        else:
            return False
        for i in range(0,len(words) - 1):
            output.write(words[i])
            for x in range(0, numOfSpacesBetweenAllWords):
                output.write(" ")
            if i < blockSize - wordsLength - numOfSpacesBetweenAllWords * (len(words) - 1):
                output.write(" ")
        output.write(words[len(words) - 1])
        if len(words) == 1:
            WriteNSpaces(blockSize - len(words[len(words) - 1]))
    if lastLine:
        return False
    else:
        return True



def RunDemo():
    Run("Demo1F.txt", "Demo1I.txt", "Demo1O.txt")
    Run("Demo2F.txt", "Demo2I.txt", "Demo2O.txt")
    Run("Demo3F.txt", "Demo3I.txt", "Demo3O.txt")





#RunDemo()


Run(sys.argv[1], sys.argv[2], sys.argv[3])


