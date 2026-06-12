import math
import time
def sieve_prime_count(n):
    # return the number of primes not exceeding n using the Sieve of Eratosthenes
    # handle edge cases
    if n<2:
        return 0
    # assume all numbers from 2 to n are prime at first
    is_prime=[True]*(n+1)
    is_prime[0]=False
    is_prime[1]=False
    p=2
    while p*p<=n:
        if is_prime[p]:
            # start from p*p because smaller multiples of p have already been marked by smaller primes
            for multiple in range(p*p,n+1,p):
                is_prime[multiple]=False
        p+=1
    sum_primes=0
    for i in range(2,n+1):
        if is_prime[i]:
            sum_primes+=1
    return sum_primes

def measure_case(n):
    # measure the running time of counting primes up to n
    start=time.perf_counter()
    pi_n=sieve_prime_count(n)
    end=time.perf_counter()
    elapsed_ms=(end-start)*1000 # convert to milliseconds
    approximation=n/math.log(n)
    ratio=pi_n/approximation
    return pi_n,approximation,ratio,elapsed_ms

def main():
    test_values=[100,1000,10000,100000,1000000,10000000,100000000]
    # table header
    print(f"{'n':>10} {'pi(n)':>12} {'n/ln(n)':>15} {'pi(n)/(n/ln(n))':>20} {'time(ms)':>15}")

    for n in test_values:
        pi_n,approximation,ratio,elapsed_ms=measure_case(n)
        print(f"{n:>10} {pi_n:>12} {approximation:>15.1f} {ratio:>20.3f} {elapsed_ms:>15.3f}")

if __name__=="__main__":
    main()