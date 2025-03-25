def validate_preference(answer):
   if answer == "Yes":
       return True
   else:
       return False
  
def main():
   answer = input("Activate Professor Preference? Yes or No: ")
   print(validate_preference(answer))
  


if __name__ == "__main__":
   main()