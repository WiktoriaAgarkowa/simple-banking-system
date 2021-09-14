import random
import math
import sqlite3
con = sqlite3.connect('card.s3db')
cur = con.cursor()

# cur.execute('''CREATE TABLE card
#                (id integer, number text, pin text, balance integer DEFAULT 0)''')


def luhnalgorithm(list_of_numbers):
    # All numbers with an odd index must be multiplied by 2
    # If the multiplied number > 9, we must decrease by 9

    calculated_card_number = []
    for index, num in enumerate(list_of_numbers):
        if (index + 1) % 2 != 0:
            num *= 2
            if num > 9:
                num -= 9
                calculated_card_number.append(num)
            else:
                calculated_card_number.append(num)
        else:
            calculated_card_number.append(num)

    # Calculate the sum of Luhn numbers to find the last number
    sum_of_numbers = 0
    for n in calculated_card_number:
        sum_of_numbers += n

    return sum_of_numbers


class Card:
    def __init__(self):
        self.card_number = None
        self.pin = None

    def create_card_number(self):
        random_customer_account_number = random.randint(10 ** 8, (10 ** 9) - 1)
        numbers = [int(x) for x in str(random_customer_account_number)]

        # Use the Luhn algorithm
        sum_of_numbers = luhnalgorithm(numbers)

        # Increasing by 8 because every number of card always starts with "4"
        # According to the Luhn algorithm, the first digit should also be multiplied by 2
        sum_of_numbers += 8

        # Find the last number:
        # Converting the sum to a decimal, rounding up
        # converting to a whole number, subtracting the sum to find the last digit
        last_number = (math.ceil(sum_of_numbers / 10) * 10) - sum_of_numbers

        self.card_number = f'400000{str(random_customer_account_number)}{last_number}'
        print('Your card has been created')
        print(f'Your card number: \n{self.card_number}')

        return self.card_number

    def create_pin(self):
        self.pin = random.randint(1000, 9999)
        print(f'Your card PIN: \n{self.pin}')
        return self.pin


def start():
    stop = False

    while True and not stop:
        print('1. Create an account \n2. Log into account \n0. Exit')
        choice = input('>')

        if choice == '0':
            print('Bye!')
            break

        elif choice == '1':
            new_card = Card()
            new_card.create_card_number()
            new_card.create_pin()
            id = new_card.card_number
            cur.execute("INSERT INTO card VALUES (?, ?, ?, 0)", (id, new_card.card_number, new_card.pin))
            con.commit()
            continue

        elif choice == '2':
            print('Enter your card number:')
            number_request = input('>')

            cur.execute("SELECT number, pin FROM card WHERE number=?", (number_request,))
            card = cur.fetchall()

            print('Enter your PIN:')
            pin_request = input('>')

            if not card or pin_request != card[0][1]:
                print('Wrong card number or PIN!')

            elif card and pin_request == card[0][1]:
                print('You have successfully logged in!')

                while True:
                    print('1. Balance \n2. Add income \n3. Do transfer \n4. Close account \n5. Log out \n0. Exit')
                    choice = input('>')

                    if choice == '1':
                        cur.execute('SELECT balance FROM card WHERE number = ?', (number_request,))
                        balance = cur.fetchone()
                        print(f'Balance: {balance[0]}')
                        continue

                    elif choice == '2':
                        print('Enter income:')

                        income = int(input())
                        cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (income, number_request))
                        con.commit()
                        print('Income was added!')
                        continue

                    elif choice == '3':

                        print('Enter card number:')
                        transfer_acc_number = input()

                        # Take the actual balance of the card from database
                        cur.execute('SELECT balance FROM card WHERE number = ?', (number_request,))
                        card = cur.fetchone()

                        # Prepare the number of card for verification
                        numbers = [int(el) for el in transfer_acc_number]

                        # Checking the card by Luhn Algorithm
                        last_number_of_card = numbers.pop()  # Take the last number
                        sum_of_numbers = luhnalgorithm(numbers)

                        sum_of_numbers = sum_of_numbers + last_number_of_card

                        if sum_of_numbers % 10 != 0:
                            print('Probably you made a mistake in the card number. Please try again!')
                            continue

                        elif transfer_acc_number == number_request:
                            print("You can't transfer money to the same account!")
                            continue

                        # Take the card where we want to transfer money
                        cur.execute('SELECT number FROM card WHERE number = ?', (transfer_acc_number,))
                        transfer_number_card = cur.fetchall()

                        # If this card not exist...
                        if not transfer_number_card:
                            print('Such a card does not exist')
                            continue

                        print('Enter how much money you want to transfer:')
                        amount = input()

                        if int(amount) > card[0]:
                            print('Not enough money!')
                        else:
                            cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?',
                                        (amount, transfer_acc_number))
                            cur.execute('UPDATE card SET balance = balance - ? WHERE number = ?',
                                        (amount, number_request))
                            con.commit()
                            print('Success!')

                    elif choice == '4':
                        cur.execute('DELETE FROM card WHERE number = ?', (number_request,))
                        print('The account has been closed!')
                        break

                    elif choice == '5':
                        print('You have successfully logged out!')
                        break

                    elif choice == '0':
                        print('Bye!')
                        stop = True
                        break


start()
