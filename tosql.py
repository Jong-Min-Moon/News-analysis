def merge(mypath):
    file_list = os.listdir(mypath)
    file_list.sort()

    data = pd.read_csv( mypath + '/' + file_list[0], encoding='utf-8-sig')
    for filename in file_list[1:]:
        data = data.append(pd.read_csv(mypath + '/' + filename, encoding='utf-8-sig'), ignore_index=True)
        print(filename)
    
    return(data)

data = merge('./NN')
data_topic = merge('./LDAs')
data['Document_No'] = np.arange(0, len(data))
data_comment = merge('./NC')
data_comment = pd.merge(data_comment, data[['url', 'Document_No']], how = 'left', on = 'url')