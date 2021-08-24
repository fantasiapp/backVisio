import time

def buildStructure(name:str, steps:list, pdvs:list):
    if not steps:
        return [name, list(pdvs.keys())]
    nextKey = steps[0]
    children = [buildStructure(name, steps[1:], associatedPdvs) for name, associatedPdvs in diceByKey(nextKey, pdvs).items()]
    return [name, children]

def diceByKey(index, pdvs:list):
    dicedBykey = {}
    for id, pdv in pdvs.items():
        if pdv[index] not in dicedBykey:
            dicedBykey[pdv[index]] = {}
        dicedBykey[pdv[index]][id] = pdv
    return dicedBykey 

def diceSales(sales:list):
    dicedSales = {}
    start = time.time()
    for sale in sales:
        id = sale.pdv.id
        if id not in dicedSales:
            dicedSales[id] = []
        dicedSales[id].append([sale.industry.id, sale.product.id, sale.volume]) 
    print(f'duration: {time.time() - start}')
    return dicedSales

def formatPdv(pdvs:list, associatedSales:dict):
    return {pdv['id']:[value for key, value in pdv.items() if key != 'id'] + associatedSales.get(pdv['id'], [[]]) for pdv in pdvs}