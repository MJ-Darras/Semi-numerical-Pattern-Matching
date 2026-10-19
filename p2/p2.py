import sys
import random

# this function reads a file and return its content
def read_file(file_path: str):
    f = open(file_path, 'r')
    line = f.readlines()
    f.close()
    return line

class SNPM:
    """
    Semi-Numerical Pattern Matching
    """
    def __init__(self, i_str: str, pat: str) -> None:
        self.i_str = i_str
        self.pat = pat
        self.n = len(self.i_str)
        self.m = len(self.pat)

        self.t = max(32, self.m)
        self.b = 128
        self.p = None

        self.r_pat = 0
        self.r_str_j = 0

        self.instances = []
    
    def mod_exp(self, base:int, power: int, modulus: int) -> int:
        """
        Implementation of the modular exponentiation method.
        """
        # new base accumulator 
        b = base
        # power binary
        pb = bin(power)[2:]
        # power binary length
        pb_len = len(pb)
        # result accumulator
        result = 1

        b = b % modulus
        if(pb[-1] == "1"):
            result = (result * b) % modulus
        # print(f"iteration {1}\tb->{b}\tpb->{pb[-1]}\tr->{result}\n")

        for i in range(pb_len-2, -1, -1):
            b = (b * b) % modulus
            if(pb[i] == "1"):
                result = (result * b) % modulus
            # print(f"iteration {pb_len - i}\tb->{b}\tpb->{pb[i]}\tr->{result}\n")
        return result
    
    def randomized_primality(self, n: int, k:int) -> bool:
        """
        A function that tests if a number is prime.
        Inputs:
        n -> input number
        k -> a parameter that determines the accuracy of the test
        Output:
        True  -> probably prime
        False -> composite
        """
        # check for 1 or lower
        if(n <= 1):
            return False

        # check for 2 and 3
        if(n == 2 or n == 3):
            return True

        # check for even numbers
        if(n % 2 == 0):
            return False

        s = 0
        t = n - 1

        # 2^s * t = n - 1
        while (t % 2 == 0):
            s += 1
            t //= 2

        for i in range(k):
            a = random.randint(2, n-2)
            xo = self.mod_exp(a, t, n) 
            xs = 0
            
            # case 4
            if (xo == 1):
                continue
            
            xip = xo
            
            for j in range(1, s+1):
                xi = (xip * xip) % n
                
                if (xi == 1):
                    # case 2
                    if(xip != n-1):
                        return False
                    # case 3
                    else:
                        xs = 1
                        break
                xip = xi
            # case 1
            if(xs != 1):
                return False
            
        return True
    
    def find_p(self) -> int:
        result = None
        while True:
            # print((1 << (self.t-1)), ((1 << self.t) - 1))

            ri = random.randint((1 << (self.t-1)), ((1 << self.t) - 1))
            # print(ri, "\n")
            
            if(self.randomized_primality(ri, 64)):
                # print(f"{ri} is prime!")
                result = ri
                break
        return result
    
    def pattern_match(self):
        self.p = self.find_p()
        # print(self.p)

        p_beta = 1
        
        # compute r(pat[1...m])
        for k in range(self.m - 1, -1, -1):
            self.r_pat = (self.r_pat + (ord(self.pat[k]) * p_beta)) % self.p
            p_beta = (p_beta * self.b) % self.p
        
        # print(f"\n{self.pat}->{self.r_pat}\n")

        # compute r(i_str[1...n])
        s_beta = 1
        for c in range(self.m - 1, -1, -1):
            self.r_str_j = (self.r_str_j + (ord(self.i_str[c]) * s_beta)) % self.p
            s_beta = (s_beta * self.b) % self.p

        # print(f"{self.i_str[0]}{self.i_str[:self.m]} {self.i_str[self.m-1]}\t{self.r_str_j} {self.r_pat} {self.r_str_j == self.r_pat}")
        
        # First m chars in i_str
        if (self.r_str_j == self.r_pat):
            found = True
            for x in range(self.m):
                if(self.i_str[x] != self.pat[x]):
                    found = False
                    break

            if(found):
                self.instances.append(str(1))

        # m minus one
        mmo_beta = self.mod_exp(self.b, self.m-1, self.p)

        # All other possible instances
        for j in range(1,self.n-self.m+1):
            hash = self.r_str_j 
            # remove most significant char
            hash = (hash - (ord(self.i_str[j-1]) * mmo_beta)) % self.p
            # shift all chars by beta
            hash = (hash * self.b) % self.p
            # add new char
            hash = (hash + ord(self.i_str[j+self.m-1])) % self.p 
            # set r of str to new hash
            self.r_str_j = hash

            if(hash == self.r_pat):
                f = True
                for y in range(j, j+self.m):
                    if(self.i_str[y] != self.pat[y-j]):
                        f = False
                        break
                if(f):
                    self.instances.append(str(j + 1))

            # print(f"{self.i_str[j-1]}{self.i_str[j:j+self.m]} {self.i_str[j+self.m-1]}\t{hash} {self.r_pat} {hash == self.r_pat}")
        
        with open("output_a2q2.txt", "w") as f:
            f.write("\n".join(self.instances))


if __name__ == '__main__':
    #retrieve the file paths from the commandline arguments
    _, filename1, filename2 = sys.argv

    # since we know the program takes two arguments
    file1content = read_file(filename1)
    file2content = read_file(filename2)

    snpm = SNPM(file1content[0], file2content[0])
    snpm.pattern_match()

    # print("\nContent of first file : ", file1content[0])
    # print("\nContent of second file : ", file2content[0])