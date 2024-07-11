import matplotlib.pyplot as plt
import numpy as np

class CO2CaptureCostCalculator:
    def __init__(self, co2_captured_per_year, energy_cost_per_ton_co2, capital_cost_per_ton_co2,
                 fixed_opex_per_ton_co2, variable_opex_per_ton_co2, project_lifetime,
                 co2_capture_efficiency, discount_rate=0.05, inflation_rate=0.02,
                 capture_technology='post_combustion'):

        # --- Thorough Input Validation ---
        if not (50000 <= co2_captured_per_year <= 5000000):
            raise ValueError("CO2 captured per year is unrealistic. Should be between 50,000 and 5,000,000 tons.")
        if not (10 <= energy_cost_per_ton_co2 <= 600):
            raise ValueError("Energy cost per ton of CO2 is outside the expected range (10-600 USD).")
        if not (50 <= capital_cost_per_ton_co2 <= 300):
            raise ValueError("Capital cost per ton of CO2 is outside the expected range (50-300 USD).")
        if not (5 <= fixed_opex_per_ton_co2 <= 25):
            raise ValueError("Fixed operating expense (OPEX) per ton of CO2 is outside the expected range (5-25 USD).")
        if not (1 <= variable_opex_per_ton_co2 <= 10):
            raise ValueError("Variable operating expense (OPEX) per ton of CO2 is outside the expected range (1-10 USD).")
        if not (10 <= project_lifetime <= 40):  # Typical lifetime for industrial projects
            raise ValueError("Project lifetime is unrealistic. Should be between 10 and 40 years.")
        if not (0.7 <= co2_capture_efficiency <= 0.95):
            raise ValueError("CO2 capture efficiency is unrealistic. Should be between 0.7 and 0.95.")
        
        # --- Store Validated Input Parameters ---
        self.co2_captured_per_year = co2_captured_per_year
        self.energy_cost_per_ton_co2 = energy_cost_per_ton_co2
        self.capital_cost_per_ton_co2 = capital_cost_per_ton_co2
        self.fixed_opex_per_ton_co2 = fixed_opex_per_ton_co2
        self.variable_opex_per_ton_co2 = variable_opex_per_ton_co2
        self.project_lifetime = project_lifetime
        self.co2_capture_efficiency = co2_capture_efficiency
        self.discount_rate = discount_rate
        self.inflation_rate = inflation_rate
        self.capture_technology = capture_technology


    def calculate_total_cost_and_co2_captured(self):
        years = np.arange(self.project_lifetime)
        discount_factors = 1 / (1 + self.discount_rate) ** years
        inflation_factors = (1 + self.inflation_rate) ** years

        # --- Calculate Costs Per Year (with Degradation & Maintenance) ---
        annual_energy_cost = (self.co2_captured_per_year * self.energy_cost_per_ton_co2 
                              * (1 + 0.01 * years))  # 1% annual degradation
        annual_fixed_opex = (self.fixed_opex_per_ton_co2 * self.co2_captured_per_year 
                             * (1 + 0.02 * years))  # 2% annual maintenance
        annual_variable_opex = self.variable_opex_per_ton_co2 * self.co2_captured_per_year

        annual_costs = annual_energy_cost + annual_fixed_opex + annual_variable_opex

        # Apply Discounting and Inflation to Yearly Costs
        discounted_costs = annual_costs * discount_factors * inflation_factors
        total_operational_cost = discounted_costs.sum()

        total_capital_cost = self.co2_captured_per_year * self.capital_cost_per_ton_co2
        total_cost = total_capital_cost + total_operational_cost

        # Total CO2 captured over the project lifetime, considering capture efficiency
        total_co2_captured = (self.co2_captured_per_year * self.project_lifetime 
                             * self.co2_capture_efficiency)

        return total_cost, total_co2_captured

    def calculate_cost_per_ton_co2(self):
        """
        Calculate the cost per ton of CO2 captured.
        """
        total_cost, total_co2_captured = self.calculate_total_cost_and_co2_captured()
        
        if total_co2_captured == 0:
            raise ValueError("Total CO2 captured cannot be zero. Please check your inputs.")

        cost_per_ton_co2 = total_cost / total_co2_captured 
        return cost_per_ton_co2

class CO2SensitivityAnalysis:
    """
    A class for conducting sensitivity analysis on CO2 capture project parameters. 
    This analysis helps understand how changes in key inputs affect the project's 
    economic viability.
    """
    
    def __init__(self, calculator, co2_sale_price_per_ton=50, 
                 co2_sale_percentage=0.8, carbon_tax=100, tax_credit_percentage=0.2, learning_rate=0.10, carbon_tax_threshold=100000):
        self.calculator = calculator

        # --- Store Additional Parameters for Realism ---
        self.co2_sale_price_per_ton = co2_sale_price_per_ton
        self.co2_sale_percentage = co2_sale_percentage
        self.carbon_tax = carbon_tax
        self.tax_credit_percentage = tax_credit_percentage
        self.learning_rate = learning_rate
        self.carbon_tax_threshold = carbon_tax_threshold

    def analyze_parameter(self, parameters, range_values):
        """
        Analyzes the impact of changing parameters on the levelized cost of CO2.
        """

        original_values = {param: getattr(self, param) if hasattr(self, param) else getattr(self.calculator, param) for param in parameters}
        results = {param: [] for param in parameters}

        try:
            for param, values in zip(parameters, range_values):
                for value in values:
                    if hasattr(self, param):
                        setattr(self, param, value)
                    else:
                        setattr(self.calculator, param, value)
                    lco2 = self.calculate_levelized_cost_of_co2()
                    results[param].append(lco2)

                # Reset the parameter to its original value
                setattr(self, param, original_values[param]) if hasattr(self, param) else setattr(self.calculator, param, original_values[param]) 

        except Exception as e:
            print(f"Error occurred during analysis: {e}")

        # Ensure all parameters are reset to their original values
        finally:
            for param in parameters:
                setattr(self, param, original_values[param]) if hasattr(self, param) else setattr(self.calculator, param, original_values[param]) 
            
        return results

    @staticmethod
    def plot_results(parameters, range_values, results, title="Sensitivity Analysis"):
        """
        Creates a plot to visualize the results of the sensitivity analysis.
        """
        fig, axes = plt.subplots(len(parameters), 1, figsize=(12, 4 * len(parameters)))

        if len(parameters) == 1:
            axes = [axes]

        for ax, param, values, result in zip(axes, parameters, range_values, results.values()):
            ax.plot(values, result, marker='o', linestyle='-')
            ax.set_xlabel(param.replace('_', ' ').capitalize(), fontsize=12)
            ax.set_ylabel('Cost per Ton CO2 Captured (USD)', fontsize=12)
            ax.set_title(f"Sensitivity Analysis: {param.replace('_', ' ').capitalize()}", fontsize=14)
            ax.grid(True, linestyle='--')
            formatter = plt.FuncFormatter(lambda x, pos: f'${x:.2f}')
            ax.yaxis.set_major_formatter(formatter)

        plt.tight_layout()
        plt.show()

    def calculate_levelized_cost_of_co2(self):
        """
        Calculates the Levelized Cost of CO2 (LCO2) over the project lifetime, considering:
        - Potential CO2 sales revenue
        - Carbon tax or incentives
        - Tax credits
        - Learning curve effects on variable costs
        """
        years = np.arange(self.calculator.project_lifetime)
        discount_factors = 1 / (1 + self.calculator.discount_rate) ** years

        total_cost, total_co2_captured = self.calculator.calculate_total_cost_and_co2_captured()
        annual_co2_captured = total_co2_captured / self.calculator.project_lifetime

        # --- Cost and Revenue Calculations ---
        annual_costs = total_cost / self.calculator.project_lifetime
        annual_revenue = annual_co2_captured * self.co2_sale_price_per_ton * self.co2_sale_percentage
        annual_tax = max(0, annual_co2_captured - self.carbon_tax_threshold) * self.carbon_tax
        tax_credit = self.calculator.capital_cost_per_ton_co2 * self.calculator.co2_captured_per_year * self.tax_credit_percentage

        # --- Apply Learning Curve ---
        cumulative_co2_captured = np.cumsum(annual_co2_captured)
        annual_variable_opex_learning = self.calculator.variable_opex_per_ton_co2 * (cumulative_co2_captured / self.calculator.co2_captured_per_year) ** (-self.learning_rate)

        # --- Discounted Cash Flow Analysis ---
        net_annual_costs = (annual_costs - annual_revenue + annual_tax - annual_variable_opex_learning)
        discounted_annual_costs = net_annual_costs * discount_factors

        levelized_cost_of_co2 = discounted_annual_costs.sum() / total_co2_captured

        return levelized_cost_of_co2

# --- Usage Example ---
calculator = CO2CaptureCostCalculator(co2_captured_per_year=1000000, energy_cost_per_ton_co2=30,
                                      capital_cost_per_ton_co2=200, fixed_opex_per_ton_co2=15,
                                      variable_opex_per_ton_co2=5, project_lifetime=30, co2_capture_efficiency=0.9)

sensitivity_analysis = CO2SensitivityAnalysis(calculator)

parameters = ['energy_cost_per_ton_co2', 'capital_cost_per_ton_co2', 'fixed_opex_per_ton_co2', 
              'variable_opex_per_ton_co2', 'project_lifetime', 'co2_capture_efficiency']
range_values = [np.linspace(10, 50, 5), np.linspace(100, 300, 5), np.linspace(5, 25, 5), 
                np.linspace(1, 10, 5), np.linspace(10, 40, 5), np.linspace(0.7, 0.95, 5)]

results = sensitivity_analysis.analyze_parameter(parameters, range_values)
sensitivity_analysis.plot_results(parameters, range_values, results)
