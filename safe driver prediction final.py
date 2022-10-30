# -*- coding: utf-8 -*-
"""whale从头来过.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16hYd3A_TlVldkML7pKgqzFnWI2F5nGgE
"""

import numpy as np
import pandas as pd

from collections import Counter

import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (15,12)
plt.style.use('ggplot')

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

from sklearn.metrics import roc_curve, roc_auc_score

train = pd.read_csv('/content/drive/MyDrive/whaleagain/train.csv',index_col=0)

train

test = pd.read_csv('/content/drive/MyDrive/whaleagain/test.csv',index_col=0)

test

import pandas as pd
import numpy as np
from tabulate import tabulate

def meta(train,test,missing_values = -1,cols_ignore_missing = []):
    
    df = pd.concat([train,test]).reset_index(drop=True).fillna('未知')
    data = []
    for col in df.columns:
        # 定义role
        if col == 'target':
            role = 'target'
        elif col == 'id':
            role = 'id'
        else:
            role = 'feature'
        
        # 定义category
        if 'ind' in col:
            category = 'individual'
        elif 'car' in col:
            category = 'car'
        elif 'calc' in col:
            category = 'calculated'
        elif 'reg' in col:
            category = 'region'
        else:
            category = 'other'
        
        
        # 定义 level of measurements
        if 'bin' in col or col == 'target':
            level = 'binary'
        elif 'cat' in col[-3:] or col == 'id':
            level = 'nominal'
        elif df[col].dtype == 'float64' and df[col].replace(missing_values,np.nan).max()-df[col].replace(missing_values,np.nan).min() > 1:
            level = 'interval'
        elif df[col].dtype == 'float64' and df[col].replace(missing_values,np.nan).max()-df[col].replace(missing_values,np.nan).min() <= 1:
            level = 'ratio'
        elif df[col].dtype == 'int64':
            level = 'ordinal'
            
        # 定义 data type
        dtype = df[col].dtype
        
        # 定义 unique
        if col == 'id' or df[col].dtype == 'float64':
            uniq = 'Ignore'
        else:
            if col in cols_ignore_missing:
                uniq = df[col].nunique()
            else:
                uniq = df[col].replace({missing_values:np.nan}).nunique()
                
        # 定义 cardinality
        if uniq == 'Ignore':
            cardinality = 'Ignore'
        elif uniq <= 10:
            cardinality = 'Low Cardinality'
        elif uniq <= 30:
            cardinality = 'Medium Cardinality'
        else:
            cardinality = 'High Cardinality'
        
        # 定义 missing
        if col in cols_ignore_missing:
            missing = 0
        else:
            missing = sum(df[col] == missing_values)
            
        # 定义 missing percent
        missing_percent = f'{missing}({round(missing*100/len(df),2)}%)'
        
        # 定义 imputation
        if missing > df.shape[0]*0.4:
            imputation = 'remove'
        elif missing > 0:
            if level == 'binary' or level == 'nominal':
                imputation = ('mode')
            if level == 'ordinal':
                imputation = ('mode','median')
            if level == 'interval' or level == 'ratio':
                imputation = ('mode','median','mean')        
        else:
            imputation = "No Missing"
            
        # 定义 keep
        keep = True
        if col  == 'id' or imputation == 'remove':
            keep = False
        col_dict = {
            'colname': col,
            'role': role,
            'category': category,
            'level': level,
            'dtype': dtype,
            'cardinality': uniq,
            'cardinality_level':cardinality,
            'missing': missing,
            'missing_percent': missing_percent,
            'imputation':imputation,
            'keep': keep,
        }
        data.append(col_dict)
    meta = pd.DataFrame(data, columns=list(col_dict.keys()))
    meta.set_index('colname', inplace=True)
    
    return meta

def data_report(train,test,metadata,verbose = False):
    
    fullset = pd.concat([train,test]).reset_index(drop=True).fillna('未知')
    
    print(f"train总行数：{Fore.RED}{train.shape[0]}{Style.RESET_ALL} | test总行数：{Fore.BLUE}{test.shape[0]}{Style.RESET_ALL}")
    print(f"train总列数：{Fore.RED}{train.shape[1]}{Style.RESET_ALL} | test总列数：{Fore.BLUE}{test.shape[1]}{Style.RESET_ALL}")
    print(f"train总元素数：{train.size}")
    print(f"test总元素数：{test.size}")
    print('-'*50+ f"{Fore.RED}INFO{Style.RESET_ALL}"  + '-'*50)
    print('【train info】')
    train.info(verbose = verbose)
    print('-'*104)
    print('【test info】')
    test.info(verbose = verbose)
    
    if verbose:
    
        print('-'*48 + f"{Fore.RED}SUMMARY{Style.RESET_ALL}" + '-'*48)


        ############ SUMMARY #############
        print('*'*48 + f"{Fore.BLUE} COUNTS {Style.RESET_ALL}" + '*'*48)
        print('【Counts groupby role & level】'.upper())
        role_level_count = pd.DataFrame(
        {
            'count':metadata.groupby(['role','level']).size()
        }
        ).reset_index().sort_values(by = 'count',ascending=False)
        print(tabulate(role_level_count,tablefmt="grid",headers = ['role','level','count']))

        print('【Counts groupby role & category】'.upper())
        role_cate_count = pd.DataFrame(
        {
            'count':metadata.groupby(['role','category']).size()
        }
        ).reset_index().sort_values(by = 'count',ascending=False)
        print(tabulate(role_cate_count,tablefmt="grid",headers = ['role','category','count']))

        print('【Counts groupby role & cardinality_level】'.upper())
        role_cardinality_count = pd.DataFrame(
        {
            'count':metadata.groupby(['role','cardinality_level']).size()
        }
        ).reset_index().sort_values(by = 'count',ascending=False)
        print(tabulate(role_cardinality_count,tablefmt="grid",headers = ['role','cardinality_level','count']))


        print('*'*48 + f"{Fore.BLUE} MISSING {Style.RESET_ALL}" + '*'*48)
        print('【Cols to drop】'.upper())
        for col in metadata[metadata['keep'] == False].index:
            print(f" • {col}")

        print('【Cols to impute using (mode)】'.upper())
        for col in metadata[metadata['imputation'] == ('mode')].index:
            print(f" • {col}")

        print('【Cols to impute using (mode|median)】'.upper())
        for col in metadata[metadata['imputation'] == ('mode','median')].index:
            print(f" • {col}")

        print('【Cols to impute using (mode|median|mean)】'.upper())
        for col in metadata[metadata['imputation'] == ('mode','median','mean')].index:
            print(f" • {col}")

        print('*'*48 + f"{Fore.BLUE} CARDINALITY {Style.RESET_ALL}" + '*'*48)
        print('【Cols with medium cardinality】 ==> '.upper()+f'{Fore.YELLOW}PLEASE TAKE CARE OF USING ONEHOT-ENCODING{Style.RESET_ALL}')
        for col in metadata[metadata['cardinality_level'] == 'Medium Cardinality'].index:
            print(f" • {col}")

        print('【Cols with High cardinality】 ==> '.upper()+f'{Fore.YELLOW}PLEASE APPLY TARGET-ENCODING{Style.RESET_ALL}')
        for col in metadata[metadata['cardinality_level'] == 'High Cardinality'].index:
            print(f" • {Fore.GREEN}{col}{Style.RESET_ALL}")


        print('-'*42 + f"{Fore.RED}DESCRIPTIVE ANALYSIS{Style.RESET_ALL}" + '-'*42)
        conti_descrip = fullset[metadata[metadata['level'].isin(['interval','ratio'])].index].describe()
        print(tabulate(conti_descrip.T,tablefmt="grid",headers = conti_descrip.T.columns))

        print('-'*50 + f"{Fore.RED}META{Style.RESET_ALL}" + '-'*50)
        cols = ['role','category', 'level', 'dtype','cardinality', 'missing_percent','keep']
        print(tabulate(metadata[cols],tablefmt="grid",headers = cols))

#check missing values

metadata = meta(train,test)

missing_data = metadata[['missing','missing_percent','imputation']][metadata['missing']>0].sort_values(by = 'missing',ascending=False)

missing_data

cols_to_drop = missing_data[missing_data.imputation == 'remove'].index.to_list()

cols_to_imp = missing_data.index[2:].to_list()
cols_to_imp_3m = missing_data[missing_data.imputation == ('mode', 'median', 'mean')].index.to_list()
cols_to_imp_2m = missing_data[missing_data.imputation == ('mode', 'median')].index.to_list()
cols_to_imp_1m = missing_data[missing_data.imputation == ('mode')].index.to_list()

#multi variable filling

set1 = ['ps_reg_03','ps_car_14']

from sklearn.experimental import enable_iterative_imputer  # noqa
# now you can import normally from sklearn.impute
from sklearn.impute import IterativeImputer

from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor(n_estimators=10, random_state=123)

imp_mean = IterativeImputer(estimator=rf, missing_values=-1, random_state=0)

imp_mean = imp_mean.fit(train[set1])

train[set1] = imp_mean.transform(train[set1])

train

imp_mean2 = IterativeImputer(estimator=rf, missing_values=-1, random_state=0)

imp_mean2 = imp_mean2.fit(test[set1])

test[set1] = imp_mean2.transform(test[set1])

test['ps_reg_03']

missing_data[4:]
# 这些是还没填充的变量，我们就都用mode来填充，
# 因为最后两个缺失值太少了，没有影响。

cols = ["ps_car_07_cat", "ps_ind_05_cat","ps_car_09_cat","ps_ind_02_cat","ps_car_01_cat","ps_ind_04_cat","ps_car_02_cat","ps_car_11","ps_car_12"]

from sklearn.impute import SimpleImputer

mode_imputer = SimpleImputer(missing_values = -1, strategy='most_frequent')

mode_imputer=mode_imputer.fit(train[cols])

train[cols]=mode_imputer.transform(train[cols])

train[cols]=train[cols].astype('int64')

mode_imputer = SimpleImputer(missing_values = -1, strategy='most_frequent')

mode_imputer=mode_imputer.fit(test[cols])

test[cols]=mode_imputer.transform(test[cols])

test[cols]=test[cols].astype('int64')

# drop columns
train.drop(cols_to_drop,axis=1,inplace=True)

test.drop(cols_to_drop,axis=1,inplace=True)

# check out if we still have -1 
(train == -1).sum().sum()

train.to_csv('/content/drive/MyDrive/whaleagain/train_missing.csv')



test.to_csv('/content/drive/MyDrive/whaleagain/test_missing.csv')



#change the balance of the train dataset

def undersampling(df, desired_prop_rate = 0.15):
    # 获取target=0和1的index
    idx_class_0 = df.query('target == 0').index
    idx_class_1 = df.query('target == 1').index
    
    # 获取target=0和1的个数
    count_class_0 = df.target.value_counts()[0]
    count_class_1 = df.target.value_counts()[1]
    
    # 根据上面的公式计算undersampling rate
    undersampling_rate = (count_class_1*(1-desired_prop_rate))/(desired_prop_rate*count_class_0)
    undersampled_majority_size = round(undersampling_rate*count_class_0)
    
    print(f"关于target=0的欠采样比率为:【{round(undersampling_rate,2)}】")
    print(f"在欠采样之后，target=0的数量为：【{undersampled_majority_size}】")
    
    
    from sklearn.utils import shuffle
    # 用shuffle函数对target=0的所有数据打乱抽样，seed=100,抽样数为刚刚计算的值
    undersampled_idx = shuffle(idx_class_0,n_samples=undersampled_majority_size, random_state=100)
    
    # 把undersampling之后的idx和之前的target=1的idx合并，并在train里面根据idx把数据索引出来
    idx_total = idx_class_1.union(undersampled_idx)
    
    df = df.loc[idx_total].reset_index(drop=True)
    
    return df

undersampling(df = train)

undersampling(df = train).to_csv('/content/drive/MyDrive/whaleagain/train_balanced.csv')

#feature engineering  target encoder, WOE,etc

def add_noise(series, noise_level):
    return series * (1 + noise_level * np.random.randn(len(series)))

def target_encode(trn_series=None, 
                  tst_series=None, 
                  target=None, 
                  min_samples_leaf=1, 
                  smoothing=1,
                  noise_level=0):
    """
    Smoothing is computed like in the following paper by Daniele Micci-Barreca
    https://kaggle2.blob.core.windows.net/forum-message-attachments/225952/7441/high%20cardinality%20categoricals.pdf
    trn_series : training categorical feature as a pd.Series
    tst_series : test categorical feature as a pd.Series
    target : target data as a pd.Series
    min_samples_leaf (int) : minimum samples to take category average into account
    smoothing (int) : smoothing effect to balance categorical average vs prior  
    """ 
    assert len(trn_series) == len(target)
    assert trn_series.name == tst_series.name
    temp = pd.concat([trn_series, target], axis=1)
    # 集散这一列关于target的group mean
    averages = temp.groupby(by=trn_series.name)[target.name].agg(["mean", "count"])
    # 平滑
    smoothing = 1 / (1 + np.exp(-(averages["count"] - min_samples_leaf) / smoothing))
    # 计算所有target的mean
    prior = target.mean()
    # The bigger the count the less full_avg is taken into account
    # 如果某一类别的值的个数特别多，比如104这一类就有21255行，那么我们就要削减其关于target的mean的权值。
    averages[target.name] = prior * (1 - smoothing) + averages["mean"] * smoothing
    averages.drop(["mean", "count"], axis=1, inplace=True)
    
    # 分别对train和test计算mean
    ft_trn_series = pd.merge(
        trn_series.to_frame(trn_series.name),
        averages.reset_index().rename(columns={'index': target.name, target.name: 'average'}),
        on=trn_series.name,
        how='left')['average'].rename(trn_series.name + '_mean').fillna(prior)

    ft_trn_series.index = trn_series.index 
    ft_tst_series = pd.merge(
        tst_series.to_frame(tst_series.name),
        averages.reset_index().rename(columns={'index': target.name, target.name: 'average'}),
        on=tst_series.name,
        how='left')['average'].rename(trn_series.name + '_mean').fillna(prior)

    ft_tst_series.index = tst_series.index
    return add_noise(ft_trn_series, noise_level), add_noise(ft_tst_series, noise_level)

# 读取数据
train_idx = pd.read_csv("/content/drive/MyDrive/whaleagain/train_balanced.csv",index_col=0).index
test_idx = pd.read_csv("/content/drive/MyDrive/whaleagain/test_missing.csv",index_col=0).index

train=pd.read_csv("/content/drive/MyDrive/whaleagain/train_balanced.csv",index_col=0)
test=pd.read_csv("/content/drive/MyDrive/whaleagain/test_missing.csv",index_col=0)

train_idx   #因为id不见了！我balance之后train的id不见了。。为什么会这样。算了，到时候就按照前面是train后面是test好了。然后我们的test index是没问题的



from sklearn.model_selection import train_test_split

X_trn, X_val, y_trn, y_val = train_test_split(
    train.drop('target',axis=1), train.target, test_size=0.2, random_state=1996)

pip install colorama

import colorama
from colorama import Fore, Style

# Commented out IPython magic to ensure Python compatibility.
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
f_cats = [f for f in X_trn.columns if "_cat" in f]

min_samples_leaf = 100
smoothing = 10
noise_level=0.01

print(f"min_samples_leaf:{Fore.BLUE}{min_samples_leaf}{Style.RESET_ALL}\n"
      f"smoothing:{Fore.BLUE}{smoothing}{Style.RESET_ALL}\n"
      f"noise_level:{Fore.BLUE}{noise_level}{Style.RESET_ALL}")

print("-"*100)
print("%20s   %20s  %25s  %22s" % ("", f"{Fore.BLUE}编码前{Style.RESET_ALL}", 
                                   f"{Fore.RED}编码后{Style.RESET_ALL}", 
                                   f"{Fore.GREEN}前后变化{Style.RESET_ALL}"))
for f in f_cats:
    print("%-20s: " % f, end="")
    tf_scores = []
    f_scores = []
    for trn_idx, val_idx in folds.split(X_trn.values, y_trn.values):
        trn_f, trn_tgt = X_trn[f].iloc[trn_idx], y_trn.iloc[trn_idx]
        val_f, val_tgt = X_trn[f].iloc[trn_idx], y_trn.iloc[trn_idx]
        trn_tf, val_tf = target_encode(trn_series=trn_f, 
                                       tst_series=val_f, 
                                       target=trn_tgt, 
                                       min_samples_leaf=min_samples_leaf, 
                                       smoothing=smoothing,
                                       noise_level=noise_level)
        f_scores.append(max(roc_auc_score(val_tgt, val_f), 1 - roc_auc_score(val_tgt, val_f)))
        tf_scores.append(roc_auc_score(val_tgt, val_tf))
    print(" %.6f ± %.6f | %6f ± %.6f | %6f" 
#           % (np.mean(f_scores), np.std(f_scores), np.mean(tf_scores), np.std(tf_scores), np.mean(tf_scores)-np.mean(f_scores)))

train_encoded, test_encoded = target_encode(train["ps_car_11_cat"], 
                             test["ps_car_11_cat"], 
                             target=train.target, 
                             min_samples_leaf=100,
                             smoothing=10,
                             noise_level=0.01)

train["ps_car_11_cat_tar_enc"] = train_encoded.astype('float64')
test['ps_car_11_cat_tar_enc'] = test_encoded.astype('float64')
#train['target']=train['target'].astype('int64')

fullset = pd.concat([train,test],ignore_index=True)

fullset

metadata=meta(train,test)

continuous_cols = metadata[(metadata.level == 'interval')|(metadata.level == 'ratio') & (metadata.keep == True)].index.tolist()

continuous_cols

plt.figure(figsize = [20,10])   # 设置画布大小
sns.heatmap(data = fullset[continuous_cols].corr(), 
            vmax=1,
            center=0,
            square=True,
           annot = True,  # 显示文字
          fmt='.2f',      # 保留两位
           cmap = 'Blues',   # 颜色
           linewidths = .3,  # 分割线宽度
           cbar_kws={"shrink": .75})

#WOE

def woe_iv_encoding(data, feat, target, max_intervals, verbose = False):
    
    feat_bins = pd.qcut(x = data[feat], q = max_intervals, duplicates='drop')
    gi = pd.crosstab(feat_bins,data[target])
    gb = pd.Series(data=data[target]).value_counts()

    bad = gi[1]/gi[0]
    good = gb[1]/gb[0]

    # 计算woe
    woe = np.log(bad) - np.log(good)

    # 计算iv
    iv = (bad-good)*woe

    # 计算整个特征的iv
    f_iv = iv.sum()  # 5.2958917587905745
    if verbose == True:
        print(f"根据当前的间隔数{max_intervals}，特征{feat}所计算的总information value为：{f_iv}")
        print('='*80)

    # 进行映射操作
    dic = iv.to_dict()

    iv_bins = feat_bins.map(dic)  # 连续型变量离散化

    return iv_bins.astype('float64')

for col in continuous_cols: #from metadata
    fullset[f"{col}_woe"] = woe_iv_encoding(data = fullset, feat = col, target = 'target', max_intervals = 20)
    #sns.displot(fullset_copy[f"{col}_woe"])

fullset

#feature interation and feature selection

#train['ps_reg_03'].isnull().values.any() #TRAIN的也要改！

#fullset[continuous_cols]

from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)

interactions = pd.DataFrame(data=poly.fit_transform(fullset[continuous_cols]), 
                            columns=poly.get_feature_names_out(continuous_cols))


interactions.drop(continuous_cols, axis=1, inplace=True)  # Remove the original columns
# Concat the interaction variables to the train data
print('特征交互前，训练集有 {}个变量 '.format(fullset.shape[1]))
fullset = pd.concat([fullset, interactions], axis=1)
print('特征交互后，训练集有 {}个变量'.format(fullset.shape[1]))



from xgboost import XGBClassifier
from xgboost import plot_importance

plt.figure(figsize = [100,20])

X = fullset.loc[train.index].drop(['target'], axis=1)
y = fullset.loc[train.index].target

model = XGBClassifier()

model.fit(X, y)
# plot feature importance



# 特征工程的strategy作为key，对应的变量名组成的list作为value
from sklearn.feature_selection import SelectFromModel
feat_dict = {}
for thres in ['median','mean','1.25*mean']:
    model_select = SelectFromModel(model, threshold=thres, prefit=True)
    print(f'筛选前总计：{X.shape[1]}个特征')
    n_features = model_select.transform(X.values).shape[1]
    print(f'筛选后总计： {n_features}个特征【{thres}】')
    print('#'*60)
    selected_vars = list(X.columns[model_select.get_support()])
    feat_dict[thres] = selected_vars

types = ['weight', 'gain', 'cover', 'total_gain', 'total_cover']

for ty in types:
    feat_dict[ty] = list(model.get_booster().get_score(importance_type=ty).keys())

final_train = fullset.loc[train.index][feat_dict['1.25*mean']+['target']]
final_test = fullset.iloc[144627:][feat_dict['1.25*mean']]

final_test

#记得此时test_index跟id符合

test1=final_test.copy()

test1['id']=test_idx

test1

final_train.to_csv("/content/drive/MyDrive/whaleagain/final_train.csv")
final_test.to_csv("/content/drive/MyDrive/whaleagain/final_test.csv")



#model prediction



# 调参之后，较优的参数组合

from xgboost import XGBClassifier
MAX_ROUNDS = 400
OPTIMIZE_ROUNDS = False
LEARNING_RATE = 0.07
EARLY_STOPPING_ROUNDS = 50  

model = XGBClassifier(    
                        n_estimators=MAX_ROUNDS,
                        max_depth=4,
                        objective="binary:logistic",
                        learning_rate=LEARNING_RATE, 
                        subsample=.8,
                        min_child_weight=6,
                        colsample_bytree=.8,
                        scale_pos_weight=1.6,
                        gamma=10,
                        reg_alpha=8,
                        reg_lambda=1.3,
                     )

from sklearn.decomposition import PCA

from sklearn.model_selection import KFold

K = 10
kf = KFold(n_splits = K, random_state = 1, shuffle = True)
np.random.seed(1996)

def eval_gini(y_true, y_prob):
    y_true = np.asarray(y_true)
    y_true = y_true[np.argsort(y_prob)]
    ntrue = 0
    gini = 0
    delta = 0
    n = len(y_true)
    for i in range(n-1, -1, -1):
        y_i = y_true[i]
        ntrue += y_i
        gini += y_i * delta
        delta += 1 - y_i
    gini = 1 - 2 * gini / (ntrue * (n - ntrue))
    return gini

def gini_xgb(preds, dtrain):
    labels = dtrain.get_label()
    gini_score = -eval_gini(labels, preds)
    return [('gini', gini_score)]

def XGB_gini(df_train,tar_enc = True,pca = False):
    
    '''
    df_train: 已处理的训练集数据
    tar_enc: 是否对类别型变量使用target encoding
    pca: 是否使用pca
    '''    
    
    y = df_train.target
    X = df_train.drop('target',axis=1)
    
    
    y_valid_pred = 0*y
    y_test_pred = 0
    
    train = pd.concat([X,y],axis=1)
    for i, (train_index, test_index) in enumerate(kf.split(train)):

        # 分成训练集、验证集、测试集

        y_train, y_valid = y.iloc[train_index].copy(), y.iloc[test_index]
        X_train, X_valid = X.iloc[train_index,:].copy(), X.iloc[test_index,:].copy()        
        X_test = final_test.copy()
        
        
        if pca == True:
            n_comp = 20
            print('\nPCA执行中...')
            pca = PCA(n_components=n_comp, svd_solver='full', random_state=1001)
            X_train = pd.DataFrame(pca.fit_transform(X_train))
            X_valid = pd.DataFrame(pca.transform(X_valid))
            X_test = pd.DataFrame(pca.transform(final_test.copy()))
        print( f"\n{i}折交叉验证： ")
        
        if pca == False:
            if tar_enc == True:
                f_cat = [f for f in X.columns if '_cat' in f and 'tar_enc' not in  f]
                for f in f_cat:
                    X_train[f + "_avg"], X_valid[f + "_avg"], X_test[f + "_avg"] = target_encode(
                                                                    trn_series=X_train[f],
                                                                    val_series=X_valid[f],
                                                                    tst_series=X_test[f],
                                                                    target=y_train,
                                                                    min_samples_leaf=100,
                                                                    smoothing=10,
                                                                    noise_level=0
                                                                    )

    #     from category_encoders.target_encoder import TargetEncoder
    #     tar_enc = TargetEncoder(cols = f_cat).fit(X_train,y_train)
    #     X_train = tar_enc.transform(X_train) # 转换训练集
    #     X_test = tar_enc.transform(X_test) # 转换测试集


            X_train.drop(f_cat,axis=1,inplace=True)
            X_valid.drop(f_cat,axis=1,inplace=True)
            X_test.drop(f_cat,axis=1,inplace=True)


        # 对于当前折，跑XGB
        if OPTIMIZE_ROUNDS:
            eval_set=[(X_valid,y_valid)]
            fit_model = model.fit( X_train, y_train, 
                                   eval_set=eval_set,
                                   eval_metric=gini_xgb,
                                   early_stopping_rounds=EARLY_STOPPING_ROUNDS,
                                   verbose=False
                                 )
            print( "  Best N trees = ", model.best_ntree_limit )
            print( "  Best gini = ", model.best_score )
        else:
            fit_model = model.fit( X_train, y_train )

        # 生成验证集的预测结果
        pred = fit_model.predict_proba(X_valid)[:,1]
        print( "  normalized gini coefficent = ", eval_gini(y_valid, pred) )
        y_valid_pred.iloc[test_index] = pred

        # 累积计算测试集预测结果
        y_test_pred += fit_model.predict_proba(X_test)[:,1]

        del X_test, X_train, X_valid, y_train

    y_test_pred /= K  # 取各fold结果均值

    print( "\n整个训练集（合并）的normalized gini coefficent:" )
    print( "  final normalized gini coefficent = ", eval_gini(y, y_valid_pred) )
    
    return y_test_pred,eval_gini(y, y_valid_pred)

y_test_pred, gini_score = XGB_gini(df_train=final_train,tar_enc=True)

#it works!

submission = pd.DataFrame()
submission['id'] = test_idx
submission['target'] = y_test_pred

submission

submission.to_csv('/content/drive/MyDrive/whaleagain/xgb_submit2.csv', float_format='%.6f', index=False)

import numpy as np
import pandas as pd

def add_noise(series, noise_level):
    return series * (1 + noise_level * np.random.randn(len(series)))


def target_encode(trn_series=None,    # Revised to encode validation series
                  val_series=None,
                  tst_series=None,
                  target=None,
                  min_samples_leaf=1,
                  smoothing=1,
                  noise_level=0):
    """
    Smoothing is computed like in the following paper by Daniele Micci-Barreca
    https://kaggle2.blob.core.windows.net/forum-message-attachments/225952/7441/high%20cardinality%20categoricals.pdf
    trn_series : training categorical feature as a pd.Series
    tst_series : test categorical feature as a pd.Series
    target : target data as a pd.Series
    min_samples_leaf (int) : minimum samples to take category average into account
    smoothing (int) : smoothing effect to balance categorical average vs prior
    """
    assert len(trn_series) == len(target)
    assert trn_series.name == tst_series.name
    temp = pd.concat([trn_series, target], axis=1)
    # Compute target mean
    averages = temp.groupby(by=trn_series.name)[target.name].agg(["mean", "count"])
    # Compute smoothing
    smoothing = 1 / (1 + np.exp(-(averages["count"] - min_samples_leaf) / smoothing))
    # Apply average function to all target data
    prior = target.mean()
    # The bigger the count the less full_avg is taken into account
    averages[target.name] = prior * (1 - smoothing) + averages["mean"] * smoothing
    averages.drop(["mean", "count"], axis=1, inplace=True)
    # Apply averages to trn and tst series
    ft_trn_series = pd.merge(
        trn_series.to_frame(trn_series.name),
        averages.reset_index().rename(columns={'index': target.name, target.name: 'average'}),
        on=trn_series.name,
        how='left')['average'].rename(trn_series.name + '_mean').fillna(prior)
    # pd.merge does not keep the index so restore it
    ft_trn_series.index = trn_series.index
    ft_val_series = pd.merge(
        val_series.to_frame(val_series.name),
        averages.reset_index().rename(columns={'index': target.name, target.name: 'average'}),
        on=val_series.name,
        how='left')['average'].rename(trn_series.name + '_mean').fillna(prior)
    # pd.merge does not keep the index so restore it
    ft_val_series.index = val_series.index
    ft_tst_series = pd.merge(
        tst_series.to_frame(tst_series.name),
        averages.reset_index().rename(columns={'index': target.name, target.name: 'average'}),
        on=tst_series.name,
        how='left')['average'].rename(trn_series.name + '_mean').fillna(prior)
    # pd.merge does not keep the index so restore it
    ft_tst_series.index = tst_series.index
    return add_noise(ft_trn_series, noise_level), add_noise(ft_val_series, noise_level), add_noise(ft_tst_series, noise_level)