def is_prime_trial(n):
    # determine whether n is prime using trial division
    # handle edge cases
    if n==1:
        return False
    if n==2: # the only even prime
        return True
    if n%2==0: # other even numbers are not prime
        return False
    primes=[2] # list of primes found so far
    i=3
    while i*i<=n:
        # 1. determine whether i is prime
        is_i_prime=True
        for p in primes:
            if p * p>i:
                break
            if i%p==0:
                is_i_prime=False
                break
        # 2. if i is prime, add it to the list of primes and test whether i divides n
        if is_i_prime:
            primes.append(i)
            if n%i==0:
                return False
        i+=2 # only test odd numbers
    return True

def find_mersenne_prime_exponents(limit_power):
    # find all prime exponents p such that 2^p-1 is prime and 2^p-1<=2^limit_power-1
    result=[]
    # since 2^p-1<=2^limit_power-1, p<=limit_power
    for p in range(2,limit_power+1):
        # for a Mersenne prime, p itself must be prime
        if is_prime_trial(p):
            mersenne_number=2**p-1
            if is_prime_trial(mersenne_number):
                result.append(p)
    return result

def main():
    # print the values of p for all Mersenne primes up to 2^40 - 1
    exponents=find_mersenne_prime_exponents(40)
    for p in exponents:
        print(p)

if __name__=="__main__":
    main()