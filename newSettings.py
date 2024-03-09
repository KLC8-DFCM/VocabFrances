import pandas as pd
from datetime import date

vocabFile = 'defaultWords.csv'

trainingTypesEnum = {
    0 : 'Random2French',
    1 : 'French2Random',
    2 : 'French2Portuguese',
    3 : 'Portuguese2French',
    4 : 'French2English',
    5 : 'English2French'
}

print("Welcome to the settings configuration. Please answer the following questions to configure the settings for the training.\n")

newSettings = {}

newSettings['vocabTrainFile'] = input('Custom train file name? ')
newSettings['lastDate'] = date.today().strftime("%d/%m/%Y") 

print("Initial date is assumed to be today (", newSettings['lastDate'], ")\n")

print("Now select the training fashion")
print("Available training types: Random2French (0), French2Random (1), French2Portuguese (2), Portuguese2French (3), French2English (4), English2French (5) ")

newSettings['trainingType'] = trainingTypesEnum[int(input('Enter the training type: '))]
newSettings['probRessample'] = float(input('Enter the probability of ressample (between 0.0 and 1.0): '))
newSettings['minAmountTransfer'] = int(input('Enter the minimum amount of transfer to review bag: '))
newSettings['maxAmountRetransfer'] = int(input('Enter the maximum amount of retransfer (out of the review bag): '))

print("Settings configured. The new settings are: ", newSettings)

# Save settings to file
settings = pd.read_csv('settings.csv', sep=',')

# New line to append
newSettingsDf = pd.DataFrame([newSettings])
settings = pd.concat([settings, newSettingsDf])

# Save to file
settings.to_csv('settings.csv', index=False)

# Create a new vocab train file for the stats
vocab = pd.read_csv(vocabFile, sep=',')

# Create new dataframe for the stats, that will represent the tracking of the words in the training
vocabTrainFile = pd.DataFrame(columns=['nDaysReviewed','nDaysLastReview','nTimesCorrect','nTimesReviewCorrect','ReviewBag'])

# Create lots of empty lines, filled with 0, with the indexes taken from the vocab file
emptyLines = []
for i in range(0, vocab.shape[0]):
    newData = pd.DataFrame.from_dict(
        {
         'nDaysReviewed':[0], 
         'nDaysLastReview':[0], 
         'nTimesCorrect':[0], 
         'nTimesReviewCorrect':[0],
         'ReviewBag':[0]
         }
         )
    emptyLines.append(newData)
    # vocabTrainFile = vocabTrainFile.append(, ignore_index=True)

vocabTrainFile = pd.concat(emptyLines, ignore_index=True)
vocabTrainFile.to_csv(newSettings['vocabTrainFile'] + '.csv', index=False, sep=',')
