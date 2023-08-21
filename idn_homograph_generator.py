import sys
import idna
import unicodedata
import itertools
import math

# convert a string to Unicode based on its Hex values
def hex_to_unicode(hex_string):
    try:
        unicode_code_point = int(hex_string, 16)
        unicode_character = chr(unicode_code_point)
        return unicode_character
    except:
        return ""
        

# encodes a domain from Unicode to punycode
def convert_to_punycode(domain):

    try:
        normalized = unicodedata.normalize('NFC', domain)
        punycoded = idna.encode(normalized).decode('utf-8')
        
        return punycoded
    except Exception:
        return None


# build the similar_chars dictionary based on the user's wordlist
def build_dictionary(filename):

    similar_chars_dict = {}
    lines = []
    try:
        with open(filename,'r') as f:
            lines = f.read().strip().split('\n')
    except FileNotFoundError:
        print(f'[!] Error - {filename} not found')
        sys.exit(1)
    except Exception as e:
        print(f'[!] Error - {e}')
        sys.exit(1)

    for line in lines:
        # len(line) is 1 when there are no confusables for a specific letter
        if len(line) == 1:
            similar_chars_dict[line] = [line]
        else:
            # split each line by the separator |
            temp = line.split('|')
            # key is the first value, which should be a latin letter
            key = temp.pop(0)
            # convert each hex string into the unicode character
            unicode_chars = [hex_to_unicode(char) for char in temp] 
            # add the latin letter back into the unicode_chars list
            unicode_chars.insert(0,key)
            # remove duplicates from the list of unicode characters
            unicode_chars = list(set(unicode_chars))
            
            similar_chars_dict[key] = unicode_chars

    return similar_chars_dict
        

# calculates the number of possible IDN homographs
def calculate_number_of_combinations(input_string, similar_characters):

    # to calculate number of combinations,
    # multiply the number of possible characters for each character

    p = 1    
    possibilities_list = []
    
    for char in input_string:
        if char in similar_characters:
            num_of_possible_chars = len(similar_characters[char])
            
            p *= num_of_possible_chars
                
            possibilities_list.append(str(num_of_possible_chars))
        else:
            possibilities_list.append("1")
    
    print(f'[-] Number of combinations for each character of "{input_string}" = {", ".join(possibilities_list)}')

    return p


# generates possible IDN homographs in batches
# WARNING: requires LARGE(!!) amount of RAM for long strings with many possible combinations
def generate_combinations_intensive(input_string, similar_chars_dict, batch_size):
    variations = []

    for char in input_string:
        if char in similar_chars_dict:
            variations.append(similar_chars_dict[char])
        else:
            variations.append([char])

    all_combinations = list(itertools.product(*variations))
    
    for idx in range(0, len(all_combinations), batch_size):
        yield [''.join(combination) for combination in all_combinations[idx : idx + batch_size]]


# lazy generates possible IDN homographs
# slow but does not require much RAM at all
def generate_combinations_lazy(input_string, similar_chars_dict):
    def substitute_char(char):
        if char in similar_chars_dict:
            return similar_chars_dict[char]
        else:
            return [char]

    substitutions = [substitute_char(char) for char in input_string]
    combinations = itertools.product(*substitutions)

    for combination in combinations:
        yield ''.join(combination)


# prompt user for confirmation
def get_confirmation(batch_size):
    RED_COLOR_CODE = '\033[91m'
    RESET_COLOR_CODE = '\033[0m'    

    warning = f"""
{RED_COLOR_CODE}
[!] WARNING!!!
[!] THE MODE YOU HAVE SELECTED IS "intensive"!
[!] BASED ON YOUR INPUT DOMAIN AND WORDLIST,
[!] THE PROGRAM COULD CONSUME ALL YOUR RAM!
[!] THE NUMBER OF STRINGS GENERATED IN EACH BATCH IS {batch_size}.
{RESET_COLOR_CODE}
"""
    
    while True:
        print(warning)
        user_input = input('[!] ARE YOU SURE YOU WANT TO PROCEED? [y/n]: ').lower()

        if user_input == 'y':
            return
        elif user_input == 'n':
            print('[-] Program exiting . . .')
            sys.exit(1)
        else:
            print('[!] Invalid input received, please enter [y/n] only. . .')


def main():

    if len(sys.argv) < 3:
        print("[!] Usage: python idn_homograph_generator.py <dictionary_file> <domain> [lazy/intensive]")
        sys.exit(1)
    
    dictionary_file = sys.argv[1]
    domain = sys.argv[2].strip().lower()

    # check for optional input of mode
    mode = "lazy"
    if len(sys.argv) == 4:
        mode = sys.argv[3].strip().lower()

        if mode != "lazy" and mode != "intensive":
            print("[!] Usage: python idn_homograph_generator.py <dictionary_file> <domain> [lazy/intensive]")
            sys.exit(1)
    
    # 1. Build dictionary of Unicode characters to use
    similar_chars_dict = build_dictionary(dictionary_file)
    print(f'\n[-] Loaded dictionary from {dictionary_file}')

    for key in similar_chars_dict:
        print(f'[{key}] -> {", ".join(similar_chars_dict[key])}')
    
    #2. Calculate the number of possibilities for the provided domain
    possibilities = calculate_number_of_combinations(domain, similar_chars_dict)
    print(f'[-] Number of possible combinations for "{domain}" = {possibilities}')
    
    # 3. Generate possible IDN homographs 
    if mode == "lazy":
        combination_generator = generate_combinations_lazy(domain, similar_chars_dict)
        count = 0
        for combination in combination_generator:
            count+=1
            punycoded = convert_to_punycode(combination)
            if punycoded:
                print(f'[{count}] - {combination} -> {punycoded}')

                with open(f'{domain}.txt','a+',encoding='utf-8') as results_file:
                    results_file.write(f'{combination},{punycoded}\n')

    else:
        # By default, the recommended batch size for each generation attempt
        # is set at 1% of the number of possibilities for a domain
        batch_size = math.ceil(possibilities/100)
        # if batch_size is 1% of possibilities, number of batches will always be 100..
        # change the number above to adjust the number of batches
        number_of_batches = int(math.ceil(possibilities/batch_size))
        
        get_confirmation(batch_size)
    
        print(f'[-] Generating IDN homographs for "{domain}" in batches of {batch_size}.')
        print(f'[-] Total number of batches = {number_of_batches}')

        combinations_generator = generate_combinations_intensive(domain, similar_chars_dict, batch_size)
        batch_idx = 1
        
        while True:
            batch_combinations = next(combinations_generator, None)
            if batch_combinations:
                print(f"\nBatch {batch_idx}:")
                for idx, combination in enumerate(batch_combinations):
                    punycoded = convert_to_punycode(combination)
                    if punycoded:            
                        print(f'[{idx+1}] - {combination} -> {punycoded}')

                        with open(f'{domain}.txt','a+',encoding='utf-8') as results_file:
                            results_file.write(f'{combination},{punycoded}\n')

                batch_idx += 1
            else:
                break

    print(f'[-] Program completed running . . . results saved to "{domain}.txt"')
    
if __name__ == '__main__':
    main()
