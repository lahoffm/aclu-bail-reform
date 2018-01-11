# Some calculations to estimate dollars saved by state of Georgia in a year
# if the misdemeanor bail reform policy were to pass.
import math

def p(calculation):
    print("${:,}".format(round(calculation,2)))

print("low-end, medium, high-end estimate")
x = 54.03 # dollars saved per misdemeanor booking from Tableau
v = 3.18 # variance of dollars saved from Tableau
p(x*500000*0.55)
p(x*600000*0.65)
p(x*700000*0.75)

print('plus-minus 95% conf. interval 590for low-end, medium, high-end estimate')
p(500000*math.sqrt(v)*1.96)
p(600000*math.sqrt(v)*1.96)
p(700000*math.sqrt(v)*1.96)
