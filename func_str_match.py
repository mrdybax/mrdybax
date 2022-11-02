import pandas as pd
from fuzzywuzzy import process, fuzz
import numpy as np


def mesclar_valores_similares(dataframe, colunas, score_tresh = 75):
    dataframe = dataframe.copy(deep=True)
    if isinstance(colunas, str):
        colunas = [colunas]
    for coluna in colunas:
        valores_unicos = dataframe[coluna].value_counts().index.tolist()
        score_sort = [(x,) + i for x in valores_unicos for i in process.extract(x, valores_unicos, scorer=fuzz.token_sort_ratio)]
        similarity_sort = pd.DataFrame(score_sort, columns=['brand_sort','match_sort','score_sort'])
        similarity_sort['check_score'] = similarity_sort['score_sort'] >= score_tresh
        similarity_sort['check_brand'] = similarity_sort['brand_sort'] !=  similarity_sort['match_sort']
        similarity_sort['combination'] = similarity_sort['brand_sort'] + " " + similarity_sort['match_sort']
        similarity_sort['combination_sorted'] = [' '.join(sorted(x)) for x in similarity_sort['combination'].str.split()]
        
        high_score_sort = similarity_sort[(similarity_sort['check_score'] ==True)
                                        & (similarity_sort['check_brand'] == True)] \
                                        .drop_duplicates('combination_sorted')
        
        high_score_dict = high_score_sort.drop_duplicates('match_sort')
        
        while not high_score_dict.empty:   
            high_score_dict_it = high_score_dict[~high_score_dict['match_sort'].isin(high_score_dict['brand_sort'])]
            dict_replaces = pd.Series(high_score_dict_it['brand_sort'].values, index=high_score_dict_it['match_sort']).to_dict()
            dataframe[coluna] = dataframe[coluna].map(dict_replaces).fillna(dataframe[coluna])
            valores_unicos = dataframe[coluna].value_counts().index.tolist()
            score_sort = [(x,) + i for x in valores_unicos for i in process.extract(x, valores_unicos, scorer=fuzz.token_sort_ratio)]
            similarity_sort = pd.DataFrame(score_sort, columns=['brand_sort','match_sort','score_sort'])
            similarity_sort['check_score'] = similarity_sort['score_sort'] >= score_tresh
            similarity_sort['check_brand'] = similarity_sort['brand_sort'] !=  similarity_sort['match_sort']
            similarity_sort['combination'] = similarity_sort['brand_sort'] + " " + similarity_sort['match_sort']
            similarity_sort['combination_sorted'] = [' '.join(sorted(x)) for x in similarity_sort['combination'].str.split()]
            high_score_sort = similarity_sort[(similarity_sort['check_score'] ==True) & (similarity_sort['check_brand'] == True)] \
                                .drop_duplicates('combination_sorted')
    
            #quando o dict zerar, o loop fecha (não há mais valores pra serem repostos)
            high_score_dict = high_score_sort.drop_duplicates('match_sort')
            
    return dataframe