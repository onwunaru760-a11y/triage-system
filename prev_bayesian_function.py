### Bayesian ESI Function ###
import numpy as np
def bayesian_esi(patient, answers):
    ESI_levels = [1, 2, 3, 4, 5]
    priors = np.array(
        [0.05, 0.15, 0.3, 0.3, 0.2])  # prior probabilities representing how much each ESI level is before seeing patient data(it's just a simulation )
    posterior = np.copy(priors)  # Start with prior → update with evidence → get posterior(this is a core Bayesian idea)
    likelihood = {
        "low_bp": {1: 0.8, 2: 0.01, 3: 0.05, 4: 0.02, 5: 0.01},
        "high_pain": {1: 0.6, 2: 0.4, 3: 0.2, 4: 0.1, 5: 0.05},
        "age_above_65": {1: 0.3, 2: 0.4, 3: 0.5, 4: 0.3, 5: 0.2},
        "pregnant": {1: 0.5, 2: 0.4, 3: 0.2, 4: 0.1, 5: 0.05},
        "sob": {1: 0.7, 2: 0.3, 3: 0.1, 4: 0.05, 5: 0.01},
        "radiation": {1: 0.6, 2: 0.5, 3: 0.2, 4: 0.1, 5: 0.05}
    }  # the likelihood figures are simulated and is not backed by real world clinical data

    # i want this to return a boolean so it'll have either a positive or negative outcome - either true or false(important for working with bayes)
    evidence = {
        "low_bp": patient["systolic_bp"] < 90,
        "high_pain": patient["pain_score"] >= 8,
        "age_above_65": patient["age"] >= 65,
        "pregnant": patient["pregnant"] == "Yes",
        "sob": answers.get("Any shortness of breath?", 'No') == "Yes",
        "radiation": answers.get(
        "Any radiation to jaw or left arm?", 'No') == "Yes"
    }


    for feature, present in evidence.items():
        # returns the key,value pairs as a tuple to be looped over
        for i, esi in enumerate(ESI_levels):  # enumerate returns the index and actual value in the list
            prob = likelihood.get(feature, {}).get(esi, 0.5)
            if present:
                posterior[i] *= prob
            else:
                posterior[i] *= (1 - prob)
        posterior /= posterior.sum()

    most_likely_esi = ESI_levels[np.argmax(posterior)]  # np.argmax finds the index of the largest value in an array
    return most_likely_esi, posterior

