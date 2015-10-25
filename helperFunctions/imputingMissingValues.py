from sklearn import preprocessing
import numpy as np

from sendMessages import printParent
from sendMessages import messageParent
from sendMessages import obviousPrint

emptyEquivalents = ["na","n/a","none",'',"","undefined","missing","blank","empty", None]

# standardizes all missing values to None
# removes all strings (values that can't be converted to a float) from "Numerical" columns
# removes all values in the emptyEquivalents array from categorical columns
# doesn't touch ID or Output columns
def standardizeMissingValues(dataDescription, matrix ):
    cleanedColumnMatrix = []
    columnsWithMissingValues = {}

    # split data into columns
    columns = zip(*matrix)

    # iterate through the columns. for each one:
    for idx, column in enumerate(columns):
        cleanColumn = []

        # check and see if it is a continuous field
        if dataDescription[idx] == "continuous":

            for num in column:
                try:
                    # if it is continuous, try to convert each field to a float
                    cleanColumn.append( float( num ) )
                except:
                    # remove all non-numerical values
                    cleanColumn.append( None )
                    # and keep track of this column as having msising values
                    columnsWithMissingValues[idx] = True

        elif dataDescription[idx] == "categorical":
            # if it's categorical
            for value in column:
                if str(value).lower() in emptyEquivalents:
                    # replace all values we have defined above as being equivalent to a missing value with the standardized version the inputer will recognize next: np.nan
                    cleanColumn.append( None )
                    # and keep track of this column as having msising values
                    columnsWithMissingValues[idx] = True
                
                else:
                    cleanColumn.append(value)

        cleanedColumnMatrix.append( cleanColumn )

    return [ cleanedColumnMatrix, columnsWithMissingValues ]


# TODO TODO: reorder these functions
    # calculate the fillInVals first, in it's own function
    # then, for each value in fillInVals that is not None, create the missing columns in it's own function
    # then, impute the missing values in it's own function
def calculateReplacementValues( columnMatrix, columnsWithMissingValues, dataDescription ):

    # fillInVals will have keys for each column index, and values for what the filled in value should be
        # this way we only need to check continuous or categorical once
    fillInVals = {}
    # for colIndex, column in enumerate(columnMatrix):
        # do this only for columns with missing values
    for colIndex in columnsWithMissingValues:
        try:
            # we have a string in our columnsWithMissingValues obj (countOfMissingValues), so we need to try to convert it into an int to make sure we're actually on a numerical key representing a column number
            colIndex = int( colIndex )
            if dataDescription[ colIndex ] == 'continuous':
            # Manually calculating the median value
            # the numpy way of doing this assumes that None is a number and includes it when calculating the median value
            # whereas we want the median of all the values other than None. 
                # copy the list
                copiedList = list( columnMatrix[ colIndex ])
                # sort the list
                copiedList.sort(reverse=True)
                # find the index of None
                for rowIndex, value in enumerate(copiedList):
                    if value == None:
                        noneIndex = rowIndex
                        break
                        # TODO: delete the copied list
                # divide that number in half (make it an int)
                medianIndex = int( noneIndex / 2 )
                # access that position in the copied & sorted list
                medianVal = copiedList[ medianIndex ]
                # store that number into fillInVals
                fillInVals[ colIndex ] = medianVal
                # TODO: delete that sorted/copied list

            elif dataDescription[ colIndex ] == 'categorical':
                column = columnMatrix[ colIndex ]
                # the mode value
                fillInVals[ colIndex ] = max(set(column), key=column.count)
        except: 
            pass
            printParent('we failed to create a fillInVals value for this key')
            printParent(colIndex)

    # remove all values of None from fillInVals
    # this way we will only create imputed columns if we can replace missing values in that column with something useful
    fillInVals = { k: v for k, v in fillInVals.items() if v is not None}

    printParent('fillInVals')
    printParent(fillInVals)
    return fillInVals


def createImputedColumns( columnMatrix, dataDescription, columnsWithMissingValues, headerRow ):
    # we want to keep track of the total number of imputed values for each row
    # but it only makes sense to have a total column if we have more than 1 column with missing values
    # we can probably get rid of this with robust feature selection
    if( len( columnsWithMissingValues.keys() ) > 1 ):
        # create a new empty list that is filled with blank values (None) that is the length of a standard column
        emptyList = [ 0 ] * len( columnMatrix[0] )
        columnMatrix.append( emptyList )
        # keep track of this new column in our headerRow and our dataDescription row
        dataDescription.append( 'Continuous' )
        headerRow.append( 'countOfMissingValues' )
        # keep track of where this new column is
        columnsWithMissingValues[ 'countOfMissingValues' ] = len(headerRow) - 1
    
    for colIndex in columnsWithMissingValues:
        try:
            # we have countOfMissingValues as a key in columnsWithMissingValues, so we need to skip over that
            colIndex = int(colIndex)
            # create a copy of the existing column and append it to the end. this way we can modify one column, but leave the other untouched
            newColumn = list( columnMatrix[ colIndex ])
            columnMatrix.append( newColumn )

            # include prettyNames for dataDescription and header row
            dataDescription.append( dataDescription[colIndex] ) 
            headerRow.append( 'imputedValues' + headerRow[ colIndex ] )

            # we now have a map between the original (untouched) column index, and the new cloned (with imputed values) column index
            columnsWithMissingValues[ colIndex ] = len( headerRow ) -1

            # create a new empty column to hold information on whether this row has an imputed value for the current column
            emptyList = [ 0 ] * len( columnMatrix[0] )
            columnMatrix.append( emptyList )
            # keep track of this new column in our headerRow and our dataDescription row
            dataDescription.append( 'Continuous' )
            headerRow.append( 'missing' + headerRow[ colIndex ] )
        except:
            pass

    return [ columnMatrix, dataDescription, columnsWithMissingValues, headerRow ]


def impute( columnMatrix, dataDescription, colMap ):
    # we have one column dedicated just to holding the count of the total number of missing values for this row
    countOfMissingValsColIndex = colMap[ 'countOfMissingValues' ]

    # NOT TODO:
        # remove any imputedValues columns that might hold None values
            # this happens when the median or mode value for that column is None, i.e., when we are just missing TONS of data
        # 1. remove the imputedValuesCOLNAME and missingCOLNAME columns
        # 2. adjust indices in colMap
            # iterate through the keys of colMap. for each one:
                # if the value is greater than the index of the column we are deleting
                    # reduce that value by 2 (one for the imputedValuesCOLNAME column and one for the missingCOLNAME column)
        # 3. see if we still need countOfMissingValues column
            # if not
                # delete that column
                # reduce indices of all relevant values in colMap, similarly to what we did for the previous removal step

    for colIndex, column in enumerate(columnMatrix):
        if dataDescription[ colIndex ] == 'categorical':
            isCategorical = True
        else:
            isCategorical = False
        # iterate through columns list, starting at the index position of the new columns
        try:
            # check to make sure this colIndex is indeed a cloned column with missing values (not a column holding a boolean flag for whether a missing value was found)
            # find the column where we are going to store the imputed values for this column
            # if this column is not one of the columns we've identified earlier as having missing values, this will throw an error and exit the try statement
            imputedColIndex = colMap[ colIndex ]
            # if so
            for rowIndex, value in enumerate(column):
                # iterate through list, with rowIndex
                # for each item:
                # check for missing values. if they exist:
                if value == None:

                    # there are several components we must balance here:
                        # np.median does not like columns with mixed values (numbers and strings)
                        # the random forest classifier does not appear to like None or nan
                        # and of course, we need to clean the input (no strings in numerical columns, have a reliable missingValues value we can look for, etc.)
                    # we need to remove all np.nan from our input, otherwise the classifier fails later on. 
                    columnMatrix[ colIndex ][ rowIndex ] = "NA"


                    # replace missing value in the imputedColumn we have appended at the right-hand side of the dataset for each column with missing values
                    # replace it for this row that we are iterating over
                    # replace it with the previously calculated value for this column
                    columnMatrix[ imputedColIndex ][ rowIndex ] = fillInVals[ colIndex ]
                    # find the flag column for this column in colMap dictionary
                        # it is just one over from the imputedColumn
                        # set that value equal to 1
                    columnMatrix[ imputedColIndex + 1 ][ rowIndex ] = 1
                    # find the column holding the count of all missing values for that row
                        # increment that value by 1
                    columnMatrix[ countOfMissingValsColIndex ][ rowIndex ] += 1

        except:
            pass
            # if this is not a column we've previously identified as having missing values, do nothing
    return columnMatrix


# cleanAll is the function that will be publicly invoked. 
# cleanAll defers to the standardize and impute functions above
def cleanAll(dataDescription, matrix, headerRow ):

    # standardize missing values to all be None
    standardizedResults = standardizeMissingValues(dataDescription, matrix)
    cleanedColumnMatrix = standardizedResults[ 0 ]
    columnsWithMissingValues = standardizedResults[ 1 ]

    # calculate the replacement values for columns that are missing values
    fillInVals = calculateReplacementValues( cleanedColumnMatrix, columnsWithMissingValues, dataDescription )

    # create the new columns for each column that has a missing value
    newColumnsResults = createImputedColumns( cleanedColumnMatrix, dataDescription, columnsWithMissingValues, headerRow )

    # store results from creating the imputed columns
    cleanedColumnMatrix = newColumnsResults[ 0 ]
    dataDescription = newColumnsResults[ 1 ]
    columnsWithMissingValues = newColumnsResults[ 2 ]
    headerRow = newColumnsResults[ 3 ]

    # impute the missing values and boolean flags for the newly copied columns
    cleanedColumnMatrix = impute( cleanedColumnMatrix, dataDescription, columnsWithMissingValues )

    # turn back into a row matrix from a column matrix
    cleanedRowMatrix = zip(*cleanedColumnMatrix)

    # return all the new values (X, dataDescription, headerRow)
        # since we are adding on new columns, we have modified the dataDescription and headerRow variables
    return [ cleanedRowMatrix, dataDescription, headerRow ]
