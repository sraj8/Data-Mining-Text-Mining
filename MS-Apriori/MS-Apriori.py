import itertools
import re
from sys import argv
from operator import itemgetter
from collections import OrderedDict


def read_file(transaction_file, parameter_file):
    T = {}
    M = {}
    cannot_be_together = []
    must_have = []
    t = 1
    with open(transaction_file) as file:
        for transaction in file:
            transList = []
            transarr = re.findall(r'\{(.*?)\}',transaction)
            str1 = ''.join(transarr)
            T[int(t)] = [x.strip() for x in str1.split(',')]
            t = t + 1
        
    with open(parameter_file) as param:
        param_data = [line for line in param]
    for d in param_data:
        if "MIS" in d:
            match = re.match(r'^.*\((.*)\).*= (\d*\.\d*)', d)
            M[match.group(1)] = float(match.group(2))
        elif "SDC" in d:
            max_sup_diff = float(re.match(r'.*= (.*)', d).group(1))
        elif "must-have" in d:
            must_have = [x.strip() for x in d.split(':')[1].split('or')]
        elif "cannot_be_together" in d:
            cannot_be_together = re.findall(r'{.*?}',d)
            
    return T,M,max_sup_diff,cannot_be_together,must_have


def sortOnMIS(M):
    #sorted_m = sorted(M.items(), key=operator.itemgetter(1))
    sorted_m = sorted(M.items(), key=itemgetter(1))
    return sorted_m


def init_pass(T,sorted_m):
    L = []
    supp = calculate_support(T,sorted_m)
    first_sorted_m = sorted_m[0]
    len_t = len(T)
    L.append(first_sorted_m[0])
    mis_i = first_sorted_m[1]
    for m in sorted_m:
        if first_sorted_m[0] not in m:
            if supp[m[0]] >= mis_i:
                L.append(m[0])
    return L,supp



##final
def calculate_support(T,sorted_m):
    supp={}
    len_t = len(T)
    for m in sorted_m:
        count=0
        for t in T.values():
            if m[0] in t:
                count +=1
        supp[m[0]] = count/len_t
    return supp


def calculate_F1(L,sorted_m,supp,must_have,F,T):
    F1=[]
    newF=[]
    fNewCount=[]
    fNewTailCount=[]
    cCount=[]
    for l in L:
        F1=[]
        mis_l = [m[1] for m in sorted_m if m[0] == l]
        if supp[l] >= mis_l[0]:
            if must_have:
                if l in must_have:
                    F1.append(l)
                    
            else:
                F1.append(l)
                
        if F1:
            newF.append(F1)
                
                
            
            
    
    for f in newF:
        c_count = 0
        for t in T.values():
            if set(f).issubset(t):
                    c_count = c_count+1
        
        fNewCount.append(c_count)
                
                
            

    
    return newF,fNewCount



def MS_candidate_gen(f,supp,max_sup_diff,sorted_m):
    C = []
    for f1 in f:
        for i in range(f.index(f1)+1,len(f)):
            f2 = f[i]
            if f2[:len(f2)-1] == f1[:len(f1)-1] and f1[len(f1)-1] != f2[len(f2)-1]:
                if abs(supp[f1[len(f1)-1]] - supp[f2[len(f2)-1]]) <= max_sup_diff:
                    mis_f1 = [m[1] for m in sorted_m if m[0] == f1[len(f1)-1]]
                    mis_f2 = [m[1] for m in sorted_m if m[0] == f2[len(f2)-1]]
                    if mis_f2 >= mis_f1:
                        
                        unionf1f2 = list(f1)
                        unionf1f2.append(f2[len(f2)-1])
                        if unionf1f2 not in C:
                            C.append(unionf1f2)
                            c = C[len(C)-1]
                            tempS = list(genSubSets(c))
                            listS=[]
                            for s in tempS:
                                listS.append(list(s))
                            for s in listS:
                                mis_c2 = [m[1] for m in sorted_m if m[0] == c[1]]
                                mis_c1 = [m[1] for m in sorted_m if m[0] == c[0]] 
                                if set(c[0]).issubset(s) or mis_c2 == mis_c1:
                                    if tuple(s) in f:
                                        C.remove(c)
                
                                    
            
    return C   



def level2_candidate_gen(L,max_sup_diff,supp,sorted_m):
    C2 = []
    for l in L:
        mis_l = [m[1] for m in sorted_m if m[0] == l]
        if supp[l] >= mis_l[0]:
            count = L.index(l) + 1
            for i in range(count, len(L)):
                if (supp[L[i]] >= mis_l[0] and abs(supp[L[i]] - supp[l]) <= max_sup_diff) :
                    C2.append([l,L[i]])
            count = count + 1
    return C2


# In[282]:


def apply_item_constraints(F, cannot_be_together, must_have,fCount,fTailCount):
    F1 = []
    fNewCount=[]
    fNewTailCount=[]
    
    
    for f in F:

        if len(f) == 1:
            if must_have:
                if set(f).intersection(set(must_have)) or f in must_have:
                        i = F.index(f)
                        if fCount:
                            fNewCount.append(fCount[i])
                        if fTailCount:
                            fNewTailCount.append(fTailCount[i])
                        F1.append(f)
            else:
                i = F.index(f)
                if fCount:
                    fNewCount.append(fCount[i])
                if fTailCount:
                    fNewTailCount.append(fTailCount[i])
                F1.append(f)

            
        else:
            
            remove = False

            if must_have:
                if set(f).intersection(set(must_have)) or f in must_have:
                    for items in cannot_be_together:
                        itemsarr = re.findall(r'\{(.*?)\}',items)
                        itemstr = ''.join(itemsarr)
                        itemList = [x.strip() for x in itemstr.split(",")]
                        c = genSubSets(itemList)
                        for item in c:
                            if set(item).issubset(set(f)):
                                remove = True
                                break
                    if not remove:
                        i = F.index(f)
                        if fCount:
                            fNewCount.append(fCount[i])
                        if fTailCount:
                            fNewTailCount.append(fTailCount[i])
                        F1.append(f)

            else:
                for items in cannot_be_together:
                        itemsarr = re.findall(r'\{(.*?)\}',items)
                        itemstr = ''.join(itemsarr)
                        itemList = [x.strip() for x in itemstr.split(",")]
                        c = genSubSets(itemList)
                        for item in c:
                            if set(item).issubset(set(f)):
                                remove = True
                                break
                if not remove:
                    i = F.index(f)
                    if fCount:
                        fNewCount.append(fCount[i])
                    if fTailCount:
                        fNewTailCount.append(fTailCount[i])
                    F1.append(f)
                
           
               
    return F1,fNewCount,fNewTailCount


def ms_apriori(transaction_file,parameter_file,output_file):
    T,M,max_sup_diff,cannot_be_together,must_have = read_file(transaction_file,parameter_file)
    sorted_m = sortOnMIS(M)
    L,supp = init_pass(T,sorted_m)
    F=[]
    FCount=[]
    FtailCount=[[]]
    f,f1Count = calculate_F1(L,sorted_m,supp,must_have,F,T)
    FCount.append(f1Count)
    F.append(f)
    k = 1 
    C=[[]]
    while F[k-1]:
        
       
        if k == 1:
             C.append(level2_candidate_gen(L,max_sup_diff,supp,sorted_m))
        else:
            C.append(MS_candidate_gen(F[k-1],supp,max_sup_diff,sorted_m))
        
        cCount=[0]*len(C[k])
        fCount=[]
        tailCount = [0]*len(C[k])
        fTailCount=[]
        for t in T.values():
            c_count = 0 
            for c in C[k]:
                if set(c).issubset(t):
                    cCount[c_count]=cCount[c_count]+1
                if set(c[1:]).issubset(t):
                    tailCount[c_count] = tailCount[c_count]+1
                
                c_count = c_count+1
        c_count=0
        f=[]
        for c in C[k]:
            mis_c1 = [m[1] for m in sorted_m if m[0] == c[0]]
            if cCount[c_count]/len(T) >= mis_c1[0]:
                f.append(c)
                fCount.append(cCount[c_count])
                fTailCount.append(tailCount[c_count])
            c_count = c_count+1
            
        F.append(f)
        FCount.append(fCount)
        FtailCount.append(fTailCount)
        k =k+1
        
    
    newF=[]
    newFCount=[]
    newFtailCount=[]
    for i in range(0,len(F)):
        f,fCount,fTailCount = apply_item_constraints(F[i], cannot_be_together, must_have,FCount[i],FtailCount[i])        
        newF.append(f)
        newFCount.append(fCount)
        newFtailCount.append(fTailCount)
    
    
  
    
    newF.pop()
    newFCount.pop()
    newFtailCount.pop()
    display(output_file,newF,newFCount,newFtailCount)
    
    


from itertools import combinations

def genSubSets(s):

    c = []
    n = len(s)

    for i in range(1,n):
        c.extend(combinations(s, i + 1))
        

    return c


def display(output_file,F,count_list,tail_list):
    out_file = open(output_file, 'w')
    freq_no = 0
    i=0
    for f in F:
        if not f:
            del(F[i])
            del(count_list[i])
            del(tail_list[i])
        i=i+1
    
    print(F)
    i=0

    if len(F) == 0 and freq_no < 1:
        freq_no = freq_no + 1
        out_file.write(('Frequent ' + str(freq_no) + '-itemsets\n'))
        out_file.write("\n\n    Total number of frequent "+ str(freq_no) + "-itemsets = " + str(len(F)) + "\n\n\n")

    for k in range(len(F)):
        freq_no = freq_no + 1
        out_file.write(('Frequent ' + str(freq_no) + '-itemsets\n'))
        index = 0
        for f in F[k]:
                if k == 0:
                    out_file.write('\n    ' + str(count_list[0][F[k].index(f)]) + ' : {' + str(f[k]) + '}')
                else:
                    tail_count = 0
                    count = 0
                    tail_count = tail_list[k]
                    count = count_list[k]
                    out_file.write("\n    " + str(count[index]) + " : " + '{' + ', '.join(f) + '}')
                    out_file.write("\nTailcount = " + str(tail_count[index]))
                    index = index + 1
        out_file.write("\n\n    Total number of frequent "+ str(freq_no) + "-itemsets = " + str(len(F[k])) + "\n\n\n")
        
if __name__ == "__main__" :
    transaction_file = argv[1]
    parameter_file = argv[2]
    output_file = argv[3]
    ms_apriori(transaction_file, parameter_file, output_file)







