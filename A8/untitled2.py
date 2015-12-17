# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 23:58:10 2015

@author: Home
"""
 
def ans(x):
    if x >= 0 and x < 2147483647:
        temp = list(str(x))
        z = sum(int(x) for x in temp)
        if len(str(z)) > 1:
            z = ans(z)
    return z
    [ans(z) if len(str(sum(int(x) for x in temp))) > 1 else z]
'''
    temp = bin(x)
    if x < 0 :
        y = temp[3:]
        #[w if str(w) == 'nan' else w for w in temp]
        y = ['0' if str(w)=='1' else '1' for w in y]
        y.insert(0,'-0b')
        x = int(''.join(y),2)
        print x
    else:
        y = temp[2:]
        y = ['0' if str(w)=='1' else '1' for w in y]
        y.insert(0,'0b')
        
        x = int(''.join(y),2)
        
        print x
        '''
    
x = int(raw_input('Number:'))
z = ans(x)
print z


    