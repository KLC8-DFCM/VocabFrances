import pandas as pd
import numpy as np
import random
from datetime import date, datetime
from dateutil import relativedelta
import os
import scipy
from colorama import Fore

# Register : 

# wordFrench, wordEnglish, wordPortuguese, 
# nDaysReviewed, nDaysLastReview,
# nDaysCorrect, nDaysLastCorrect,

# Configs :

# probRessample, minAmountTransfer, maxAmountRetransfer

wordsFile = "defaultWords.csv"

'''
DEFAULT_SETTINGS = {
    'vocabFile': 'defaultWords.csv',
    # 'initialDate': '07/01/2024', # Bom, demorou um pouco ...
    'initialDate': '06/03/2024',
    'trainingType': 'Portuguese2French', # Random2French, French2Random, French2Portuguese, Portuguese2French, French2English, English2French  
    'probRessample': 0.1,
    'minAmountTransfer': 7,
    'maxAmountRetransfer': 3
}
'''

trainingTypes = {
    'Random2French': {
        'sourceLanguage': 'Random',
        'targetLanguage': 'French'
    },
    'French2Random': {
        'sourceLanguage': 'French',
        'targetLanguage': 'Random'
    },
    'French2Portuguese': {
        'sourceLanguage': 'French',
        'targetLanguage': 'Portuguese'
    },
    'Portuguese2French': {
        'sourceLanguage': 'Portuguese',
        'targetLanguage': 'French'
    },
    'French2English': {
        'sourceLanguage': 'French',
        'targetLanguage': 'English'
    },
    'English2French': {
        'sourceLanguage': 'English',
        'targetLanguage': 'French'
    }
}

trainingTypesEnum = {
    0 : 'Random2French',
    1 : 'French2Random',
    2 : 'French2Portuguese',
    3 : 'Portuguese2French',
    4 : 'French2English',
    5 : 'English2French'
}

langEnum = [
    'French',
    'English',
    'Portuguese'
]

colorMap = {
    'French': Fore.BLUE,
    'English': Fore.RED,
    'Portuguese': Fore.YELLOW
}

allSettings = None
currSettingsIndex = None

def get_settings():
    
    global allSettings
    global currSettingsIndex
    
    allSettings = pd.read_csv('settings.csv', sep=',') 

    # Ask the user if it wants to use the default settings
    print(allSettings, '\n')

    currSettingsIndex = input('What settings do you want to use ?(return an index) ')

    currSettings = allSettings.iloc[int(currSettingsIndex)]
    
    print('Settings: ', currSettings, '\n')

    return currSettings


# Valores de nDaysReviewed e nTimesReviewCorrect são somente incrementados, para manter
# o fator de "recall" historicamente preservado, mesmo que a palavra fique indo e 
# voltando entre os estados de revisão e não revisão (softmax(nDaysLastReview * (1 - fator)))
# sendo fator = nTimesReviewCorrect/(1 + nDaysReviewed)
def update_data(data, word, answer, settings):
    
    # Talvez deixar so o update msm
    # if word['ReviewBag'] == 0:
    if data['stats'][data['words']['wordFrench'] == word['wordFrench']]['ReviewBag'].values[0] == 0:
        if answer:
            data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'],'nTimesCorrect'] += 1
            # print(data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'], 'nTimesCorrect'])
            # print("AQUI subiu 1")

        if data['stats'][data['words']['wordFrench'] == word['wordFrench']]['nTimesCorrect'].values[0] >= settings['minAmountTransfer']:
            data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'], 'ReviewBag'] = 1
            data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'], 'nDaysLastReview'] = 0
    else:

        data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'], 'nDaysReviewed'] += 1
        
        # Não é pedante essa variável com relação à última pois esta
        # é atualizada a cada dia diferente
        data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'], 'nDaysLastReview'] = 0

        if answer:
            data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'], 'nTimesReviewCorrect'] += 1
        
        if data['stats'][data['words']['wordFrench'] == word['wordFrench']]['nTimesReviewCorrect'].values[0] >= settings['maxAmountRetransfer']:
            data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'], 'ReviewBag'] = 0
            data['stats'].loc[data['words']['wordFrench'] == word['wordFrench'], 'nTimesCorrect'] = 0
            # As outras variáveis são mantidas como estão, para manter algo como um histórico minimamente decente

def init_data(data, word, settings):

    # Stored date format: dd/mm/yyyy
    # settings['initialDate'] = 'dd/mm/yyyy'
    init_date = datetime.strptime(settings['lastDate'], '%d/%m/%Y')
    curr_date = date.today()

    diff = relativedelta.relativedelta(curr_date, init_date).days

    if diff > 0:
        # Esta certo pois a maquina de estados, interna, da parte toda de como
        # trata-se o acerto (ou nao) da palavra, é que vai zerar o contador
        data['stats'].loc[data['stats']['ReviewBag'].isin([1]), 'nDaysLastReview'] += diff

    return data

def load_data(settings):
    return {
            'words': pd.read_csv(wordsFile, sep=','),
            'stats': pd.read_csv(settings['vocabTrainFile'] + '.csv', sep=',')
            }

def getProb(inBagData):

    # print(inBagData)

    nDaysLastReviews = np.array(inBagData['nDaysLastReview'])
    # print(nDaysLastReviews)

    nTimesReviewCorrect = np.array(inBagData['nTimesReviewCorrect'])
    # print(nTimesReviewCorrect)

    nDaysReviewed = np.array(inBagData['nDaysReviewed'])

    logLikelihood = nDaysLastReviews * (1 - nTimesReviewCorrect/(1 + nDaysReviewed))
    # print(logLikelihood)


    return scipy.special.softmax(
        logLikelihood
    )


def get_word(data, settings):

    # Sample value from uniform distribution, from 0 to 1
    sample_source = np.random.uniform()

    word = None

    inBagWords = data['words'][data['stats']['ReviewBag'] == 1]
    size= len(inBagWords)

    if sample_source <= settings['probRessample'] and size> 0 : # ReviewBag
        
        inBagStats = data['stats'][data['stats']['ReviewBag'] == 1]
        probs = getProb(inBagStats)
        
        indexSampled = np.random.choice(size, p=probs)

        word = inBagStats.iloc[indexSampled]
        
    else:
        
        outOfBag = data['words'][data['stats']['ReviewBag'] == 0]

        size = len(outOfBag)

        sampleOutOfBag = np.random.uniform(low = 0, high = size)
        indexSampled = int(np.floor(sampleOutOfBag))
        # print(indexSampled)
        
        word = outOfBag.iloc[indexSampled]
        # print(outOfBag.iloc[indexSampled])

    return word

def ask_word(word, settings):
    
    trainingNow = trainingTypes[settings['trainingType']]
    
    sourceLang = trainingNow['sourceLanguage'] 
    indexSrc = None

    targetLang = trainingNow['targetLanguage'] 
    indexTarget = None

    if sourceLang == 'Random':

        langSrcProbs = np.random.binomial(n=1,p=0.5)

        indexTarget = 1 + langEnum.index(targetLang)
        indexSrc = (indexTarget+langSrcProbs) % 3
    else:
        indexSrc = langEnum.index(sourceLang)
    
    if targetLang == 'Random':

        langTargetProbs = np.random.binomial(n=1,p=0.5)

        indexSrc = 1 + langEnum.index(sourceLang)
        indexTarget = (indexSrc +langTargetProbs) % 3            
    else:
        indexTarget = langEnum.index(targetLang)

    question = word['word' + langEnum[indexSrc]]
    expectedAnswer = word['word' + langEnum[indexTarget]]

    prompt = f'How would you say {colorMap[langEnum[indexSrc]]}' + question + f'{Fore.RESET}' f' in {colorMap[langEnum[indexTarget]]}' + langEnum[indexTarget] + f'{Fore.RESET} ?\n'
    answer = input(prompt)
    print()

    correctAnswer = (answer == expectedAnswer)

    if not correctAnswer:
        print('Expected answer : ' + f"{colorMap[langEnum[indexTarget]]}" + expectedAnswer + f'{Fore.RESET}\n')

    return correctAnswer

def stop(data, settings):
    return input('Next word ? (y/n) ') == 'n'

def save_data(data, settings):

    # Update the last date in the settings file 
    settings.loc['lastDate'] = date.today().strftime('%d/%m/%Y')
    allSettings.iloc[int(currSettingsIndex)] = settings
    allSettings.to_csv('settings.csv', index=False)

    # Save the data in the training file
    data['stats'].to_csv(settings['vocabTrainFile'] + '.csv', index=False)
    

def main():

    # Variables needed to make the logic work 
    answer = None 
    word = None 

    # Get train settings
    settings = get_settings()

    # Load data
    data = load_data(settings)

    # Init data
    data = init_data(data, word, settings)

    # Start loop
    while True:

        # Get word
        word = get_word(data, settings)
        # print(word, '\n')

        # Ask word
        correctAnswer = ask_word(word, settings)
        # print(correctAnswer)

        # Update data
        update_data(data, word, correctAnswer, settings)

        # Check if stop
        if stop(data, settings):
            break
    
    # Save data
    save_data(data, settings)

main()