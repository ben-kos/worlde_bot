import math

def valid_guess(word,array):
    '''
    Takes in a word, compares it against the array of known wordle information, and return True if it is a valid guess.
    '''
    return is_incorrect_position(word, array) and is_correct_position(word, array) and is_correct_letter_frequencies(word, array)

def index_of_letter(letter):
    '''
    Returns the index of the letter list for the information array.
    '''
    return ord(letter) - ord('a')

def is_incorrect_position(word, array):
    '''
    Takes in a word and compares it to an array of known wordle information. If the word has a letter where a previous
    guess precluded that letter (with a black or yellow tiles), returns False
    '''
    for j in range(len(word)):
        i = index_of_letter(word[j])
        if array[i][j] == 'b' or array[i][j] == 'y':
            return False
    return True

def is_correct_position(word, array):
    '''
    Takes in a word and compares it to an array of known wordle information. If the word does not have a letter where a
    previous guess mandated a letter be (with a green tile), returns False.
    '''
    for j in range(len(word)):
        i = index_of_letter(word[j])
        for k in range(len(array)):
            if array[k][j] == 'g' and i != k:
                return False
    return True

def is_correct_letter_frequencies(word, array):
    '''
    Takes in a word and compares it to an array of known wordle information. If the word does not have the correct
    frequency of letters, (based on the number of green, yellow, and black tiles for that letter), returns False.
    '''
    for j in range(len(word)):
        count = word.count(word[j])
        i = index_of_letter(word[j])
        letter_frequency = array[i][-2]
        is_exactly_count = array[i][-1]
        if is_exactly_count:
            if letter_frequency != count:
                return False
        else:
            if letter_frequency > count:
                return False
    for j in range(len(array)):
        letter_to_check = chr(j+ord('a'))
        if array[j][-2] >= 1:
            if letter_to_check not in word:
                return False
    return True


def generate_array(guess, check, array):
    '''
    Updates a 2D array of length 26 and width 7. The vertical position in the array represents a letter. The first
    5 horizontal positions in the array represent the 5 letters of the wordle game. The 6th position represents
    the minimum number of that letter that must be in the word, while the 7th position represents if we know the
    exact number of letters in a word (True for exact, False for at least)

    guess: The user's guess
    check: The 5 color sequence for that guess
    array: The array of information about the solution from previous guesses

    returns the updated array
    '''
    for j in range(len(guess)):
        i = index_of_letter(guess[j])
        letter_count = compute_letter_freq(guess[j], guess, check)
        array[i][j] = check[j]
        array[i][-2] = letter_count[0]
        array[i][-1] = letter_count[1]
    return array

def compute_letter_freq(letter, guess, check):
    '''
    Takes in information based on the current guess and updates the minimum number of letters in the answer. If a black
    tile is ever found, the exact number of letters in the answer can be computed.

    letter: The letter we are analyzing
    guess: The user's current guess
    check: The 5 color sequence for the current guess

    returns a list with the minimum count for the letter, and if the minimum count is actually the exact count
    '''
    count = 0
    is_exact = False
    for i in range(len(guess)):
        if (check[i] == 'g' or check[i] == 'y') and guess[i] == letter:
            count += 1
        if check[i] == 'b' and guess[i] == letter:
            is_exact = True
    return [count, is_exact]

def compute_wordle_information(guess, answer):
    '''
    Computes color sequences if the answer is known

    guess: The guess the program is analyzing
    answer: The known answer to the game

    returns the 5 color sequence
    '''
    sequence = ''
    frequency_array = [0 for x in range(26)]
    green_frequency_array = [0 for x in range(26)]
    for j in range(len(answer)):
        i = index_of_letter(answer[j])
        frequency_array[i] += 1
        if guess[j] == answer[j]:
            green_frequency_array[i] += 1
    for j in range(len(guess)):
        count = guess[:j+1].count(guess[j])
        i = index_of_letter(guess[j])
        if guess[j] == answer[j]:
            sequence += 'g'
            green_frequency_array[i] -= 1
        elif guess[j] in answer and count <= frequency_array[i] and frequency_array[i] - count >= green_frequency_array[i]:
            sequence += 'y'
        else:
            sequence += 'b'
    return sequence

def compute_probability_distribution(guess, word_list):
    '''
    Computes a probability distribution of color outputs for a given guess. Takes in the current guess and a list of
    possible words, then adds up how many times each unique color sequence is encountered. Assumes a uniform distribution
    of words, so computes probability by dividing the number of times a color sequence is encountered by the total number
    of words in the list.

    guess: The current guess the probability distribution is being computed for
    word_list: The list of words used in the probability distribution computation

    returns a dictionary containing each color sequence and it's corresponding probability
    '''
    probability_dictionary = {}
    for word in word_list:
        color_sequence = compute_wordle_information(guess, word)
        if color_sequence in probability_dictionary:
            probability_dictionary[color_sequence] += 1
        else:
            probability_dictionary[color_sequence] = 1
    for key in probability_dictionary:
        probability_dictionary[key] = probability_dictionary[key]/len(word_list)
    return probability_dictionary

def compute_entropy(guess, word_list):
    '''
    Takes in a guess and a list of words, then computes the information entropy for each of the words in the list based
    on the current guess. The equation used is H(X) = sum(P(x_i) * log(1/P(x_i))). The word with the highest entropy
    should give the most information about the answer, and should likely be guessed next.

    guess: The guess who's entropy is being computed
    word_list: A list of words to be analyzed for which would give the most information about the answer.

    returns the entropy of the particular guess.
    '''
    probability_dictionary = compute_probability_distribution(guess, word_list)
    entropy = 0
    for key in probability_dictionary:
        val = probability_dictionary[key]
        entropy += (val*math.log(1/val, 2))
    return entropy

def generate_entropy_list(word_list, possible_guesses):
    '''
    Takes in a list of words to be analyzed for their entropy, and a list of possible remaining guesses for which we
    want to generate the most information about. The list of words to be used as a possible guess need not be the same
    as the list of possible remaining guesses.

    word_list: The list of possible choices to make to get information about the answer.
    possible_guesses: The list of remaining possible answers.

    returns a sorted list of all possible choices and the information entropy they would return based on the remaining
    possible answers
    '''
    entropy_list = []
    for word in word_list:
        entropy = compute_entropy(word, possible_guesses)
        entropy_list.append([word, entropy])
    entropy_list = sorted(entropy_list, key=lambda x: x[1], reverse=True)
    return entropy_list

def play_wordle():
    '''
    Plays wordle with the user, giving suggestions about which word to guess and which words are possible remaining
    solutions. See comments for individual functionality.
    '''
    f = open('sgb-words.txt','r')                               #Reads in the list of all words
    lines = [line.strip('\n') for line in f.readlines()]
    f.close()
    guess_array = [[0 for x in range(7)] for y in range(26)]
    loop_continuance = True
    guess_suggestion = 'tares'                                  #Original best guess is computed offline to save runtime
    loop_count = 0
    while loop_continuance:
        possible_guesses = []
        loop_count += 1
        print('We suggest you guess', guess_suggestion)
        print('This is guess number', loop_count)
        guess = input('What is your guess? ')
        check = input('What was the color sequence? ex. gbbyy ')
        if check == 'ggggg':                                    #Winning sequence for the game
            print('You won wordle in', loop_count, 'turns!')
            break
        guess_array = generate_array(guess, check, guess_array) #Uses users current guess and the color sequence to update guess array
        for j in range(len(lines)):
            if valid_guess(lines[j], guess_array):
                possible_guesses.append(lines[j])               #Loops through all words and selects possible solutions
        entropy_list = generate_entropy_list(lines, possible_guesses)   #Generates a list of 'best' guesses. Utilizes all
        print('The possible words are', possible_guesses)               #words instead of solution words to avoid falling
        guess_suggestion = entropy_list[0][0]                           #into traps. (If river, rimer, ricer were all in
        for guess in possible_guesses:                                  #the solution set, should guess something with a v, m, and c)
            for i in range(len(entropy_list)):
                if entropy_list[i][0] == guess:
                    if entropy_list[0][1] == entropy_list[i][1]:
                        guess_suggestion = guess                #If the best guess is in the solution set, suggests a solution guess
        if loop_count >=6:
            print('You lost wordle')
            loop_continuance = False


def computer_play_wordle(answer):
    '''
    Plays wordle against a known answer. Removes user inputs and computes the game internally. Used in analyzing
    efficiency of different information methods. See play_wordle() for individual functionality.

    returns the number of guesses required to compute the correct answer.
    '''
    f = open('sgb-words.txt', 'r')
    lines = [line.strip('\n') for line in f.readlines()]
    f.close()
    guess_array = [[0 for x in range(7)] for y in range(26)]
    guess_suggestion = 'tares'
    loop_count = 0
    while True:
        possible_guesses = []
        loop_count += 1
        guess = guess_suggestion
        check = compute_wordle_information(guess, answer)
        if check == 'ggggg':
            return loop_count
        guess_array = generate_array(guess, check, guess_array)
        for j in range(len(lines)):
            if valid_guess(lines[j], guess_array):
                possible_guesses.append(lines[j])
        entropy_list = generate_entropy_list(lines, possible_guesses)
        guess_suggestion = entropy_list[0][0]
        for guess in possible_guesses:
            for i in range(len(entropy_list)):
                if entropy_list[i][0] == guess:
                    if entropy_list[0][1] == entropy_list[i][1]:
                        guess_suggestion = guess
        if loop_count >= 6:
            return loop_count + 1

def get_bot_efficiency():
    '''
    The program plays wordle with every word in a list of words. It computes the average number of turns to win the game,
    and if there were any words that the computer could not solve.
    '''
    f = open('sgb-words.txt', 'r')
    lines = [line.strip('\n') for line in f.readlines()]
    f.close()
    win_count = 0
    my_loading_bar = 0
    fail_array = []
    for ele in lines:
        print(my_loading_bar)
        turn_count = computer_play_wordle(ele)
        my_loading_bar += 1
        win_count += turn_count
        if turn_count >= 7:
            fail_array.append(ele)
    average_turn_to_win = win_count / len(lines)
    print('The failure words are', fail_array)
    print('The average turn to solve is', average_turn_to_win)