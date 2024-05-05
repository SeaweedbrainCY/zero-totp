from getpass import getpass



print("Welcome to this utility to update the server side encryption key.")
print("You can use this utility to re-encrypt your database stored data with a new key.")
print("This is useful if you want to rotate your keys.")
print("Please make sure to backup your database before running this utility.\n")
print("Did you backup your database? (y/N) : ", end="")
backup = input()
if backup.lower() != "y":
    print("Please backup your database before running this utility.")
    exit(1)

print("Please enter your old server side encryption key:", end="")
old_key = getpass()
print("Please enter your new server side encryption key:", end="")
new_key = getpass()
print("Please confirm your new server side encryption key:", end="")
new_key_confirm = getpass()

if new_key != new_key_confirm:
    print("The new key and the confirmation key do not match.")
    exit(1)



