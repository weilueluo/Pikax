

import os, math



def test():
    l = [1,3,7,2,3,12,5,1,1,1,11,2,16,1,2,3,1,1,1]
    l = [1,2,11,2,5]
    l = _rearrange_into_optimal_chunks(l)
    print(l)


if __name__ == '__main__':
    test()
