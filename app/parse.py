from citytours import parse_tour

tour = parse_tour('tours/birthday_deals.csv')
print(tour.fields)
