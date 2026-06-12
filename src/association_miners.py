import time
import itertools
from collections import defaultdict

# ----------------------------------------------------
# 1. Algoritmo Apriori (Personalizado)
# ----------------------------------------------------
def mine_apriori(transactions, min_support):
    """
    Algoritmo Apriori personalizado.
    Retorna un diccionario de {itemset_frozenset: conteo_soporte}
    de tamaño 1, 2 y 3.
    """
    N = len(transactions)
    min_count = min_support * N
    frequent_itemsets = {}
    
    # L1: Frecuentes de tamaño 1
    counts = defaultdict(int)
    for t in transactions:
        for item in t:
            counts[item] += 1
    L1 = {frozenset([item]): count for item, count in counts.items() if count >= min_count}
    frequent_itemsets.update(L1)
    
    # L2: Frecuentes de tamaño 2
    C2 = set()
    L1_list = list(L1.keys())
    for i in range(len(L1_list)):
        for j in range(i+1, len(L1_list)):
            C2.add(L1_list[i].union(L1_list[j]))
            
    counts2 = defaultdict(int)
    for t in transactions:
        for candidate in C2:
            if candidate.issubset(t):
                counts2[candidate] += 1
    L2 = {c: count for c, count in counts2.items() if count >= min_count}
    frequent_itemsets.update(L2)
    
    # L3: Frecuentes de tamaño 3
    C3 = set()
    L2_list = list(L2.keys())
    for i in range(len(L2_list)):
        for j in range(i+1, len(L2_list)):
            union = L2_list[i].union(L2_list[j])
            if len(union) == 3:
                # Poda: si algún subconjunto de tamaño 2 no es frecuente, no es candidato
                subsets = [frozenset(s) for s in itertools.combinations(union, 2)]
                if all(s in L2 for s in subsets):
                    C3.add(union)
                    
    counts3 = defaultdict(int)
    for t in transactions:
        for candidate in C3:
            if candidate.issubset(t):
                counts3[candidate] += 1
    L3 = {c: count for c, count in counts3.items() if count >= min_count}
    frequent_itemsets.update(L3)
    
    return frequent_itemsets


# ----------------------------------------------------
# 2. Algoritmo Eclat (Personalizado - Enfoque Vertical)
# ----------------------------------------------------
def mine_eclat(transactions, min_support):
    """
    Algoritmo Eclat personalizado.
    Retorna un diccionario de {itemset_frozenset: conteo_soporte}
    utilizando cruce vertical de transacciones.
    """
    N = len(transactions)
    min_count = min_support * N
    frequent_itemsets = {}
    
    # Construir base de datos vertical: item -> set(IDs de transacciones)
    vertical_db = defaultdict(set)
    for idx, t in enumerate(transactions):
        for item in t:
            vertical_db[item].add(idx)
            
    def eclat_recurse(prefix_set, items_list, prefix_tids):
        for i, (item, tids) in enumerate(items_list):
            new_prefix = prefix_set.union([item])
            intersection_tids = prefix_tids.intersection(tids) if prefix_tids is not None else tids
            count = len(intersection_tids)
            if count >= min_count:
                frequent_itemsets[frozenset(new_prefix)] = count
                # Limitar recursión hasta tamaño 3 para que sea comparable
                if len(new_prefix) < 3:
                    suffix_items = items_list[i+1:]
                    eclat_recurse(new_prefix, suffix_items, intersection_tids)
                    
    # Filtrar frecuentes 1-itemsets
    items_list = sorted(
        [(item, tids) for item, tids in vertical_db.items() if len(tids) >= min_count],
        key=lambda x: x[0]
    )
    eclat_recurse(set(), items_list, None)
    return frequent_itemsets


# ----------------------------------------------------
# 3. Algoritmo FP-Growth (Personalizado)
# ----------------------------------------------------
class FPTreeNode:
    def __init__(self, item, parent):
        self.item = item
        self.parent = parent
        self.count = 0
        self.children = {}
        self.next_node = None

def mine_fpgrowth(transactions, min_support):
    """
    Algoritmo FP-Growth personalizado.
    Retorna un diccionario de {itemset_frozenset: conteo_soporte}.
    """
    N = len(transactions)
    min_count = min_support * N
    
    # 1. Contar frecuencias y filtrar frecuentes 1-itemsets
    counts = defaultdict(int)
    for t in transactions:
        for item in t:
            counts[item] += 1
            
    frequent_items = {item: count for item, count in counts.items() if count >= min_count}
    if not frequent_items:
        return {}
        
    # Ordenar items frecuentes de forma descendente por conteo
    freq_items_sorted = sorted(frequent_items.keys(), key=lambda x: (frequent_items[x], x), reverse=True)
    
    # 2. Función auxiliar para construir el árbol
    def build_tree(trans_list):
        root = FPTreeNode(None, None)
        header_table = {item: None for item in freq_items_sorted}
        
        for t in trans_list:
            t_filtered = [item for item in t if item in frequent_items]
            t_filtered.sort(key=lambda x: (frequent_items[x], x), reverse=True)
            
            curr = root
            for item in t_filtered:
                if item in curr.children:
                    curr.children[item].count += 1
                else:
                    new_node = FPTreeNode(item, curr)
                    new_node.count = 1
                    curr.children[item] = new_node
                    
                    # Actualizar puntero en la tabla cabecera
                    if header_table[item] is None:
                        header_table[item] = new_node
                    else:
                        node = header_table[item]
                        while node.next_node is not None:
                            node = node.next_node
                        node.next_node = new_node
                curr = curr.children[item]
        return root, header_table

    root, header_table = build_tree(transactions)
    frequent_itemsets = {}
    
    # 3. Minar el árbol recursivamente
    def mine_tree(tree_root, h_table, prefix):
        sorted_header_items = sorted(
            [item for item in h_table if h_table[item] is not None],
            key=lambda x: (frequent_items[x] if x in frequent_items else 0, x)
        )
        
        for item in sorted_header_items:
            new_prefix = prefix.union([item])
            
            node = h_table[item]
            support_count = 0
            while node is not None:
                support_count += node.count
                node = node.next_node
                
            if support_count >= min_count:
                frequent_itemsets[frozenset(new_prefix)] = support_count
                
                # Limitar recursión hasta tamaño 3
                if len(new_prefix) < 3:
                    # Obtener base de patrones condicionales
                    cond_pattern_base = []
                    node = h_table[item]
                    while node is not None:
                        path = []
                        parent = node.parent
                        while parent.item is not None:
                            path.append(parent.item)
                            parent = parent.parent
                        path.reverse()
                        if path:
                            for _ in range(node.count):
                                cond_pattern_base.append(path)
                        node = node.next_node
                        
                    # Contar frecuencias condicionales
                    cond_counts = defaultdict(int)
                    for path in cond_pattern_base:
                        for p_item in path:
                            cond_counts[p_item] += 1
                            
                    cond_frequent = {p_item: c for p_item, c in cond_counts.items() if c >= min_count}
                    if cond_frequent:
                        cond_root = FPTreeNode(None, None)
                        cond_header_table = {item_name: None for item_name in freq_items_sorted if item_name in cond_frequent}
                        
                        for path in cond_pattern_base:
                            path_filtered = [p_item for p_item in path if p_item in cond_frequent]
                            path_filtered.sort(key=lambda x: (frequent_items[x] if x in frequent_items else 0, x), reverse=True)
                            
                            curr = cond_root
                            for p_item in path_filtered:
                                if p_item in curr.children:
                                    curr.children[p_item].count += 1
                                else:
                                    new_node = FPTreeNode(p_item, curr)
                                    new_node.count = 1
                                    curr.children[p_item] = new_node
                                    if cond_header_table[p_item] is None:
                                        cond_header_table[p_item] = new_node
                                    else:
                                        n = cond_header_table[p_item]
                                        while n.next_node is not None:
                                            n = n.next_node
                                        n.next_node = new_node
                                curr = curr.children[p_item]
                        mine_tree(cond_root, cond_header_table, new_prefix)
                        
    mine_tree(root, header_table, set())
    return frequent_itemsets


# ----------------------------------------------------
# 4. Función de Comparación (Benchmark)
# ----------------------------------------------------
def benchmark_miners(transactions, min_support):
    """
    Ejecuta los 3 algoritmos, mide sus tiempos y verifica
    si los itemsets frecuentes y sus soportes son idénticos.
    """
    # 1. Apriori
    t0 = time.perf_counter()
    apriori_res = mine_apriori(transactions, min_support)
    t1 = time.perf_counter()
    apriori_time = t1 - t0
    
    # 2. FP-Growth
    t0 = time.perf_counter()
    fp_res = mine_fpgrowth(transactions, min_support)
    t1 = time.perf_counter()
    fp_time = t1 - t0
    
    # 3. Eclat
    t0 = time.perf_counter()
    eclat_res = mine_eclat(transactions, min_support)
    t1 = time.perf_counter()
    eclat_time = t1 - t0
    
    # Verificación de consistencia
    apriori_keys = set(apriori_res.keys())
    fp_keys = set(fp_res.keys())
    eclat_keys = set(eclat_res.keys())
    
    match_all = (apriori_keys == fp_keys == eclat_keys)
    if match_all:
        for k in apriori_keys:
            if not (apriori_res[k] == fp_res[k] == eclat_res[k]):
                match_all = False
                break
                
    result_summary = {
        "apriori_time": apriori_time,
        "fpgrowth_time": fp_time,
        "eclat_time": eclat_time,
        "itemsets_count": len(apriori_keys),
        "results_match": match_all
    }
    
    return result_summary, apriori_res

