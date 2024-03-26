

def main():
    import random
    guesses_made = 0
    name = input('Hello! What is your name?\n')
    number = random.randint(1, 20)
    print('Well, {0}, I am thinking of a number between 1 and 20.'.format(name))
    print(number)
    guess = 0

    for _ in range(6):

        guess = int(input('Take a guess: '))

        guesses_made += 1

        if guess < number:
            print('Your guess is too low.')
        elif guess > number:
            print('Your guess is too high.')
        else:
            print('Good job, {0}! You guessed my number in {1} guesses!'.format(name, guesses_made))
        print()

    if guess != number:
        print('Nope. The number I was thinking of was {0}'.format(number))

    return


if __name__ == '__main__':
    main()

