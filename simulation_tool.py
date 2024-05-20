import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, Entry, StringVar, Radiobutton, messagebox

def generate_demand(distribution, mean, std_dev, lam, days):
    if distribution == 'normal':
        return np.random.normal(loc=mean, scale=std_dev, size=days)
    elif distribution == 'poisson':
        return np.random.poisson(lam, size=days)

def simulate_inventory(demand, policy, reorder_point, order_quantity, lead_time):
    days = len(demand)
    on_hand = np.zeros(days)
    in_shipment = np.zeros(days)
    service_level = np.zeros(days)
    orders = []
    order_in_transit = False

    for day in range(days):
        # Update on-hand inventory by receiving items in shipment after the lead time
        if day >= lead_time:
            on_hand[day] = on_hand[day - 1] + in_shipment[day] - demand[day]
        else:
            on_hand[day] = (on_hand[day - 1] if day > 0 else 0) - demand[day]

        # Check for reorder
        if not order_in_transit:
            if policy == 's_Q' and on_hand[day] < reorder_point:
                orders.append((day, order_quantity))
                if day + lead_time < days:
                    in_shipment[day + lead_time] += order_quantity
                order_in_transit = True
            elif policy == 'R_s_S' and day % 10 == 0:
                if on_hand[day] < reorder_point:
                    orders.append((day, order_quantity))
                    if day + lead_time < days:
                        in_shipment[day + lead_time] += order_quantity
                    order_in_transit = True

        # Reset order_in_transit if order has arrived
        if order_in_transit and day >= lead_time and in_shipment[day] > 0:
            order_in_transit = False

        service_level[day] = 1 if on_hand[day] >= 0 else 0

    service_level_performance = np.mean(service_level)
    return pd.DataFrame({
        'Day': np.arange(days),
        'Demand': demand,
        'On Hand': on_hand,
        'In Shipment': in_shipment,
        'Service Level': service_level
    }), service_level_performance

def run_simulation():
    try:
        mean_demand = float(mean_var.get()) if mean_var.get() else 0
        std_dev_demand = float(std_dev_var.get()) if std_dev_var.get() else 0
        lam_demand = float(lam_var.get()) if lam_var.get() else 0
        days = int(days_var.get()) if days_var.get() else 0
        reorder_point = int(reorder_point_var.get()) if reorder_point_var.get() else 0
        order_quantity = int(order_quantity_var.get()) if order_quantity_var.get() else 0
        lead_time = int(lead_time_var.get()) if lead_time_var.get() else 0
        distribution_type = dist_var.get()
        policy_type = policy_var.get()

        if not all([mean_demand, std_dev_demand, days, reorder_point, order_quantity, lead_time]):
            raise ValueError("All input fields must be filled with valid numeric values.")

        demand = generate_demand(distribution_type, mean_demand, std_dev_demand, lam_demand, days)
        inventory_results, service_level_performance = simulate_inventory(demand, policy_type, reorder_point, order_quantity, lead_time)

        inventory_results.to_csv('inventory_simulation_results.csv', index=False)
        plt.figure(figsize=(10, 5))
        plt.plot(inventory_results['Day'], inventory_results['On Hand'], label='On Hand Inventory', color='red')
        plt.title('Inventory Levels Over Time')
        plt.xlabel('Day')
        plt.ylabel('Inventory Level')
        plt.legend()
        plt.grid(True)
        plt.show()

        messagebox.showinfo("Simulation Complete", f"Simulation complete.\nResults saved to 'inventory_simulation_results.csv'.\nAverage Service Level: {service_level_performance:.2f}")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", "An error occurred: " + str(e))

root = Tk()
root.title("Inventory Management Simulation")

# Variables
mean_var = StringVar()
std_dev_var = StringVar()
lam_var = StringVar()
days_var = StringVar()
reorder_point_var = StringVar()
order_quantity_var = StringVar()
lead_time_var = StringVar()
dist_var = StringVar(value='normal')
policy_var = StringVar(value='s_Q')

# Distribution Selection
Label(root, text="Demand Distribution:").grid(row=0, column=0)
Radiobutton(root, text="Normal", variable=dist_var, value='normal').grid(row=0, column=1)
Radiobutton(root, text="Poisson", variable=dist_var, value='poisson').grid(row=0, column=2)

# Mean Demand
Label(root, text="Mean Demand:").grid(row=1, column=0)
Entry(root, textvariable=mean_var).grid(row=1, column=1, columnspan=2)

# Std Dev Demand
Label(root, text="Std Dev of Demand:").grid(row=2, column=0)
Entry(root, textvariable=std_dev_var).grid(row=2, column=1, columnspan=2)

# Lambda Demand
Label(root, text="Lambda for Poisson:").grid(row=3, column=0)
Entry(root, textvariable=lam_var).grid(row=3, column=1, columnspan=2)

# Simulation Days
Label(root, text="Number of Simulation Days:").grid(row=4, column=0)
Entry(root, textvariable=days_var).grid(row=4, column=1, columnspan=2)

# Reorder Point
Label(root, text="Reorder Point:").grid(row=5, column=0)
Entry(root, textvariable=reorder_point_var).grid(row=5, column=1, columnspan=2)

# Order Quantity
Label(root, text="Order Quantity:").grid(row=6, column=0)
Entry(root, textvariable=order_quantity_var).grid(row=6, column=1, columnspan=2)

# Lead Time
Label(root, text="Lead Time (days):").grid(row=7, column=0)
Entry(root, textvariable=lead_time_var).grid(row=7, column=1, columnspan=2)

# Policy Selection
Label(root, text="Inventory Policy:").grid(row=8, column=0)
Radiobutton(root, text="s, Q", variable=policy_var, value='s_Q').grid(row=8, column=1)
Radiobutton(root, text="R, s, S", variable=policy_var, value='R_s_S').grid(row=8, column=2)

# Run Button
Button(root, text="Run Simulation", command=run_simulation).grid(row=9, column=0, columnspan=3)

root.mainloop()