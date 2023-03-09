import numpy as np
import pandas as pd
from openpyxl.writer.excel import save_workbook
import openpyxl

from natsort import index_natsorted
from pandas.io.excel import ExcelWriter
import locale

# чтение excel файла, dtype - перевод int в object
df = pd.read_excel('DATA.xlsx',  dtype={'ZZ_BRANCH': object,
                                            'ZZ_FROM_DATE': object,
                                                'ZZ_CONT_DATE': object,
                                                    'ZZ_CONT_END_DATE': object,
                                        })
df = df.sort_values(by='TYPE')

# новая датафрейм для подключения колонки TYPE
new_db = pd.DataFrame({'TYPE': [1,2,3,4,5,6,7],
                        'Pазмер ячейки (мм)': ['50 мм', '75 мм', '125 мм', '175 мм', '300 мм', '60 мм', '110 мм']})
new_db.sort_values(by='TYPE')

#функция разделения цифр на /, для правильности чтения дат
def toHuman(row):
    return row[6:] + '/' + row[4:6] + '/' + row[:4]

# вызов функции для каждых строк в столбце
df['ZZ_FROM_DATE'] = df['ZZ_FROM_DATE'].apply(lambda x: toHuman(x))

df['ZZ_CONT_DATE'] = df['ZZ_CONT_DATE'].apply(lambda x: toHuman(x))

df['ZZ_CONT_END_DATE'] = df['ZZ_CONT_END_DATE'].apply(lambda x: toHuman(x))
# функции для вычесления процента в столбце
def about_price():
    procent_price = (df.ZZ_PRICE/100 * 12)
    new_price = df.ZZ_PRICE - procent_price
    return new_price
df['ZZ_PRICE'] = about_price()

def zz_vat_price():
    procent_price = (df.ZZ_VAT_PRICE / 100 * 12)
    new_price = df.ZZ_VAT_PRICE - procent_price
    return new_price
df['ZZ_VAT_PRICE'] = zz_vat_price()

def zz_price_without():
    procent_price = (df.ZZ_PRICE_WITHOUT / 100 * 12)
    new_price = df.ZZ_PRICE_WITHOUT - procent_price
    return new_price
df['ZZ_PRICE_WITHOUT'] = zz_price_without()

# cоздание нового столбца, прибовляя значение двух имеющихся столбцов
df['№ договора и дата'] = '№ ' + df['ZZ_CONTRACT'] + ' от ' + df['ZZ_FROM_DATE'].astype(str)


# По тому же исходнику сгруппируй по размеру ячейки общую сумму с учетем ндс.
#
# Например,
# 50 мм - 360000
# 75 мм - 720000
# И тд

# df['Общая сумма с ндс'] =

# джоин с помощью мердж

df3 = df.merge(new_db, on='TYPE')

df3 = df3.sort_values(by='TYPE')

# удаление строк
# del df3['TYPE']
del df3['ZZ_FROM_DATE']
del df3['ZZ_CONTRACT']

# переименование строк
df3 = df3.rename(columns={"ZZ_BRANCH": "МФО",
                           "ZZ_DEP_CLIENT": "Наименование клиента",
                           "ZZ_CONTRACT": "ZZ_CONTRACT",
                           "ZZ_CONT_END_DATE": "срок пользования до",
                           "ZZ_PRICE_WITHOUT": "Сумма дохода банка",
                           "ZZ_VAT_PRICE": "НДС",
                           "ZZ_PRICE":"Сумма с учетом НДС",
                           "ZZ_CONT_DATE": "срок пользования от"})

# добавление строки автодобавления одного числа, на след строку
df3.insert(0, '#',  range(1, 1+len(df3)))

# изменения наименования строк
df3 = df3[['#', 'МФО', 'Наименование клиента', '№ договора и дата', 'Pазмер ячейки (мм)',
                'срок пользования от', 'срок пользования до', 'Сумма дохода банка', 'НДС', 'Сумма с учетом НДС', 'TYPE']]

# def sum2():
#     if df3['Pазмер ячейки (мм)'] == df3['Pазмер ячейки (мм)']:
#         df3['Сумма с учетом НДС'].sum()

df4 = df3.groupby(['TYPE', 'Pазмер ячейки (мм)'],
                  sort=True).agg({'Сумма с учетом НДС': 'sum'}).reset_index()
# df4['Сумма с учетом НДС'] = df4['Сумма с учетом НДС'].astype(str).
df4['Сумма с учетом НДС'] = df4['Сумма с учетом НДС'].map('{:,.2f}'.format)
df4['Сумма с учетом НДС'] = df4['Сумма с учетом НДС'].str.replace(',', ' ')
df4['Сумма с учетом НДС'] = df4['Сумма с учетом НДС'].str.replace('.', ',',  regex=False)
# df4['Сумма с учетом НДС'] = df4['Сумма с учетом НДС'].apply('{:0>6} '.format)
# df4 = df4.sort_values(by='TYPE)')
# df4 = df4.sort_values(by='Pазмер ячейки (мм)', key=lambda x: np.argsort(index_natsorted(df4['Pазмер ячейки (мм)'])))
df4 = df4.sort_values(['TYPE'])
# df4 = df4['Сумма с учетом НДС'].round(2)


# добавление запятых в цифровой формат
# df5 = df4['Сумма с учетом НДС'].map('{:,.2f}'.format)

del df4['TYPE']
del df3['TYPE']
# del df4['TYPE']
# del df3['TYPE']
# del df4['ZZ_FROM_DATE']
# del df4['ZZ_CONTRACT']
print('done')


with ExcelWriter('box10.xlsx') as writer:
    df3.to_excel(writer, sheet_name="Лист 1", index=False)
    df4.to_excel(writer, sheet_name="Лист 2", index=False)

# print(df4)
# df4.to_excel('lastbox2.xlsx', sheet_name='List1')

# df = pd.read_excel('box7.xlsx')
# df.to_excel('box7.xlsx', sheet_name="models")
# with ExcelWriter('box7.xlsx', mode="a") as writer:
#     df.sample(10).to_excel(writer, sheet_name="Лист 1")
#     df.sample(10).to_excel(writer, sheet_name="Лист 2")

# print(sum2())

# сохранение всех таблицы в excel файл
# df3.to_excel('name_for_ex.xlsx', index=False)
