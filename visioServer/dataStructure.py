def buildTree(name, steps:list, pdvs:list):
    if not steps:
        return [name, list(pdvs.keys())]
    nextKey = steps[0]
    children = [buildTree(name, steps[1:], associatedPdvs) for name, associatedPdvs in diceByKey(nextKey, pdvs).items()]
    return [name, children]

def diceByKey(index, pdvs:list):
    dicedBykey = {}
    for id, pdv in pdvs.items():
        if pdv[index] not in dicedBykey:
            dicedBykey[pdv[index]] = {}
        dicedBykey[pdv[index]][id] = pdv
    return dicedBykey 

def formatSales(sales:list):
    print('Formating sales...')
    dicedSales = {}
    for sale in sales:
        id = str(sale.pdv.id)
        if id not in dicedSales:
            dicedSales[id] = []
        dicedSales[id].append([sale.industry.id, sale.product.id, sale.volume])
    return dicedSales