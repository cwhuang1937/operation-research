from pulp import *
import pandas as pd
import matplotlib.pyplot as plt

# input for user
shop = input('請輸入你想分析的店(可輸入『Family』或『Mos』或『KFC』或『McDonald』): ')
gender = input('請輸入你的性別(可輸入『男生』或『女生』): ')
fitness_type = input('請輸入你的需求(可輸入『健身』或『減脂』): ')
age = int(input('請輸入你的年齡: '))
height = float(input('請輸入你的身高: '))
weight = float(input('請輸入你的體重: '))
days = int(input('請輸入你一周運動的天數: '))

df = pd.read_csv('data/' + shop + '.csv')

# get data from file
meals = df['name'].tolist()
cal = dict(zip(meals, df['cal'].tolist()))
protein = dict(zip(meals, df['protein'].tolist()))
carb = dict(zip(meals, df['carb'].tolist()))
fat = dict(zip(meals, df['fat'].tolist()))
cost = dict(zip(meals, df['cost'].tolist()))

# analyze your information
TDEE = 0.0
BMR = 0.0

if gender == '男生':
    BMR = 13.7*weight + 5.0*height - 6.8*age + 66
else:
    BMR = 9.6*weight + 1.8*height - 4.7*age + 655

if days == 0:
    TDEE = BMR*1.2
elif days >= 1 and days <= 2:
    TDEE = BMR*1.375
elif days >= 3 and days <= 5:
    TDEE = BMR*1.55
else:
    TDEE = BMR*1.725

if fitness_type == '增肌':
    carb_upper = TDEE * 0.6 / 4
    carb_lower = TDEE * 0.5 / 4
    fat_upper = TDEE * 0.3 / 9
    fat_lower = TDEE * 0.2 / 9
    TDEE_upper = TDEE + 300
    TDEE_lower = TDEE
else:
    carb_upper = TDEE * 0.3 / 4
    carb_lower = TDEE * 0.2 / 4
    fat_upper = TDEE * 0.6 / 9
    fat_lower = TDEE * 0.5 / 9
    TDEE_upper = TDEE
    TDEE_lower = TDEE - 300

print('你的BMR為: {:.1f}大卡'.format(BMR))
print('你的TDEE為: {:.1f}大卡'.format(TDEE))
while(1):
    mode = input('你想要看該家店價錢與蛋白質的分析，請輸入『mode1』\n若想要自行輸入價錢來查看該店可吃到的食物，請輸入『mode2』:')

    if mode == 'mode1':
        X = []
        Y = []
        for money in range(100, 1001, 10):

            # build problem
            prob = LpProblem("Food for fitness", LpMaximize)
            meals_var = LpVariable.dicts("Meals", meals, 0, None, 'Integer')

            # add objective function
            prob += lpSum([protein[i] * meals_var[i] for i in meals])

            # add restricted function
            prob += lpSum([cost[i] * meals_var[i] for i in meals]) <= money

            prob += lpSum([cal[i] * meals_var[i] for i in meals]) <= TDEE_upper
            prob += lpSum([cal[i] * meals_var[i] for i in meals]) >= TDEE_lower

            prob += lpSum([carb[i] * meals_var[i] for i in meals]) <= carb_upper
            prob += lpSum([carb[i] * meals_var[i] for i in meals]) >= carb_lower

            prob += lpSum([fat[i] * meals_var[i] for i in meals]) <= fat_upper
            prob += lpSum([fat[i] * meals_var[i] for i in meals]) >= fat_lower

            if shop == 'Family':
                for i in meals:
                    prob += lpSum(meals_var[i]) <= 2

            # solve problem
            prob.solve()

            # append to list for drawing result
            X.append(money)
            if LpStatus[prob.status] == 'Infeasible':
                Y.append(0)
            else:
                Y.append(value(prob.objective))

        plt.figure(1, figsize=(200, 200))
        plt.plot(X, Y, 'r', linewidth=4)
        plt.xlabel('Cost(NT dollars)')
        plt.ylabel('Protein(g)')
        plt.show()       
    elif mode == 'mode2':
        money = int(input('請輸入你一天想花多少錢在這家店上面: '))

        # build problem
        prob = LpProblem("Food for fitness", LpMaximize)
        meals_var = LpVariable.dicts("Meals", meals, 0, None, 'Integer')

        # add objective function
        prob += lpSum([protein[i] * meals_var[i] for i in meals])

        # add restricted function
        prob += lpSum([cost[i] * meals_var[i] for i in meals]) <= money

        prob += lpSum([cal[i] * meals_var[i] for i in meals]) <= TDEE_upper
        prob += lpSum([cal[i] * meals_var[i] for i in meals]) >= TDEE_lower

        prob += lpSum([carb[i] * meals_var[i] for i in meals]) <= carb_upper
        prob += lpSum([carb[i] * meals_var[i] for i in meals]) >= carb_lower

        prob += lpSum([fat[i] * meals_var[i] for i in meals]) <= fat_upper
        prob += lpSum([fat[i] * meals_var[i] for i in meals]) >= fat_lower

        if shop == 'Family':
            for i in meals:
                prob += lpSum(meals_var[i]) <= 2

        # solve problem
        prob.solve()

        if LpStatus[prob.status] == 'Infeasible':
            print('你輸入的價錢無法在這家店達到你想要的需求')
        else:
            for i in meals:
                if meals_var[i].value() != 0:
                    print('{}: {}份\n熱量={}大卡, 蛋白質={}g, 碳水化合物={}g, 脂肪={}g, 價錢={}元'.format(meals_var[i], int(meals_var[i].value()), cal[i], protein[i], carb[i], fat[i], cost[i]))
            print('你可以攝取到的總蛋白質={:.1f}g'.format(float(value(prob.objective))))
