import sys
from sendMessages import printParent
from sendMessages import messageParent
from sendMessages import obviousPrint

import concat
import minMax
import imputingMissingValues

# grab arguments
trainingFile = sys.argv[1]
testingFile = sys.argv[2]
test = sys.argv[3]

concattedResults = concat.inputFiles(trainingFile, testingFile)

# we are identifying whether each column is "output","id","categorical", or "continuous"
dataDescription = [x.lower() for x in concattedResults[0]]
headerRow = [x.lower() for x in concattedResults[1]]
trainingLength = concattedResults[2]
allData = concattedResults[3]

if(test):
    messageParent([dataDescription, headerRow, trainingLength, allData], 'concat.py')


imputedResults = imputingMissingValues.cleanAll(dataDescription, trainingLength, allData)

if(test):
    messageParent(imputedResults, 'imputingMissingValues.py')

# immediate next steps:
    # 1. update tests to handle categorical data
    # 2. make sure all the tests still pass...
    # 3. convert entire dataset to have categorical data encoded properly
        # ugly possibility: convert to dicts, then use dictvectorizer
    # 4. run training data through rfecv- fit_transform
        # make sure that rfecv is saved and written to file!
    # 5. run testing data through that same rfecv to make sure it's handled in the exact same way
    # 6. at this point, we are ready to start considering specific formatting (min-max, brain.js, and sci-kit learn)


minMaxNormalizedResults = minMax.normalize(dataDescription, imputedResults)

if(test):
    messageParent(minMaxNormalizedResults, 'minMax.py')

