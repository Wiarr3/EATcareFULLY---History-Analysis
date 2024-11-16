import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def total_macros(df):
    try:
        protein_total = df['proteins_total'].sum()
        fat_total = df['fat_total'].sum()
        carbs_total = df['carbohydrates_total'].sum()
        return protein_total, fat_total, carbs_total
    except Exception as e:
        print(f"Error calculating total macros: {e}")


def plot_macros(df, freq='D', filename_prefix=""):

    try:
        df = df.drop(columns=['id'], errors='ignore')
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').resample(freq).sum()

        if freq == 'D':
            freq_str = "Days"
            x_format = mdates.DateFormatter('%d')
        elif freq == 'W':
            freq_str = "Weeks"
            x_format = mdates.DateFormatter('Week %U')
        else:
            freq_str = "Months"
            x_format = mdates.DateFormatter('%B')

        fig, ax = plt.subplots(figsize=(12, 6))
        df[['proteins_total', 'carbohydrates_total', 'fat_total']].plot(
            kind='bar', stacked=True, ax=ax, title=f"Macro Consumption Over {freq_str}"
        )
        ax.set_ylabel("Consumption (g)")
        ax.set_xlabel("Date")
        ax.xaxis.set_major_formatter(x_format)
        plt.xticks(rotation=45)

        if filename_prefix:
            filename = f"{filename_prefix}_combined.png"
            plt.savefig(filename)
            plt.close(fig)
            print(f"Saved combined macro plot to {filename}")
        else:
            plt.show()

        for macro in ['proteins_total', 'carbohydrates_total', 'fat_total']:
            fig, ax = plt.subplots(figsize=(12, 6))
            df[macro].plot(kind='line', ax=ax, title=f"{macro.split('_')[0].capitalize()} Consumption Over {freq_str}")
            ax.set_ylabel("Consumption (g)")
            ax.set_xlabel("Date")
            ax.xaxis.set_major_formatter(x_format)
            plt.xticks(rotation=45)

            if filename_prefix:
                filename = f"{filename_prefix}_{macro}.png"
                plt.savefig(filename)
                plt.close(fig)
                print(f"Saved {macro} plot to {filename}")
            else:
                plt.show()

    except Exception as e:
        print(f"Error plotting macros: {e}")

def list_days_with_deviation(df, macro='proteins_total', threshold=1.5):
    try:
        df = df.drop(columns=['id'], errors='ignore')
        df['date'] = pd.to_datetime(df['date'])
        daily_macro = df.set_index('date').resample('D').sum()[macro]

        mean = daily_macro.mean()
        std_dev = daily_macro.std()

        high_deviation_days = daily_macro[daily_macro > mean + threshold * std_dev]
        low_deviation_days = daily_macro[daily_macro < mean - threshold * std_dev]

        return high_deviation_days.index.tolist(), low_deviation_days.index.tolist()
    except Exception as e:
        print(f"Error listing days with deviation for {macro}: {e}")

def weekly_macros_stats(df, month, year):

    df = df.drop(columns=['id'], errors='ignore')
    try:
        df['date'] = pd.to_datetime(df['date'])
        monthly_df = df[(df['date'].dt.month == month) & (df['date'].dt.year == year)]

        weekly_macros = monthly_df.set_index('date').resample('W').sum()[['proteins_total', 'carbohydrates_total', 'fat_total']]
        weekly_macros_df = weekly_macros.reset_index().rename(columns={'date': 'Week Start',
                                                                       'proteins_total': 'Protein (g)',
                                                                       'carbohydrates_total': 'Carbohydrates (g)',
                                                                       'fat_total': 'Fat (g)'})
        return weekly_macros_df

    except Exception as e:
        print(f"Error calculating weekly macros stats: {e}")


def top_macro_products(df, macro_column='proteins_total', top_n=5):

    try:
        top_products = df.groupby('name')[macro_column].sum().nlargest(top_n)

        total_macro = df[macro_column].sum()

        top_products_df = top_products.reset_index()
        top_products_df['Percentage'] = (top_products_df[macro_column] / total_macro * 100).round(2)

        return top_products_df
    except Exception as e:
        print(f"Error getting top products for {macro_column}: {e}")


def calorie_stats(df, month, year):

    try:
        df = df.drop(columns=['id'], errors='ignore')
        df['date'] = pd.to_datetime(df['date'])
        monthly_df = df[(df['date'].dt.month == month) & (df['date'].dt.year == year)]

        daily_calories = monthly_df.set_index('date').resample('D').sum()['energy_kcal_total']

        total_calories = daily_calories.sum()

        std_calories = daily_calories.std()

        weekly_calories = daily_calories.resample('W').sum()
        weekly_calories_df = weekly_calories.reset_index().rename(columns={'date': 'Week Start', 'energy_kcal_total': 'Calories'})

        return total_calories, std_calories, weekly_calories_df

    except Exception as e:
        print(f"Error calculating calorie stats: {e}")


def plot_calorie_consumption_over_time(df, freq='D', filename=None):
    try:
        df = df.drop(columns=['id'], errors='ignore')
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').resample(freq).sum()

        if freq == 'D':
            freq_str = "Days"
            x_format = mdates.DateFormatter('%d')
        elif freq == 'W':
            freq_str = "Weeks"
            x_format = mdates.DateFormatter('Week %U')
        else:
            freq_str = "Months"
            x_format = mdates.DateFormatter('%B')

        fig, ax = plt.subplots(figsize=(12, 6))
        df['energy_kcal_total'].plot(kind='line', ax=ax, title=f"Calorie Consumption Over {freq_str}")
        ax.set_ylabel("Calories")
        ax.set_xlabel(f"Over {freq_str}")
        ax.xaxis.set_major_formatter(x_format)
        plt.xticks(rotation=45)

        if filename:
            plt.savefig(filename)
            plt.close(fig)
            print(f"Saved plot to {filename}")
        else:
            plt.show()
    except Exception as e:
        print(f"Error plotting calorie consumption over time: {e}")


def plot_calorie_limit_bar(df, freq='D', calorie_margin=300, filename=None):
    try:
        df = df.drop(columns=['id'], errors='ignore')
        df['date'] = pd.to_datetime(df['date'])
        daily_calories = df.set_index('date').resample(freq).sum()['energy_kcal_total']

        mean_calories = daily_calories.mean()
        upper_limit = mean_calories + calorie_margin
        lower_limit = mean_calories - calorie_margin

        colors = ['green' if lower_limit <= value <= upper_limit else 'red' for value in daily_calories]

        fig, ax = plt.subplots(figsize=(12, 6))
        daily_calories.plot(kind='bar', color=colors, ax=ax, title="Daily Calorie Consumption with Limits")

        ax.axhline(mean_calories, color='blue', linestyle='-', linewidth=1, label=f'Mean ({mean_calories:.2f} kcal)')
        ax.axhline(upper_limit, color='orange', linestyle='--', linewidth=1,
                   label=f'Upper Limit ({upper_limit:.2f} kcal)')
        ax.axhline(lower_limit, color='purple', linestyle='--', linewidth=1,
                   label=f'Lower Limit ({lower_limit:.2f} kcal)')
        ax.set_ylabel("Calories")
        ax.set_xlabel("Date")
        ax.legend()
        plt.xticks(rotation=45)

        if filename:
            plt.savefig(filename)
            plt.close(fig)
            print(f"Saved plot to {filename}")
        else:
            plt.show()
    except Exception as e:
        print(f"Error plotting calorie limit bar: {e}")


def top_caloric_products(df, top_n=5):
    try:
        top_caloric = df.groupby('name')['energy_kcal_total'].sum().nlargest(top_n)
        return top_caloric
    except Exception as e:
        print(f"Error getting top caloric products: {e}")


def nutriscore_stats(df):
    try:
        nutriscore_mapping = {'a': 5, 'b': 4, 'c': 3, 'd': 2, 'e': 1}
        reverse_mapping = {v: k.upper() for k, v in nutriscore_mapping.items()}

        df['nutriscore_mapped'] = df['nutriscore'].map(nutriscore_mapping)
        average_nutriscore_numeric = round(df['nutriscore_mapped'].mean())
        average_nutriscore_letter = reverse_mapping.get(average_nutriscore_numeric, "N/A")
        products_below_c = df[df['nutriscore_mapped'] < 3].shape[0]

        return average_nutriscore_letter, products_below_c
    except Exception as e:
        print(f"Error calculating Nutri-Score stats: {e}")


def plot_nutriscore(df, filename=None):
    try:
        df['date'] = pd.to_datetime(df['date'])
        nutriscore_counts = df['nutriscore'].value_counts()
        nutriscore_counts.index = nutriscore_counts.index.str.upper()

        fig, ax = plt.subplots()
        nutriscore_counts.plot(kind='pie', autopct='%1.1f%%', title="Nutri-Score Products", ax=ax)
        plt.ylabel("")

        if filename:
            plt.savefig(filename)
            plt.close(fig)
            print(f"Saved Nutri-Score plot to {filename}")
        else:
            plt.show()
    except Exception as e:
        print(f"Error plotting Nutri-Score: {e}")
