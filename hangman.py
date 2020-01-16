from shutil import get_terminal_size
from os.path import isfile, abspath

# region NEW FUNCTIONS
def center_string(string):
    """
    Formatting given string to be centered in terminal when printed.

    :param string: String that's intended for output in terminal.
    :type string: str
    :return: The string, modified to be centered in terminal.
    :rtype: str
    """
    NEW_LINE = '\n'
    PAD_UNIT = ' '

    term_col_num = get_terminal_size().columns

    # padding of each line of the string will be done according to the size of the longest line in that string
    # in order for everything to be aligned correctly
    string_lines_list = string.split(NEW_LINE)
    longest_len = len(max(string_lines_list, key=len))

    # preparing the padding for each line of the string
    pad_str = PAD_UNIT * ((term_col_num - longest_len) // 2)

    # the first line wont be padded on it's own
    string_lines_list[0] = pad_str + string_lines_list[0]
    # adding another newline to space-out on-screen text
    return NEW_LINE + (NEW_LINE + pad_str).join(string_lines_list)


def input_centered(string):
    """
    A wrapper around the stock input function, except that the prompt text will be centered in the terminal.

    :param string: The prompt text before the user input.
    :type string: str
    :return: User input.
    :rtype: str
    """
    return input(center_string(string))


def print_centered(string, use_logo=False):
    """
    A wrapper around the stock print function, except that the text will be centered in the terminal.
    
    :param string: The text to be printed.
    :param use_logo: Whether to print the logo before the string.
    :type string: str
    :type use_logo: bool
    :return: None
    """
    if use_logo:
        print_game_logo()

    print(center_string(string))

    return None


def sys_comment(comment, is_error=False):
    """
    Game system comment formatting before output to console.

    :param comment: The text to be printed as a comment.
    :param is_error: If the comment is an error comment.
    :type comment: str
    :type is_error: bool
    :return: None
    """
    COMMENT_STR = "[*]"
    if is_error:
        COMMENT_STR = "[X]"

    print_centered("{} {} {}".format(COMMENT_STR, comment, COMMENT_STR), use_logo=True)

    return None


def clear_player_screen():
    """
    This will "clear" the terminal screen by printing enough newlines to scroll the latest printed text out
    of sight.

    :return: None
    """
    print('\n' * get_terminal_size().lines, end='')

    return None


def get_verified_input(prompt, verify_by_func, msg_wrong=None):
    """
    A modular function to get verified input from the user.

    :param prompt: The text to be displayed to the user.
    :param verify_by_func: The function to verify the validity of the input.
    :param msg_wrong: The error message to be displayed, if the input is not acceptable.
    :type prompt: str
    :type verify_by_func: function
    :type msg_wrong: str
    :return: The verified user-input.
    :rtype: str
    """
    if msg_wrong is None:
        # stock error message
        msg_wrong = "Invalid input."

    # raw
    answer = input_centered(prompt)
    # the answer must match conditions of verification
    while not verify_by_func(answer):
        sys_comment(msg_wrong, is_error=True)
        answer = input_centered(prompt)
    
    # at this point, the answer is verified to be valid
    return answer


def is_castable_to_int(string):
    """
    Checks if a string can be casted to int. Accepting formats: [number], -[number], +[number].

    :param string: The string to be checked.
    :type string: str
    :return: True - if string can be casted to int, False - otherwise.
    :rtype: bool
    """
    # if string has at least 2 chars and starts with either + or -
    # then it could be a positive or a negative representation of an integer
    if len(string) > 1 and string[0] in ['+', '-']:
        # check if the rest is a number
        return string[1:].isdecimal()
    # if no prefix found - the whole string should be a decimal number
    return string.isdecimal()


def is_yes_or_no(string, check_no=True):
    """
    Checks if the string represents a yes/no answer. Case-insensitive.
    Formats accepted: yes, no, y, n.

    :param string: The string to be checked.
    :param check_no: If set to False - the function will only return True for a 'yes'.
    :type string: str
    :type check_no: bool
    :return: Depending on the value of check_no, either True for both 'yes' and 'no' or only for a 'yes'.
    :rtype: bool
    """
    OPTIONS = (('yes', 'y'), ('no', 'n'))
    string_lower = string.lower()

    return (string_lower in OPTIONS[0]) or (check_no and string_lower in OPTIONS[1])


def get_yes_no(question):
    """
    Gets a user to answer a yes-or-no question.

    :param question: The question to be asked of the user.
    :type question: str
    :return: True - if the user answered with a 'yes'; False - if answered with a 'no'.
    :rtype: bool
    """
    complete_question = question + " ([Y]es/[N]o): "

    answer = get_verified_input(prompt=complete_question, verify_by_func=is_yes_or_no)

    # returns True is yes, False if no
    return is_yes_or_no(answer, check_no=False)


def change_field(field_name, verify_input_func, error_msg=None, input_mod_func=None):
    """
    Generalized function to be used to change a setting.

    :param field_name: The setting name that the user will recognize.
    :param verify_input_func: Function to be used to verify if the user input is acceptable.
    :param error_msg: Message to be displayed if the user input is unacceptable.
    :param input_mod_func: Function to modify the received input before displaying.
    :type field_name: str
    :type verify_input_func: function
    :type error_msg: str
    :type input_mod_func: function
    :return: User input for the setting that's supposed to be changed.
    :rtype: Uncertain.
    """

    # prompt to be displayed to user when asking to change the setting
    prompt = "Enter the {}: ".format(field_name)
    field_val = get_verified_input(prompt=prompt, verify_by_func=verify_input_func, msg_wrong=error_msg)

    if not input_mod_func is None:
        # modifying input before printing in system feedback
        field_val = input_mod_func(field_val)

    sys_comment('Using {}: {}'.format(field_name, field_val))

    # returning new value of setting
    return field_val


def change_secret_word(word_list_path):
    """
    Get a new secret word from the word-list.

    :param word_list_path: The word-list from which the secret word will be drawn.
    :type word_list_path: str
    :return: The secret word.
    :rtype: str
    """
    FIELD_NAME = "secret word index"
    secret_word_index = change_field(FIELD_NAME, is_castable_to_int, input_mod_func=int)

    return choose_word(word_list_path, secret_word_index)


def change_word_list():
    """
    Prompt for a path to a word-list.

    :return: The full file path of the word-list.
    :rtype: str
    """
    ERROR_MSG = "The path specified either doesn't exist or is not of a file."
    FIELD_NAME = "word-list path"

    return change_field(FIELD_NAME, isfile, error_msg=ERROR_MSG, input_mod_func=abspath)


def show_current_game_state(num_of_tries, secret_word, old_letters_guessed):
    """
    Shows the hangman ascii art and the revealed parts of the secret word that correspond to already-guessed letters
    and the number of failed guessing attempts.

    :param num_of_tries: Number of times the player guessed wrong.
    :param secret_word: The secret word to be guessed.
    :param old_letters_guessed: List of all previously guessed letters.
    :type num_of_tries: int
    :type secret_word: str
    :type old_letters_guessed: list
    :return: None
    """
    print_hangman(num_of_tries)
    # 4.
    print_show_hidden_word_box(secret_word, old_letters_guessed)

    return None


def print_show_hidden_word_box(secret_word, old_letters_guessed, use_logo=False):
    """
    Prints the hidden word inside an ascii box.

    :param secret_word: The word for the player to guess.
    :param old_letters_guessed: List of letters the user guessed previously.
    :param use_logo: Whether or not to print the hangman game ascii logo.
    :type secret_word: str
    :type old_letters_guessed: list
    :type use_logo: bool
    :return: None
    """
    # strings for the box drawing
    bottom_top_box_line = chr(9552) * (len(secret_word) * 2 + 5)
    right_left_line = chr(9553)
    corners = ( (chr(9556), chr(9559)), (chr(9562), chr(9565)))
    
    # using format to assemble the box around the word
    print_centered("{0}{bl}{1}\n{2}   {hw}   {2}\n{3}{bl}{4}".format(corners[0][0], corners[0][1], right_left_line, corners[1][0], corners[1][1], hw=show_hidden_word(secret_word, old_letters_guessed), bl=bottom_top_box_line), use_logo=use_logo)

    return None


def print_game_logo():
    """
    Prints the hangman game logo as ASCII-art.

    :return: None
    """

    HANGMAN_ASCII_ART = r"""
  _    _
 | |  | |
 | |__| | __ _ _ __   __ _ _ __ ___   __ _ _ __
 |  __  |/ _` | '_ \ / _` | '_ ` _ \ / _` | '_ \
 | |  | | (_| | | | | (_| | | | | | | (_| | | | |
 |_|  |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                      __/ |
                     |___/
"""
    
    clear_player_screen()
    print_centered(HANGMAN_ASCII_ART)

    return None
# endregion NEW FUNCTIONS
#############################################################################################
# region BASE FUNCTIONS
def show_hidden_word(secret_word, old_letters_guessed):
    """
    Reveals parts of the secret word that were guessed correctly. Non guessed parts will appear as underscores.

    :param secret_word: The secret word to be guessed by the player.
    :param old_letters_guessed: A list of letter the player guessed previously.
    :type secret_word: str
    :type old_letters_guessed: list
    :return: The secret word with correctly-guessed letters shown, and not-guessed letters replaced with an underscore.
    :rtype: str
    """
    revealed_word_chars_list = []

    for letter in secret_word:
        # if letter hasn't been guessed - hide it
        if letter not in old_letters_guessed:
            revealed_word_chars_list.append('_')
        # if guessed - show it
        else:
            revealed_word_chars_list.append(letter)

    return " ".join(revealed_word_chars_list)


def check_valid_input(letter_guessed, old_letters_guessed):
    """
    Checks whether the guessed letter is valid for the game (not longer than 1 character in length, is
    from the english alphabet and hasn't been guessed previously).

    :param letter_guessed: The letter that the user guessed.
    :param old_letters_guessed: A list of the letters the user guessed previously.
    :type letter_guessed: str
    :type old_letters_guessed: list
    :return: True is letter is valid, False - otherwise.
    :rtype: bool
    """
    # if exactly 1-char-long and is from english alphabet and hasn't been previously guessed
    # using ('a' <= letter_guessed <= 'z') because isalpha() returns True for multiple languages, not only english
    return (len(letter_guessed) == 1) and ('a' <= letter_guessed <= 'z') and (letter_guessed not in old_letters_guessed)


def try_update_letter_guessed(letter_guessed, old_letters_guessed):
    """
    If the letter is valid (meaning, it is a single english letter and was never before guessed), the function will add
    it to the list of guessed letters and return True.
    If the letter is invalid, the function will print out the letter 'X' and below it the list of previously guessed
    letters as a string of lowercase letters, sorted alphabetically and delimited by arrows, and return False.

    :param letter_guessed: the letter the player guessed
    :param old_letters_guessed: list of previously guessed letters
    :type letter_guessed: str
    :type old_letters_guessed: list
    :return: True if the guessed letter is valid and False - otherwise
    :rtype: bool
    """
    ARROW_STR = ' -> '
    X_STR = 'X'
    letter_lower = letter_guessed.lower()
    
    if not check_valid_input(letter_lower, old_letters_guessed):
        print_centered(X_STR, use_logo=True)
        # printing previous guesses, alphabetically-sorted, with arrows between them
        print_centered(ARROW_STR.join(sorted(old_letters_guessed)))
        return False

    # letter is valid - adding to list of guessed letters
    old_letters_guessed.append(letter_lower)
    return True


def check_win(secret_word, old_letters_guessed):
    """
    Checks if the player has won the game.

    :param secret_word: The secret word that the user has to guess.
    :param old_letters_guessed: Letters that the user guessed previously.
    :type secret_word: str
    :type old_letters_guessed: list
    :return: True, if all the letters of secret_word appear in old_letters_guessed, otherwise - False
    :rtype: bool
    """
    for i in secret_word:
        if i not in old_letters_guessed:
            return False
    # all letters from secret_word are in old_letters_guessed - the player won
    return True


def choose_word(file_path, index):
    """
    Retrieves a word, that will be the secret word for the user to guess in the game,
    from a space-separated word-list, based on the given index. If the index is out of the list's bounds - the count
    will continue in a circular fashion.
    Will intentionally tolerate negative index values and zero.

    :param file_path: The path to the text file.
    :param index: The index of the word to get.
    :type file_path: str
    :type index: int
    :return: The secret word to be guessed.
    :rtype: str
    """
    # read the words from file into a list
    with open(file_path, 'r') as word_list_file:
        words_list = word_list_file.read().split()

    words_num = len(words_list)
    # index in-file counting from 1 - fixing to match lists indexing
    index -= 1
    # if the index is out the list's bounds- the counting continues in a circular fashion
    # (correctly takes care of negative values as well)
    index %= words_num

    return words_list[index]


def print_hangman(num_of_tries):
    """
    Prints the hangman progress ascii-image corresponding to the user's error-count.

    :param num_of_tries: Number of times the user guessed wrong.
    :type num_of_tries: int
    :return: None
    """

    HANGMAN_PHOTOS = {
        0: "x-------x\n\n\n\n\n\n",
        1: "x-------x\n"
           "|\n"
           "|\n"
           "|\n"
           "|\n"
           "|\n",
        2: "x-------x\n"
           "|       |\n"
           "|       0\n"
           "|\n"
           "|\n"
           "|\n",
        3: "x-------x\n"
           "|       |\n"
           "|       0\n"
           "|       |\n"
           "|\n"
           "|\n",
        4: "x-------x\n"
           "|       |\n"
           "|       0\n"
           "|      /|\\\n"
           "|\n"
           "|\n",
        5: "x-------x\n"
           "|       |\n"
           "|       0\n"
           "|      /|\\\n"
           "|      / \n"
           "|\n",
        6: "x-------x\n"
           "|       |\n"
           "|       0\n"
           "|      /|\\\n"
           "|      / \\\n"
           "|\n"
    }

    print_centered(HANGMAN_PHOTOS[num_of_tries])
    return None


def hangman(secret_word):
    """
    The game logic.

    :param secret_word: The word for the player to guess.
    :type secret_word: str
    :return: None
    """
    MAX_TRIES = 6               # const max number of wrong guesses
    SAD_FACE = ":("
    WIN_STR = "WIN"
    LOSE_STR = "LOSE"
    LETTER_PROMPT = "Guess a letter: "

    old_letters_guessed = []    # list for keeping track of guessed letters
    num_of_tries = 0            # counter for wrong guesses

    # 3. + 4.
    show_current_game_state(num_of_tries, secret_word, old_letters_guessed)

    # 5.
    while num_of_tries < MAX_TRIES:
        letter_guessed = input_centered(LETTER_PROMPT)
        is_valid_guess = try_update_letter_guessed(letter_guessed, old_letters_guessed)

        # 6.
        # if a valid guess
        if is_valid_guess:
            # if correct guess
            if letter_guessed in secret_word:
                print_show_hidden_word_box(secret_word, old_letters_guessed, use_logo=True)

                if check_win(secret_word, old_letters_guessed):
                    # 7.
                    print_centered(WIN_STR)
                    # end the game
                    break

            # if technically valid, but wrong guess
            else:
                print_centered(SAD_FACE, use_logo=True)

                num_of_tries += 1
                show_current_game_state(num_of_tries, secret_word, old_letters_guessed)

                if not num_of_tries < MAX_TRIES:
                    # 7.
                    print_centered(LOSE_STR)

    return None
# endregion BASE FUNCTIONS


def main():
    """
    Main function that's tying all the components of the game together.

    :return: None
    """

    # after first round it will ask if want to change word list
    first_round = True

    # 1.
    print_game_logo()

    # will break out of loop when the player wouldn't want another round
    while True:
        if not first_round:
            if get_yes_no("Would you like to switch to a different word-list?"):
                # 2.1.
                print_game_logo()
                word_list_path = change_word_list()
            else:
                sys_comment("Playing with the same word-list")
        else:
            # 2.1.
            word_list_path = change_word_list()
            first_round = False

        # 2.2.
        secret_word = change_secret_word(word_list_path)

        # starting the game
        hangman(secret_word)

        # finished the game - ask if want another round
        if get_yes_no("Would you like to play another game?"):
            sys_comment("Starting another game")
        else:
            sys_comment("Quitting")
            break

    return None


if __name__ == '__main__':
    main()
