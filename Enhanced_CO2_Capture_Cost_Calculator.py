import matplotlib.pyplot as plt

class CO2CaptureCostCalculator:
    """
    A class to calculate the cost of CO2 capture and its efficiency.
    Enhanced with additional validation and more comprehensive calculations.
    """
    def __init__(self, cost_of_amines, energy_cost, annual_energy_use, capital_cost, operational_cost,
                 project_lifetime, co2_capture_efficiency, co2_capture_per_ton_amine):
        self.validate_inputs(cost_of_amines, energy_cost, annual_energy_use, capital_cost, operational_cost,
                            project_lifetime, co2_capture_efficiency, co2_capture_per_ton_amine)
        self.cost_of_amines = cost_of_amines
        self.energy_cost = energy_cost
        self.annual_energy_use = annual_energy_use
        self.capital_cost = capital_cost
        self.operational_cost = operational_cost
        self.project_lifetime = project_lifetime
        self.co2_capture_efficiency = co2_capture_efficiency
        self.co2_capture_per_ton_amine = co2_capture_per_ton_amine

    @staticmethod
    def validate_inputs(*args):
        for arg in args:
            if arg <= 0:
                raise ValueError("All input values must be greater than 0.")
            # Additional validations can be added based on domain knowledge.

    def calculate_total_cost_and_co2_captured(self):
        """
        Calculate the total cost and total CO2 captured over the project's lifetime.
        """
        annual_energy_cost = self.energy_cost * self.annual_energy_use
        total_operational_cost = (self.operational_cost + annual_energy_cost) * self.project_lifetime
        total_cost = self.capital_cost + total_operational_cost
        total_co2_captured = self.co2_capture_per_ton_amine * self.project_lifetime * self.co2_capture_efficiency
        return total_cost, total_co2_captured

    def calculate_cost_per_ton_co2(self):
        """
        Calculate the cost per ton of CO2 captured.
        """
        total_cost, total_co2_captured = self.calculate_total_cost_and_co2_captured()
        return total_cost / total_co2_captured if total_co2_captured > 0 else float('inf')

    # Additional functions for more comprehensive calculations can be added here.

class CO2SensitivityAnalysis:
    """
    A class for conducting sensitivity analysis on the CO2CaptureCostCalculator parameters.
    Enhanced to handle a broader range of parameters dynamically.
    """
    def __init__(self, calculator):
        self.calculator = calculator

    def analyze_parameter(self, parameters, range_values):
        """
        Analyze the impact of changing one or more parameters over specified ranges.
        Enhanced to handle exceptions more gracefully.
        """
        original_values = {param: getattr(self.calculator, param) for param in parameters}
        results = {param: [] for param in parameters}

        try:
            for param, values in zip(parameters, range_values):
                for value in values:
                    setattr(self.calculator, param, value)
                    cost_per_ton = self.calculator.calculate_cost_per_ton_co2()
                    results[param].append(cost_per_ton)
                setattr(self.calculator, param, original_values[param])
        except Exception as e:
            print(f"Error occurred during analysis: {e}")
        finally:
            for param in parameters:
                setattr(self.calculator, param, original_values[param])
        return results

    @staticmethod
    def plot_results(parameters, range_values, results, title="Sensitivity Analysis"):
        """
        Plot the results of the sensitivity analysis.
        Enhanced with better visualization.
        """
        plt.figure(figsize=(10, 6))
        for param, values in zip(parameters, range_values):
            plt.plot(values, results[param], label=param)

        plt.xlabel('Parameter Values')
        plt.ylabel('Cost per Ton CO2 (USD)')
        plt.title(title)
        plt.grid(True)
        plt.legend()
        plt.show()

# Example Usage
calculator = CO2CaptureCostCalculator(500, 0.1, 100000, 1000000, 50000, 10, 0.9, 1.5)
total_cost, total_co2_captured = calculator.calculate_total_cost_and_co2_captured()
cost_per_ton_co2 = calculator.calculate_cost_per_ton_co2()
print(f"Total cost over 10 years: USD {total_cost:,.2f}")
print(f"Total CO2 captured over 10 years: {total_co2_captured:.2f} tons")
print(f"Cost per ton of CO2 captured: USD {cost_per_ton_co2:.2f}")

analysis = CO2SensitivityAnalysis(calculator)
parameters_to_analyze = ["project_lifetime", "co2_capture_efficiency"]
ranges = [range(5, 21), [i / 10.0 for i in range(1, 10)]]
sensitivity_results = analysis.analyze_parameter(parameters_to_analyze, ranges)

CO2SensitivityAnalysis.plot_results(parameters_to_analyze, ranges, sensitivity_results)

# based on general industry data
calculator = CO2CaptureCostCalculator(
    cost_of_amines=600,  # Example value in USD
    energy_cost=0.08,  # Example energy cost per kWh
    annual_energy_use=200000,  # Example annual usage in kWh
    capital_cost=1500000,  # Example capital cost in USD
    operational_cost=100000,  # Annual operational cost in USD
    project_lifetime=25,  # Lifetime of the project in years
    co2_capture_efficiency=0.85,  # 85% capture efficiency
    co2_capture_per_ton_amine=2  # Example capture rate per ton of amine
)

total_cost, total_co2_captured = calculator.calculate_total_cost_and_co2_captured()
cost_per_ton_co2 = calculator.calculate_cost_per_ton_co2()
print(f"Total cost over 25 years: USD {total_cost:,.2f}")
print(f"Total CO2 captured over 25 years: {total_co2_captured:.2f} tons")
print(f"Cost per ton of CO2 captured: USD {cost_per_ton_co2:.2f}")

analysis = CO2SensitivityAnalysis(calculator)
parameters_to_analyze = ["project_lifetime", "co2_capture_efficiency"]
ranges = [range(10, 31), [i / 10.0 for i in range(5, 10)]]
sensitivity_results = analysis.analyze_parameter(parameters_to_analyze, ranges)

CO2SensitivityAnalysis.plot_results(parameters_to_analyze, ranges, sensitivity_results)
