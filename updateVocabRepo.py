import pandas as pd
import os

# The key uniqueness is in the wordFrench column, so it's not possible to have two entries with the same French word.

# Keeps asking the user for new register entries, and updates "registerFILE" with the new entries,
# until the user enters the $ character.

# The register is a csv file with the following columns:
# wordFrench, wordEnglish, wordPortuguese,
# nDaysReviewed, nDaysLastReview,
# nDaysCorrect, nDaysLastCorrect,

# The 3 first columns are the words in French, English and Portuguese, requested from user
# All the other columns are automatically updated by the program (vocab.py), but initially they are all 0 (in this file, updateVocabRepo.py)

vocabColumns = ('wordFrench', 'wordEnglish', 'wordPortuguese') #, 'nDaysReviewed', 'nDaysLastReview', 'nTimesCorrect', 'nTimesReviewCorrect', 'ReviewBag') 
statsColumns = ('nDaysReviewed', 'nDaysLastReview', 'nTimesCorrect', 'nTimesReviewCorrect', 'ReviewBag')
word = ["", "", ""]

fileName = 'defaultWords.csv' 
settings = "settings.csv"

allCSVFiles = [fileName, settings]
allConfigFiles = []

# Check all files in this directory
allFilesDir = os.listdir()

for file in allFilesDir:
    if file[-4:] == ".csv" and file not in allCSVFiles:
        allConfigFiles.append(file)

# print(allConfigFiles)

# registerFILE = pd.read_csv(fileName, index_col=0)

# Explains to the user the code:
print("This program will ask you for new register entries, and update the file", fileName, "with the new entries.")
print("Type $, in the French word field, to stop.\n")

while True: 
    
    word[0] = input("French word/expression: ")
    if word[0] == "$":
        break
    word[1] = input("English word/expression: ")
    word[2] = input("Portuguese word/expression: ")

    # Shows the new register entry
    print("New register entry: ", word)

    # Asks if it's right, and if it's not, doesn't update the register
    answer = input("Is this right? (y/n) ")

    if answer == "y":

        newVocabRegister = pd.DataFrame([word], columns=vocabColumns)
        newVocabRegister.to_csv(fileName, mode='a', header=False, index = False)
        
        print("Register updated.\n")

        for file in allConfigFiles:

            newVocabStats = pd.DataFrame.from_dict({
                'nDaysReviewed':[0], 
                'nDaysLastReview':[0], 
                'nTimesCorrect':[0], 
                'nTimesReviewCorrect':[0],
                'ReviewBag':[0]
            })

            newVocabStats.to_csv(file, mode='a', header=False, index = False)
        
        print("Stats updated on all files.\n")

    else:
        print("Register not updated.\n")
        continue
