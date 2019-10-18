import pandas as pd
import numpy as np


# Extracting dataframe containg political parties' votes in each constituency
# 42 rows representing constituencies
# 6 columns representing parties, plus the number of mandates per constituency
def fetch_figures_2015():
    df = pd.read_excel('2015-gl-lis-okr.xls')
    df_mandates = pd.read_excel('okregi_sejm.xlsx')[['Liczba mandatów']]
    df['Liczba mandatów'] = df_mandates['Liczba mandatów']
    results = df[['pis', 'po', 'k15', 'n', 'psl', 'Liczba mandatów']]
    return results

# Extracting dataframe containg political parties' votes in each constituency
# 42 rows representing constituencies
# 6 columns representing parties, plus the number of mandates per constituency
def fetch_figures_2019():
    df = pd.read_excel('wyniki_gl_na_listy_po_okregach_sejm.xlsx')
    df_mandates = pd.read_excel('okregi_sejm.xlsx')[['Siedziba OKW', 'Liczba mandatów']]
    df['Liczba mandatów'] = df_mandates['Liczba mandatów']
    results = df[['pis', 'ko', 'sld', 'psl', 'konf', 'Liczba mandatów']]
    return results


def example1():
    print(fetch_figures_2019())


# For an array of votes received by each party, return the mandate breakdown array
# Instead of creating a matrix of votes and their quotients...
# ... dynamically update curr_votes array after the biggest value has been picked up
def dhondt_counter(votes, mandates_to_share):
    mandates_counter = np.zeros(len(votes))
    curr_votes = list(votes)
    for mandate in range(mandates_to_share):
        winner = np.argmax(curr_votes)  # determining who gets the mandate
        mandates_counter[winner] += 1  # adding the mandate to the winning party
        curr_votes[winner] = votes[winner] / (mandates_counter[winner] + 1) # dividing party's votes by the next number
    return mandates_counter


# For an array of votes received by OTHER parties return the minimum votes needed to receive target_mandates
def get_target_result(votes_of_others, mandates_to_share, target_mandates):
    divisors = np.array([1 / (i + 1) for i in range(mandates_to_share)])
    input_array = np.array(votes_of_others)
    table = np.round(np.outer(input_array, divisors))  # Creating the d'Hondt table via the outer product
    flat_votes = table.flatten()
    flat_votes.sort()  # Flattening all table inputs into a sorted array
    # Having a sorted array of *mandates_to_share* biggest table inputs...
    # ... let's determine the value of the smallest input that a party must have
    # Ex. if a party's target is 5 mandates, then the fifth quotient of their vote needs to equal...
    # ...the fifth worst input in the array
    min_index = len(flat_votes) - mandates_to_share + target_mandates - 1 # Extracting which input of an array we treat as a benchmark
    minimum_vote = target_mandates * (flat_votes[int(min_index)] + 1) # Adjusting this input for the total number of votes needed
    return minimum_vote


def example2():
    print(dhondt_counter([500, 234, 844, 1987], 19))     # Initial input
    print(get_target_result([234, 844, 1987], 19, 3))   # Checking how much #1 needs to improve
    print(dhondt_counter([510, 234, 844, 1987], 19))     # Checking if #1 improved


# Takes improver (an array index) and calculates the # of votes need to get *change* more mandates
def votes_to_improve(votes_input, mandates_to_share, improver, change):
    votes = list(votes_input)  # Creating a separate list instance
    initial_mandates = dhondt_counter(votes, mandates_to_share)     # Calculating initial breakdown
    target_mandates = initial_mandates[improver] + change       # Determining the number of mandates that a party needs to win
    previous_vote = votes.pop(improver)                         # Deleting the party's result from the list (recall the 'others' input)
    needed_vote = get_target_result(votes, mandates_to_share, target_mandates) # Calculating the amount of votes needed to achieve the benchmark
    margin = needed_vote - previous_vote
    return margin


def example3():
    print(votes_to_improve([500, 234, 844, 1987], 19, 0, 1))  # Comparing with example2()


# Takes the election dataframe input and returns minimum margin needed for the ruling party to lose 1 mandate...
# ... in each constituency
def show_winning_margin_by_constituency(election_data):
    margins = []
    for constituency in range(41):  # Iterating through constituencies & appending smallest margins to the list
        votes = list(election_data.iloc[constituency])[:-1]
        mandates_to_share = list(election_data.iloc[constituency])[-1]
        least_margin = np.inf  # Storage variable
        for i in range(1, 5):  # Iterating through each opposition's party margin in a constituency
            single_party_margin = votes_to_improve(votes, mandates_to_share, improver=i, change=1)  # Votes needed to gain one more mandate
            if single_party_margin < least_margin:  # We are only interested in the smallest margin
                # The following two lines distinguish two vote arrays. votes - the actual one...
                # ... and the improver_gain_votes, a breakdown of votes where the improver managed to increase their vote by *margin*
                imporver_gain_votes = list(votes)
                imporver_gain_votes[i] = imporver_gain_votes[i] + single_party_margin
                # This statment checks if the mandate gained by the opposition party takes away a mandate from...
                # ... the ruling party. If not, ignore the margin
                # In the event that all parties improvement only takes away other opposition party's mandate...
                # ... don't update the least_margin
                if dhondt_counter(imporver_gain_votes, mandates_to_share)[0] < dhondt_counter(votes, mandates_to_share)[0]:
                    least_margin = single_party_margin
        margins.append(least_margin)  # Appending least_margin after iterating through opposition in a constituency
    return margins


def main():
    elections = fetch_figures_2019()  # Can be changed to 2015
    turnout = np.sum(np.sum(elections.drop("Liczba mandatów", axis=1)))
    margin_list = show_winning_margin_by_constituency(elections)
    print(f'The margin list for each constituency in the order given by the PKW: \n{margin_list} \n')
    margin_list.sort()
    print(f'Margins sorted in ascending order: \n{margin_list} \n')
    print(f'The minimum number of votes needed for the ruling party to lose majority: {int(np.sum(margin_list[:5]))} \n'
          f'Which is {np.round(int(np.sum(margin_list[:5])) / turnout * 100, 4)}% of votes')


if __name__ == "__main__":
    main()
