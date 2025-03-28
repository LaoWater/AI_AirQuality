import requests
import json
import matplotlib.pyplot as plt


def fetch_graph_data(access_token):
    """
    Fetch data from a Graph API.
    For this example, we use the Microsoft Graph API endpoint for the signed-in user.
    """
    url = "https://graph.microsoft.com/v1.0/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code} {response.text}")


def save_data_to_file(data, filename="graph_data.json"):
    """
    Save JSON data to a file in the current directory.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")


def create_plot(data):
    """
    Create a plot based on the received data.

    For demonstration, we assume that the data might contain a key 'numbers' with a list of numeric values.
    If not, we simulate some numeric data.
    """
    # Try to extract numeric data from the API response
    if isinstance(data, dict) and "numbers" in data:
        numeric_data = data["numbers"]
    else:
        # Simulated numeric data for plotting
        numeric_data = [10, 20, 15, 30, 25]

    plt.figure(figsize=(8, 6))
    plt.plot(numeric_data, marker='o', linestyle='-', color='b')
    plt.title("Graph API Data Plot")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.grid(True)
    plt.savefig("plot.png")
    print("Plot saved as plot.png")
    plt.show()


def main():
    # Replace with your actual access token for the Graph API
    access_token = "EwBIBMl6BAAUBKgm8k1UswUNwklmy2v7U/S+1fEAAWcPMHMrkFZLdS7/AzZIlrBXsNxqOU+ny1FgdGQ8V5FmltD9mo+rRQ8oOfc4EIYmKMbmFS6L55ILUiAUwrURAAYDXbrAi824trYuw8UcE1iLmZz6kL1AeSzOLZqJEOTURjq9ujQ4Dq0KgIcJ2dTGsDes8o68Zprdu9aGh270UkKk4kTz2IvxiEHhj7sjDU61up9cYn5lyNFZvPX0bWMkDKTLLCyDSJnQfE+i34gzyLEUgTSmJ/2tLcyLD9xzdxWe4C6FNAuU0AFdhs4lvdWPRa1gZdzdPzojVhUQuv/54JEClwPJcYh79JbRlYSdejUPXbuhwIb1ZmuYErO7S+sQ6DsQZgAAECuk+U5Y8tyUjRsil6InDfUQA+REEeJCZLKnY149iVRKmu51GscoHLwWqslcixTzrnW+eTc0EHETyVBWo4evpMqSYF/4IznYK0Jitcf020BsJXcLgKTAkVkklHQde61+is7TT4s/k5fhLHFQH6GMIgjDEDQd3ML/0fUDPul+7ZFpKvWPZVBn5Lx6TJFgplEzxd0RGgjs811xZlh9c1NNTU7WjP17f2yFvFtGPsdZE8aSe/lYjJMtOwoe3hj+R/IpsmN+M2ewmDtbJ68MXMhTiMl4OZ6hz8lcjTilq1OlCaembwQONnaH1FrYwu2ks6eOgHvxOy3F4eRFvqwowBDwRxq/M0mgEfa/IbMhJkDHBoI9ArNS4cF7PMRoWA5KUoNJgZkxa3WsTQhdMSGGEiFcFCbzILPiKpZB5LpP96+xuJqoIKSq03R8CgxtBlwb+N62472mBBoZup700vWsRQCqDR759mhNia/syqZYcBiilBGCI5FzorM1mXzWSdkQ+Mm/YmY5DtjezEXgXVi4vj8C/i62pBO9URapGkAyHKKlf+hjvfgrbweS4N86sXDvNlrdNLux4tXjMj1/yNOhEgoBI1Xde3z/BxUy7bXV5lx8VU0Oyybg6GkJVV0RvNQnjcXpOUazniZ4kQlY1tlih6mBDQKkCFNcsERSp9pnPDu2j2n5RKU2oGWJtvRDBg9ILs6F2DzlQfXOdeXg8Dr4B1rLyKZyTB0Mf5Er0RsU5XCeWSShyfJim8nrk2ouicfz4V4wERZtJJTc0FzrR/5XWljhF7mKyua7gwzJMXvKzXrUvS5xgqpXMY5HlSd2vL9WbMOpklX0Muyx95rvsP6YxfTkHTYDtafUTY3BC2IK00/2BXE/G9/j+O4Zr9SQDFAUaTLWaNVXBBZbxsT1n57qRJNS0oNYVXnnIkTtjjneui7S45H4zT+WL+1a3ytOp/V6vo+/srGNc5sEtT+Sp+Rw9R47z7HlSiufC1eLQGaEZ3BWj3bhxNHq1t4HTWAvnkB7/KU0lKxwZA3UGXgKF4Rhrf4X7D6JdcKw/VJ/90zKOUuP2x9mLthFAw=="

    try:
        # Fetch the data from the API
        data = fetch_graph_data(access_token)

        # Save the data to a JSON file
        save_data_to_file(data)

        # Create and display a plot based on the data
        create_plot(data)

    except Exception as e:
        print("An error occurred:", e)


if __name__ == '__main__':
    main()
