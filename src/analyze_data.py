import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from src.utils import days_passed_in_month


def total_macros(df, preferences, month, year):
    try:
        protein_total = df['proteins_total'].sum()
        fat_total = df['fat_total'].sum()
        carbs_total = df['carbohydrates_total'].sum()

        days_passed = days_passed_in_month(month, year)

        if days_passed > 0:
            protein_daily_deviation = (protein_total - preferences.protein_threshold) / days_passed
            fat_daily_deviation = (fat_total - preferences.fat_threshold) / days_passed
            carbs_daily_deviation = (carbs_total - preferences.carbon_threshold) / days_passed
        else:
            protein_daily_deviation = 0
            fat_daily_deviation = 0
            carbs_daily_deviation = 0
        return protein_total, protein_daily_deviation, fat_total, fat_daily_deviation, carbs_total, carbs_daily_deviation
    except Exception as e:
        print(f"Error calculating total macros: {e}")


def plot_macros(df, preferences, freq='D', filename_prefix=""):
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
            if macro == 'proteins_total':
                threshold = preferences.protein_threshold
            elif macro == 'carbohydrates_total':
                threshold = preferences.carbon_threshold
            elif macro == 'fat_total':
                threshold = preferences.fat_threshold

            upper_limit = threshold * 1.1
            lower_limit = threshold * 0.9

            colors = ['green' if lower_limit <= value <= upper_limit else 'red' for value in df[macro]]

            fig, ax = plt.subplots(figsize=(12, 6))
            df[macro].plot(
                kind='bar',
                color=colors,
                ax=ax,
                title=f"{macro.split('_')[0].capitalize()} Consumption Over {freq_str}"
            )

            ax.axhline(threshold, color='green', linestyle='-', linewidth=2, label=f'Threshold ({threshold:.2f} g)')
            ax.axhline(upper_limit, color='red', linestyle='--', linewidth=1,
                       label=f'Upper Limit ({upper_limit:.2f} g)')
            ax.axhline(lower_limit, color='red', linestyle='--', linewidth=1,
                       label=f'Lower Limit ({lower_limit:.2f} g)')

            ax.set_ylabel("Consumption (g)")
            ax.set_xlabel("Date")
            ax.xaxis.set_major_formatter(x_format)
            ax.legend()
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
    if macro_column == 'protein_total':
        macro_column = 'proteins_total'
    try:
        top_products = df.groupby('name')[macro_column].sum().nlargest(top_n)

        total_macro = df[macro_column].sum()

        top_products_df = top_products.reset_index()
        top_products_df['Percentage'] = (top_products_df[macro_column] / total_macro * 100).round(2)

        return top_products_df
    except Exception as e:
        print(f"Error getting top products for {macro_column}: {e}")


def calorie_stats(df, preferences, month, year):

    try:
        df = df.drop(columns=['id'], errors='ignore')
        df['date'] = pd.to_datetime(df['date'])
        monthly_df = df[(df['date'].dt.month == month) & (df['date'].dt.year == year)]

        daily_calories = monthly_df.set_index('date').resample('D').sum()['energy_kcal_total']

        total_calories = daily_calories.sum()

        std_calories = daily_calories.std()

        days_passed = days_passed_in_month(month, year)

        if days_passed > 0:
            daily_calorie_deviation = (total_calories - preferences.calorie_threshold) / days_passed
        else:
            daily_calorie_deviation = 0

        weekly_calories = daily_calories.resample('W').sum()
        weekly_calories_df = weekly_calories.reset_index().rename(columns={'date': 'Week Start', 'energy_kcal_total': 'Calories'})

        return total_calories, std_calories, daily_calorie_deviation, weekly_calories_df

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
        df['energy_kcal_total'].plot(kind='bar', ax=ax, title=f"Calorie Consumption Over {freq_str}")
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



def plot_calorie_limit_bar(df, preferences, freq='D', filename=None):
    try:
        df = df.drop(columns=['id'], errors='ignore')
        df['date'] = pd.to_datetime(df['date'])
        daily_calories = df.set_index('date').resample(freq).sum()['energy_kcal_total']

        threshold = preferences.calorie_threshold
        upper_limit = threshold * 1.1
        lower_limit = threshold * 0.9

        colors = ['green' if lower_limit <= value <= upper_limit else 'red' for value in daily_calories]

        fig, ax = plt.subplots(figsize=(12, 6))
        daily_calories.plot(kind='bar', color=colors, ax=ax, title="Daily Calorie Consumption with Limits")

        ax.axhline(threshold, color='green', linestyle='-', linewidth=2, label=f'Threshold ({threshold:.2f} kcal)')
        ax.axhline(upper_limit, color='red', linestyle='--', linewidth=1,
                   label=f'Upper Limit ({upper_limit:.2f} kcal)')
        ax.axhline(lower_limit, color='red', linestyle='--', linewidth=1,
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


def generate_dietary_advice(df, preferences, month, year):
    df = df.drop(columns=['id'], errors='ignore')
    try:
        total_calories, std_calories, daily_calorie_deviation, _ = calorie_stats(df, preferences, month, year)
        daily_calories = df.set_index('date').resample('D').sum()['energy_kcal_total']

        calorie_exceed_days = daily_calories[daily_calories > preferences.calorie_threshold * 1.1].count()
        calorie_shortage_days = daily_calories[daily_calories < preferences.calorie_threshold * 0.9].count()
        avg_calorie_percentage = ((daily_calories.mean() / preferences.calorie_threshold) - 1) * 100

        if daily_calorie_deviation > 0:
            top_caloric_product = top_caloric_products(df, top_n=1).index[0]
            calorie_suggestion = (
                f"You consumed too many calories on average ({daily_calorie_deviation:.2f} kcal/day over the limit). "
                f"Consider reducing or avoiding {top_caloric_product}."
            )
        elif daily_calorie_deviation < 0:
            top_caloric_product = top_caloric_products(df, top_n=1).index[0]
            calorie_suggestion = (
                f"You consumed too few calories on average ({abs(daily_calorie_deviation):.2f} kcal/day below the limit). "
                f"Consider adding more {top_caloric_product} or similar high-calorie foods to your diet."
            )
        else:
            calorie_suggestion = "Your caloric intake is within the recommended limits."

        calorie_advice = (
            f"In {month}-{year}, you exceeded your daily caloric limit {calorie_exceed_days} times. You had caloric shortage on {calorie_shortage_days} days. "
            f"On average, you consumed {avg_calorie_percentage:.1f}% {'more' if avg_calorie_percentage > 0 else 'less'} calories than your daily threshold. "
            + calorie_suggestion
        )

        protein_total, protein_daily_deviation, fat_total, fat_daily_deviation, carbs_total, carbs_daily_deviation = total_macros(
            df, preferences, month, year
        )

        macro_daily_deviations = {
            'Protein': protein_daily_deviation,
            'Fat': fat_daily_deviation,
            'Carbohydrates': carbs_daily_deviation,
        }

        macro_advice = ""
        for macro, deviation in macro_daily_deviations.items():
            if deviation > 0:
                top_product = top_macro_products(df, macro_column=f"{macro.lower()}_total").iloc[0]['name']
                macro_advice += (
                    f"You consumed too much {macro.lower()} on average ({deviation:.2f}g/day over the limit). "
                    f"Consider reducing your intake of {top_product}." + "\n")
            elif deviation < 0:
                macro_advice += (
                    f"You consumed too little {macro.lower()} on average ({abs(deviation):.2f}g/day below the limit). "
                    f"Consider including more sources of {macro.lower()} in your diet." + "\n")

        total_macros_sum = protein_total + fat_total + carbs_total
        carb_ratio = (carbs_total / total_macros_sum) * 100 if total_macros_sum else 0
        protein_ratio = (protein_total / total_macros_sum) * 100 if total_macros_sum else 0
        fat_ratio = (fat_total / total_macros_sum) * 100 if total_macros_sum else 0

        balance_advice = (
            f"Your macronutrient balance was {carb_ratio:.1f}% carbohydrates, {protein_ratio:.1f}% protein, and {fat_ratio:.1f}% fat. "
            "Ideally, your diet should consist of approximately 50% carbohydrates, 25% protein, and 25% fat. "
        )

        return calorie_advice + "\n" + macro_advice + balance_advice

    except Exception as e:
        return f"Error generating dietary advice: {e}"

