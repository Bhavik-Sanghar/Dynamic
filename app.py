from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__, template_folder='templates')

# Load data from CSV
data = pd.read_csv("Resturent_Pizza.csv")

def calculate_dynamic_price(row):
    dynamic_price = row['Avg_Price']  # Start with the average price

    # Adjust price based on order time
    if int(row['order_time'].split(':')[0]) >= 17 and int(row['order_time'].split(':')[0]) <= 21:
        dynamic_price *= 1.1  # Increase price by 10% during dinner time (5 PM to 9 PM)

    # Adjust price based on location
    location_factors = {'Kolkata': 1.05, 'Gujarat': 1.08, 'Channai': 1.07, 'Mumbai': 1.06, 'Delhi': 1.1}
    if row['Location'] in location_factors:
        dynamic_price *= location_factors[row['Location']]

    # Adjust price based on order quantity
    if row['Quantity'] >= 2:
        dynamic_price *= 0.95  # Apply a 5% discount for orders of 2 or more pizzas
    elif row['Quantity'] >= 5:
        dynamic_price *= 0.9  # Apply a 10% discount for orders of 5 or more pizzas

    # Adjust price based on pizza size
    size_factors = {'L': 1.14, 'M': 1.13, 'S': 1.0}  # Adjust these factors as needed
    if row['pizza_size'] in size_factors:
        dynamic_price *= size_factors[row['pizza_size']]

    return dynamic_price

# Apply dynamic pricing logic to the dataset
data['Dynamic_Price'] = data.apply(calculate_dynamic_price, axis=1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_price', methods=['POST'])
def calculate_price():
    # Receive pizza options from the frontend form
    pizza = request.form.get('pizza')
    location = request.form.get('location')
    size = request.form.get('size')
    quantity = int(request.form.get('quantity'))

    # Filter the dataset based on the selected options
    filtered_data = data[(data['pizza_name'] == pizza) & 
                         (data['Location'] == location) & 
                         (data['pizza_size'] == size)]

    if len(filtered_data) == 0:
        return jsonify({'error': 'No matching pizza found'}), 404

    # Retrieve normal and dynamic prices from the filtered data
    normal_price = filtered_data['Avg_Price'].iloc[0]
    dynamic_price = filtered_data['Dynamic_Price'].iloc[0]

    # Multiply dynamic price by quantity
    total_price_dynamic = dynamic_price * quantity

    # Return both prices as JSON response
    return jsonify({
        'normal_price': normal_price,
        'dynamic_price': dynamic_price,
        'total_price_dynamic': total_price_dynamic
    })

if __name__ == '__main__':
    app.run(debug=True)
