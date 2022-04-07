from gurobipy import *
from majorityFunction import *
import time, psutil, math
import os

#Use any other character than x to declare don't cares, since the prefix "0x" can generate conflit if the "x" is also used to declare don't cares
#You can only declare don't cares in binary format;
#You still have to validate the inputs, asking for a rewriting of the input if its not a valid binary or hex (size of string for instance).
print("Type a input truth table(3<=n<=10) in binary or hexadecimal format: ")
print("Example: 01001111 or 0x4f")
tt = input()
    
isHex = False  
start_time = time.time()
memoryUsage = psutil.Process()
printInFile = False

if tt[:2] == "0x": #verifies if string is in hex format
    isHex = True
    ttSize = len(tt)*4 #define string size
    tt = bin(int(tt, 16))[2:]
    tt = tt.zfill(ttSize-len(tt)-1) #fills up the necessary 0's to the string
    
n = int(math.log(len(tt),2))
        
primitiveList = []
buildPrimitives(primitiveList, n, len(tt))
covered = False
    
for i in range(0,len(primitiveList)):
    if primitiveList[i].tt == tt:
        print(primitiveList[i].expression)
        covered = True
        break
            
#Model for 2-level functions        
if covered == False:
    rootInvertedPrimitives = []
    primitivesCost = dict()
    for i in range(0,len(primitiveList)):
        primitivesCost[i] = primitiveList[i].cost
        
        if primitiveList[i].rootInverted == True:
            rootInvertedPrimitives.append(i)
                        
    d2 = Model("D2")
    S = d2.addVars(2, lb=0, vtype=GRB.BINARY, name="S")
    X = d2.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X")
            
    d2.addConstr(X.sum() == 3, "c1")
    d2.setObjective(X.prod(primitivesCost) - 100*(S.sum()), GRB.MINIMIZE)
                
    for t in range(0,len(tt)):
        auxTT = []
        for i in range(0,len(primitiveList)):
            if primitiveList[i].tt[t] == '1':
                auxTT.append(i)
        if tt[t] == '1':
            d2.addConstr(quicksum(X[i] for i in auxTT) >= 2, name="m"+str(t)) 
        elif tt[t] == '0':
            d2.addConstr(quicksum(X[i] for i in auxTT) <= 1, name="m"+str(t))
                
    d2.addConstr((S[0] == 1) >> (X[0] + X[1] + quicksum(X[i] for i in rootInvertedPrimitives) == 3))
    d2.addConstr((S[1] == 1) >> (quicksum(X[i] for i in rootInvertedPrimitives) == 3))
                
    d2.optimize()
                
    if d2.status != GRB.INFEASIBLE:
        end_time = time.time()
        printMajorityExpression(2, 3 , d2, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage)
    else:
        hasGate = []
        hasGateCost = dict()
        noGateCost = dict()
        for i in range(0,len(primitiveList)):
            if primitiveList[i].cost >= 10000:
                hasGate.append(i)
                hasGateCost[i] = primitiveList[i].cost
                noGateCost[i] = 0
            else:
                hasGateCost[i] = 0
                noGateCost[i] = primitiveList[i].cost
                        
        r5 = Model("R5")
        r5.Params.method = 0
        S = r5.addVars(4, lb=0, vtype=GRB.BINARY, name="S")
        X2rootInverted = r5.addVar(lb=0, vtype=GRB.BINARY, name="X2rootInverted")
        X1 = r5.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X1") #level 1
        X2 = r5.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X2") #level 2
        W = r5.addVars(len(primitiveList), lb=0, vtype=GRB.BINARY, name="W") #len(primitiveList) ao invés de len(hasGate) é o correto?
                
        r5.addConstr(X1.sum() == 2, "c1")
        r5.addConstr(X2.sum() == 3, "c2")
                
        for t in range(0,len(tt)):
            auxTT = []
            for i in range(0,len(primitiveList)):
                if primitiveList[i].tt[t] == '1':
                    auxTT.append(i)
            if tt[t] == '1':
                r5.addConstr(quicksum(X1[i] for i in auxTT)*3 + quicksum(X2[i] for i in auxTT) >= 5, name="m"+str(t)) 
            elif tt[t] == '0':
                r5.addConstr(quicksum(X1[i] for i in auxTT)*3 + quicksum(X2[i] for i in auxTT) <= 4, name="m"+str(t))    
                
        r5.addConstr((X2rootInverted == 1) >> (quicksum(X2[i] for i in rootInvertedPrimitives) >= 2)) 
        r5.addConstr((S[0] == 1) >> (X2rootInverted + X1[0] + X1[1] + quicksum(X1[i] for i in rootInvertedPrimitives) == 3)) #Omega.I applied to level 1 considering constants and level 2 root inversion
        r5.addConstr((S[1] == 1) >> (X2rootInverted + quicksum(X1[i] for i in rootInvertedPrimitives) == 3)) #Omega.I applied to level 1 without considering constants but considering level 2 root inversion
        r5.addConstr((S[2] == 1) >> (X2[0] + X2[1] + quicksum(X2[i] for i in rootInvertedPrimitives) == 3)) #Omega.I applied to level 2 considering constants
        r5.addConstr((S[3] == 1) >> (quicksum(X2[i] for i in rootInvertedPrimitives) == 3)) #Omega.I applied to level 2 without considering constants
                        
        r5.addConstrs((W[i] == 1) >> (X1[i] + X2[i] >= 1) for i in hasGate)
        r5.addConstrs((W[i] == 0) >> (X1[i] + X2[i] == 0) for i in hasGate)
                
        r5.setObjective(W.prod(hasGateCost) + X1.prod(noGateCost) + X2.prod(noGateCost) - 100*(S.sum()), GRB.MINIMIZE)
                
        r5.optimize()
                
        if r5.status == GRB.INFEASIBLE or r5.objVal >= 50000:
            r7 = Model("R7")
            r7.Params.method = 3
            S = r7.addVars(6, lb=0, vtype=GRB.BINARY, name="S")
            X2rootInverted = r7.addVar(lb=0, vtype=GRB.BINARY, name="X2rootInverted")
            X3rootInverted = r7.addVar(lb=0, vtype=GRB.BINARY, name="X3rootInverted")
            X1 = r7.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X1") #level 1
            X2 = r7.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X2") #level 2 func 1
            X3 = r7.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X3") #level 2 func 2
            W = r7.addVars(len(primitiveList), lb=0, vtype=GRB.BINARY, name="W") #len(primitiveList) ao invés de len(hasGate) é o correto? 
            tX2 = r7.addVars(len(tt), lb=0, vtype=GRB.BINARY, name="tX2")
            r7.addConstr(X1.sum() == 1, "c1")
            r7.addConstr(X2.sum() == 3, "c2")
            r7.addConstr(X3.sum() == 3, "c3")
                    
            for t in range(0,len(tt)):
                auxTT = []
                for i in range(0,len(primitiveList)):
                    if primitiveList[i].tt[t] == '1':
                        auxTT.append(i)
                r7.addConstr((tX2[t] == 1) >> (quicksum(X2[i] for i in auxTT) >= 2))
                r7.addConstr((tX2[t] == 0) >> (quicksum(X2[i] for i in auxTT) <= 1))
                if tt[t] == '1':
                    r7.addConstr((quicksum(X1[i] for i in auxTT) + tX2[t])*3 + quicksum(X3[i] for i in auxTT) >= 5, name="m"+str(t)) 
                elif tt[t] == '0':
                    r7.addConstr((quicksum(X1[i] for i in auxTT) + tX2[t])*3 + quicksum(X3[i] for i in auxTT) <= 4, name="m"+str(t))   
                            
            r7.addConstr((X2rootInverted == 1) >> (quicksum(X2[i] for i in rootInvertedPrimitives) >= 2)) 
            r7.addConstr((X3rootInverted == 1) >> (quicksum(X3[i] for i in rootInvertedPrimitives) >= 2))
            r7.addConstr((S[0] == 1) >> (X2rootInverted + X3rootInverted + X1[0] + X1[1] + quicksum(X1[i] for i in rootInvertedPrimitives) == 3)) 
            r7.addConstr((S[1] == 1) >> (X2rootInverted + X3rootInverted + quicksum(X1[i] for i in rootInvertedPrimitives) == 3))
            r7.addConstr((S[2] == 1) >> (X2[0] + X2[1] + quicksum(X2[i] for i in rootInvertedPrimitives) == 3))
            r7.addConstr((S[3] == 1) >> (quicksum(X2[i] for i in rootInvertedPrimitives) == 3))
            r7.addConstr((S[4] == 1) >> (X3[0] + X3[1] + quicksum(X3[i] for i in rootInvertedPrimitives) == 3)) 
            r7.addConstr((S[5] == 1) >> (quicksum(X3[i] for i in rootInvertedPrimitives) == 3))
                    
            r7.addConstrs((W[i] == 1) >> (X1[i] + X2[i] + X3[i] >= 1) for i in hasGate)
            r7.addConstrs((W[i] == 0) >> (X1[i] + X2[i] + X3[i] == 0) for i in hasGate)
                
            r7.setObjective(W.prod(hasGateCost) + X1.prod(noGateCost) + X2.prod(noGateCost) + X3.prod(noGateCost) - 100*S.sum(), GRB.MINIMIZE)
                    
            r7.optimize()
                
            if r5.status != GRB.INFEASIBLE and r7.status != GRB.INFEASIBLE:
                end_time = time.time()
                if r5.objVal <= r7.objVal:
                    printMajorityExpression(3, 5 , r5, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage)
                else:
                    printMajorityExpression(3, 7 , r7, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage)
            elif r7.status == GRB.INFEASIBLE or r7.objVal >= 70000: 
                r9 = Model("R9")
                r9.Params.method = 5
                S = r9.addVars(8, lb=0, vtype=GRB.BINARY, name="S")
                X1rootInverted = r9.addVar(lb=0, vtype=GRB.BINARY, name="X1rootInverted")
                X2rootInverted = r9.addVar(lb=0, vtype=GRB.BINARY, name="X2rootInverted")
                X3rootInverted = r9.addVar(lb=0, vtype=GRB.BINARY, name="X3rootInverted")
                X1 = r9.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X1") #level 2 func 1
                X2 = r9.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X2") #level 2 func 2
                X3 = r9.addVars(len(primitiveList), lb=0, vtype=GRB.INTEGER, name="X3") #level 2 func 3
                xI = r9.addVar(lb=0, vtype=GRB.BINARY, name="xI") #all functions in lvl 2 are inverted then root level 1 also is
                W = r9.addVars(len(primitiveList), lb=0, vtype=GRB.BINARY, name="W") #len(primitiveList) ao invés de len(hasGate) é o correto?
                tX1 = r9.addVars(len(tt), lb=0, vtype=GRB.BINARY, name="tX1")
                tX2 = r9.addVars(len(tt), lb=0, vtype=GRB.BINARY, name="tX2")
                r9.addConstr(X1.sum() == 3, "c1")
                r9.addConstr(X2.sum() == 3, "c2")
                r9.addConstr(X3.sum() == 3, "c3")
                        
                for t in range(0,len(tt)):
                    auxTT = []
                    for i in range(0,len(primitiveList)):
                        if primitiveList[i].tt[t] == '1':
                            auxTT.append(i)   
                        
                    r9.addConstr((tX1[t] == 1) >> (quicksum(X1[i] for i in auxTT) >= 2))
                    r9.addConstr((tX1[t] == 0) >> (quicksum(X1[i] for i in auxTT) <= 1))
                    r9.addConstr((tX2[t] == 1) >> (quicksum(X2[i] for i in auxTT) >= 2))
                    r9.addConstr((tX2[t] == 0) >> (quicksum(X2[i] for i in auxTT) <= 1))
                        
                    if tt[t] == '1':
                        r9.addConstr((tX1[t] + tX2[t])*3 + quicksum(X3[i] for i in auxTT) >= 5, name="m"+str(t))   
                    elif tt[t] == '0':
                        r9.addConstr((tX1[t] + tX2[t])*3 + quicksum(X3[i] for i in auxTT) <= 4, name="m"+str(t))
                            
                r9.addConstr((X1rootInverted == 1) >> (quicksum(X1[i] for i in rootInvertedPrimitives) >= 2))
                r9.addConstr((X2rootInverted == 1) >> (quicksum(X2[i] for i in rootInvertedPrimitives) >= 2)) 
                r9.addConstr((X3rootInverted == 1) >> (quicksum(X3[i] for i in rootInvertedPrimitives) >= 2))
                r9.addConstr((S[0] == 1) >> (X1[0] + X1[1] + quicksum(X1[i] for i in rootInvertedPrimitives) == 3)) 
                r9.addConstr((S[1] == 1) >> (quicksum(X1[i] for i in rootInvertedPrimitives) == 3))
                r9.addConstr((S[2] == 1) >> (X2[0] + X2[1] + quicksum(X2[i] for i in rootInvertedPrimitives) == 3))
                r9.addConstr((S[3] == 1) >> (quicksum(X2[i] for i in rootInvertedPrimitives) == 3))
                r9.addConstr((S[4] == 1) >> (X3[0] + X3[1] + quicksum(X3[i] for i in rootInvertedPrimitives) == 3)) 
                r9.addConstr((S[5] == 1) >> (quicksum(X3[i] for i in rootInvertedPrimitives) == 3))
                r9.addConstr((xI == 1) >> (X1rootInverted + X2rootInverted + X3rootInverted == 3))
                    
                r9.addConstrs((W[i] == 1) >> (X1[i] + X2[i] + X3[i] >= 1) for i in hasGate)
                r9.addConstrs((W[i] == 0) >> (X1[i] + X2[i] + X3[i] == 0) for i in hasGate)
                
                r9.setObjective(W.prod(hasGateCost) + X1.prod(noGateCost) + X2.prod(noGateCost)+ X3.prod(noGateCost) - 100*(S.sum() + xI), GRB.MINIMIZE)
                r9.optimize()
                    
                if r7.status != GRB.INFEASIBLE and r9.status != GRB.INFEASIBLE:
                    end_time = time.time()
                    if r7.objVal <= r9.objVal:
                        printMajorityExpression(3, 7 , r7, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage)
                    else:
                        printMajorityExpression(3, 9 , r9, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage)
                elif r9.status != GRB.INFEASIBLE:
                    end_time = time.time()
                    printMajorityExpression(3, 9 , r9, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage)
                else:
                    print("d4")       
            else:
                end_time = time.time()
                printMajorityExpression(3, 7 , r7, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage)
        else:
            end_time = time.time()
            printMajorityExpression(3, 5 , r5, primitiveList, printInFile, tt, isHex, start_time, end_time, memoryUsage)