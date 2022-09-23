import copy
import math

def parse(input: str):
    #Takes the line the user inputted and tries to make a token out of it by splitting everything into list
    #Then take the returned list and make any numbers in a string format into a number format
    #And make lists in lists
    madeTokens = makeToken(input)
    #Check if the very very first character is a quote
    if madeTokens[0] == "'":
        #If it is then we change it out for a special string used later in the program
        return ["Literal single quote'"] + convertTokens(madeTokens[1:])
    else:
        return convertTokens(madeTokens)

def makeToken(input: str):
    #First replace all '(' with ' ( ' and ')' with ' ) '
    #This will come in handy when we split the string via any spaces.
    #Then we split the string into a list by taking any non space character and making it an element in the list
    return input.replace('(', ' ( ').replace(')', ' ) ').replace("'", " ' ").split()

def convertTokens(tokens: list):
    #Check if the list is empty
    if len(tokens) == 0:
        #If it is something is wrong. So we just return an error
        raise IndexError("Tokens has no length")

    #Otherwise we want to take the first element off of the list
    token = tokens.pop(0)

    #If that element is an opening parenthesis we want to make a new list inside of a list
    if token == "(":
        newList = []
        #Then we keep adding to the new list until we reach a closing parenthesis
        while tokens[0] != ")":
            #This is done through recurision of this function
            newList.append(convertTokens(tokens))
        #Next, pop off the closing parenthesis, because we have reached it
        tokens.pop(0)
        #Just return the new list
        return newList

    #If the element is a closing parenthesis then we have encoutered a syntax problem with lisp. Every ( is closed with a ) and removed
    elif token == ')':
        #So we return a syntax error if this is true
        raise ArithmeticError()
    #If non of the above is true, then we have encountered just a standard element. 
    else:
        #Then we want to change it from a string to a number if applicable
        return makeAtom(token)



def makeAtom(token: str):
    #We try to make it a number
    try: return int(token)
    #If it fails to make it a number i.e the input is: '<' 
    except ValueError:
        #Then we just return the symbol/character
        return token


def run(tokenized: list):
    #We want to run what the user inputted and get an output

    try:
        #We check if the length is 0 this is used in the case the input is ()
        if len(tokenized) == 0:
            #If it is then we just return NIL
            return "NIL"
            #Then we pop the top element of the list, will throw an error that we catch if it is not a list
        token = tokenized.pop(0)
        #Check if the token we just popped is a number
        if isinstance(token, int):
            #If the length of the to be processed token is greater than 0
            if len(tokenized) > 0:
                #We just return everything
                return [token] + tokenized
            return token

        
        #Format: ' anything
        #Just returns the top value of the list
        if token == "'":
            #Return the next thing in the list
            return tokenized.pop(0)

        #Used in the very specific scenario where the user starts their input with '
        #i.e '(2)
        elif token == "Literal single quote'":
            return "(" + " ".join([str(item) for item in tokenized]) + ")"

        
        #Format: set! variable value
        #Only works on variables that have been previously defined
        elif token == "set!":
            #First we take the variable we want to change
            setVar = tokenized.pop(0)
            #Then we check if the variable exists in the global set of variables
            if setVar in variables:
                #If the variable does exist then we take the value we want to assign it
                value = tokenized.pop(0)
                #Then we change the variable to the new value
                variables[setVar] = run(value)
                #Say the variable has been reassigned
                print("Variable " + str(setVar) + " reassigned")
                #Print out the new value by returning the value
                return value
            else:
                #If the variable doesn't exist we send an error back
                raise SyntaxError("set! could not find variable to set")


        #Format: define variable value
        #Used to make new variables
        elif token == "define":
            #First we take the name of the variable we want to define
            varName = tokenized.pop(0)
            #Then we take the value
            value = tokenized.pop(0)
            #We check if the value is a '
            if value == "'":
                #If it is, then we want to process it
                value = run([value] + tokenized)
                #Then we added the variable with the vale
                variables[varName] = value
            #Otherwise
            else:
                #We just added the new variable
                variables[varName] = run(value)
            #Print out the variable name that has been added
            print("Variable " + str(varName) + " added")
            #Return the new variables value
            return value


        #Format: if condition isMet isNotMet
        elif token == "if":
            #First we grab the condition of the if statement
            cond = tokenized.pop(0)
            #Then we check all of the variables
            for v in list(variables.keys()):
                j = 0
                #Then we check all of the characters in the condition
                for k in cond:
                    #If the character in the condition is equal to one of the variables the user assigned previously
                    if k == v:
                        #Then we change the value in the condition with the value of the variable
                        cond[j] = variables[v]
                    j = j + 1
            
            #Then we run the condition
            if condition(cond):
                #If the condition is true, then we run and return the true part of the statement
                return run(tokenized.pop(0))
            else:
                #If condition is false, then we run and return the false part of the statement
                return run(tokenized.pop(1))


        #Format: funcname arguments
        #We check if the users input is one of the functions defined        
        elif token in list(functions.keys()):
            #Get the arguemtns part of the function
            arguments = tokenized.pop(0)
            #Get the function: returns a list [arugments, body]
            functionCall = copy.deepcopy(functions[token])
            #Get the arguments
            funcCallArgu = functionCall.pop(0)
            #Get the body
            body = functionCall.pop(0)
            #Then we run the arguments of the function in case its in an expression format
            arguments = run(arguments)
            #Check if the amount of arguments is not empty
            if len(funcCallArgu) > 0:
                #If its not
                j = 0
                #Check if the arguments is no longer a list
                if isinstance(arguments, int):
                    #If it is no longer a list
                    #We pass if recursively to account for many lists in many lists
                    #This process will change all variables to their assigned value
                    body = recursiveDepth(body, arguments, funcCallArgu[j])
                #If the argument is a list
                else:
                    #Go through all of the arguments
                    for i in arguments:
                        #Go through everything in the body and change any variables with the value of the argument
                        body = recursiveDepth(body, i, funcCallArgu[j])
                        #Used to count the current variable to change
                        j = j + 1
                    #After the loop we just run the function then return
                return run(body)
            #If the function has no arguments, we just return the body of the function
            else:
                return run(body)

        #Format: defun name arugments body 
        elif token == "defun":
            #First grab the function name
            funcName = tokenized.pop(0)
            #Then grab the arguments of the function
            arguments = tokenized.pop(0)
            #Then grab the body of the function
            body = tokenized.pop(0)
            #Make a list
            arguBody = []
            #Add to the list the argmuents in the form of a list
            arguBody.append(arguments)
            #Add the body to the list in the form of a list
            arguBody.append(body)
            #Then add the new function
            functions[funcName] = arguBody
            #Print the function name being added
            return "Function " + str(funcName) + " added"
            

        #Format: + number number
        elif token == "+":
            #Returns the sum of two numbers, performs run for cases like: (+ (+ 2 3) 5)
            return int(run(tokenized.pop(0)) + run(tokenized.pop(0)))
        
        #Format: - number number
        elif token == "-":
            #Returns the one nubmer minus another, performs run for cases like: (- (- 2 3) 5)
            return int(run(tokenized.pop(0))) - int(run(tokenized.pop(0)))
        
        #Format: * number number
        elif token == "*":
            #Returns the product of two numbers, performs run for cases like: (* (* 2 3) 5)
            return int(run(tokenized.pop(0)) * run(tokenized.pop(0)))
        
        #Format: / number number
        elif token == "/":
            #Returns the integer division of two numbers, performs run for cases like: (/ (/ 2 3) 5)
            return int(run(tokenized.pop(0)) / run(tokenized.pop(0)))


        #Format: car '() or car (cdr )
        elif token == "car":
            #First we pop the next element in the list
            next = tokenized.pop(0)
            #Check if it is a ' 
            if next == "'":
                #If it is, then we want to process the list, then return the first value of the list
                return run([next] + tokenized).pop(0)
            #Otherwise, we process the input of the user
            return run(next).pop(0)
            

        #Format: cdr '() or cdr (car )
        elif token == "cdr":
            #First we pop the first value
            next = tokenized.pop(0)
            #Check if the value is a '
            if next == "'":
                #If it is, we want to process the list and return the list of everything after the fist element
                return run([next] + tokenized)[1:]
            #If it isn't then process the string and return everything after the first element
            return run(next)[1:]


        #Format: cons ' '() adds a single element to the list
        #Alternative format: cons '() '() adds a list to the list
        elif token == "cons":
            #How it looks parsed is below
            # 1:' 2:value/list 3:' 4:list
            #Find the first value indicated by the '
            #Surrounded by [] to make it a list, maybe its a list in a list
            first = [run(tokenized[0:2])]
            #Find the second value indicated by the '
            second = run(tokenized[2:4])
            #Return the sum of the two lists
            return first + second


        #Format: sqrt (expression or number)
        #Function that should already be built in
        elif token == "sqrt":
            #First run the next value incase its an expression
            #Then take the square root of it and return
            return math.sqrt(run(tokenized.pop(0)))
        

        #Format: pow number/expression number/expression
        #Function that should already be built in
        elif token == "pow":
            #First run the next two values incase they're an expression
            #Then square number one, by number two and return the value
            return math.pow(run(tokenized.pop(0)), run(tokenized.pop(0)))



        #Format for symbols: symbol statement
        #Format for and: and statement statement
        #Format for or: or statement statement
        #Format for not: not statement
        elif token == ">" or "<" or "=" or "!=" or "and" or "or" or "not":
            #See condition function below
            if condition([token] + tokenized) == True:
                #Return the string T for True
                return "T"
            else:
                #Return the string NIL for false
                return "NIL"

        #If nothing else works, just return the top element
        else:
            return token

    #Used to catch any exceptions that might happen
    except AttributeError:
        if isinstance(tokenized, int):
            return tokenized
        if tokenized in variables:
            return copy.deepcopy(variables[tokenized])
        if tokenized in functions:
            return functions[tokenized]
    except TypeError:
        if isinstance(tokenized, int):
            return tokenized
        if tokenized in variables:
            return copy.deepcopy(variables[tokenized])
        if tokenized in functions:
            return functions[tokenized]

    

#Used to recursivly search through a list to change any variables to the value it finds
def recursiveDepth(item, currentArgument, toChange):
    #First check if the item is a list
    if isinstance(item, list):
        #If it is, we make a new list
        newList = []
        
        #Then for everything in the list
        for element in item:
            #We pass the element recursively
            element = recursiveDepth(element, currentArgument, toChange)
            #Add the result to the new list
            newList.append(element)
            #Return the new list
        return newList
    #If item is not a list
    else:
        #Check if the item is the element to change
        if item == toChange:
            #If it is then change the variable to the value
            item = currentArgument
        #Return the maybe changed item
        return item
    


#A big statement to check any type of condition
def condition(cond: list):
    #We use a try incase the passed value is T or NIL
    try:
        #Pop the top symbol
        symbol = cond.pop(0)
        #Then check the symbol and perform the symbol with the next 2 values
        if symbol == ">":
            if cond.pop(0) > cond.pop(0):
                return True
            else:
                return False
        elif symbol == "<":
            if cond.pop(0) < cond.pop(0):
                return True
            else:
                return False
        elif symbol == "=":
            if cond.pop(0) == cond.pop(0):
                return True
            else:
                return False
        elif symbol == "!=":
            if cond.pop(0) != cond.pop(0):
                return True
            else:
                return False
        elif symbol == "and":
            if condition(cond.pop(0)) and condition(cond.pop(0)):
                return True
            else:
                return False
        elif symbol == "or":
            if condition(cond.pop(0)) or condition(cond.pop(0)):
                return True
            else:
                return False
        elif symbol == "not":
            if condition(cond.pop(0)):
                return False
            else:
                return True
    #If the user enters T or NIL
    except AttributeError:
        #T = True
        if cond == "T":
            return True
        #NIL = False
        elif cond == "NIL":
            return False


    

def main():
    #Make a dictionary to store variables and functions
    global variables
    variables = {}
    global functions
    functions = {}
    done = False

    #Create a new output file
    file = open("Lisp output.txt", "w")


    print("Welcome to a python clisp interpreter")
    #Loop until the user quits
    while not done :
        #Get users input
        userin = str(input("> "))
        #Check if they want to quit
        if userin == "(quit)":
            print("bye")
            done = True
            file.close()
            continue
        #Stop certain things from happening
        elif len(userin) == 3 and userin != "'()" and userin != "NIL":
            print("No function found")
            continue
        elif userin == ")":
            print("Cannot start with ')'")
            continue
        try:
            #Try to run the input and process it
            #Write the output to the output file
            parsing = run(parse(userin))
            file.write(str(parsing) + "\n")
            print(parsing)

        #Catach any errors and print a statement in response
        except SyntaxError:
            print("Syntax is incorrect")
        except IndexError:
            print("Input could not be determined")
        except ProcessLookupError:
            print("Could not find function")
        except ValueError:
            print("Input was not numbers")
        except ZeroDivisionError:
            print("Cannot divide by zero")
        except ArithmeticError:
            print("Too many ')'")



    
#Call the main function
if __name__ == "__main__":
    main()


