"""
data_manager.py
Computes summary statistics from a list of laptop dicts.
Each laptop dict has keys
    name (str), price (float), price_str (str), rating (float)
"""

def get_statistics(laptops: list[dict]) -> dict:
    #Compute summary statistics for the scraped laptop dataset (ex. total, average price, minimum price)
    if not laptops:
        return {}

    prices  = [l["price"]  for l in laptops]
    ratings = [l["rating"] for l in laptops]
    rated   = [l for l in laptops if l["rating"] > 0]

    highest_rated = max(laptops, key=lambda l: l["rating"]) if rated else laptops[0]
    lowest_priced = min(laptops, key=lambda l: l["price"])

    return {
        "total":          len(laptops),
        "avg_price":      round(sum(prices)  / len(prices),  2),
        "min_price":      round(min(prices),  2),
        "max_price":      round(max(prices),  2),
        "avg_rating":     round(sum(ratings) / len(ratings), 2),
        "highest_rated":  highest_rated["name"],
        "lowest_priced":  lowest_priced["name"],
        "rated_count":    len(rated),
    }
