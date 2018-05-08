from random import randrange, randint
from time import sleep
import textwrap
import signal
import sys

small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31] # etc.
do_sleep = False

def test_prime(n, k):
    """Return True if n passes k rounds of the Miller-Rabin primality
    test (and is probably prime). Return False if n is proved to be
    composite.

    """
    if n < 2: return False
    for p in small_primes:
        if n < p * p: return True
        if n % p == 0: return False
    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2 # Floor
    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def find_mmi(e,phi):
    for i in range(0,phi-1):
        if (e*i) % phi == 1:
            return i
    return False

def find_prime(min, max):
    tested = []
    while True:
        i = randint(min,max)
        if i in tested:
            continue
        prime = test_prime(i, 1000)
        if prime:
            return i

def find_e(phi):
    prime = False
    while not prime:
        rand = randint(0, phi)
        prime = test_prime(rand,10000)
        if prime and phi % rand != 0:
            return rand

def calc_phi(p,q):
    return p*q - p - q + 1

def encrypt(m, pub):
    return m**pub['e'] % pub['mod']

def decrypt(c, d, mod):
    return c**d % mod

def interrupted(signum, frame):
    raise NameError("Stop waiting")

def prompt(timeleft):
    try:
        input("[Press Enter to continue] (" + timeleft + ")")
        return True
    except NameError:
        return False

def blankline():
    print()

def pause(seconds):
    blankline()
    signal.signal(signal.SIGALRM, interrupted)
    for i in range(0, seconds):
        timeleft = str(seconds - i)
        signal.alarm(1)
        if prompt(timeleft):
            signal.alarm(0)
            print("\033[A\r", end="") #Up one line and back to column 0
            break;
        signal.alarm(0)
        print("\r" + " "*80 + "\r", end="", flush=True) # Back to col 0, space out line and back to col 0 again

    signal.alarm(0)
    print("\r" + " "*80 + "\033[A\r", end="", flush=True) # Back to col0, space out line, move up one line and back to col0

def output(text):
    print (textwrap.fill(text, width=80))

def start():
    print("#######################################")
    print("### Welcome to Viktor RSA Lesson ####")
    print("#######################################")
    output("To begin, you need to know the basic concepts of private-public key cryptography. I have a blog post where I explain these concepts in greater detail, which you can find at https://viha.se/blog/tags/internet_cryptography?order=reverse")
    blankline()
    output("But the short version is that there are 2 keys: a private one and a public one. Stuff that is encrypted with the private key can only be decrypted with the public key, and vice verse. This means that Bob can generate a keypair, and put the public key on his website, then anyone who wants to send a message they only want Bob to be able to read, they enrypt the message with Bobs public key")
    blankline()
    pause(10)

    output("But lets just get into the gritty details.")
    blankline()
    output("To generate the keypair, we need two prime numbers. For the purpose of demonstration we'll use very small numbers.")
    output("Would you like me to generate these? (Answer no if you want to supply them yourself)")
    answered = False
    p = -1
    q = -1
    while not answered:
        tmp = input("[yes/no]: ")
        if tmp == "yes":
            answered = True
            p = find_prime(10,90)
            q = find_prime(10,90)
        elif tmp == "no":
            answered = True
            while p == -1:
                tmp = input("p: ")
                tmp = int(tmp)
                if not test_prime(tmp, 1000):
                    print(str(tmp) + " is not a prime number, try again..")
                else:
                    p = tmp
            while q == -1:
                tmp = input("q: ")
                tmp = int(tmp)
                if not test_prime(tmp, 1000):
                    print(str(tmp) + " is not a prime number, try again..")
                else:
                    q= tmp

        else:
            print("Answer yes or no:")

    mod = p*q
    blankline()
    output("So, what we have now are two prime numbers, lets call them p and q")
    blankline()
    output("  p = " + str(p))
    output("  q = " + str(q))
    blankline()
    pause(5)
    output("Next up, we'll compute the 'modulus' which is:")
    blankline()
    pause(5)
    output("  p * q = modulus")
    pause(5)
    output("  " + str(p) + " * " + str(q) + " = " + str(mod))
    pause(5)
    blankline()
    output("The next number we need is phi(modulus)")
    output("This is called the 'totient' of the product")
    output("The formula for this is this:")
    blankline()
    output("  (p -1)(q-1) = p*q - p - q + 1 = phi( modulus ) ")
    pause(5)
    output("or, using our numbers:")
    blankline()
    pause(5)
    phi = calc_phi(p,q)
    print("  " + str(p) + " * " + str(q) + " - "  + str(p) + " - " + str(q) + " + 1 = " + str(phi))
    blankline()
    pause(5)
    output("The next number we need we'll call e. This is a bit harder to calculate. The requirements for e is that it should be 1 < e < phi(modulus) and that it should be a 'coprime' of phi(modulus). Now I don't now what 'coprime' is, but according to wikipedia, if we choose e as a prime number, we only have to check that e is not a 'divisor' of phi(modulus).")
    pause(5)
    output("The fastest way to do this when dealing with numbers of this magnitude is to just brute force it.")
    blankline()
    pause(5)
    output("So what we do is that we pick a random number in the allowed range, and then using the Miller-Rabin primality test. If we find a prime number we check if phi(modulus) % x == 0. If this is true, then we try again until we find a number that is not a divisor.")
    blankline()
    pause(5)
    output("So back to our numbers, lets try to find a prime between 1 and " + str(phi))
    pause(5)
    e = find_e(phi)
    output("hmmm, lets see... " + str(e) + " will probably do...")
    pause(5)
    output("Is it in the range 1 < " + str(e) + " < " + str(phi) + "... yes that is correct")
    rem = phi % e
    pause(5)
    output("Is " + str(e) + " a divisor of " + str(phi) + "? Well... " + str(phi) + " % " + str(e) + " = " + str(rem) + ". So no, its not a divisor.")
    blankline()
    pause(5)
    output("The final number we must derive is called 'd'. This is the private key, and also the most difficult one to calculate. This one is also bruteforced, since the math is too hard for me to do.")
    blankline()
    pause(5)
    output("Here we need to get the 'modular multiplicative inverse'. This is the formula to find that:")
    blankline()
    pause(5)
    output("  (d * e) % phi(modulus) = 1")
    blankline()
    pause(5)
    output("How we do this is simple test all numbers d between 0 and phi(modulus) and check if they make that equation equal to 1.")
    d = find_mmi(e,phi)
    pause(5)
    output("In this case this number is : " + str(d))
    blankline()
    pause(5)
    output("So to summarize:")
    pause(1)
    output("We have the following numbers:")
    pause(1)
    output("  p = " + str(p))
    pause(1)
    output("  q = " + str(q))
    pause(1)
    output("  modulus = " + str(mod))
    pause(1)
    output("  phi(modulus) = " + str(phi))
    pause(1)
    output("  e = " + str(e))
    pause(1)
    output("  d = " + str(d))
    blankline()
    pause(5)
    output("The public key consists of both modulus and e, these are commonly refered to as the modulus and the exponent. And the private key is simply the number e")
    blankline()
    pause(5)
    output("The function to encrypt an integer m with the public key is this:")
    blankline()
    output("  m^e % modulus = c")
    blankline()
    pause(5)
    output("And the function to decrypt c with the private key is:")
    blankline()
    output("  c ^ d % modulus = m")
    blankline()
    pause(5)
    output("Although a limit of this is that the integer can only be as large as the modulus")
    blankline()
    pause(5)
    output("So lets put this to the test. What integer would you like to encrypt?")
    m = input("[0 - " + str(mod) + "]: ")
    m = int(m)
    pub = {'e': e, 'mod':mod}
    c = encrypt(m, pub)
    newm = decrypt(c, d, mod)
    blankline()
    output("  " + str(m) + "^" + str(e) + " % " + str(mod) + " = "  + str(c))
    blankline()
    output("So if we encrypt your number " + str(m) + " it becomes " + str(c) + ". This new integer can then be sent to Bob. He can then decrypt it using his private key like so:")
    blankline()
    pause(5)
    output("  " + str(c) + "^" + str(d) + " % " + str(mod) + " = " + str(newm))
    blankline()


if __name__ == "__main__":
    start()

def test():
    p = 23
    q = 19
    m = 64

    mod = p * q
    phi = calc_phi(p,q)
    e = find_e(phi)
    d = find_mmi(e, phi)
    print("mod: " + str(mod))
    print("phi: " + str(phi))
    print("e: " + str(e))
    print("d: " + str(d))

    pub = {'e': e, 'mod':mod}
    c = encrypt(m, pub)
    print("Message: " + str(m) + " encrypted: " + str(c))
    md = decrypt(c, d, mod)
    print("Decrypted: " + str(md))
    