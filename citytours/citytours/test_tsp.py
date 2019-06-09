from traveling_salesman import solve_tsp

if __name__ == "__main__":
    locations = ["510 N 4th Ave, Ann Arbor",
                 "1050 Wall Street, Ann Arbor",
                 "1647 Beal Ave, Ann Arbor"]
    print(solve_tsp(locations))

    locations = ['Rappourt, Ann Arbor',
                 "Arbor Brewing Company, Ann Arbor",
                 "HopCat, Ann Arbor"]
    print(solve_tsp(locations))
