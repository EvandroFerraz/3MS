from gurobipy import *
import psutil

class MajorityFunction:
    def __init__(self, tt, expression, gates, inverters, literals, cost, rootInverted):
        self.tt = tt
        self.expression = expression
        self.gates = gates
        self.inverters = inverters
        self.literals = literals
        self.cost = cost
        self.rootInverted = rootInverted


def buildTT(expression, n, ttSize, exprSize):
    
    TT = "" 
    for i in range(0,ttSize):
        b = 0
        vBinary = bin(i)[2:].zfill(n)
        for j in range(0,exprSize):
            if expression[j] == "'":
                for c in range(1,n+1):
                    if chr(c+64) == expression[j-1]:
                        if vBinary[c-1] == "1":
                            b = b-1
                        if vBinary[c-1] == "0":
                            b = b+1

            if expression[j] == "1":
                b = b+1

            for a in range (1,len(vBinary)+1):
                if chr(a+64) == expression[j]:
                    if vBinary[a-1] == '1':
                        b = b + 1          
        if exprSize == 2:
            if b == 1:
                TT = TT + "1"
            else:
                TT = TT + "0"
        else: 
            if b > 1:
                TT = TT + "1"
            else:
                TT = TT + "0"
    return TT

def buildPrimitives(primitiveList, n, ttSize):
            
    #set P0
    tt0 = "0"
    tt1 = "1"
    for i in range(1,ttSize):
        tt0 = tt0+"0"
        tt1 = tt1+"1"
    primitiveList.append(MajorityFunction(tt0,"0",0,0,0,0,False))
    primitiveList.append(MajorityFunction(tt1,"1",0,0,0,0,False))
    
    #set P1
    for i in range(1,n+1):
        tt1 = buildTT(chr(i+64)+" ",n,ttSize,2)
        tt0 = buildTT(chr(i+64)+"'",n,ttSize,2)      
        primitiveList.append(MajorityFunction(tt1,chr(i+64),0,0,1,1,False))
        primitiveList.append(MajorityFunction(tt0,chr(i+64)+"'",0,1,1,101,True))
    
    #setP2
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            #Patern M(A,B,0)
            tt1 = buildTT(chr(i+64)+chr(j+64)+"1",n,ttSize,3) #OR
            tt0 = buildTT(chr(i+64)+chr(j+64)+"0",n,ttSize,3) #AND
            primitiveList.append(MajorityFunction(tt1,"M("+chr(i+64)+","+chr(j+64)+",1)",1,0,2,10002,False))
            primitiveList.append(MajorityFunction(tt0,"M("+chr(i+64)+","+chr(j+64)+",0)",1,0,2,10002,False))  
            
            #Patern M(A',B,0) and M'(A,B',1) to apply Omega.I
            tt1 = buildTT(chr(i+64)+"'"+chr(j+64)+"1",n,ttSize,4) #OR
            tt0 = buildTT(chr(i+64)+"'"+chr(j+64)+"0",n,ttSize,4) #AND
            primitiveList.append(MajorityFunction(tt1,"M("+chr(i+64)+"',"+chr(j+64)+",1)",1,1,2,10102,False))
            primitiveList.append(MajorityFunction(tt0,"M("+chr(i+64)+"',"+chr(j+64)+",0)",1,1,2,10102,False))
            primitiveList.append(MajorityFunction(tt1,"M'("+chr(i+64)+","+chr(j+64)+"',0)",1,2,2,10202,True))
            primitiveList.append(MajorityFunction(tt0,"M'("+chr(i+64)+","+chr(j+64)+"',1)",1,2,2,10202,True))
            
             #Patern M(A,B',0) and M'(A',B,1) to apply Omega.I
            tt1 = buildTT(chr(i+64)+chr(j+64)+"'1",n,ttSize,4) #OR
            tt0 = buildTT(chr(i+64)+chr(j+64)+"'0",n,ttSize,4) #AND
            primitiveList.append(MajorityFunction(tt1,"M("+chr(i+64)+","+chr(j+64)+"',1)",1,1,2,10102,False))
            primitiveList.append(MajorityFunction(tt0,"M("+chr(i+64)+","+chr(j+64)+"',0)",1,1,2,10102,False))
            primitiveList.append(MajorityFunction(tt1,"M'("+chr(i+64)+"',"+chr(j+64)+",0)",1,2,2,10202,True))
            primitiveList.append(MajorityFunction(tt0,"M'("+chr(i+64)+"',"+chr(j+64)+",1)",1,2,2,10202,True))
            
            #Patern M'(A,B,0)
            tt1 = buildTT(chr(i+64)+"'"+chr(j+64)+"'1",n,ttSize,5) #OR
            tt0 = buildTT(chr(i+64)+"'"+chr(j+64)+"'0",n,ttSize,5) #AND
            primitiveList.append(MajorityFunction(tt1,"M'("+chr(i+64)+","+chr(j+64)+",0)",1,1,2,10102,True))
            primitiveList.append(MajorityFunction(tt0,"M'("+chr(i+64)+","+chr(j+64)+",1)",1,1,2,10102,True))
    
    #set P3
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            for k in range(j+1,n+1):
                #Patern M(A,B,C)
                tt1 = buildTT(chr(i+64)+chr(j+64)+chr(k+64),n,ttSize,3)
                primitiveList.append(MajorityFunction(tt1,"M("+chr(i+64)+","+chr(j+64)+","+chr(k+64)+")",1,0,3,10003,False))
                
                #Patern M'(A,B,C)
                tt1 = buildTT(chr(i+64)+"'"+chr(j+64)+"'"+chr(k+64)+"'",n,ttSize,6)
                primitiveList.append(MajorityFunction(tt1,"M'("+chr(i+64)+","+chr(j+64)+","+chr(k+64)+")",1,1,3,10103,True))
                
                #Patern M(A',B,C)
                tt1 = buildTT(chr(i+64)+"'"+chr(j+64)+chr(k+64),n,ttSize,4)
                primitiveList.append(MajorityFunction(tt1,"M("+chr(i+64)+"',"+chr(j+64)+","+chr(k+64)+")",1,1,3,10103,False))
                
                #Patern M(A,B',C')
                tt1 = buildTT(chr(i+64)+chr(j+64)+"'"+chr(k+64)+"'",n,ttSize,5)
                primitiveList.append(MajorityFunction(tt1,"M'("+chr(i+64)+"',"+chr(j+64)+","+chr(k+64)+")",1,2,3,10203,True))
                
                #Patern M(A,B',C)
                tt1 = buildTT(chr(i+64)+chr(j+64)+"'"+chr(k+64),n,ttSize,4)
                primitiveList.append(MajorityFunction(tt1,"M("+chr(i+64)+","+chr(j+64)+"',"+chr(k+64)+")",1,1,3,10103,False))
                
                #Patern M(A',B,C')
                tt1 = buildTT(chr(i+64)+"'"+chr(j+64)+chr(k+64)+"'",n,ttSize,5)
                primitiveList.append(MajorityFunction(tt1,"M'("+chr(i+64)+","+chr(j+64)+"',"+chr(k+64)+")",1,2,3,10203,True))
                
                #Patern M(A,B,C')
                tt1 = buildTT(chr(i+64)+chr(j+64)+chr(k+64)+"'",n,ttSize,4)
                primitiveList.append(MajorityFunction(tt1,"M("+chr(i+64)+","+chr(j+64)+","+chr(k+64)+"')",1,1,3,10103,False))
                
                #Patern M(A',B',C)
                tt1 = buildTT(chr(i+64)+"'"+chr(j+64)+"'"+chr(k+64),n,ttSize,5)
                primitiveList.append(MajorityFunction(tt1,"M'("+chr(i+64)+","+chr(j+64)+","+chr(k+64)+"')",1,2,3,10203,True))

    return primitiveList    

def printPrimitives(primitiveList):
    for i in range(0,len(primitiveList)):
        print(i, primitiveList[i].expression, primitiveList[i].tt)
       
def printMajorityExpression(d, r, m, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage):
    i = 0
    applyOmegaI = False
    outputFunction = ""
    baseCost = 10000
    if d == 2 and r == 3:
        for v in m.getVars():
            if i == 0:
                if v.x == 1:
                    applyOmegaI = True
                    outputFunction = "M'("
                else:
                    outputFunction = "M("   
            elif round(v.x,1) == 1 and i >= 2:
                print('%s %g' % (v.varName, v.x))
                if applyOmegaI == True:
                    if i == 2:
                        outputFunction = outputFunction + "1, "
                    elif i == 3:
                        outputFunction = outputFunction + "0, "
                    else:
                        outputFunction = outputFunction + primitiveList[i-2].expression.replace("'","",1) + ", "
                else:
                    outputFunction = outputFunction + primitiveList[i-2].expression + ", "
            i+=1
        outputFunction = outputFunction[:-2]
        outputFunction = outputFunction + ")"
            
    if d == 3:
        applyOmegaI2 = False
        if r == 5:
           baseCost = 20000
           inLevel1 = True         
           for v in m.getVars():
               if i == len(primitiveList)+6:
                   break
               if i == len(primitiveList)+5 and inLevel1 == True:
                   i = 5
                   inLevel1 = False
                   if applyOmegaI2 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if v.varName == "S[0]":
                   if v.x == 1:
                       applyOmegaI = True
                       outputFunction = "M'("
                   else:
                       outputFunction = "M("
               elif v.varName == "X2rootInverted" and v.x == 1:
                   applyOmegaI2 = True
               elif round(v.x,1) == 1 and i >= 5:
                   print('%s %g' % (v.varName, v.x))
                   if inLevel1 == True:
                       if applyOmegaI == True:
                           if i == 5:
                               outputFunction = outputFunction + "1, "
                           elif i == 6:
                               outputFunction = outputFunction + "0, "
                           else:
                               outputFunction = outputFunction + primitiveList[i-5].expression.replace("'","",1) + ", "
                       else:
                          outputFunction = outputFunction + primitiveList[i-5].expression + ", "
                   else:
                       if applyOmegaI2 == True:
                          if i == 5:
                              outputFunction = outputFunction + "1, "
                          elif i == 6:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-5].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-5].expression.replace("'","",1) + ", "
                          elif primitiveList[i-5].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-5].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-5].expression + ", "
               i+=1    
           outputFunction = outputFunction[:-2]
           outputFunction = outputFunction + "))"               
        elif r == 7:
            baseCost = 30000
            applyOmegaI3 = False
            inX1 = True 
            inX2 = False
            for v in m.getVars():
               if i == len(primitiveList)+9:
                   break
               if i == len(primitiveList)+8 and inX2 == True:
                   i = 8
                   inX2 = False
                   outputFunction = outputFunction[:-2]
                   outputFunction = outputFunction + "), " 
                   if applyOmegaI3 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if i == len(primitiveList)+8 and inX1 == True:
                   i = 8
                   inX1 = False
                   inX2 = True
                   if applyOmegaI2 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if v.varName == "S[0]":
                   if v.x == 1:
                       applyOmegaI = True
                       outputFunction = "M'("
                   else:
                       outputFunction = "M("
               elif v.varName == "X2rootInverted" and v.x == 1:
                   applyOmegaI2 = True
               elif v.varName == "X3rootInverted" and v.x == 1:
                   applyOmegaI3 = True
               elif round(v.x,1) == 1 and i >= 8:
                   print('%s %g' % (v.varName, v.x))
                   if inX1 == True:
                       if applyOmegaI == True:
                           if i == 8:
                               outputFunction = outputFunction + "1, "
                           elif i == 9:
                               outputFunction = outputFunction + "0, "
                           else:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("'","",1) + ", "
                       else:
                          outputFunction = outputFunction + primitiveList[i-8].expression + ", "
                   elif inX2 == True:
                       if applyOmegaI2 == True:
                          if i == 8:
                              outputFunction = outputFunction + "1, "
                          elif i == 9:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-8].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("'","",1) + ", "
                          elif primitiveList[i-8].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-8].expression + ", "
                   else:
                       if applyOmegaI3 == True:
                          if i == 8:
                              outputFunction = outputFunction + "1, "
                          elif i == 9:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-8].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("'","",1) + ", "
                          elif primitiveList[i-8].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-8].expression + ", "
                       
               i+=1    
            outputFunction = outputFunction[:-2]
            outputFunction = outputFunction + "))"     
        elif r == 9:
            baseCost = 40000
            applyOmegaI3 = False
            applyOmegaI1 = False
            inX1 = True 
            inX2 = False
            for v in m.getVars():
               if i == len(primitiveList)+12:
                   break
               if i == len(primitiveList)+11 and inX2 == True:
                   i = 11
                   inX2 = False
                   outputFunction = outputFunction[:-2]
                   outputFunction = outputFunction + "), " 
                   if applyOmegaI3 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if i == len(primitiveList)+11 and inX1 == True:
                   i = 11
                   inX1 = False
                   inX2 = True
                   outputFunction = outputFunction[:-2]
                   outputFunction = outputFunction + "), " 
                   if applyOmegaI2 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if v.varName == "S[0]":
                   if v.x == 1:
                       applyOmegaI = True
                       outputFunction = "M'("
                   else:
                       outputFunction = "M("
               elif v.varName == "X1rootInverted": 
                   if v.x == 1 and applyOmegaI == False:
                       applyOmegaI1 = True
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               elif v.varName == "X2rootInverted" and v.x == 1:
                   applyOmegaI2 = True
               elif v.varName == "X3rootInverted" and v.x == 1:
                   applyOmegaI3 = True
               elif round(v.x,1) == 1 and i >= 11:
                   print('%s %g' % (v.varName, v.x))
                   if inX1 == True:
                       if applyOmegaI1 == True:
                           if i == 11:
                               outputFunction = outputFunction + "1, "
                           elif i == 12:
                               outputFunction = outputFunction + "0, "
                           elif primitiveList[i-11].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("'","",1) + ", "
                           elif primitiveList[i-11].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-11].expression + ", "
                   elif inX2 == True:
                       if applyOmegaI2 == True:
                          if i == 11:
                              outputFunction = outputFunction + "1, "
                          elif i == 12:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-11].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("'","",1) + ", "
                          elif primitiveList[i-11].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-11].expression + ", "
                   else:
                       if applyOmegaI3 == True:
                          if i == 11:
                              outputFunction = outputFunction + "1, "
                          elif i == 12:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-11].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("'","",1) + ", "
                          elif primitiveList[i-11].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-11].expression + ", "
                       
               i+=1    
            outputFunction = outputFunction[:-2]
            outputFunction = outputFunction + "))" 
         
    Z = m.objVal + baseCost
    aux = (end_time - start_time)*0.5
    print(outputFunction)
    print('Obj: %g' % Z)
    print(end_time - start_time, "seconds")
    print(memoryUsage.memory_info().rss/1000000, "MB")
    
    if printInFile == True:
        if isHex == True:
            fileName = hex(int(tt, 2))
        else:
            fileName = tt
        f = open(fileName + ".txt", "w")
        f.write(outputFunction + "\n")
        f.write('Obj: %g' % Z + "\n")
        f.write(str(aux) + " seconds\n")
        f.write(str(memoryUsage.memory_info().rss/1000000) + " MB\n")
        f.close() 
        print("Results saved on 3MS directory.")
                    
def majorityExprToVHDL(d, r, m, primitiveList, tt, isHex):
    i = 0
    applyOmegaI = False
    outputFunction = ""
    if d == 2:
        for v in m.getVars():
            if i == 0:
                if v.x == 1:
                    applyOmegaI = True
                    outputFunction = "M'("
                else:
                    outputFunction = "M("   
            elif round(v.x,1) == 1 and i >= 2:
                print('%s %g' % (v.varName, v.x))
                if applyOmegaI == True:
                    if i == 2:
                        outputFunction = outputFunction + "1, "
                    elif i == 3:
                        outputFunction = outputFunction + "0, "
                    else:
                        outputFunction = outputFunction + primitiveList[i-2].expression.replace("'","",1) + ", "
                else:
                    outputFunction = outputFunction + primitiveList[i-2].expression + ", "
            i+=1
        outputFunction = outputFunction[:-2]
        outputFunction = outputFunction + ")"
            
    if d == 3:
        applyOmegaI2 = False
        if r == 5:
           inLevel1 = True         
           for v in m.getVars():
               if i == len(primitiveList)+6:
                   break
               if i == len(primitiveList)+5 and inLevel1 == True:
                   i = 5
                   inLevel1 = False
                   if applyOmegaI2 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if v.varName == "S[0]":
                   if v.x == 1:
                       applyOmegaI = True
                       outputFunction = "M'("
                   else:
                       outputFunction = "M("
               elif v.varName == "X2rootInverted" and v.x == 1:
                   applyOmegaI2 = True
               elif round(v.x,1) == 1 and i >= 5:
                   print('%s %g' % (v.varName, v.x))
                   if inLevel1 == True:
                       if applyOmegaI == True:
                           if i == 5:
                               outputFunction = outputFunction + "1, "
                           elif i == 6:
                               outputFunction = outputFunction + "0, "
                           else:
                               outputFunction = outputFunction + primitiveList[i-5].expression.replace("'","",1) + ", "
                       else:
                          outputFunction = outputFunction + primitiveList[i-5].expression + ", "
                   else:
                       if applyOmegaI2 == True:
                          if i == 5:
                              outputFunction = outputFunction + "1, "
                          elif i == 6:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-5].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-5].expression.replace("'","",1) + ", "
                          elif primitiveList[i-5].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-5].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-5].expression + ", "
               i+=1    
           outputFunction = outputFunction[:-2]
           outputFunction = outputFunction + "))"               
        elif r == 7:
            applyOmegaI3 = False
            inX1 = True 
            inX2 = False
            for v in m.getVars():
               if i == len(primitiveList)+9:
                   break
               if i == len(primitiveList)+8 and inX2 == True:
                   i = 8
                   inX2 = False
                   outputFunction = outputFunction[:-2]
                   outputFunction = outputFunction + "), " 
                   if applyOmegaI3 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if i == len(primitiveList)+8 and inX1 == True:
                   i = 8
                   inX1 = False
                   inX2 = True
                   if applyOmegaI2 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if v.varName == "S[0]":
                   if v.x == 1:
                       applyOmegaI = True
                       outputFunction = "M'("
                   else:
                       outputFunction = "M("
               elif v.varName == "X2rootInverted" and v.x == 1:
                   applyOmegaI2 = True
               elif v.varName == "X3rootInverted" and v.x == 1:
                   applyOmegaI3 = True
               elif round(v.x,1) == 1 and i >= 8:
                   print('%s %g' % (v.varName, v.x))
                   if inX1 == True:
                       if applyOmegaI == True:
                           if i == 8:
                               outputFunction = outputFunction + "1, "
                           elif i == 9:
                               outputFunction = outputFunction + "0, "
                           else:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("'","",1) + ", "
                       else:
                          outputFunction = outputFunction + primitiveList[i-8].expression + ", "
                   elif inX2 == True:
                       if applyOmegaI2 == True:
                          if i == 8:
                              outputFunction = outputFunction + "1, "
                          elif i == 9:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-8].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("'","",1) + ", "
                          elif primitiveList[i-8].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-8].expression + ", "
                   else:
                       if applyOmegaI3 == True:
                          if i == 8:
                              outputFunction = outputFunction + "1, "
                          elif i == 9:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-8].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("'","",1) + ", "
                          elif primitiveList[i-8].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-8].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-8].expression + ", "        
               i+=1    
            outputFunction = outputFunction[:-2]
            outputFunction = outputFunction + "))"     
        elif r == 9:
            applyOmegaI3 = False
            applyOmegaI1 = False
            inX1 = True 
            inX2 = False
            for v in m.getVars():
               if i == len(primitiveList)+12:
                   break
               if i == len(primitiveList)+11 and inX2 == True:
                   i = 11
                   inX2 = False
                   outputFunction = outputFunction[:-2]
                   outputFunction = outputFunction + "), " 
                   if applyOmegaI3 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if i == len(primitiveList)+11 and inX1 == True:
                   i = 11
                   inX1 = False
                   inX2 = True
                   outputFunction = outputFunction[:-2]
                   outputFunction = outputFunction + "), " 
                   if applyOmegaI2 == True and applyOmegaI == False:
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               if v.varName == "S[0]":
                   if v.x == 1:
                       applyOmegaI = True
                       outputFunction = "M'("
                   else:
                       outputFunction = "M("
               elif v.varName == "X1rootInverted": 
                   if v.x == 1 and applyOmegaI == False:
                       applyOmegaI1 = True
                       outputFunction = outputFunction + "M'("
                   else:
                       outputFunction = outputFunction + "M("
               elif v.varName == "X2rootInverted" and v.x == 1:
                   applyOmegaI2 = True
               elif v.varName == "X3rootInverted" and v.x == 1:
                   applyOmegaI3 = True
               elif round(v.x,1) == 1 and i >= 11:
                   print('%s %g' % (v.varName, v.x))
                   if inX1 == True:
                       if applyOmegaI1 == True:
                           if i == 11:
                               outputFunction = outputFunction + "1, "
                           elif i == 12:
                               outputFunction = outputFunction + "0, "
                           elif primitiveList[i-11].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("'","",1) + ", "
                           elif primitiveList[i-11].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-11].expression + ", "
                   elif inX2 == True:
                       if applyOmegaI2 == True:
                          if i == 11:
                              outputFunction = outputFunction + "1, "
                          elif i == 12:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-11].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("'","",1) + ", "
                          elif primitiveList[i-11].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-11].expression + ", "
                   else:
                       if applyOmegaI3 == True:
                          if i == 11:
                              outputFunction = outputFunction + "1, "
                          elif i == 12:
                              outputFunction = outputFunction + "0, "
                          elif primitiveList[i-11].rootInverted == True:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("'","",1) + ", "
                          elif primitiveList[i-11].rootInverted == False:
                               outputFunction = outputFunction + primitiveList[i-11].expression.replace("(","'(",1) + ", "
                       else:
                            outputFunction = outputFunction + primitiveList[i-11].expression + ", "
                       
               i+=1    
            outputFunction = outputFunction[:-2]
            outputFunction = outputFunction + "))" 
         
    print(outputFunction)
