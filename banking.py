import random
import sqlite3
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
conn.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, pin TEXT, balance INTEGER)")
conn.commit()

def checksum(string):
    digits = list(map(int, string))
    odd_sum = sum(digits[-1::-2])
    even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
    return (odd_sum + even_sum) % 10

def verify(string):
    return (checksum(string) == 0)

def generate(string):
    cksum = checksum(string + '0')
    return (10 - cksum) % 10

def append(string):
    return string + str(generate(string))

class MyBank:

    def __init__(self):
        self.current_user = []

    def menu(self):
        while True:
            menu_choice = int(input("""
            Please choose one of menu options:
            1. Create an account
            2. Log into account
            0. Exit
            """))
            if menu_choice == 1:
                bank.create_acc()
            elif menu_choice == 2:
                bank.log_in()
            elif menu_choice == 0:
                bank.app_exit()
            else:
                print("Incorrect input! Please try again.")
                continue

    def create_acc(self):
        random.seed()
        pin = [random.randint(0, 9) for i in range(4)]
        card_pin = "".join(map(str, pin))
        bin = [random.randint(0, 9) for i in range(9)]

        card_number = append("400000" + "".join(map(str, bin)))
        cur.execute("SELECT * FROM card")
        id_calc = len(cur.fetchall()) + 1
        cur.execute("INSERT INTO card VALUES (?, ?, ?, ?)", (id_calc, card_number, card_pin, 0))
        conn.commit()

        print("""
        Your card has been created
        Your card number:""")
        print(card_number)
        print("Your card PIN:")
        print(card_pin)

    def log_in(self):
        input_login = input("Enter your card number:")
        input_pin = input("Enter your PIN:")
        input_mix = "SELECT number, pin FROM card WHERE number = :number AND pin = :pin"
        cur.execute(input_mix, {'number' :input_login, 'pin' :input_pin})
        if cur.fetchone() == None:
            print("Wrong card number or PIN!")
        else:
            self.current_user = [input_login, input_pin]
            print("You have successfully logged in!")
            bank.user_panel()


    def user_panel(self):
        while True:
            user_choice = int(input("""
            Please choose one of menu options:
            1. Balance
            2. Add income
            3. Do transfer
            4. Close account
            5. Log out
            0. Exit
            """))
            if user_choice == 1:
                bank.balance()
            elif user_choice == 2:
                self.add_income()
            elif user_choice == 3:
                self.transfer()
            elif user_choice == 4:
                self.close_account()
            elif user_choice == 5:
                self.current_user = []
                print("You have successfully logged out!")
                bank.menu()
            elif user_choice == 0:
                bank.app_exit()
            else:
                print("Incorrect input! Please try again.")
                continue

    def app_exit(self):
        print("Bye!")
        exit()

    def balance(self):
        input_b = "SELECT balance FROM card WHERE number = :number AND pin = :pin"
        cur.execute(input_b, {'number': self.current_user[0], 'pin': self.current_user[1]})
        print(cur.fetchone())

    #Two ways just to try it out.
    def add_income(self):
        input_income = int(input("Enter income:"))
        input_b = "SELECT balance FROM card WHERE number = :number AND pin = :pin"
        cur.execute(input_b, {'number': self.current_user[0], 'pin': self.current_user[1]})
        new_balance = input_income + int(''.join(map(str, cur.fetchone())))
        cur.execute(f"UPDATE card SET balance = {new_balance} WHERE number = {self.current_user[0]} AND {self.current_user[1]}")
        conn.commit()
        print("Income was added!")

    def close_account(self):
        cur.execute(f"DELETE FROM card WHERE number = {self.current_user[0]} AND {self.current_user[1]}")
        conn.commit()
        self.current_user = []
        print("The account has been closed!")
        bank.menu()

    def transfer(self):
        print("Transfer")
        transfer_to = input("Enter card number:")
        if verify(transfer_to) == True:
            cur.execute(f"SELECT number FROM card WHERE EXISTS (SELECT number FROM card WHERE number = {transfer_to})")
            if cur.fetchone() == None:
                print("Such a card does not exist.")
            else:
                transfer_amount = input("Enter how much money you want to transfer:")
                cur.execute(f"SELECT balance FROM card WHERE number = {self.current_user[0]} AND {self.current_user[1]}")
                curr_balance = int(''.join(map(str, cur.fetchone())))
                if int(transfer_amount) <= curr_balance:
                    new_balance_out = curr_balance - int(transfer_amount)
                    cur.execute(f"SELECT balance FROM card WHERE number = {transfer_to}")
                    curr_balance_in = int(''.join(map(str, cur.fetchone())))
                    new_balance_in = curr_balance_in + int(transfer_amount)
                    cur.execute(f"UPDATE card SET balance = {new_balance_out} WHERE number = {self.current_user[0]} AND {self.current_user[1]}")
                    cur.execute(f"UPDATE card SET balance = {new_balance_in} WHERE number = {transfer_to}")
                    conn.commit()
                    print("Success!")
                else:
                    print("Not enough money!")
        else:
            print("Probably you made mistake in the card number. Please try again!")
bank = MyBank()
bank.menu()