import pandas as pd
city_df = pd.read_csv('city.txt', header=None)
city_df = city_df.apply(lambda col: col.str[3:])
city_list = city_df[0].to_list()
print(city_list)
crop_df = pd.read_csv('crop.txt', header=None)
crop_list = crop_df[0].to_list()
print(crop_list)
# city = '南投縣'
for city in city_list:
    print(city)
    final_df = pd.DataFrame()
    for i in range(86, 102):
        if len(str(i)) == 2:
            i = '0' + str(i)
        df = pd.read_csv(f'{i}.csv')
        if city[0] == '臺':
            city = '台' + city[1:]
        df = df[df['縣市鄉鎮名稱'].str.contains(city)]
        df['作物'] = pd.Categorical(df['作物'], categories=crop_list, ordered=True)
        df = df.sort_values('作物')
        # print(df)
        final_df = pd.concat([final_df, df])
# print(final_df)
    final_df.to_csv(f'{city}.csv', encoding='utf-8-sig', index=False)
    # final_df.to_excel(f'{city}.xlsx)')