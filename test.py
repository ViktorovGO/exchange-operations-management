# # создание списка дат и ставок из выбранного интервала
# for i in range(count_rows):
#     if  date_from <= datetime.strptime(torg_date_Activ[i], '%d.%m.%Y') <= date_to:
#         rate_interval.append(rate[i])
#         date_interval.append(torg_date_Activ[i])
#         regnum_interval.append(regnum_Activ[i])
#
# set_reg_interval = list(set(regnum_interval))  #список уникальных кодов бумаги из выбранного интревала
# set_reg_interval.sort()
#
# # создание списка средних значений и дисперсии для выбранного интервала
# for i in set_reg_interval:
#     for j,v in enumerate(regnum_interval):
#         if i == v:
#             one_regnum_rate.append(float(rate_interval[j].replace(',', '.')))
#     if len(one_regnum_rate) == 1:
#         variance_rate.append(0)
#     else:
#         variance_rate.append(round(variance(one_regnum_rate), 9))
#     mean_rate.append(round(mean(one_regnum_rate), 7))
#     one_regnum_rate = []
#
# print(variance_rate)
# print((mean_rate))