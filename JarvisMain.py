"""
This is Jarvis's Main Brain.
Site of  user settings and most important functions
"""
import speech_recognition as sr
import win32com.client as wincl
import pyttsx3
from googlesearch import search
from newspaper import Article
import mysql.connector as ms
import datetime
import keyring
import os
import random
from time import sleep
from itertools import cycle
import wikipedia
import webbrowser
import wolframalpha
import pickle
import JarvisVocab
import JarvisMusic


#  BASIC USER SETTINGS. EDIT AS REQUIRED
name = 'Achintya'
voice_id = 0                          # Sets the voice to be used by Jarvis
voice_rate = 200                      # Sets the rate for Jarvis's voice
text_input = True                     # Sets text/voice input mode
startup = '''\nJarvis: A Python AI-
Jarvis initialising'''

#  DO NOT EDIT THESE
wolfram_client = wolframalpha.Client('LUXTPQ-Q5E8Q8QTUL')
engine = pyttsx3.init()              # Audio engine initialisation
voices = engine.getProperty('voices')


#  Function definitions
#  Important senses
def listen_up():
    global text_input
    '''Speech Recognition function that uses Google Speech Recognition.
    Takes no attributes returns a string'''
    if text_input:
        print(name, '\b: ', end='')
        spoken = input()
        return spoken
    else:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print()
            audio = r.listen(source)

        try:
            spoken = r.recognize_google(audio)  # can set key = 'API KEY'
            print(name, ': ', spoken, sep='')
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio."
                  "You can type in your input: ")
            spoken = input()
        except sr.RequestError as e:
            print("Could not request results from GSR service; {0}".format(e))
            print("You can also type in your input: ")
            spoken = input()
        return spoken


def speak_out(text, end='\n', sep=' '):
    global voice_id
    global voice_rate
    global voices
    '''This function converts input text to speech
    using Microsoft Windows Speech Engine.
    Takes one string input, returns nothing.'''
    '''VOICE'''
    engine.setProperty('voice', voices[voice_id].id)   # id sets voice
    '''RATE'''
    engine.setProperty('rate', voice_rate)             # rate sets speed
    print('Jarvis: ' + text, end=end, sep=sep)
    engine.say(text)
    engine.runAndWait()


def iterate(seq, command):
    '''This function is used to process user Input. Takes two sequences of any type
    returns a list which has those elements of first sequence
    which are also in the second sequence
    '''
    match = [i for i in seq if i in command]
    return match


#  Beautifications
def load_type_dots():
    for i in range(3):
        print('.', flush=True, end='', sep='')
        sleep(0.7)
    print()


def load_type_rotate():
    for frame in cycle(r'-\|/-\|/'):
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.2)


#  Settings
def set_user_settings():
    '''This function is used to specify user details.
    Stores the data in 'user1.dat'.
    Details stored-
    name as name
    mysql_user as mysqluser
    mysql_pass as mysqlpass
    Takes no input, returns nothing.
    '''
    # Create new user data
    user = {}
    speak_out("If you'd like to access your MySQL databases and\
    \b\b\b\brun queries from within Jarvis, you must \
    \b\b\b\btell me your MySQL username and password.\
    \b\b\b\bType them in at the prompts. Would you like to proceed?")
    ans = listen_up()
    if ans in JarvisVocab.affirmative:
        speak_out("Great. So what's your username? ")
        mysql_user = input()
        speak_out("Enter your password: ")
        mysql_pass = input()
        keyring.set_password('mysql', mysql_user, mysql_pass)
        speak_out("I'll remember these when you next access MySQL")
        user['mysqluser'] = mysql_user
    else:
        speak_out('Alright that works too')
    with open('user.dat', 'wb') as user_file:
        pickle.dump(user, user_file)


def get_user_settings():
    global mysql_user, mysql_pass
    try:
        user_file = open('user.dat', 'rb')
        user = pickle.load(user_file)
        if not user:
            set_user_settings()
            user_file = open('user.dat', 'rb')
            user = pickle.load(user_file)
        mysql_user = user['mysqluser']
        mysql_pass = keyring.get_password('mysql', mysql_user)
        if not(mysql_pass):
            speak_out('Please enter your MySQL password')
            mysql_pass = input()
            keyring.set_password('mysql', mysql_user, mysql_pass)
    except FileNotFoundError:
        speak_out("Your settings file doesn't exist, let me create one for you")
        set_user_settings()


def settingsToggle(parameter):
    '''
    This is used to change voice_type, voice_rate and text_input
    for the current Jarvis session.
    It does not change the default values.
    To change default values, change the variables under #  USER SETTINGS
    at the beginning (line 27) of this file
    '''
    global voice_rate, voice_id, text_input
    speak_out("You would like to change " + parameter[0] + ". Correct?")
    ans = listen_up()
    if iterate(JarvisVocab.affirmative, ans):
        if parameter[0] == 'type':
            try:
                speak_out("What would you like to set the voice type to?")
                choice = listen_up()
                voice_id = int(choice)
                speak_out("This is my new voice.")
            except Exception:
                speak_out("That's not a valid input. "
                          "Voice Types can be 0, 1 or 2")

        elif parameter[0] == 'rate':
            try:
                speak_out("What would you like to set the voice rate to?")
                choice = listen_up()
                voice_rate = int(choice)
            except Exception as e:
                speak_out("That's not a valid input. "
                          "Voice rate must be a number, "
                          "100 represents the normal rate")
                print(e)
        else:
            if text_input:
                text_input = False
                speak_out("Text input is disabled")
            else:
                text_input = True
                speak_out("Text input is enabled")
    else:
        speak_out("Oops I must have misheard. Sorry")


#  MySQL related
def sqlquery_format(sqlQuery):
    global text_input
    if text_input:
        return sqlQuery
    sqlQuery.replace('asterix', '*')
    sqlQuery.replace('star', '*')
    sqlQuery.repalace('semicolon', ';')
    sqlQuery.replace('comma', ',')
    sqlQuery.replace('open bracket', '(')
    sqlQuery.replace('close bracket', ')')
    return sqlQuery


def mysqlConnectivity():
    '''
    Provided you have a working installation of mysql on your system,
    Jarvis can access it.
    Given credentials, they are stored with the user settings
    '''
    global userCursor, mysqlConnection, mysql_user, mysql_pass
    get_user_settings()
    try:
        mysqlConnection = ms.connect(host='localhost', user=mysql_user,
                                     passwd=mysql_pass)
        # mysqlConnection = ms.connect(host = 'localhost', user = 'root',
        #                              passwd = 'password')
    except Exception as e:
        speak_out('An error occured.')
        print(e)
    else:
        if mysqlConnection.is_connected():
            print('Say your queries just as you would in SQL, '
                  'omega exits MySQL')
            userCursor = mysqlConnection.cursor()
            runQuery()


def runQuery():
    speak_out('What is your query? ')
    query = listen_up()
    query = sqlquery_format(query)
    if query != 'omega':
        try:
            userCursor.execute(query)
            print(userCursor)
            data = userCursor.fetchall()
            if data == ['No result set to fetch from.']:
                print('Command executed')
            else:
                for row in data:
                    print(row)
        except Exception as e:
            print(e)
        runQuery()
    else:
        speak_out('Okay, closing MySQL Connection...')
        mysqlConnection.close()
        speak_out('Closed Succesfully')
        pass


#  Jarvis functions. When adding more functions, add here
def default_state():
    '''Default State of Jarvis.
    It returns to this state after every succesful execution of a command.
    It awaits input for the next command.'''
    speak_out("How can I help? ")
    command = listen_up()
    return command.lower()


def search_state(search_engine, search_query=''):
    if search_engine == '.com':
        print('Opening browser')
        webbrowser.get().open(search_query)
    elif search_query:
        try:
            results = wolfram_client.query(search_query)
            if results['@success'] == 'false':
                speak_out("Oops I couldn't find an answer")
            else:
                speak_out(next(results.results).text)
        except Exception as e:
            speak_out("An error occured ")
            print(e)
    else:
        speak_out('What should I search for?')
        query = listen_up()
        if search_engine == 'wikipedia':
            try:
                results = wikipedia.summary(query, sentences=2)
                speak_out("Here's what I found, ")
                speak_out(results)
                speak_out("Would you like to open this wikipedia page?")
                answer = listen_up()
                if iterate(JarvisVocab.affirmative, answer):
                    speak_out("Alright")
                    webbrowser.open(wikipedia.page(query).url)
                else:
                    speak_out("Okay")
            except Exception:
                suggestions = wikipedia.suggest(query)
                speak_out("I could not find any article as such,"
                          "maybe you meant" + suggestions)
                search_state('wikipedia')

        elif search_engine == 'maps':
            speak_out("I'm opening the relevant page on google maps")
            webbrowser.open("https://www.google.com/maps/search/?api=1&query="
                            + query.replace(' ', '+'))

        elif search_engine == 'google':
            for result in search(query, country='india', num=6, start=0, stop=6):
                print(result)
                article = Article(result)
                article.download()
                article.parse()
                print('Published on: ', article.publish_date)
                print('Title: ', article.title)
            speak_out("I can open any link in a new page if you like, "
                      "just say 'open <url>'")
            default_state()

        else:
            try:
                results = wolfram_client.query(query)
                if results['@success'] == 'false':
                    speak_out("Oops looks like Wolfram doesn't have an answer")
                else:
                    speak_out(next(results.results).text)
            except Exception as e:
                speak_out("An error occured that did not allow WolframAlpha"
                          "to answer your query ")
                print(e)


def userTutorial():
    '''In Program equivalent of the help function'''
    speak_out("Let me show you to make the best use of your assistant")
    speak_out("Each time you start me up, I greet you and go into a "
              "default state, where I await your command.")
    speak_out("Once you speak your command into the mic, "
              "Google Speech Recognition analyses what you said.")
    speak_out("After this, I look for keywords in your commands,"
              " or what modern assistants call intent.")
    speak_out("This would be best explained as the action you want me to do."
              " Like search, sleep, turn on the wifi etc.")
    speak_out("Hence, it is best to first tell me a verb like search,"
              " then tell me what to search for once I ask for it.")
    speak_out("Keeping your commands as brief as possible helps,"
              " as I'm not really gonna worry about your grammar or anything.")
    speak_out("For instance, "
              "'Jarvis, search google for chocolate ice cream stores' and "
              "'Jarvis, google search' have the same value for me."
              " I only recognise the words, 'google search'"
              " and go into search state.)")
    speak_out("Your user settings are stored in a file 'user1.txt'"
              "in the same directory my program code exists in."
              "The first line is your name, the second line your email id and"
              "the third its password. These files are not encrypted"
              "any way but do not pose a significant risk to your data as "
              "nobody actually looks for such files in such places."
              "Sending emails is done completely encrypted using ssl.")
    speak_out("When you initialise the music player,"
              " it will ask you to select the music directory")


def greet():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak_out(f"Good Morning {name}!")
    elif hour >= 12 and hour < 18:
        speak_out(f"Good Afternoon {name}!")
    else:
        speak_out(f"Good Evening {name}!")


def power_options(operation):
    if operation == 'shutdown':
        speak_out("Powering off in 5 seconds", end='')
        os.system("shutdown /s /t 5")
        load_type_dots()
    elif operation == 'reboot':
        speak_out("Rebooting in 5 seconds", end='')
        os.system("shutdown /r /t 5")
        load_type_dots()
    else:
        speak_out('Sorry! an unexpected error occured :(')


def sendEmail(receiver_email='', content=''):
    if receiver_email == '':
        speak_out("Whom should I send the email to: ")
        receiver_email = input()
    speak_out("What is the subject?")
    subject = listen_up()
    speak_out("And the content?")
    content = listen_up()
    try:
        outlook = wincl.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = receiver_email
        mail.Subject = subject
        mail.Body = content
        mail.Send()
    except Exception as e:
        speak_out('Oops. An Error occurred')
        print(e)
    else:
        speak_out("All done! I am showing you a copy of the email\n")
        print('To: ', receiver_email)
        print('Subject: ', subject, '\n')
        print(content, '\n')


def jokeState():
    joke1 = ("What do you get when u put a vest on an alligator?",
             "An investigator")
    joke2 = ("Why shouldn't you write with a broken pencil?",
             "Because it's pointless")
    joke3 = ("What do you call a bear with no teeth?", "A gummy bear")
    joke4 = ("What do you call a shoe made of banana?", "A slipper")
    joke5 = ("How do you make holy water?", "You boil the hell out of it")
    joke6 = ("Why can't you trust an atom?",
             "Because they make up literally everything")
    joke7 = ("What happens when a frog's car breaks?", "It gets toad")
    joke8 = ("How do prisoners call each other?", "On their cell phones")
    joke9 = ("Why do butchers link sausages?", "To make ends meat")
    joke10 = ("Why do bankers quit their jobs?", "Because they lose interest")
    joke11 = ("How do construction workers party?", "They raise the roof")
    joke12 = ("What do you call bees that are fat?", "Obese")
    joke13 = ("What do you call a fish with no eyes?", "A fsh")
    joke14 = ("What do you call an almond in space?", "An astronut")
    joke15 = ("Why doesn't a bread like warm weather?",
              "Because it makes things toasty")
    JokeSet = [joke1, joke2, joke3, joke4, joke5, joke6, joke7, joke8, joke9,
               joke10, joke11, joke12, joke13, joke14, joke15]
    return JokeSet[random.randint(0, 14)]


def numberGuess():
    """
    Simple 'Guess the number' game that you can play with Jarvis.
    """
    range1 = input("Enter lower limit of range: ")
    range2 = input("Enter upper limit of range: ")
    if not(range1.isdigit()) or not(range2.isdigit()) or range1 > range2:
        print("That isn't a valid range")
        return numberGuess
    answer = random.randint(int(range1), int(range2))
    count = 0
    while count <= 10:
        guess = input("Enter your guess from " + range1 + " to " + range2 + ": ")
        if not guess.isdigit():
            print("That's not a number, try again")
            continue
        guess = int(guess)
        if guess == answer:
            print("Hooray! You guessed it in ", count, "attempts")
            break
        elif guess < answer*1.1 and guess > answer*0.9:     # Guess within 10% of answer
            print('Hot')
        elif guess < answer*1.2 and guess > answer*0.8:     # Guess within 20% of answer
            print('Warm')
        else:
            print('Cold')
        count += 1
    else:
        print("Oops. You lost. The number was", answer)


#  ___main___
print(startup, end='')
load_type_dots()
greet()
speak_out("Jarvis here, at your service.")


while True:
    command = default_state().split()
    if iterate(JarvisVocab.farewell, command):
        speak_out('Alright, shutting myself down. Goodbye ' + name)
        break

    elif iterate(JarvisVocab.mails, command):
        sendEmail()

    elif iterate(JarvisVocab.searchTerms, command):
        medium = iterate(JarvisVocab.searchTerms, command)
        # print(medium)
        if medium == ['search']:
            medium = ['google']
        elif 'search' in command:
            medium.remove('search')
        elif medium[0] == 'open':  # or medium[0] == ['.com']:
            link = command[-1]
            search_state('.com', link)
            continue
        search_state(medium[0])
        continue

    elif iterate(JarvisVocab.greetings, command):
        greet()
        continue

    elif iterate(JarvisVocab.gratitude, command):
        speak_out("You are welcome")
        continue

    elif iterate(JarvisVocab.sql, command):
        speak_out('Connecting to your MySQL server', end='')
        load_type_dots()
        mysqlConnectivity()
        continue

    elif iterate(JarvisVocab.powerOptions, command):
        choice = iterate(JarvisVocab.powerOptions, command)
        choice = choice[0]
        if choice == ['power'] or choice == ['options']:
            speak_out('Would you like to shutdown, reboot or send the computer'
                      ' to sleep?')
            choice = listen_up()
            if choice not in JarvisVocab.powerOptions:
                speak_out("I don't think that's a valid selection")
                continue
        power_options(choice)
        continue

    elif iterate(JarvisVocab.joke, command):
        answer = 'yes'
        while iterate(JarvisVocab.affirmative, answer):
            theJoke = jokeState()
            speak_out(theJoke[0])
            speak_out(theJoke[1])
            speak_out('Would you like another one? ')
            answer = listen_up()
        continue

    elif iterate(JarvisVocab.settings, command):
        print(iterate(JarvisVocab.settings, command))
        set_user_settings()
        continue

    elif iterate(JarvisVocab.game, command):
        numberGuess()
        continue

    elif iterate(JarvisVocab.toggles, command):
        settingsToggle(iterate(JarvisVocab.toggles, command))
        continue

    elif iterate(JarvisVocab.music, command):
        JarvisMusic.main()
        pass

    else:
        search_state('wolfram', command)
        continue
