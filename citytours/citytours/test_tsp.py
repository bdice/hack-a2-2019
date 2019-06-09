from traveling_salesman import solve_tsp
import pandas as pd

if __name__ == "__main__":
    data = pd.read_csv('../../tour_data/birthday_deals.csv')
    data = data.loc[~data['Address'].isna()]
    data = data.head(6)
    locations = data['Address'].tolist()
    print(solve_tsp(locations))
