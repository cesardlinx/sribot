from datetime import datetime

MONTHS = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
          'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

year = '2019'
month = 'ENERO'
current_year = datetime.now().year
current_month_index = datetime.now().month - 1
previous_years = current_year - int(year)

initial_index = MONTHS.index(month)

if previous_years:
    # months in the first year
    months = MONTHS[initial_index:]
    for month in months:
        print('Year: {}, Month: {}'.format(year, month))

# months in the actual year
months = MONTHS[:current_month_index]
year = str(current_year)
for month in months:
    print('Year: {}, Month: {}'.format(year, month))
