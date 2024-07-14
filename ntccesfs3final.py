##  ---------------------- FUNCS ---------------------------


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import string
import time
from tkinter import *

spam_df = pd.read_csv('spam.csv', encoding="ISO-8859-1")

#subset and rename columns
spam_df = spam_df[['v1', 'v2']]
spam_df.rename(columns={'v1': 'spam', 'v2': 'text'}, inplace=True)

#convert spam column to binary
spam_df.spam = spam_df.spam.apply(lambda s: True if s=='spam' else False)

#lowercase everything and remove punctuation
spam_df.text = spam_df.text.apply(lambda t: t.lower().translate(str.maketrans('', '', string.punctuation)))

#shuffle
spam_df = spam_df.sample(frac=1)

#TESTING
#for t in spam_df[spam_df.spam == True].iloc[:5].text:
#    print(t)
#    print('-------')

    
#get training set
train_spam_df = spam_df.iloc[:int(len(spam_df)*0.7)]

#get testing set
test_spam_df = spam_df.iloc[int(len(spam_df)*0.7):]
FRAC_SPAM_TEXTS = train_spam_df.spam.mean()
#TESTING
#print(FRAC_SPAM_TEXTS)                                  


#get all words from spam and non-spam datasets
train_spam_words = ' '.join(train_spam_df[train_spam_df.spam == True].text).split(' ')
train_non_spam_words = ' '.join(train_spam_df[train_spam_df.spam == False].text).split(' ')

common_words = set(train_spam_words).intersection(set(train_non_spam_words))
train_spam_bow = dict()
for w in common_words:
    train_spam_bow[w] = train_spam_words.count(w) / len(train_spam_words)
train_non_spam_bow = dict()
for w in common_words:
    train_non_spam_bow[w] = train_non_spam_words.count(w) / len(train_non_spam_words)



def predict_text(t):
    #if some word doesnt appear in either spam or non-spam BOW, disregard it
    valid_words = [w for w in t if w in train_spam_bow]
    
    #get the probabilities of each valid word showing up in spam and non-spam BOW
    spam_probs = [train_spam_bow[w] for w in valid_words]
    non_spam_probs = [train_non_spam_bow[w] for w in valid_words]
    
    #PROBS
    global data_df
    data_df = pd.DataFrame()
    data_df['word'] = valid_words
    data_df['spam_prob'] = spam_probs
    data_df['non_spam_prob'] = non_spam_probs
    data_df['ratio'] = [s/n if n > 0 else np.inf for s,n in zip(spam_probs, non_spam_probs)]
    #print(data_df)   FOR TESTING ONLY, Has been printed later on in window
     
    #calculate spam score as sum of logs for all probabilities
    global spam_score
    spam_score = sum([np.log(p) for p in spam_probs]) + np.log(FRAC_SPAM_TEXTS)
    
    #calculate non-spam score as sum of logs for all probabilities
    global non_spam_score
    non_spam_score = sum([np.log(p) for p in non_spam_probs]) + np.log(1-FRAC_SPAM_TEXTS)
    
    #if verbose, report the two scores
    #if verbose:
        #print('Spam Score: %s'%spam_score)
        #print('Non-Spam Score: %s'%non_spam_score)
   
    #if spam score is higher, mark this as spam
    global result
    if spam_score >= non_spam_score:
        result = "SPAM"
    else:
        result = "NOT SPAM"
    # print("\nMail detected as " + result)

#########################################################################
#                                 MAIN                                  #
#########################################################################

root = Tk()
root.title("EMAIL SPAM FILTERING SYSTEM")

heading  = Label(root, text = "Email Spam Checker", font = ("Helvetica", 25))
heading.grid(row = 0, column = 1, pady = 50)
subtext = Label(root, text="Enter Mail to be checked below:")
subtext.grid(row = 1, column = 0, pady = 20)

def checkcommand():
    subject = textbar.get()
    predict_text(subject.split())
    resultLabel = Label(root, text="DETECTED AS "+result)
    resultLabel.grid(row = 5, column = 1) #--------------------
    global executed
    executed = True
    x = checkboxvar.get()
    if x == 1:
        computationcommand()

def computationcommand():
    if executed == True:
        computationlabel = Label(root, text=data_df)
        computationlabel.grid(row = 6, column = 1, columnspan = 1)
        computationlabel2 = Label(root, text="SPAM SCORE= {}".format(spam_score))
        computationlabel2.grid(row = 7, column = 1, columnspan = 1)
        computationlabel3 = Label(root, text="NON SPAM SCORE= {}".format(non_spam_score))
        computationlabel3.grid(row = 8, column = 1, columnspan = 1)
        
def resetcommand():
    textbar.delete(0,END)

textbar = Entry(root, width = 100)
textbar.grid(row = 2, column = 0, columnspan = 3)

resetbutton = Button(root, text = "Reset", command = resetcommand)
resetbutton.grid(row = 2, column=3)

checkbutton = Button(root, text = "Check for spam", padx = 10, pady = 5, command  = checkcommand)
checkbutton.grid(row = 3, column = 1)

checkboxvar = IntVar()
computationcheckbox = Checkbutton(root, text = "Show computation", variable= checkboxvar)
computationcheckbox.grid(row = 4, column = 1)

# computationbutton = Button(root, text = "Show computation", command = computationcommand)
# computationbutton.grid(row = 4, column = 1)

exitbutton = Button(root, text= "End Program", command = root.quit)
exitbutton.grid(row = 4, column = 3)

root.mainloop()
