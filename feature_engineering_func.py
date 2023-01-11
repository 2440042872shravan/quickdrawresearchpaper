import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy import vectorize
import json
import time
np.random.seed(32113)
#Example of loading the json data
#category = "airplane"
#filepath = "./data/raw_data/full%2Fraw%2Fairplane.ndjson"
#df = pd.read_json(filepath, lines=True)

# This is to esemble the country code
def ensemble_function_for_feature_engineering_(df,category,sample=60000,purpose='word',\
                                            countries = ['US','BR','RU','KR']):
    time_to_start = time.time()
    df_test1 = feature_eng_pt1(df)
    df_test2 = feature_eng_pt2(df_test1)
    df_test3 = feature_eng_pt3(df_test2)
    df_subset = feature_eng_pt4(df_test3)
    df_subset2 = feature_eng_pt5(df_test3)
    df_final = pd.concat([df_test3,df_subset,df_subset2], axis=1)

    if purpose == 'word':
        df_final.index = range(len(df_final))
        random_ind = np.random.choice(list(df_final.index), sample, replace=False)
        df_final = df_final.loc[list(random_ind)]
    elif purpose == 'country':
        df_final = df_final[(df_final['countrycode']==countries[0])|\
                (df_final['countrycode']==countries[1])|\
               (df_final['countrycode']==countries[2])|(df_final['countrycode']==countries[3])]
    df_final.index = df_final['key_id']
    df_final.to_pickle("./data/MY_feature_{}.pkl".format(category)) 
    print("--- %s seconds ---" % (time.time() - time_to_start))

#
def The_feature_engineering__for_CNN(df,category,sample=60000,purpose='word',countries = ['US','BR','RU','KR']):
    start_time = time.time()
    #runs CNN feature engineering functions
    df_1 = CNN_feat_eng_pt1(df)
    df_2 = CNN_feat_eng_pt2(df_1)
    #If purpose = 'word' it will randomly select 'sample' number of datapoints from df_final
    if purpose == 'word':
        df_2.index = range(len(df_2))
        random_ind = np.random.choice(list(df_2.index), sample, replace=False)
        df_2 = df_2.loc[list(random_ind)]
    #If purpose = 'country', it will correct all datapoints from the selected countries.
    elif purpose == 'country':
        df_2 = df_2[(df_2['countrycode']==countries[0])|(df_2['countrycode']==countries[1])|\
               (df_2['countrycode']==countries[2])|(df_2['countrycode']==countries[3])]
    df_2.index = df_2['key_id']
    df_2.to_pickle("./data/{}.pkl".format(category))
    print("--- %s seconds ---" % (time.time() - start_time))
    return df_2



def feature_eng_pt1(df_cf):

    # create feature "stroke_number"
    df_cf['stroke_number']=df_cf['drawing'].str.len()

    #create feature "final_time"
    df_cf['final_time'] = [df_cf.loc[index,'drawing']\
                [df_cf.stroke_number[index]-1][2][-1] for index in df_cf.index]

    #setting boolean and changing recognized features to 1 and 0.
    b_loon = {True: 1, False:0}
    df_cf['recognized'] = df_cf['recognized'].map(b_loon)

    #filtered data by stroke number, recognized and final time features
    df_cf = df_cf[(df_cf['recognized']==1) & (df_cf['stroke_number'] <= 15)]
    df_cf = df_cf[(df_cf['final_time']<=20000)]
    return df_cf

def feature_eng_pt2(df_cf):
    X = {}
    Y = {}
    Xperst = {}
    Yperst = {}
    Ymax ={}
    time = {}
    tperst = {}
    Tdiff = {}
    ttnum_dp = {}
    Tdiffmax = {}
    Tdiffmin = {}
    Tdiffstd = {}
    dpps = {}
    dppps = {}
    dp_max = {}
    dp_min = {}
    dp_std = {}
    sumtimeps = {}

    for i in df_cf.index:
        num = df_cf.stroke_number[i]
        #store X,Y,time of the stroke in a temp list
        Xt = [df_cf.loc[i,'drawing'][stroke][0] for stroke in range(num)]
        Yt = [df_cf.loc[i,'drawing'][stroke][1] for stroke in range(num)]
        tt = [df_cf.loc[i,'drawing'][stroke][2] for stroke in range(num)]
        # calculate the difference between final and initial time of a stroke
        Tdifftemp = [(df_cf.loc[i,'drawing'][stroke][2][-1] - df_cf.loc[i,'drawing'][stroke][2][0])\
                     for stroke in range(num)]
        # calculate the length of the stroke list
        dpps_temp = [len(df_cf.loc[i,'drawing'][stroke][2]) for stroke in range(num)]

        #store all X(or Y or time) info of an image into a list
        Xtemp = [item for stroke in Xt for item in stroke]
        Ytemp = [item for stroke in Yt for item in stroke]
        time[i] = [item for stroke in tt for item in stroke]

        #normalizing X and Y
        Xmintemp = np.min(Xtemp)-1
        Xmaxtemp = np.max(Xtemp)+1
        Ymintemp = np.min(Ytemp)-1
        #runs user defined function array_normalizer to normalize
        Xnorm = _array_normalizer(Xtemp, Xmintemp,Xmaxtemp,Xmintemp)
        Ynorm = _array_normalizer(Ytemp, Xmintemp,Xmaxtemp,Ymintemp)
        Ymax[i] = np.max(Ynorm)
        X[i] = Xnorm
        Y[i] = Ynorm
        #store X,Y and time info from each stroke as a list
        Xperst[i] = [list(_array_normalizer(Xt[stroke],Xmintemp,Xmaxtemp,Xmintemp)) for stroke in range(len(Xt))]
        Yperst[i] = [list(_array_normalizer(Yt[stroke],Xmintemp,Xmaxtemp,Ymintemp)) for stroke in range(len(Yt))]
        tperst[i] = [tt[stroke] for stroke in range(len(tt))]
        
        #total number of datapoints 
        ttnum_dp[i] = len(Xnorm)
        
        #store time spent on each stroke
        Tdiff[i] = Tdifftemp
        #store index of stroke that user spent most time
        Tdiffmax[i] = np.argmax(Tdifftemp)
        #store index of stroke that user spent least time
        Tdiffmin[i] = np.argmin(Tdifftemp)
        #time standard deviation for each stroke
        Tdiffstd[i] = np.std(Tdifftemp)
        
        #number of datapoints for each stroke
        dpps[i] = dpps_temp
        #number of datapoints stored as a percentage
        dppps[i] = np.array(dpps_temp)/float(len(Xtemp))
        #stroke with maximum number of datapoints
        dp_max[i] = np.argmax(dpps_temp)
        #stroke with minimum number of datapoints
        dp_min[i] = np.argmin(dpps_temp)
        #std. of datapoints per stroke
        dp_std[i] = np.std(dpps_temp)
        #total time spent on drawing
        sumtimeps[i] = sum(Tdifftemp)        
    # create new features for the drawing
    df_cf['total_number_of_datapoints'] = pd.Series(ttnum_dp)
    df_cf['X'] = pd.Series(X)
    df_cf['Y'] = pd.Series(Y)
    df_cf['Ymax'] = pd.Series(Ymax)
    df_cf['time'] = pd.Series(time)
    df_cf['total_time_of_stroke'] = pd.Series(Tdiff)
    df_cf['dp_per_stroke'] = pd.Series(dpps)
    df_cf['dp_percent_per_stroke'] = pd.Series(dppps)
    df_cf['stroke_with_max_time'] = pd.Series(Tdiffmax)
    df_cf['stroke_with_min_time'] = pd.Series(Tdiffmin)
    df_cf['std_of_time'] = pd.Series(Tdiffstd)
    df_cf['ave_datapoints_per_stroke'] = df_cf['total_number_of_datapoints']/(df_cf['stroke_number'])
    df_cf['total_time_drawing'] = pd.Series(sumtimeps)
    df_cf['ave_time_per_stroke'] = df_cf['total_time_drawing']/(df_cf['stroke_number'])
    df_cf['stroke_with_max_dp'] = pd.Series(dp_max)
    df_cf['stroke_with_min_dp'] = pd.Series(dp_min)
    df_cf['X_per_stroke'] = pd.Series(Xperst)
    df_cf['Y_per_stroke'] = pd.Series(Yperst)
    df_cf['time_per_stroke'] = pd.Series(tperst)
    df_cf['std_of_dp'] = pd.Series(dp_std)
    df_cf = df_cf[df_cf['Ymax']<=1.5]
    return df_cf

def feature_eng_pt3(df_cf):
    direction = {}
    for index in df_cf.index:
        dx = [float(df_cf.drawing[index][stroke][1][-1] - df_cf.drawing[index][stroke][1][0]) \
          for stroke in range(df_cf.stroke_number[index])]
        dy = [float(df_cf.drawing[index][stroke][0][-1] - df_cf.drawing[index][stroke][0][0]) \
          for stroke in range(df_cf.stroke_number[index])]
        dx = np.array(dx)
        dy = np.array(dy)
        dx[dx==0] = 0.000001
        vecrad_direction = np.vectorize(_radian_direction)
        direction[index] = vecrad_direction(dy,dx)
    df_cf['direction'] = pd.Series(direction)
    return df_cf

def feature_eng_pt4(df_cf):
    ar = np.zeros((len(df_cf),75))
    c = 0
    for index_ in df_cf.index:
        stroke = (df_cf.stroke_number[index_])
        ar[c][:stroke] = np.array(df_cf['dp_percent_per_stroke'][index_])
        ar[c][15:15+stroke] = np.array(df_cf['direction'][index_])
        ar[c][30:30+stroke] = np.array(df_cf['total_time_of_stroke'][index_])
        ar[c][45:45+stroke] = np.array(df_cf['dp_per_stroke'][index_])
        ar[c][60:75] = np.array([0]*stroke+[1]*(15-stroke))
        c += 1
    subset = pd.DataFrame(ar)
    subset.index = df_cf.index
    for num in range(15):
        subset = subset.rename(columns={num:"datapoint_percentage_stroke{}".format(num)})
    for num in range(15,30):
        subset = subset.rename(columns={num:"direction_stroke{}".format(num-15)})
    for num in range(30,45):
        subset = subset.rename(columns={num:"time_stroke{}".format(num-30)})
    for num in range(45,60):
        subset = subset.rename(columns={num:"datapoint_stroke{}".format(num-45)})
    for num in range(60,75):
        subset = subset.rename(columns={num:"switch_stroke{}".format(num-60)})
    return subset

def feature_eng_pt5(df_cf):
    ar = np.zeros((len(df_cf),300))
    c = 0
    for index_ in df_cf.index:
        Xpoints = [_value_from_stroke(df_cf['dp_per_stroke'][index_][stroke],\
                                    df_cf['dp_percent_per_stroke'][index_][stroke],\
                                    df_cf['X_per_stroke'][index_][stroke])\
                                    for stroke in range(df_cf.stroke_number[index_])]

        Ypoints = [_value_from_stroke(df_cf['dp_per_stroke'][index_][stroke],\
                                    df_cf['dp_percent_per_stroke'][index_][stroke],\
                                    df_cf['Y_per_stroke'][index_][stroke])\
                                    for stroke in range(df_cf.stroke_number[index_])]

        tpoints = [_value_from_stroke(df_cf['dp_per_stroke'][index_][stroke],\
                                    df_cf['dp_percent_per_stroke'][index_][stroke],\
                                    df_cf['time_per_stroke'][index_][stroke])\
                                    for stroke in range(df_cf.stroke_number[index_])]

        X = [item for stroke in Xpoints for item in stroke]
        Y = [item for stroke in Ypoints for item in stroke]
        time = [item for stroke in tpoints for item in stroke]
        #if the number datapoints turn out to be less than 100, it will fill
        #empty cell with it's last data points.
        if len(X)<100:
            X = X + [X[-1]]*(100-len(X))
        if len(Y)<100:
            Y = Y + [Y[-1]]*(100-len(Y))
        if len(time)<100:
            time = time + [time[-1]]*(100-len(time))
        ar[c][:100] = np.array(X[0:100])
        ar[c][100:200] = np.array(Y[0:100])
        ar[c][200:300] = np.array(time[0:100])
        c += 1
    subset = pd.DataFrame(ar)
    subset.index = df_cf.index
    for num in range(100):
        subset = subset.rename(columns={num:"X_{}".format(num)})
    for num2 in range(100,200):
        subset = subset.rename(columns={num2:"Y_{}".format(num2-100)})
    for num3 in range(200,300):
        subset = subset.rename(columns={num3:"time_{}".format(num3-200)})
    return subset
def _array_normalizer(array1,Xmin,Xmax,array_min):

    return (np.array(array1)-np.array([array_min]*len(array1)))/float(Xmax-Xmin)

def _radian_direction(dy,dx):

    if dy < 0.0 and dx > 0.0:
        return (2*np.pi + np.arctan(dy/dx))
    elif dy >=0.0 and dx > 0.0:
        return (np.arctan(dy/dx))
    else:
        return np.pi + np.arctan(dy/dx)


def _value_from_stroke(stroke_length,percentage,xperstroke):
   
    idxs = np.around(np.linspace(0,stroke_length-1,int(np.around(percentage*100))))
    return [xperstroke[int(ind)] for ind in idxs]


def CNN_feat_eng_pt1(df):

    # create feature "stroke_number"
    df['stroke_number']=df['drawing'].str.len()
    b_loon = {True: 1, False:0}
    df['recognized'] = df['recognized'].map(b_loon)
    df_cf = df[(df['recognized']==1) & (df['stroke_number'] <= 15)]
    df_cf['final_time'] = [df_cf.loc[i,'drawing'][df_cf.stroke_number[i]-1][-2][-1] for i in df_cf.index]


     # process:
    # 1. make a list or int
    # 2. store contents of 1. in a new dictionary
    # 3. make new column in your dataframe with 2. dictionary

    X = {}
    Y = {}
    Ymax ={}
    time = {}
    ttnum_dp = {}
    sumtimeps = {}

    for i in df_cf.index:
        num = df_cf.loc[i,'stroke_number']
        #store X,Y,time of the stroke in a temp list
        Xt = [df_cf.loc[i,'drawing'][stroke][0] for stroke in range(num)]
        Yt = [df_cf.loc[i,'drawing'][stroke][1] for stroke in range(num)]
        tt = [df_cf.loc[i,'drawing'][stroke][2] for stroke in range(num)]

        # calculate the difference between final and initial time of a stroke
        Tdifftemp = [(df_cf.loc[i,'drawing'][stroke][2][-1] - df_cf.loc[i,'drawing'][stroke][2][0])\
                     for stroke in range(num)]

        # normalizing X and Y
        Xtemp = [item for stroke in Xt for item in stroke]
        Ytemp = [item for stroke in Yt for item in stroke]
        time[i] = [item for stroke in tt for item in stroke]

        #normalizing X and Y
        Xmintemp = np.min(Xtemp)-10
        Xmaxtemp = np.max(Xtemp)+10
        Ymintemp = np.min(Ytemp)-10
        Xnorm = _array_normalizer(Xtemp, Xmintemp,Xmaxtemp,Xmintemp)
        Ynorm = _array_normalizer(Ytemp, Xmintemp,Xmaxtemp,Ymintemp)
        Ymax[i] = np.max(Ynorm)
        X[i] = Xnorm
        Y[i] = Ynorm
        ttnum_dp[i] = len(Ynorm)
        sumtimeps[i] = sum(Tdifftemp)
    # create new features
    df_cf['total_number_of_datapoints'] = pd.Series(ttnum_dp)
    df_cf['Ymax'] = pd.Series(Ymax)
    df_cf['time'] = pd.Series(time)
    df_cf['total_time_drawing'] = pd.Series(sumtimeps)
    df_cf['X'] = pd.Series(X)
    df_cf['Y'] = pd.Series(Y)
    df_cf = df_cf[df_cf['Ymax']<=1.5]
    df_cf = df_cf[df_cf['final_time']<=20000]
    return df_cf


def CNN_feat_eng_pt2(df_cf):
    orig_index = df_cf.index
    df_cf.index = range(len(df_cf))
    image_pile = np.zeros((len(df_cf),1176))
    for ind in df_cf.index:
        image = np.zeros((42,28))
        xarray = np.around(np.array(df_cf.loc[ind,'X'])*28)
        yarray = np.around(np.array(df_cf.loc[ind,'Y'])*42/float(df_cf.loc[ind,'Ymax']))
        xarray[xarray>=28.] = 27
        yarray[yarray>=42.] = 41
        for item in range(len(xarray)):
            image[int(np.around(yarray[item])),int(np.around(xarray[item]))] = df_cf.loc[ind,'time'][item]
        image_pile[ind] = image.reshape(1,1176)
    return pd.DataFrame(image_pile, index = orig_index)
    df_final = pd.DataFrame(image_pile, index = orig_index)
    df_cf_country = df_cf['countrycode']
    df_cf_word = df_cf['word']
    df_cf_keyid = df_cf['key_id']
    df_cf_country.index = orig_index
    df_cf_word.index = orig_index
    df_cf_keyid.index = orig_index
    return pd.concat([df_final,df_cf_country,df_cf_word,df_cf_keyid], axis=1)
    df_final.to_pickle("./data/{}_15.pkl".format(category))

def load_json(filename):
    df = pd.read_json(filename, lines=True)
    test = df.groupby(df['countrycode']).count()
    final_df =df.sort_values(by=['2'], ascending=False)
    return df

def pic_viewer(df_cf, _id):
    plt.scatter(df_cf.X[_id],df_cf.Y[_id])
    plt.gca().invert_yaxis()
